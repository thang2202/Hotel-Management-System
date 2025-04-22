from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib import messages
from urllib.parse import unquote
from django.core.exceptions import ObjectDoesNotExist

from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType

from datetime import datetime
from decimal import Decimal

def check_room_availability(request):
    if request.method == "POST":
        try:
            id = request.POST.get("hotel-id")
            checkin = request.POST.get("checkin")
            checkout = request.POST.get("checkout")
            adult = request.POST.get("adult")
            children = request.POST.get("children")
            room_type = request.POST.get("room-type")

            hotel = Hotel.objects.get(status="Live", id=id)
            
            # Cố gắng lấy loại phòng theo tham số được mã hóa
            try:
                room_type = RoomType.objects.get(hotel=hotel, slug=room_type)
            except ObjectDoesNotExist:
                # Nếu không tìm thấy, hãy thử với tham số đã giải mã
                decoded_room_type = unquote(room_type)
                try:
                    # Cố gắng tìm theo tên nếu slug không khớp
                    room_type = RoomType.objects.get(hotel=hotel, type=decoded_room_type)
                except ObjectDoesNotExist:
                    messages.warning(request, 'Vui lòng chọn loại phòng khác. Bạn đã chọn loại phòng này rồi.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # return redirect("hotel:room_type_detail", hotel.slug, room_type.slug)
            url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type.slug])
            url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&adult={adult}&children={children}&room_type={room_type.slug}"
            return HttpResponseRedirect(url_with_params)

        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect("hotel:index")


def booking_data(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    context = {
        "hotel":hotel,
    }
    return render(request, "booking/booking_data.html", context)


def add_to_selection(request):
    room_selection = {}

    room_selection[str(request.GET['id'])] = {
        'hotel_id': request.GET['hotel_id'],
        'hotel_name': request.GET['hotel_name'],
        'room_name': request.GET['room_name'],
        'room_price': request.GET['room_price'],
        'number_of_beds': request.GET['number_of_beds'],
        'room_number': request.GET['room_number'],
        'room_type': request.GET['room_type'],
        'room_id': request.GET['room_id'],
        'checkin': request.GET['checkin'],
        'checkout': request.GET['checkout'],
        'adult': request.GET['adult'],
        'children': request.GET['children'],
    }

    if 'selection_data_obj' in request.session:
        if str(request.GET['id']) in request.session['selection_data_obj']:

            selection_data = request.session['selection_data_obj']
            selection_data[str(request.GET['id'])]['adult'] = int(room_selection[str(request.GET['id'])]['adult'])
            selection_data[str(request.GET['id'])]['children'] = int(room_selection[str(request.GET['id'])]['children'])
            request.session['selection_data_obj'] = selection_data
        else:
            selection_data = request.session['selection_data_obj']
            selection_data.update(room_selection)
            request.session['selection_data_obj'] = selection_data
    else:
        request.session['selection_data_obj'] = room_selection
    data = {
        "data":request.session['selection_data_obj'], 
        'total_selected_items': len(request.session['selection_data_obj'])
        }
    return JsonResponse(data)


def delete_session(request):
    request.session.pop('selection_data_obj', None)
    return redirect(request.META.get("HTTP_REFERER"))


def delete_selection(request):
    hotel_id = str(request.GET['id'])
    if 'selection_data_obj' in request.session:
        if hotel_id in request.session['selection_data_obj']:
            selection_data = request.session['selection_data_obj']
            del request.session['selection_data_obj'][hotel_id]
            request.session['selection_data_obj'] = selection_data


    total = 0
    total_days = 0
    room_count = 0
    adult = 0 
    children = 0 
    checkin = "" 
    checkout = "" 
    children = 0 
    hotel = None

    if 'selection_data_obj' in request.session:
        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            adult += int(item["adult"])
            children += int(item["children"])
            room_type_ = item["room_type"]
            
            hotel = Hotel.objects.get(id=id)
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
        
    
    context = render_to_string("hotel/async/selected_rooms.html", { "data":request.session['selection_data_obj'],  "total_selected_items": len(request.session['selection_data_obj']), "total":total, "total_days":total_days, "adult":adult, "children":children,    "checkin":checkin,    "checkout":checkout,    "hotel":hotel})

    print("data ======", context)
    
    return JsonResponse({"data": context, 'total_selected_items': len(request.session['selection_data_obj'])})

