from multiprocessing.dummy import current_process
from pyexpat.errors import messages

from django.shortcuts import render, redirect
from django.db.models import Min, Max, Avg, Sum
from matplotlib.style.core import context
from numpy.ma.extras import average
from socks import method

from .models import Employee, Apartment, Room, Tenant, RoomType, Parking


def detail_page(request):
    return render(request, "landlord/home.html")


def employee_page(request):
    condition = {}
    name_filter = request.GET.get('filter')
    occupation_filter = request.GET.get('occupation')
    salary_filter = request.GET.get('salary')
    order = request.GET.get('order')

    if name_filter:
        condition["name__icontains"] = name_filter
    if occupation_filter:
        condition["occupation"] = occupation_filter
    if salary_filter:
        condition["salary__lt"] = salary_filter
    if not order:
        order = "name"

    employee = Employee.objects.filter(**condition)
    occupations = Employee.objects.values_list('occupation', flat=True).distinct()
    min_salary = Employee.objects.aggregate(Min('salary'))['salary__min']
    max_salary = Employee.objects.aggregate(Max('salary'))['salary__max']
    max_salary += (100 - (max_salary%100))

    average_this_salary = 0
    min_this_salary = 0
    max_this_salary = 0

    current_sal = max_salary
    if request.method == 'GET' and salary_filter:
        current_sal = salary_filter

    if employee:
        average_this_salary = employee.aggregate(Avg('salary'))['salary__avg']
        min_this_salary = employee.aggregate(Min('salary'))['salary__min']
        max_this_salary = employee.aggregate(Max('salary'))['salary__max']
        sum_this_salary = employee.aggregate(Sum('salary'))['salary__sum']

    context = {
        'employee': employee.order_by(order),
        'num_employee': employee.count(),
        'current_occ': occupation_filter,
        'current_sal': current_sal,
        'occupations': occupations,
        'min_salary': str(min_salary),
        'max_salary': str(max_salary),
        'avg_this_salary': f"{average_this_salary:,.2f}",
        'sum_this_salary': f"{sum_this_salary:,.2f}",
        'min_this_salary': f"{min_this_salary:,.2f}",
        'max_this_salary': f"{max_this_salary:,.2f}",
        "current_order": order,
    }
    return render(request, "landlord/employee.html", context=context)


def add_employee(request):
    if not request.user.is_authenticated:
        return redirect("landlord:employee")
    if request.method == "POST":
        landlord = request.user
        apartment = Apartment.objects.get(landlord=landlord)
        name = request.POST.get("employee_name")
        salary = request.POST.get("employee_salary")
        occupation = request.POST.get("employee_occupation")
        Employee.objects.create(apartment=apartment, name=name, salary=salary, occupation=occupation)
        return redirect("landlord:employee")
    return redirect("landlord:employee")


def delete_employee(request, employee_id):
    landlord = request.user
    try:
        apartment = Apartment.objects.get(landlord=landlord)
        employee = Employee.objects.get(apartment=apartment, pk=employee_id)
    except(Apartment.DoesNotExist, Employee.DoesNotExist):
        return redirect("landlord:employee")
    employee.delete()
    return redirect("landlord:employee")


def edit_employee(request, employee_id):
    landlord = request.user
    try:
        apartment = Apartment.objects.get(landlord=landlord)
        employee = Employee.objects.get(apartment=apartment, pk=employee_id)
    except(Apartment.DoesNotExist, Employee.DoesNotExist):
        return redirect("landlord:employee")

    if request.method == "POST":
        name = request.POST.get("new_name")
        salary = request.POST.get("new_salary")
        occupation = request.POST.get("new_occupation")

        if name:
            employee.name = name
        if salary:
            employee.salary = salary
        if occupation:
            employee.occupation = occupation
        employee.save()
    return redirect("landlord:employee")


def tenant_page(request):
    condition ={}
    name_filter = request.GET.get('filter')
    contact_type = request.GET.get('type')
    if name_filter:
        condition["name__icontains"] = name_filter
    tenants = Tenant.objects.filter(**condition)

    if contact_type == 'email':
        tenants = tenants.filter(contact_info__icontains="@")
    if contact_type == 'number':
        tenants = tenants.exclude(contact_info__icontains="@")

    context = {
        "tenants": tenants.order_by("name"),
        "num_tenant": tenants.count(),
    }
    return render(request, "landlord/tenant.html", context=context)


def add_tenant(request):
    if request.method == "POST":
        name = request.POST.get("tenant_name")
        contact_info = request.POST.get("tenant_contact")
        Tenant.objects.create(name=name, contact_info=contact_info)
        return redirect("landlord:tenant")
    return redirect("landlord:tenant")


def delete_tenant(request, tenant_id):
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
    except(Tenant.DoesNotExist):
        return redirect("landlord:tenant")
    tenant.delete()
    return redirect("landlord:tenant")


def edit_tenant(request, tenant_id):
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
    except(Tenant.DoesNotExist):
        return redirect("landlord:tenant")

    if request.method == "POST":
        name = request.POST.get("new_name")
        contact = request.POST.get("new_contact")

        if name:
            tenant.name = name
        if contact:
            tenant.contact_info = contact
        tenant.save()
    return redirect("landlord:tenant")


