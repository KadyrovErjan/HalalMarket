from rest_framework import views
from .serializers import *
from rest_framework import status, viewsets, generics, permissions, response
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.filters import SearchFilter
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied




class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Невалидный токен'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_reset_code(request):
    """
    Проверка кода сброса и установка нового пароля.
    """
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

class SellerRequestCodeView(generics.GenericAPIView):
    serializer_class = SellerRequestCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=status.HTTP_404_NOT_FOUND)

        send_seller_verification_code(user)

        return Response({"message": f"Код подтверждения отправлен на {email}"}, status=status.HTTP_200_OK)

class SellerVerifyCodeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SellerVerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"detail": "Вы стали продавцом"})

class ClientListAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ClientListSerializer

class ClientDetailAPIView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ClientDetailSerializer

class CategoryAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubCategoryAPIView(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializers

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializers
    filter_backends = [SearchFilter]
    search_fields = ['product_name']

class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer


class SaleAPIView(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializers

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ordering.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Ordering.objects.all()

    def get_queryset(self):
        return Ordering.objects.filter(user=self.request.user)


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Продукт с таким ID не найден"})

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

class CreateOrderFromCartView(generics.CreateAPIView):
    serializer_class = OrderingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        order = Ordering.objects.create(user=request.user)
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
        cart.items.all().delete()  # очистить корзину

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'product_id'

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product_id = self.kwargs.get('product_id')
        try:
            return CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            raise Http404

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Отзывы можно фильтровать по product_id"""
        product_id = self.request.query_params.get("product_id")
        queryset = Review.objects.select_related("user", "product", "parent")
        if product_id:
            return queryset.filter(product_id=product_id, parent__isnull=True)
        return queryset.filter(parent__isnull=True)

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")
        parent = serializer.validated_data.get("parent")

        if parent:
            if product.store.owner != self.request.user:
                raise PermissionDenied("Ответ может оставить только владелец магазина.")
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all().select_related("user", "product", "parent")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        review = self.get_object()
        if review.user != self.request.user:
            raise PermissionDenied("Вы можете редактировать только свои комментарии.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы можете удалить только свои комментарии.")
        instance.delete()


class FavoriteProductCreateView(generics.CreateAPIView):
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        favorite, _ = Favorite.objects.get_or_create(user=user)
        product = serializer.validated_data['product']
        FavoriteProduct.objects.get_or_create(favorite=favorite, product=product)

# Удалить из избранного
class FavoriteProductDeleteView(generics.DestroyAPIView):
    queryset = FavoriteProduct.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

class FavoriteProductListView(generics.ListAPIView):
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FavoriteProduct.objects.filter(favorite__user=user)

class ReceiptDetailView(generics.RetrieveAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Покупатель видит только свои чеки
        return Receipt.objects.filter(order__user=self.request.user)

class StoreListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # показываем только свои магазины
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # пользователь может работать только со своими магазинами
        return Store.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)