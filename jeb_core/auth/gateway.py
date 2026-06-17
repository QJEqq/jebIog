import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)
BASE_URL = "https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/"

def sendVerificationMessage(phone_number):
    # Принудительно приводим номер к единой строке
    if hasattr(phone_number, 'as_e164'):
        phone_str = phone_number.as_e164
    else:
        phone_str = str(phone_number).strip()

    cooldown_key = f"auth_cooldown_{phone_str}"
    attemps_key = f"auth_attemps_{phone_str}"
    ban_key = f"auth_ban_{phone_str}"

    if cache.get(f"valid_code_for_{phone_str}"):
        cache.delete(f"valid_code_for_{phone_str}")

    if cache.get(cooldown_key):
        logger.error(f'{phone_str} превышения запросов в минуту')
        return {
            'status': "error",
            'message': 'Повторная отправка возможна через 1 минуту.'
        }

    attemps = cache.get(attemps_key, 0)
    if attemps >= 3:
        cache.set(ban_key, True, timeout=86400)
        cache.delete(attemps_key)

        logger.error(f'Превышен лимит попыток. Номер {phone_str} заблокирован на 24 часа.')
        return {
            'status': "error",
            'message': 'Превышено максимальное количество попыток. Отправка заблокирована на 24 часа.'
        }

    payload = {
        'public_key': settings.ZVONOK_PK,
        'campaign_id': settings.ZVONOK_CAMPAIGN_ID,
        'phone': phone_str,
    }

    try:
        response = requests.post(BASE_URL, data=payload, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('status') == 'ok':
                gen_code = res_data.get('pincode') or res_data.get('data', {}).get('pincode')
                if gen_code:
                    cache.set(cooldown_key, True, timeout=57)
                    cache.set(attemps_key, attemps + 1, timeout=3600)

                    # Пишем строго по нормализованному ключу
                    cache.set(f"valid_code_for_{phone_str}", str(gen_code), timeout=300)

                    logger.info(f"Flash Call успешно создан. Сервер выдал код для {phone_str}")
                    return {
                        'status': "success",
                        'request_id': phone_str
                    }
        return {"status": "error", "message": "Ошибка на стороне сервера отправки."}
    except Exception as e:
        logger.error(f"Сбой при отправке кода: {e}")
        return {
            "status": "error",
            "message": "Не удалось установить соединение с сервером."
        }

def checkVerificationStatus(phone_number, user_code):
    try:
        if hasattr(phone_number, 'as_e164'):
            phone_str = phone_number.as_e164
        else:
            phone_str = str(phone_number).strip()

        cache_key = f"valid_code_for_{phone_str}"
        saved_code = cache.get(cache_key)

        logger.info(f"Дебаг верификации: ключ={cache_key}, из_кэша={saved_code}, ввод={user_code}")

        if saved_code and str(saved_code).strip() == str(user_code).strip():
            cache.delete(cache_key)
            return True

        return False
    except Exception as e:
        logger.error(f'Сбой при проверке кода: {e}')
        return False