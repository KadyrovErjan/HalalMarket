from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Avg
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail


ROLE_CHOICES= (
    ('продавец', 'продавец'),
    ('клиент', 'клиент'),
    ('админ', 'админ')
)

class UserProfile(AbstractUser):
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='клиент')
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)
    phone_number = PhoneNumberField(unique=True)
    address = models.CharField(max_length=120)
    verification_code = models.CharField(max_length=6, null=True, blank=True)



@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Укажи свой реальный домен
    frontend_url = "https://example.com"  # Заменить на адрес твоего сайта или фронтенда

    # Генерация полного URL сброса пароля
    reset_url = "{}{}?token={}".format(
        frontend_url,
        reverse('password_reset:reset-password-request'),  # Django-обработчик, можно заменить
        reset_password_token.key
    )

    # Отправка письма
    send_mail(
        subject="Password Reset for Some Website",  # Тема
        message=f"Use the following link to reset your password:\n{reset_url}",  # Текст
        from_email="noreply@example.com",  # Отправитель
        recipient_list=[reset_password_token.user.email],  # Получатель
        fail_silently=False,
    )




class Category(models.Model):
    category_name = models.CharField(max_length=32)
    category_image = models.ImageField(upload_to='category_image/')

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=32)
    subcategory_image = models.ImageField(upload_to='subcategory_image/')

class Store(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.store_name} ({self.owner.username})"




class Product(models.Model):
    store = models.ForeignKey("Store", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=32)
    product_image = models.ImageField(upload_to='product_image/')
    description = models.TextField()
    price = models.PositiveSmallIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    composition = models.CharField(max_length=300)
    action = models.CharField(max_length=300)
    expiration_date = models.CharField(max_length=64)
    equipment = models.CharField(max_length=300)
    product_code = models.CharField(max_length=20)

    def get_average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    def __str__(self):
        return self.product_name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    is_active = models.BooleanField(default=False)
    description = models.TextField()
    discount_percent = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @property
    def discounted_price(self):
        if self.discount_percent and self.product.price:
            return self.product.price * (100 - self.discount_percent) // 100
        return self.product.price

    @property
    def is_currently_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return f"{self.product.product_name} - {self.discount_percent}%"

class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'

class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} {self.favorite}'

    class Meta:
        unique_together = ('product', 'favorite')


class Ordering(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    delivery_status = models.CharField(
        max_length=50,
        choices=[
            ('В обработке', 'В обработке'),
            ('В пути', 'В пути'),
            ('Доставлено', 'Доставлено'),
        ],
        default='processing'
    )

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Ordering, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True, )
    comment = models.TextField(null=True, blank=True)
    photo1 = models.ImageField(upload_to='photo1/', null=True, blank=True)
    photo2 = models.ImageField(upload_to='photo2/', null=True, blank=True)
    photo3 = models.ImageField(upload_to='photo3/', null=True, blank=True)
    photo4 = models.ImageField(upload_to='photo4/', null=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_reply(self):
        return self.parent is not None

    def __str__(self):
        if self.is_reply():
            return f"Reply by {self.user.username} to Review {self.parent.id}"
        return f"Review by {self.user.username} on {self.product.product_name}"


class Receipt(models.Model):
    order = models.OneToOneField(Ordering, on_delete=models.CASCADE, related_name="receipt")
    store_name = models.ForeignKey(Store, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Чек для заказа #{self.order.id}"


