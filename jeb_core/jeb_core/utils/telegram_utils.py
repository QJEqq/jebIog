import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolvePhoneRequest
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramPhoneChecker:
    def __init__(self):
        self.api_id = settings.TELEGRAM_API_ID
        self.api_hash = settings.TELEGRAM_API_HASH
        self.session_name = 'jeb_telegram_session'  # Уникальное имя для твоего проекта
        self.client = None
    
    async def find_telegram_id_by_phone(self, phone_number):
        
        try:
            if not self.client:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
                await self.client.start()
            
            clean_phone = self._clean_phone_number(str(phone_number))
            
            result = await self.client(ResolvePhoneRequest(phone=clean_phone))
            
            if result and result.users:
                user = result.users[0]
                return {
                    'found': True,
                    'tg_id': str(user.id),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            else:
                return {'found': False}
                
        except Exception as e:
            logger.error(f"Ошибка при поиске Telegram ID: {e}")
            return {'found': False, 'error': str(e)}
    
    def _clean_phone_number(self, phone):
        
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) == 10:
            return f'+7{digits}'
        elif len(digits) == 11 and digits.startswith('7'):
            return f'+{digits}'
        elif len(digits) == 11 and digits.startswith('8'):
            return f'+7{digits[1:]}'
        else:
            return f'+{digits}'
    
    async def close(self):
        if self.client:
            await self.client.disconnect()

def get_telegram_id(phone_number):
    checker = TelegramPhoneChecker()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(checker.find_telegram_id_by_phone(phone_number))
        return result
    finally:
        loop.run_until_complete(checker.close())
        loop.close()