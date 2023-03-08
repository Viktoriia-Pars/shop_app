from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from shop_app import settings
from .models import User
@shared_task(bind=True)
@staticmethod
def new_order_func(user_id, **kwargs):
    user = User.objects.get(id=user_id)
    #operations
    # users = get_user_model().objects.all()
    # for user in users:
    mail_subject=f"Обновление статуса заказа"
    message="Заказ сформирован"
    to_email=user.email
    send_mail(
        subject= mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=True,
    )
    return "Done"