def room_page(request):
    condition ={}
    name_filter = request.GET.get('filter')
    status_filter = request.GET.get('status')
    price_filter = request.GET.get('price')
    order_filter = request.GET.get('order')
    if name_filter:
        condition["number__istartswith"] = name_filter
    if status_filter:
        condition["status"] = status_filter
    if price_filter:
        condition["price__lt"] = price_filter

    if not order_filter:
        order_filter = "number"

    rooms = Room.objects.filter(**condition)
    room_type = RoomType.objects.all()
    all_status = Room.objects.values_list('status', flat=True).distinct()
    min_price = Room.objects.aggregate(Min('price'))['price__min']
    max_price = Room.objects.aggregate(Max('price'))['price__max']
    max_price += (100 - (max_price % 100))

    current_price = max_price
    if price_filter:
        current_price = price_filter

    average_this_price = 0
    min_this_price = 0
    max_this_price = 0
    sum_this_price = 0
    if rooms:
        average_this_price = rooms.aggregate(Avg('price'))['price__avg']
        min_this_price = rooms.aggregate(Min('price'))['price__min']
        max_this_price = rooms.aggregate(Max('price'))['price__max']
        sum_this_price = rooms.aggregate(Sum('price'))['price__sum']

    context = {
        "rooms": rooms.order_by(order_filter),
        "room_type": room_type,
        "min_price": min_price,
        "max_price": max_price,
        "current_price": current_price,
        "avg_this_price": f"{average_this_price:,.2f}",
        "min_this_price": f"{min_this_price:,.2f}",
        "max_this_price": f"{max_this_price:,.2f}",
        "sum_this_price": f"{sum_this_price:,.2f}",
        'all_status': all_status,
        'selected_status': status_filter,
        "num_room": rooms.count(),
        "current_order": order_filter,
    }
    return render(request, "landlord/room.html", context=context)


def add_room(request):
    if request.method == "POST":
        apartment = Apartment.objects.get(landlord=request.user)
        room_number = request.POST.get("room_number")
        room_type_id = request.POST.get("type")
        room_type = RoomType.objects.get(pk=room_type_id)
        price = request.POST.get("room_price")
        Room.objects.create(apartment=apartment, number=room_number, room_type=room_type, price=price)
        return redirect("landlord:room")
    return redirect("landlord:room")


def delete_room(request, room_id):
    landlord = request.user
    try:
        apartment = Apartment.objects.get(landlord=landlord)
        room = Room.objects.get(pk=room_id, apartment=apartment)
    except(Room.DoesNotExist):
        return redirect("landlord:room")
    room.delete()
    return redirect("landlord:room")


def edit_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
        room_number = request.POST.get("new_number")
        room_type_id = request.POST.get("new_type")
        room_type = RoomType.objects.get(pk=room_type_id)
        price = request.POST.get("new_price")
    except(Room.DoesNotExist):
        return redirect("landlord:room")
    if room_number:
        room.number = room_number
    if room_type:
        room.room_type = room_type
    if price:
        room.price = price
    room.save()
    return redirect("landlord:room")


def parking_page(request):
    condition ={}
    zone_filter = request.GET.get('zone')
    room_filter = request.GET.get('room')
    plate_filter = request.GET.get('plate')
    order_filter = request.GET.get('order')
    if zone_filter:
        condition["zone"] = zone_filter
    if room_filter:
        room = Room.objects.get(pk=room_filter)
        condition["room"] = room
    if plate_filter:
        condition["plate_number__startswith"] = plate_filter

    current_room = room_filter
    if not order_filter:
        order_filter = "zone"
    if room_filter:
        current_room = int(room_filter)

    parking = Parking.objects.filter(**condition)
    all_zone = Parking.objects.values_list('zone', flat=True).distinct()

    context = {
        "parking": parking.order_by(order_filter),
        "rooms": Room.objects.all().order_by("number"),
        "all_zone": all_zone,
        "current_zone": zone_filter,
        "current_room": current_room,
        "num_parking": parking.count(),
    }
    return render(request, "landlord/parking.html", context=context)


def add_parking(request):
    if request.method == "POST":
        zone = request.POST.get("parking_zone")
        room_id = request.POST.get("parking_room")
        room = Room.objects.get(pk=room_id)
        plate_number = request.POST.get("parking_plate")
        Parking.objects.create(zone=zone, room=room, plate_number=plate_number)
        return redirect("landlord:parking")
    return redirect("landlord:parking")


def delete_parking(request, parking_id):
    landlord = request.user
    try:
        parking = Parking.objects.get(room__apartment__landlord=landlord, pk=parking_id)
    except(Room.DoesNotExist, Parking.DoesNotExist):
        return redirect("landlord:parking")
    parking.delete()
    return redirect("landlord:parking")


def edit_parking(request, parking_id):
    landlord = request.user
    try:
        parking = Parking.objects.get(room__apartment__landlord=landlord, pk=parking_id)
    except(Room.DoesNotExist, Parking.DoesNotExist):
        return redirect("landlord:parking")
    zone = request.POST.get("new_zone")
    room_id = request.POST.get("new_room")
    plate_number = request.POST.get("new_plate")
    if zone:
        parking.zone = zone
    if room_id:
        room = Room.objects.get(pk=room_id)
        parking.room = room
    if plate_number:
        parking.plate_number = plate_number
    parking.save()
    return redirect("landlord:parking")
