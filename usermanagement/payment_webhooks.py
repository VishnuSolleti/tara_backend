# views.py

import hmac
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import PaymentInfo


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """Handle Razorpay Webhook Safely."""
    try:
        # Step 1: Parse payload
        webhook_body = request.body
        webhook_data = json.loads(webhook_body)

        print("Webhook Received:", webhook_data)  # (For Debugging)

        # Step 2: Verify Razorpay signature
        webhook_secret = "TaraFirst@2025"  # You must set this in Razorpay settings + Django settings

        received_signature = request.headers.get('X-Razorpay-Signature')
        print(received_signature)
        generated_signature = hmac.new(
            webhook_secret.encode(),
            webhook_body,
            hashlib.sha256
        ).hexdigest()
        print(generated_signature)
        if received_signature != generated_signature:
            return Response({'error': 'Invalid Signature'}, status=400)

        print("signature Verified")

        # Step 3: Handle webhook events
        event = webhook_data.get('event')
        print(event)
        if event == 'payment.captured':
            payment_entity = webhook_data['payload']['payment']['entity']

            razorpay_payment_id = payment_entity['id']
            razorpay_order_id = payment_entity['order_id']


            # Find PaymentIntent and update
            try:
                payment_intent = PaymentInfo.objects.get(razorpay_order_id=razorpay_order_id)

                payment_intent.status = 'paid'
                payment_intent.razorpay_payment_id = razorpay_payment_id
                print(payment_intent)

                if payment_intent.amount and not isinstance(payment_intent.amount, Decimal):
                    try:
                        payment_intent.amount = Decimal(str(payment_intent.amount))
                    except Exception as e:
                        print(f"Amount correction failed: {e}")

                payment_intent.save()

                # Optionally: Here you can trigger ModuleSubscription creation (if you want via webhook auto)

                return Response({'status': 'Payment Captured & Updated'})

            except PaymentInfo.DoesNotExist:
                return Response({'error': 'PaymentIntent not found'}, status=404)

        elif event == 'payment.failed':
            payment_entity = webhook_data['payload']['payment']['entity']

            razorpay_order_id = payment_entity['order_id']
            failure_reason = payment_entity.get('error_description', 'Unknown')

            try:
                payment_intent = PaymentInfo.objects.get(razorpay_order_id=razorpay_order_id)

                payment_intent.status = 'failed'
                payment_intent.failure_reason = failure_reason
                payment_intent.save()

                return Response({'status': 'Payment Failed & Updated'})

            except PaymentInfo.DoesNotExist:
                return Response({'error': 'PaymentIntent not found'}, status=404)

        else:
            # For now, ignore other events
            return Response({'status': f'Unhandled event {event}'})

    except Exception as e:
        print('Webhook Error:', str(e))
        return Response({'error': str(e)}, status=500)
