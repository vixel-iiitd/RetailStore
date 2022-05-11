from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('',views.index,name="home"),
    path('login2',views.login2,name="login2"),
    path('handleLogout',views.handleLogout,name="handleLogout"),
    path('add_product',views.add_product,name="add_product"),
    path('seller',views.seller,name="seller"),
    path('customer',views.customer,name="customer"),
    path('signup2',views.signup2,name="signup2"),
    path('delivery',views.delivery,name="delivery"),
    path('electronics', views.electronics, name='electronics'),
    path('groceries', views.groceries, name='groceries'),
    path('clothing', views.clothing, name='clothing'),
    path('checkout', views.checkout, name='checkout'),

    path('update_item', views.update_item, name='update_item'),
    path('create_order', views.create_order, name='create_order'),
    path('your_orders', views.your_orders, name='your_orders'),
    path('your_orders/<int:orderID>', views.order)
]
