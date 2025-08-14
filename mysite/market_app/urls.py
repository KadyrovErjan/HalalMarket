from .views import *
from rest_framework import routers
from django.urls import path, include
from market_app.views import verify_reset_code


router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('user', UserProfileAPIView.as_view(), name='user_list'),
    path('category', CategoryAPIView.as_view(), name='category_list'),
    path('subcategory', SubCategoryAPIView.as_view(), name='subcategory_list'),
    path('product', ProductAPIView.as_view(), name='product_list'),
    path('sale', SaleAPIView.as_view(), name='sale_list'),
    path('ordering', OrderingAPIView.as_view(), name='ordering_list'),
    path('orderitem', OrderItemAPIView.as_view(), name='orderitem_list'),
    path('review', ReviewAPIView.as_view(), name='review_list'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
]