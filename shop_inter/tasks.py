from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from shop_app import settings
from .models import User
@shared_task(bind=True)
def new_order_func(self,user_id):
    user = User.objects.get(id=user_id)
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

@shared_task(bind=True)
def new_order_shop(self, user_id, id):
    user = User.objects.get(id=user_id)
    mail_subject=f"Обновление статуса заказа за номером {id}"
    message="вашем магазине размещен заказ"
    to_email=user.email
    send_mail(
        subject= mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=True,
    )
    return "Done"