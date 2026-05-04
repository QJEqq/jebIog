from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model , authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()

COMMON_ATTRS = {
    'class' : 'dotted-input'
}

class CustomUserCreationForm(UserCreationForm):
    phone_number = PhoneNumberField(
        required=True,
        region='RU',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Номер телефона'})

    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Почта'})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Ваше Имя'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Ваше Имя'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Придумайте пароль'})
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Повторите пароль'})
    )

    class Meta(UserCreationForm._meta):
        model = User
        fields = ('phone_number', 'email', 'first_name')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('Данный номер уже занят!')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit: 
            user.save()
        return user
    
class CustomUserAuthForm(AuthenticationForm):
    username = forms.CharField(
        label = 'Номер телефона',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Номер телефона'})

    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Придумайте пароль'})
    )

    def clean(self):
        phone_number = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if phone_number and password :
            self.user_cache = authenticate(self.request, phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный номер телефона или пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт больше не активен.')
        return self.cleaned_data
    
class CustomUserUpdateForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        required=False,
        region='RU',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Номер телефона'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Ваше Имя'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Ваша Фамилия'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={**COMMON_ATTRS, 'placeholder': 'Почта'})
    )

    class Meta:
        model = User
       
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 
            'company', 'address1', 'address2', 'city', 
            'country', 'province', 'postal_code'
        )
        
        widgets = {
            'company': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Компания'}),
            'address1': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Адрес (строка 1)'}),
            'address2': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Адрес (строка 2)'}),
            'city': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Город'}),
            'country': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Страна'}),
            'province': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Область / Регион'}),
            'postal_code': forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder': 'Почтовый индекс'}),
        }

    def clean_email(self):
        
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Данная почта уже используется другим аккаунтом.')
        return email

    def clean_phone_number(self):
        
        phone = self.cleaned_data.get('phone_number')
        if phone:
            if User.objects.filter(phone_number=phone).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Данный номер телефона уже привязан к другому аккаунту.')
        return phone

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email

        text_fields = [
            'company', 'address1', 'address2', 'city', 
            'country', 'province', 'postal_code'
        ]
        for field in text_fields:
            value = cleaned_data.get(field)
            if value:
                cleaned_data[field] = strip_tags(value)

        return cleaned_data
