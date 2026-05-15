import logging 

logger = logging.getLogger(__name__)
def create_cryptocloud_payment(order):
    """
    Функция-заглушка для связи с CryptoCloud.
    Когда получишь ключи, наполнишь её реальным requests.post
    """
    # URL для создания счета (инвойса)
    url = "https://api.cryptocloud.plus/v2/invoice/create"
    
    # Эти данные ты получишь в личном кабинете CryptoCloud
    # Пока мы просто возвращаем None или тестовую ссылку
    try:
        # Пример того, как это будет выглядеть:
        # payload = {
        #     "shop_id": "ТВОЙ_ID",
        #     "amount": float(order.total_price),
        #     "order_id": str(order.id),
        #     "currency": "RUB"
        # }
        # headers = {"Authorization": f"Token {settings.CRYPTOCLOUD_API_KEY}"}
        # response = requests.post(url, json=payload, headers=headers, timeout=10)
        # return response.json().get('result', {}).get('link')
        
        # ВРЕМЕННАЯ ТЕСТОВАЯ ССЫЛКА (чтобы проверить редирект)
        return "https://cryptocloud.plus/success_test" 
    except Exception as e:
        logger.error(f"CryptoCloud API error: {e}")
        return None