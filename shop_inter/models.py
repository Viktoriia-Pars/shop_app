from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_rest_passwordreset.tokens import get_token_generator

from .manager import UserManager
from django.utils.translation import gettext_lazy as _

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5,
                            default='buyer')
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)

class Shop(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', blank=True, null=True, on_delete=models.CASCADE)
    filename = models.FileField(verbose_name='yaml file', blank=True)
    objects = models.Manager()
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name',)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=128, verbose_name='Категория')
    shops = models.ManyToManyField(Shop, verbose_name='Магазин')
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name',)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название продукта')
    model = models.CharField(max_length=128, verbose_name='Модель', blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, related_name="product")
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('-name',)
    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='продукт', related_name='product_info', on_delete=models.CASCADE)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД', blank=True,)
    shop = models.ForeignKey(Shop, verbose_name='магазин', on_delete=models.CASCADE)
    name= models.ForeignKey(Product, verbose_name='название продукта', related_name='product_name', blank=True, null= True, on_delete=models.CASCADE)
    model= models.CharField(max_length=128, verbose_name='Модель продукта', blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name='количество')
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='цена')
    price_rrc = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='рекомендованная цена')
    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product'),
        ]
    def __str__(self):
        return f'{[self.model, self.quantity, self.price]}'

class Parameter(models.Model):
    name = models.CharField(max_length=128, verbose_name='параметр')
    objects = models.Manager()
    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('-name',)
    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product = models.ForeignKey(ProductInfo, verbose_name='Описание продукта', blank=True, related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', on_delete=models.CASCADE, related_name='product_parameters', blank=True)
    value = models.CharField(max_length=128, verbose_name='характеристика')
    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров продукта"
        constraints = [
            models.UniqueConstraint(fields=['product', 'parameter'], name='unique_parameter'),
        ]
    def __str__(self):
        return f'{[self.parameter, self.value]}'

class OrderItem(models.Model):
    # order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, blank=True)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE,blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', on_delete=models.CASCADE,blank=True)
    quantity = models.PositiveIntegerField(verbose_name='количество')
    class Meta:
        verbose_name = 'Детали заказа'
        verbose_name_plural = "Детали заказов"
        constraints = [
            models.UniqueConstraint(fields=['product'], name='unique_order_item'),]
        # unique_together = (('product', 'quantity'),)
    def __str__(self):
        return f'{[self.product, self.shop, self.quantity]}'

class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'

class Order(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    dt = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)
    status = models.CharField(verbose_name='Статус заказа', choices=STATE_CHOICES, max_length=15,
                            default='new')
    orderitems = models.ManyToManyField(OrderItem, verbose_name='позиции заказа', related_name='order_item', through='Order_to_Orderitem')
    contact = models.ForeignKey(Contact, verbose_name='Контакт',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-dt',)
        # unique_together = (('id', 'orderitems'),)
    def __str__(self):
        return f"{self.id, self.user, self.dt, self.status} ({','.join(str(orderit.product) for orderit in self.orderitems.all())})"


class Order_to_Orderitem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE)


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
