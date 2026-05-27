from django import forms
from django.utils.html import strip_tags
from users.forms import COMMON_ATTRS
from phonenumber_field.formfields import PhoneNumberField
from .models import RepairRequest
class RepairForm(forms.ModelForm):

    DEVICE_CHOICES = [
        ('pc', 'Стационарный ПК'),
        ('laptop', 'Ноутбук'),
        ('gpu', 'Видеокарта'),
        ('other', 'Другое железо'),
    ]

    client_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Ваше Имя'})
    )

    phone_number = PhoneNumberField(
        required=True,
        region='RU',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': '8 (___) ___-__-__', 'id': 'phone-mask'})
    )

    
    device_type = forms.ChoiceField(
        required=True,
        choices=DEVICE_CHOICES,
        widget=forms.Select(attrs={**COMMON_ATTRS, 'class': COMMON_ATTRS['class'] + ' cursor-pointer'})
    )

   
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            **COMMON_ATTRS, 
            'placeholder': 'Опишите проблему (например: не включается, артефакты на экране, нужна чистка...)',
            'rows': 4  
        })
    )

    
    image = forms.ImageField(
        required=False,  
        widget=forms.FileInput(attrs={
            'class': 'w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-600/10 file:text-blue-400 hover:file:bg-blue-600/20 file:transition cursor-pointer'
        })
    )
    
    def clean_client_name(self):
        data = self.cleaned_data.get('client_name')
        return data.strip().capitalize()
    
    def clean_description(self):
        data = self.cleaned_data.get('description')
        if data:
            return strip_tags(data).strip()
        return data
    def clean_client_phone(self):
        data = self.cleaned_data.get('client_phone')

        if data:
            phone_str = str(data)
            cleaned_digits = ''.join(c for c in phone_str if c.isdigit())

            if cleaned_digits.startswith('8'):
                cleaned_digits = '+7' + cleaned_digits[1:]
            elif not cleaned_digits.startswith('+') and cleaned_digits.startswith('7'):
                cleaned_digits = '+' + cleaned_digits
                
            return cleaned_digits
        return data
    
    class Meta:
        model = RepairRequest
        
        fields = ['phone_number', 'client_name', 'device_type', 'description', 'image']

    def __init__(self,   *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            field_mapping = {
                'client_name': user.last_name,
                'phone_number': user.phone_number.national_number,
            }
            for field, value in field_mapping.items():
                if value:
                    self.fields[field].initial = value

    
    
    