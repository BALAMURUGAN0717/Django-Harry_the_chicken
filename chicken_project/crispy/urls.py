from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_details, name='profile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('product_details/<int:id>/', views.product_details, name="product_details"),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease_cart/<int:id>/', views.decrease_cart, name='decrease_cart'),
    path('remove_cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path('cart/', views.cart_view, name='cart'),
]
