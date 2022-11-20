from time import timezone

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _

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
    email = models.EmailField(_('email address'), unique=True)
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
    filename = models.FileField(verbose_name='yaml file', blank=True)
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=128, verbose_name='Категория')
    shops = models.ManyToManyField(Shop, verbose_name='Магазин')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название магазина')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product")
    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='магазин', on_delete=models.CASCADE)
    name= models.ForeignKey(Product.name, verbose_name='название магазина', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='цена')
    price_rrc = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='рекомендованная цена')
    def __str__(self):
        return f'{[self.name, self.quantity, self.price]}'

class Parameter(models.Model):
    name = models.CharField(max_length=128, verbose_name='параметр')
    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Описание продукта')
    parameter = models.ForeignKey(Parameter.name, verbose_name='Параметр', on_delete=models.CASCADE)
    value = models.CharField(max_length=128, verbose_name='характеристика')
    def __str__(self):
        return f'{[self.parameter, self.value]}'

class Order(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    dt = models.DateTimeField(verbose_name='Время создания', default=timezone.now)
    status = models.CharField(verbose_name='Статус заказа', choices=STATE_CHOICES, max_length=10,
                            default='new')
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    def __str__(self):
        return f'{[self.user, self.dt, self.status]}'

class OrderItem(models.Model):
    order = models.OneToOneField(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE,blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', on_delete=models.CASCADE,blank=True)
    quantity = models.PositiveIntegerField(verbose_name='количество')

    class Meta:
        verbose_name = 'Детали заказа'
        verbose_name_plural = "Детали заказов"

    def __str__(self):
        return f'{[self.product, self.shop, self.quantity]}'

class Contact(models.Model):
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5,
                            default='buyer')
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    value = models.CharField(max_length=128, verbose_name='Подробности')
    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"
    def __str__(self):
        return f'{self.type} {self.user} '

