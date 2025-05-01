import razorpay
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import ServiceRequest, ServicePaymentInfo
from Tara.settings.default import RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET
import hmac, hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ServicePaymentInfo, ServiceRequest, ServicePlan
import json
from rest_framework.permissions import AllowAny

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_razorpay_order_for_services(request):
    service_request_id = request.data.get('service_request_id')
    plan_id = request.data.get('plan_id')

    if not all([service_request_id, plan_id]):
        return Response({"error": "Both service_request_id and plan_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(id=service_request_id, user=request.user)

        if service_request.status != 'initiated':
            return Response({"error": "Payment not allowed. Service already processed."},
                            status=status.HTTP_400_BAD_REQUEST)

        plan = ServicePlan.objects.get(id=plan_id)

        if plan.service.id != service_request.service.id:
            return Response({"error": "Selected plan does not belong to the requested service."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update plan selection
        service_request.plan = plan
        service_request.save()

        amount = int(plan.price * 100)  # Amount in paisa

        # ✅ Step 1: Mark previous orders as not latest
        ServicePaymentInfo.objects.filter(
            service_request=service_request,
            status='initiated',
            captured=False,
            is_latest=True
        ).update(is_latest=False)

        # ✅ Step 2: Create a new Razorpay order
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        # ✅ Step 3: Save new payment info
        ServicePaymentInfo.objects.create(
            user=request.user,
            service_request=service_request,
            plan=plan,
            amount=plan.price,
            razorpay_order_id=razorpay_order['id'],
            status='initiated',
            is_latest=True
        )

        return Response({
            "message": "Razorpay order created successfully.",
            "order_id": razorpay_order['id'],
            "amount": amount,
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID
        }, status=status.HTTP_200_OK)

    except ServiceRequest.DoesNotExist:
        return Response({"error": "ServiceRequest not found."}, status=status.HTTP_404_NOT_FOUND)
    except ServicePlan.DoesNotExist:
        return Response({"error": "ServicePlan not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Failed to create Razorpay order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def service_razorpay_webhook(request):
    try:
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        received_sig = request.headers.get('X-Razorpay-Signature')
        generated_sig = hmac.new(
            webhook_secret.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(received_sig, generated_sig):
            data = json.loads(request.body)
            if data['event'] == 'payment.captured':
                payment_id = data['payload']['payment']['entity']['id']
                order_id = data['payload']['payment']['entity']['order_id']
                method = data['payload']['payment']['entity']['method']

                payment = ServicePaymentInfo.objects.get(razorpay_order_id=order_id)
                payment.mark_as_captured(payment_id, method)

                service_request = payment.service_request
                service_request.status = 'paid'
                service_request.save()

            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'error': 'Signature mismatch'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

