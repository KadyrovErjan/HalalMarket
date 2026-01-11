import random
from django.core.mail import send_mail
from django.conf import settings


def send_seller_verification_code(user):
    """
    Отправляет 6-значный код подтверждения на email продавцу.
    """
    code = random.randint(100000, 999999)  # 6-значный код

    # Сохраняем код в профиль пользователя
    user.verification_code = str(code)
    user.save(update_fields=["verification_code"])

    send_mail(
        subject="Подтверждение регистрации продавца",
        message=f"Ваш код подтверждения: {code}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[user.email],
        fail_silently=False,
    )

    return code