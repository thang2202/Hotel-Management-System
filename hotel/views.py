from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.core.mail import send_mail



from hotel.models import Coupon, CouponUsers, Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType, Notification, Bookmark, Review

from datetime import datetime
from decimal import Decimal
from .models import Blog
import json
import requests


def index(request):
    popular_hotels = Hotel.objects.filter(status="Live").order_by('-views')[:6]

    search_results = None
    room_type = request.GET.get('room_type', '').strip()  # Lấy tham số room_type từ URL

    if request.method == 'POST' or room_type:
        hotel_name = request.POST.get('hotel_name', '').strip() if request.method == 'POST' else ''
        booking_date = request.POST.get('booking_date', '').strip() if request.method == 'POST' else ''
        category = request.POST.get('tags', '').strip() if request.method == 'POST' else ''

        # Tìm kiếm khách sạn có liên kết với loại phòng
        search_results = Hotel.objects.filter(
            Q(name__icontains=hotel_name) |
            Q(address__icontains=hotel_name) |
            Q(tags__name__icontains=category) |
            Q(roomtype__type__icontains=room_type),
            status="Live"
        ).distinct()

    context = {
        "popular_hotels": popular_hotels,
        "search_results": search_results,
    }
    return render(request, "hotel/index.html", context)

def dashboard(request):
    """
    View hiển thị dashboard.
    """
    return render(request, "user_dashboard/dashboard.html", {})

def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    try:
        reviews = Review.objects.filter(user=request.user, hotel=hotel)
    except:
        reviews = None
    all_reviews = Review.objects.filter(hotel=hotel, active=True)
    
    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, hotel=hotel)
    else:
        bookmark = None
    context = {
        "hotel":hotel,
        "bookmark":bookmark,
        "reviews":reviews,
        "all_reviews":all_reviews,
    }
    return render(request, "hotel/hotel_detail.html", context)


def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type = RoomType.objects.get(hotel=hotel, slug=rt_slug)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

    id = request.GET.get("hotel-id")
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adult = request.GET.get("adult")
    children = request.GET.get("children")
    room_type_ = request.GET.get("room-type")

    print("checkin ======", checkin)

    if not all([checkin, checkout]):
        messages.warning(request, "Vui lòng nhập dữ liệu đặt phòng của bạn để kiểm tra tình trạng phòng trống.")
        return redirect("booking:booking_data", hotel.slug)

    context = {
        "hotel":hotel,
        "room_type":room_type,
        "rooms":rooms,
        "id":id,
        "checkin":checkin,
        "checkout":checkout,
        "adult":adult,
        "children":children,
        "room_type_":room_type_,
    }
    return render(request, "hotel/room_type_detail.html", context)



def selected_rooms(request):
    # request.session.pop('selection_data_obj', None)

    total = 0
    room_count = 0
    total_days = 0
    adult = 0 
    children = 0 
    checkin = "0" 
    checkout = "" 
    children = 0 
    
    if 'selection_data_obj' in request.session and request.session['selection_data_obj']:

        if request.method == "POST":
            for h_id, item in request.session['selection_data_obj'].items():
                
                id = int(item['hotel_id'])
                hotel_id = int(item['hotel_id'])

                checkin = item["checkin"]
                checkout = item["checkout"]
                adult = int(item["adult"])
                children = int(item["children"])
                room_type_ = item["room_type"]
                room_id = int(item["room_id"])
                
                user = request.user
                hotel = Hotel.objects.get(id=id)
                room = Room.objects.get(id=room_id)
                room_type = RoomType.objects.get(id=room_type_)

                

                
            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")

            booking = Booking.objects.create(
                hotel=hotel,
                room_type=room_type,
                check_in_date=checkin,
                check_out_date=checkout,
                total_days=total_days,
                num_adults=adult,
                num_children=children,
                full_name=full_name,
                email=email,
                phone=phone
            )

            if request.user.is_authenticated:
                booking.user = request.user
                booking.save()
            else:
                booking.user = None
                booking.save()


            for h_id, item in request.session['selection_data_obj'].items():
                room_id = int(item["room_id"])
                room = Room.objects.get(id=room_id)
                booking.room.add(room)

                room_count += 1
                days = booking.total_days
                price = booking.room_type.price

                room_price = price * room_count
                total = room_price * days

                # print("room_price ==",room_price)
                # print("total ==",total)
            
            booking.total += float(total)
            booking.before_discount += float(total)
            booking.save()

            messages.success(request, "Thanh toán ngay!")
            return redirect("hotel:checkout", booking.booking_id)

        hotel = None

        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])
            hotel_id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            adult = int(item["adult"])
            children = int(item["children"])
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])
            
            room_type = RoomType.objects.get(id=room_type_)

            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            room_count += 1
            days = total_days
            price = room_type.price

            room_price = price * room_count
            total = room_price * days
            
            hotel = Hotel.objects.get(id=id)

        print("hotel ===", hotel)
        context = {
            "data":request.session['selection_data_obj'], 
            "total_selected_items": len(request.session['selection_data_obj']),
            "total":total,
            "total_days":total_days,
            "adult":adult,
            "children":children,   
            "checkin":checkin,   
            "checkout":checkout,   
            "hotel":hotel,   
        }

        return render(request, "hotel/selected_rooms.html", context)
    else:
        messages.warning(request, "Bạn chưa lựa chọn phòng nào!")
        return redirect("/")

