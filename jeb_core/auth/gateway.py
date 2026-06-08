import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)
BASE_URL = "https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/"

def sendVerificationMessage(phone_number):
    cooldown_key = f"auth_cooldown_{phone_number}"
    attemps_key = f"auth_attemps_{phone_number}"
    ban_key = f"auth_ban_{phone_number}"
    
    if cache.get(cooldown_key):
        logger.error(f'{phone_number} превышения запросов в минуту')
        return{
            'status' : "error" , 
            'message' : 'Повторная отправка возможна через 1 минуту.'
        }
    attemps = cache.get(attemps_key,0)
    if attemps >= 3: 
        cache.set(ban_key, True, timeout=86400)
        cache.delete(attemps_key)
        
        logger.error(f'Превышен лимит попыток. Номер {phone_number} заблокирован на 24 часа.')
        return {
            'status': "error",
            'message': 'Превышено максимальное количество попыток. Отправка заблокирована на 24 часа.'
        }
    payload = {
        'public_key' : settings.ZVONOK_PK,
        'campaign_id' : settings.ZVONOK_CAMPAIGN_ID,
        'phone' : str(phone_number),
    }

    try:
        response = requests.post(BASE_URL, data=payload, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('status') == 'ok':
                gen_code = res_data.get('pincode') or res_data.get('data', {}).get('pincode')
                if gen_code:
                    cache.set(cooldown_key, True, timeout=57)
                    cache.set(attemps_key, attemps+1,timeout=3600)
                    cache.set(f"valid_code_for_{phone_number}", str(gen_code), timeout=300)
                    
                    logger.info(f"Flash Call успешно создан. Сервер выдал код для {phone_number}")
                    return {
                        'status' : "success",
                        'request_id' : str(phone_number)
                    }
        return {"status": "error", "message": "Ошибка на стороне сервера отправки."}
    except Exception as e:
        logger.error(f"Сбой при отправке кода: {e}")
        return {"status": "error",
                "message": "Не удалось установить соединение с сервером."
                }
    
def checkVerificationStatus(phone_number, user_code):
    try:
        cache_key = f"valid_code_for_{phone_number}"
        saved_code = cache.get(cache_key)
        

        if saved_code and str(saved_code) == str(user_code):
            cache.delete(cache_key)  
            return True
            
        return False
    except Exception as e:
        logger.error(f'Сбой при проверке кода: {e}')
        return False