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
import logging

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_CLIENT_ID, RAZORPAY_CLIENT_SECRET))

# Setup Django logger
logger = logging.getLogger(__name__)


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay Webhook Events with Logging"""
    logger.info("=== Razorpay Webhook HIT ===")

    if request.method != 'POST':
        logger.warning("Webhook received wrong HTTP method: %s", request.method)
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        webhook_secret = "TaraFirst@2025"
        received_signature = request.headers.get('X-Razorpay-Signature')
        body = request.body.decode('utf-8')

        logger.info("Webhook body: %s", body)
        logger.info("Received Signature: %s", received_signature)

        # Verify Razorpay Webhook Signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        logger.info("Expected Signature: %s", expected_signature)

        if received_signature != expected_signature:
            logger.error("Invalid webhook signature detected!")
            return JsonResponse({'error': 'Invalid webhook signature'}, status=400)

        payload = json.loads(body)
        event = payload.get('event')

        logger.info("Webhook event received: %s", event)

        if event == 'payment.captured':
            payment_entity = payload['payload']['payment']['entity']
            razorpay_order_id = payment_entity.get('order_id')
            razorpay_payment_id = payment_entity.get('id')
            payment_method = payment_entity.get('method')
            card_last4 = payment_entity.get('card', {}).get('last4') if payment_method == 'card' else None

            logger.info("Payment Captured for Order ID: %s, Payment ID: %s", razorpay_order_id, razorpay_payment_id)

            try:
                payment_info = PaymentInfo.objects.get(razorpay_order_id=razorpay_order_id)

                if payment_info.status != 'paid':
                    logger.info("Updating PaymentInfo to paid for Order ID: %s", razorpay_order_id)
                    payment_info.status = 'paid'
                    payment_info.razorpay_payment_id = razorpay_payment_id
                    payment_info.payment_method = payment_method
                    payment_info.card_last4 = card_last4
                    payment_info.payment_captured = True
                    payment_info.save()

                else:
                    logger.info("PaymentInfo already marked as paid. Skipping update.")

                return JsonResponse({'status': 'Payment processed successfully.'})

            except PaymentInfo.DoesNotExist:
                logger.error("PaymentInfo not found for Order ID: %s", razorpay_order_id)
                return JsonResponse({'error': 'PaymentInfo not found'}, status=404)

        else:
            logger.warning("Unhandled webhook event received: %s", event)
            return JsonResponse({'status': f'Unhandled event {event}'})

    except Exception as e:
        logger.exception("Exception occurred during webhook processing!")
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'status': 'Webhook received'})
