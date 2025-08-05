from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Avg


ROLE_CHOICES= (
    ('продавец', 'продавец'),
    ('клиент', 'клиент'),
    ('админ', 'админ')
)

class UserProfile(AbstractUser):
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='buyer')
    avatar = models.ImageField(upload_to='avatar/')
    phone_number = PhoneNumberField(default='+996', unique=True)

class Category(models.Model):
    category_name = models.CharField(max_length=32)
    category_image = models.ImageField(upload_to='category_image/')

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=32)
    subcategory_image = models.ImageField(upload_to='subcategory_image/')

class Product(models.Model):
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

class Ordering(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Ordering, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


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

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True, )
    comment = models.TextField(null=True, blank=True)
    photo1 = models.ImageField(upload_to='photo1/')
    photo2 = models.ImageField(upload_to='photo2/')
    photo3 = models.ImageField(upload_to='photo3/')
    photo4 = models.ImageField(upload_to='photo4/')
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








