import random
from .models import SMSCode

def send_verification_code(user):
    code = str(random.randint(1000,9999))

    SMSCode.objects.filter(user=user).delete()
    SMSCode.objects.create(user=user, code=code)

    print("\n" + "="*30)
    return code
    