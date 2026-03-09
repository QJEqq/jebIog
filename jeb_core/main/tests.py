# main/tests.py
from django.test import TestCase
from unittest.mock import patch, MagicMock, AsyncMock
from main.models import Client
from phonenumber_field.phonenumber import PhoneNumber

class ClientModelTest(TestCase):
    """Тесты для модели Client"""
    
    def setUp(self):
        self.client_data = {
            'name': 'Иван Петров',
            'phone_number': PhoneNumber.from_string('+79991234567', region='RU'),
            'email': 'ivan@example.com',
        }
    
    @patch('main.models.get_telegram_id')  # Мокаем функцию поиска Telegram
    def test_create_client_without_telegram(self, mock_get_telegram):
        """Тест создания клиента без реального обращения к Telegram"""
        # Настраиваем мок
        mock_get_telegram.return_value = {'found': False}
        
        # Создаем клиента
        client = Client.objects.create(**self.client_data)
        
        # Проверяем
        self.assertEqual(client.name, 'Иван Петров')
        self.assertEqual(str(client.phone_number), '+79991234567')
        mock_get_telegram.assert_called_once()  # Убеждаемся, что функция вызывалась
        
    @patch('main.models.get_telegram_id')
    def test_create_client_with_telegram_found(self, mock_get_telegram):
        """Тест создания клиента, когда Telegram ID найден"""
        # Настраиваем мок на успешный поиск
        mock_get_telegram.return_value = {
            'found': True,
            'tg_id': '123456789',
            'username': 'ivan_test'
        }
        
        client = Client.objects.create(**self.client_data)
        
        self.assertEqual(client.tg_id, '123456789')
        mock_get_telegram.assert_called_once()