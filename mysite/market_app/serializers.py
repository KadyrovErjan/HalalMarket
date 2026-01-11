from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_rest_passwordreset.models import ResetPasswordToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'phone_number': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует")
        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Номер телефона обязателен")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером уже существует")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)

        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                'phone_number': instance.phone_number,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь с таким email не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль"})

        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активен")

        self.context['user'] = user
        return data

    def to_representation(self, instance):
        user = self.context['user']
        refresh = RefreshToken.for_user(user)

        return {
            'user': {
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('refresh')
        try:
            RefreshToken(token)
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs

class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")

        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=str(reset_code))
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        data['token'] = token
        return data

    def save(self):
        user = self.validated_data['user']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()
        token.delete()

from .utils import send_seller_verification_code


class SellerRequestCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    """
    Сериализатор для запроса кода подтверждения продавца
    """
    def save(self, **kwargs):
        user = self.context["request"].user
        send_seller_verification_code(user)  # функция из utils.py
        return {"detail": "Код отправлен на ваш email"}


class SellerVerifyCodeSerializer(serializers.Serializer):
    """
    Сериализатор для проверки кода
    """
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context["request"].user
        entered_code = data.get("code")

        if user.verification_code != entered_code:
            raise serializers.ValidationError("Неверный код подтверждения")

        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.role = "продавец"
        user.verification_code = None
        user.save()
        return user

class OwnerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "phone_number"]
        read_only_fields = ["id"]  # id менять нельзя


class StoreSerializer(serializers.ModelSerializer):
    owner = OwnerSimpleSerializer()

    class Meta:
        model = Store
        fields = ["id", "store_name", "category", "subcategory", "owner"]

    def update(self, instance, validated_data):
        # достаем данные для владельца
        owner_data = validated_data.pop("owner", None)

        # обновляем сам магазин
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # обновляем профиль владельца, если передали данные
        if owner_data:
            owner = instance.owner
            for attr, value in owner_data.items():
                setattr(owner, attr, value)
            owner.save()

        return instance

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'role', 'avatar']


class ClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'avatar', 'email', 'address', 'phone_number']


class AdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class AdminDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'category_image']


class SubCategorySerializers(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'subcategory_name', 'subcategory_image']


class ProductListSerializers(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    subcategory = SubCategorySerializers()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'product_name', 'product_image', 'description',
            'price', 'weight', 'quantity', 'composition',
            'action', 'expiration_date', 'equipment',
            'product_code', 'avg_rating'
        ]

    def get_avg_rating(self, obj):
        return obj.get_average_rating()


class ProductDetailSerializers(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    subcategory = SubCategorySerializers()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'product_name', 'product_image', 'description',
            'price', 'weight', 'quantity', 'composition',
            'action', 'expiration_date', 'equipment',
            'product_code', 'avg_rating'
        ]

    def get_avg_rating(self, obj):
        return obj.get_average_rating()



class SaleSerializers(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    is_currently_active = serializers.ReadOnlyField()

    class Meta:
        model = Sale
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "price", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price


class OrderingSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Ordering
        fields = ["id", "user", "created_at", "is_paid", "delivery_status", "items", "total_sum"]
        read_only_fields = ["user", "created_at", "total_sum"]

    def get_total_sum(self, obj):
        return sum(item.total_price for item in obj.items.all())

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Ordering.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class CartItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

class CartItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_price = serializers.IntegerField(source='product.price', read_only=True)
    product_image = serializers.ImageField(source='product.product_image', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class CartDetailSerializer(serializers.ModelSerializer):
    items = CartItemDetailSerializer(many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']


class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = ['id', 'product', 'created_date']


class ReceiptSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="order.items", many=True, read_only=True)
    customer_name = serializers.CharField(source="order.user.username", read_only=True)
    email = serializers.EmailField(source="order.user.email", read_only=True)
    phone_number = serializers.CharField(source="order.user.phone_number", read_only=True)

    class Meta:
        model = Receipt
        fields = ["id", "store_name", "purchase_date", "delivery_date", "items", "total_sum", "delivery_cost", "customer_name", "email", "phone_number",]

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id","user","product","rating","comment", "photo1","photo2","photo3","photo4","parent","created_at", "replies",]
        read_only_fields = ["user", "created_at", "replies"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return ReviewSerializer(replies, many=True).data

    def validate(self, data):
        request = self.context.get("request")
        parent = data.get("parent")
        product = data.get("product")

        if parent:
            if product.store.owner != request.user:
                raise serializers.ValidationError("Только владелец магазина может отвечать на отзывы.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)