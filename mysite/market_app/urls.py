from .views import *
from rest_framework import routers
from django.urls import path, include
from market_app.views import verify_reset_code


router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('client', ClientListAPIView.as_view(), name='client_list'),
    path('client/<int:pk>/', ClientDetailAPIView.as_view(), name='client_detail'),

    # Places
    path('favorite/product/add/', FavoriteProductCreateView.as_view(), name='favorite-product-add'),
    path('favorite/product/delete/<int:id>/', FavoriteProductDeleteView.as_view(), name='favorite-product-delete'),
    path('favorite/product/', FavoriteProductListView.as_view(), name='favorite-product-list'),

    path('category', CategoryAPIView.as_view(), name='category_list'),
    path('subcategory', SubCategoryAPIView.as_view(), name='subcategory_list'),
    path('product', ProductListAPIView.as_view(), name='product_list'),
    path('sale', SaleAPIView.as_view(), name='sale_list'),

    path("reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),


    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),

    path('cart/', CartDetailView.as_view(), name='cart-detail'),  # GET корзина
    path('cart/add/', CartItemCreateView.as_view(), name='cart-item-add'),  # POST добавить товар
    path('cart/delete/<int:product_id>/', CartItemDeleteView.as_view(), name='cart-item-delete'), # DELETE удалить товар


    path("orders/", OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),

    path("orders/from-cart/", CreateOrderFromCartView.as_view(), name="order-from-cart"),

    path("receipts/<int:pk>/", ReceiptDetailView.as_view(), name="receipt-detail"),

    path("stores/", StoreListCreateView.as_view(), name="store-list-create"),
    path("stores/<int:pk>/", StoreDetailView.as_view(), name="store-detail"),

    path("product/add/", ProductCreateAPIView.as_view(), name="product-create"),

    path("seller/request-code/", SellerRequestCodeView.as_view(), name="seller-request-code"),
    path("seller/verify-code/", SellerVerifyCodeView.as_view(), name="seller-verify-code"),

]

