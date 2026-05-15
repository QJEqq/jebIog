from django import forms
from django.utils.html import strip_tags
from users.forms import COMMON_ATTRS
from phonenumber_field.formfields import PhoneNumberField
from .models import Order
class OrderForm(forms.ModelForm):

    phone_number = PhoneNumberField(
        required=True,
        region='RU',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': '8 (___) ___-__-__', 
            'id': 'phone-mask'})

    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Ваше Имя'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Ваша Фамилия'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Почта'})
    )


    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Город'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Город'})
    )
    postal_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Город'})
    )
    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')
        # Убираем лишние пробелы по краям и капитализируем (Иван вместо иван)
        return data.strip().capitalize()

    def clean_postal_code(self):
        code = self.cleaned_data.get('postal_code')
        # Проверяем, что в индексе только цифры и их ровно 6 (для РФ)
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Введите корректный почтовый индекс (6 цифр).")
        return code
    class Meta:
        model = Order
        # Перечисли все поля, которые у тебя есть в модели Order
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'postal_code']

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            field_mapping = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone_number': user.phone_number,

                'city': getattr(user, 'city', ''),
                'address': getattr(user, 'address', ''),
                'postal_code': getattr(user, 'postal_code', ''),
            }
            for field, value in field_mapping.items():
                if value:
                    self.fields[field].initial = value

    
    
    