def checkout(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    if booking.payment_status == "paid":
        messages.success(request, "Đơn này đã được thanh toán!")
        return redirect("/")
    else:
        booking.payment_status = "processing"
        booking.save()


    # Coupon
    now = timezone.now()
    if request.method == "POST":
        # Get code entered in the input field
        code = request.POST.get('code')
        print("code ======", code)
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
            if coupon in booking.coupons.all():
                messages.warning(request, "Mã giảm giá đã được kích hoạt")
                return redirect("hotel:checkout", booking.booking_id)
            else:
                CouponUsers.objects.create(
                    booking=booking,
                    coupon=coupon,
                    full_name=booking.full_name,
                    email=booking.email,
                    mobile=booking.phone,
                )

                if coupon.type == "Percentage":
                    discount = booking.total * coupon.discount / 100
                else:
                    discount = coupon.discount

                booking.coupons.add(coupon)
                booking.total -= discount
                booking.saved += discount
                booking.save()

                
                messages.success(request, "Mã giảm giá đã được kích hoạt")
                return redirect("hotel:checkout", booking.booking_id)
        except Coupon.DoesNotExist:
            messages.error(request, "Không tìm thấy mã giảm giá.")
            return redirect("hotel:checkout", booking.booking_id)
    
    context = {
        "booking":booking, 
        "website_address":settings.WEBSITE_ADDRESS,
    }
    return render(request, "hotel/checkout.html", context)


def momo_payment(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    momo_api_url = "https://test-payment.momo.vn/v2/gateway/api/create"
    payload = {
        "amount": booking.total,
        "orderId": booking.booking_id,
        "redirectUrl": request.build_absolute_uri(reverse('hotel:payment_success', args=[booking.booking_id])),
        "ipnUrl": request.build_absolute_uri(reverse('hotel:payment_callback')),
    }
    response = requests.post(momo_api_url, json=payload)
    return redirect(response.json().get('payUrl'))

def zalopay_payment(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    zalopay_api_url = "https://sandbox.zalopay.vn/v001/tpe/createorder"
    payload = {
        "amount": booking.total,
        "order_id": booking.booking_id,
        "callback_url": request.build_absolute_uri(reverse('hotel:payment_success', args=[booking.booking_id])),
    }
    response = requests.post(zalopay_api_url, json=payload)
    return redirect(response.json().get('order_url'))

def vnpay_payment(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    vnpay_api_url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    payload = {
        "vnp_Amount": int(booking.total * 100),
        "vnp_OrderInfo": booking.booking_id,
        "vnp_ReturnUrl": request.build_absolute_uri(reverse('hotel:payment_success', args=[booking.booking_id])),
        "vnp_IpnUrl": request.build_absolute_uri(reverse('hotel:payment_callback')),
    }
    response = requests.post(vnpay_api_url, json=payload)
    return redirect(response.url)


@csrf_exempt
def payment_callback(request):
    data = request.POST
    booking_id = data.get("orderId") or data.get("order_id")
    status = data.get("status")
    booking = Booking.objects.get(booking_id=booking_id)

    if status == "success":
        booking.payment_status = "paid"
        booking.save()
    elif status == "failed":
        booking.payment_status = "failed"
        booking.save()

    return JsonResponse({"message": "Payment status updated."})


def payment_success(request, booking_id):
    success_id = request.GET.get('success_id')
    booking_total = request.GET.get('booking_total')

    if success_id and booking_total: 
        success_id = success_id.rstrip('/')
        booking_total = booking_total.rstrip('/')
        
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        
        # Payment Verification
        if booking.total == Decimal(booking_total):
            if booking.payment_status == "processing": #processing #paid
                booking.payment_status = "paid"
                booking.save()

                noti = Notification.objects.create(booking=booking,type="Booking Confirmed",)
                if request.user.is_authenticated:
                    noti.user = request.user
                    noti.save()
                else:
                    noti = None
                    noti.save()

                # Delete the Room Sessions
                if 'selection_data_obj' in request.session:
                    del request.session['selection_data_obj']
                
                # Send Email To Customer
                merge_data = {
                    'booking': booking, 
                    'booking_rooms': booking.room.all(), 
                    'full_name': booking.full_name, 
                    'subject': f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}", 
                }
                subject = f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}"
                text_body = render_to_string("email/booking_completed.txt", merge_data)
                html_body = render_to_string("email/booking_completed.html", merge_data)
                
                msg = EmailMultiAlternatives(
                    subject=subject, 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.email], 
                    body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                    
            elif booking.payment_status == "paid":
                messages.success(request, f'Đơn của bạn đã hoàn tất.')
                return redirect("/")
            else:
                messages.success(request, 'Opps... Lỗi máy chủ nội bộ, vui lòng thử lại sau.')
                return redirect("/")
                
        else:
            messages.error(request, "Lỗi: Phát hiện thanh toán lỗi. Thanh toán này đã bị hủy.")
            booking.payment_status = "failed"
            booking.save()
            return redirect("/")
    else:
        messages.error(request, "Lỗi: Phát hiện thanh toán lỗi. Thanh toán này đã bị hủy.")
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        booking.payment_status = "failed"
        booking.save()
        return redirect("/")
    
    context = {
        "booking": booking, 
        'rooms':booking.room.all(), 
    }
    return render(request, "hotel/payment_success.html", context) 


def payment_failed(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    booking.payment_status = "failed"
    booking.save()
                
    context = {
        "booking": booking, 
    }
    return render(request, "hotel/payment_failed.html", context) 


def invoice(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    context = {
        "booking":booking,  
        "room":booking.room.all(),  
    }
    return render(request, "hotel/invoice.html", context)

def load_more_blogs(request):
    page = int(request.GET.get('page', 1))
    blogs_per_page = 4
    start = (page - 1) * blogs_per_page
    end = page * blogs_per_page

    blogs = Blog.objects.all()[start:end]
    has_more = Blog.objects.count() > end

    blogs_data = [{
        'url': blog.get_absolute_url(),
        'title': blog.title,
        'image': blog.image.url,
        'date': blog.date.strftime('%d-%m-%Y'),
        'excerpt': blog.excerpt,
    } for blog in blogs]

    return JsonResponse({'blogs': blogs_data, 'hasMore': has_more})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Tiêu đề email
        subject = f"Tin nhắn từ {name}"
        # Nội dung email
        email_message = f"Tên: {name}\nEmail: {email}\n\nNội dung:\n{message}"
        # Gửi email
        send_mail(
            subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,  # Email gửi
            [settings.DEFAULT_TO_EMAIL], # Email nhận
            fail_silently=False,
        )

        return HttpResponse(f"Cảm ơn {name}, tin nhắn của bạn đã được gửi!")
    return render(request, 'hotel/contact.html')

def about_us(request):
    return render(request, 'hotel/about_us.html')

@csrf_exempt
def update_room_status(request):
    today = timezone.now().date()

    booking = Booking.objects.filter(is_active=True, payment_status="paid")   
    for b in booking:
        if b.checked_in_tracker != True:
            if b.check_in_date > today:
                b.checked_in_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()
                

            else:
                b.checked_in_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()
        else:
            if b.check_out_date > today:
                b.checked_out_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()

            else:
                b.checked_out_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()

            

    return HttpResponse(today)