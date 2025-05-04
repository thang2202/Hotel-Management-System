from django.urls import path 
from django.urls import path
from hotel import views

app_name = "hotel"

urlpatterns = [
    # Trang chính
    path("", views.index, name="index"),

    # Các URL cụ thể
    path("dashboard/", views.dashboard, name="dashboard"),
    path("selected_rooms/", views.selected_rooms, name="selected_rooms"),
    path("checkout/<booking_id>/", views.checkout, name="checkout"),
    path("invoice/<booking_id>/", views.invoice, name="invoice"),
    path("update_room_status/", views.update_room_status, name="update_room_status"),
    path('contact/', views.contact, name='contact'),
    path('about-us/', views.about_us, name='about_us'),
    path('api/blogs', views.load_more_blogs, name='load_more_blogs'),

    # API và thanh toán
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/success/<str:booking_id>/', views.payment_success, name='payment_success'),
    path('payment/momo/<str:booking_id>/', views.momo_payment, name='momo_payment'),
    path('payment/zalopay/<str:booking_id>/', views.zalopay_payment, name='zalopay_payment'),
    path('payment/vnpay/<str:booking_id>/', views.vnpay_payment, name='vnpay_payment'),
    path('success/<booking_id>/', views.payment_success, name='success'),
    path('failed/<booking_id>/', views.payment_failed, name='failed'),

    # Chi tiết khách sạn và các chức năng liên quan
    path("detail/<slug:slug>/", views.hotel_detail, name="detail"),
    path("detail/<slug:slug>/room-type/<slug:rt_slug>/", views.room_type_detail, name="room_type_detail"),
    path('<slug:slug>/', views.hotel_detail, name='hotel_detail'),  # Đặt cuối cùng để tránh xung đột
]