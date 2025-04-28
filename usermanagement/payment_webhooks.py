# webhook.py (or inside views.py if you want)
import razorpay
import hmac
import hashlib
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import PaymentInfo, ModuleSubscription, SubscriptionCycle
from django.utils import timezone
from datetime import timedelta
from Tara.settings.default import RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET))


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay Webhook Events"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    webhook_secret = "TaraFirst@2025"
    received_signature = request.headers.get('X-Razorpay-Signature')
    body = request.body.decode('utf-8')

    # Verify Razorpay Webhook Signature
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if received_signature != expected_signature:
        return JsonResponse({'error': 'Invalid webhook signature'}, status=400)

    payload = json.loads(body)
    event = payload.get('event')

    if event == 'payment.captured':
        # Successful Payment
        payment_entity = payload['payload']['payment']['entity']
        razorpay_order_id = payment_entity.get('order_id')
        razorpay_payment_id = payment_entity.get('id')
        payment_method = payment_entity.get('method')
        card_last4 = payment_entity.get('card', {}).get('last4') if payment_method == 'card' else None

        try:
            payment_info = PaymentInfo.objects.get(razorpay_order_id=razorpay_order_id)

            if payment_info.status != 'paid':  # If already paid by verify-payment, ignore
                payment_info.status = 'paid'
                payment_info.razorpay_payment_id = razorpay_payment_id
                payment_info.payment_method = payment_method
                payment_info.card_last4 = card_last4
                payment_info.payment_captured = True
                payment_info.save()

                # (Optional) You can now trigger ModuleSubscription creation here too if you want

            return JsonResponse({'status': 'Payment processed successfully.'})

        except PaymentInfo.DoesNotExist:
            return JsonResponse({'error': 'PaymentInfo not found'}, status=404)

    else:
        return JsonResponse({'status': f'Unhandled event {event}'})

    return JsonResponse({'status': 'Webhook received'})
