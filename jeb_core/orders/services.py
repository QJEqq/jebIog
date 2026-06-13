import logging 
from yookassa import Configuration, Payment
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)
def create_cryptocloud_payment(order):
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    idempotence_key = str(uuid.uuid4())
    try:
        payment_data = {
            'amount' : {
                "value": str(order.total_price),
                "currency": "RUB"
            },
            'confirmation' : {
                'type': "redirect",
                'return_url': f"https://jebperformance.space/orders/payment/check/?order_id={order.id}"
            },
            'capture': True,
            'description': f"Оплата заказа №{order.id} | JEB",
            'metadata': {
                "order_id": order.id
            }
        }
        payment_response = Payment.create(payment_data, idempotence_key)

        order.yookassa_payment_id = payment_response.id
        order.save()
        return payment_response.confirmation.confirmation_url
    except Exception as e:
        logger.error(f'Yookassa API Error для заказа {order.id} : {e}')
        return None