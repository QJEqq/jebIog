import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

def send_telegram(object):
    TOKEN = settings.TELEGRAM_TOKEN
    CHAT_ID = settings.CHAT_ID
    PROXY = settings.TELEGRAM_PROXY

    proxies = None
    if PROXY:
        proxies = {
            'http' : PROXY,
            'https' : PROXY
        }
    type_send = object.__class__.__name__

    if type_send == 'Order':
        message = (
            "🔔 <b>Новый заказ на сайте JEB!</b>\n\n"
            f"Номер заказа: <code>#{object.id}</code>\n"
            f"Сумма оплаты: <b>{object.total_price} руб.</b>\n"
            f"Статус: Оплачен через ЮKassa ID <b>{object.yookassa_payment_id} руб.</b>\n\n"
            "<a href='https://jebperfomance.space/admin/'>Зайти в админку</a>"
        )
    elif type_send == 'RepairRequest':
        message = (
            "🛠️ <b>Новая заявка на ремонт / сборку!</b>\n\n"
            f"ID заявки: <code>#{object.id}</code>\n"
            f"Клиент: <b>{object.client_name}</b>\n"
            f"Телефон: <code>{object.phone_number}</code>\n"
            f"Что нужно сделать: <i>{object.description}</i>\n\n"
            "<a href='https://jebperfomance.space/admin/'>Открыть админку</a>"
        )

    else:
        logger.warning(f"Передан неизвестный тип объекта в send_telegram: {type_send}")
        return 
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "message_thread_id": 22893,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, proxies=proxies, timeout=5)
        if response.status_code != 200:
            logger.error(f"Ошибка ТГ API: {response.text}")
    except Exception as e:
        logger.error(f"Не удалось связаться с Telegram через прокси: {e}")

    
