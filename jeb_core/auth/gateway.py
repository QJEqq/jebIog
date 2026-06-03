import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
BASE_URL = "https://gatewayapi.telegram.org"

def get_headers():
    token = settings.TELEGRAM_TOKEN
    return {
        "Authorization" : f"Bearer {token}",
        "Content-type" : "application/json"
    }

def sendVerificationMessage(phone_number):
    url = f"{BASE_URL}/sendVerificationMessage"
    payload = {
        'phone_number' : phone_number,
        'code_length' : 4,
        "ttl" : 600
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers(), timeout=5)
        res_data = response.json()

        if res_data.get('ok'):
            request_id = res_data.get("result", {}).get("request_id")
            return request_id
    except Exception as e:
        logger.error(f"Сбой при отправке кода: {e}")
        return None
    
def checkVerificationStatus(request_id, user_code):
    url = f"{BASE_URL}/checkVerificationStatus"
    payload = {
        "request_id" : request_id,
        "code": user_code
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers(),timeout=5)
        res_data = response.json()

        if res_data.get("ok"):
            status = res_data.get("result", {}).get("verification_status", {}).get("status")
            if status == 'code_valid':
                return True
        return False
    except Exception as e:
        logger.error(f'Сбой при проверке кода: {e}')
        return False