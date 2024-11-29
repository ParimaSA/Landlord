import math
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Min, Max, Avg, Sum
from django.utils import timezone
from .models import Employee, Apartment, Room, Tenant, RoomType, Parking, LeaseContract, ApartmentLocation


def detail_page(request):
    check_room_status()
    return render(request, "landlord/home.html")


def about_us_page(request):
    return render(request, "landlord/about_us.html")


@login_required
def employee_page(request):
    condition = {}
    apartment = Apartment.objects.get(landlord=request.user)
    name_filter = request.GET.get('filter')
    occupation_filter = request.GET.get('occupation')
    salary_filter = request.GET.get('salary')
    order = request.GET.get('order')

    condition["apartment"] = apartment
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
    sum_this_salary = 0

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


@login_required
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
        "current_type": contact_type,
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


@login_required
def room_page(request):
    check_room_status()
    condition ={}
    apartment = Apartment.objects.get(landlord=request.user)
    name_filter = request.GET.get('filter')
    status_filter = request.GET.get('status')
    price_filter = request.GET.get('price')
    type_filter = request.GET.get("room_type")
    order_filter = request.GET.get('order')

    condition["apartment"] = apartment
    if name_filter:
        condition["number__istartswith"] = name_filter
    if status_filter:
        condition["status"] = status_filter
    if price_filter:
        condition["price__lt"] = price_filter
    if type_filter:
        this_type = RoomType.objects.get(pk=type_filter)
        condition["room_type"] = this_type

    selected_type = None
    if not order_filter:
        order_filter = "number"
    if type_filter:
        selected_type = int(type_filter)

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
        'selected_type': selected_type,
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


@login_required
def parking_page(request):
    condition ={}
    apartment = Apartment.objects.get(landlord=request.user)
    rooms = Room.objects.filter(apartment=apartment).order_by("number")

    zone_filter = request.GET.get('zone')
    room_filter = request.GET.get('room')
    plate_filter = request.GET.get('plate')
    order_filter = request.GET.get('order')

    parking = Parking.objects.filter(room__in=rooms)
    all_zone = parking.values_list('zone', flat=True).distinct()

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

    parking = parking.filter(**condition)

    context = {
        "parking": parking.order_by(order_filter),
        "rooms": rooms,
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


@login_required
def lease_contract_page(request):
    condition ={}
    apartment = Apartment.objects.get(landlord=request.user)
    rooms = Room.objects.filter(apartment=apartment)

    room_filter = request.GET.get('room')
    name_filter = request.GET.get('name')
    start_filter = request.GET.get('sdate')
    end_filter = request.GET.get('edate')
    status_filter = request.GET.get('status')
    order_filter = request.GET.get('order')

    contracts = LeaseContract.objects.filter(room__in=rooms)
    current_room = None

    if room_filter:
        room = Room.objects.get(pk=room_filter)
        condition["room"] = room
        current_room = int(room_filter)
    if name_filter:
        condition["tenant__name__icontains"] = name_filter
    if start_filter:
        condition["lease_start__date"] = start_filter
    if end_filter:
        condition["lease_end__date"] = end_filter
    if status_filter:
        if status_filter == "active":
            condition["lease_end__date__gt"] = timezone.now()
        if status_filter == "expired":
            condition["lease_end__date__lt"] = timezone.now()

    if not order_filter:
        order_filter = "room__number"
    if order_filter == "tenant":
        order_filter = "tenant__name"

    available_rooms = rooms.filter(status="available")
    contracts = contracts.filter(**condition)

    total_income = sum(contract.room.price * math.ceil((contract.lease_end - contract.lease_start).days/30) for contract in contracts)
    duration = 1
    if contracts.count() >=2 :
        lease_start_order = contracts.order_by("lease_start")
        lease_end_order = contracts.order_by("lease_end")
        duration = math.ceil((lease_end_order[lease_end_order.count()-1].lease_end - lease_start_order[0].lease_start).days / 30)

    context = {
        "contracts": contracts.order_by(order_filter),
        "available_rooms": available_rooms,
        "all_tenant": Tenant.objects.all().order_by("name"),
        "rooms": rooms,
        "num_contract": contracts.count(),
        "current_room": current_room,
        "current_active": contracts.filter(lease_end__date__gt=timezone.now()).count(),
        "current_expired": contracts.filter(lease_end__date__lt=timezone.now()).count(),
        "today": timezone.now(),
        "total_income": f"{total_income:,.2f}",
        "avg_income": f"{total_income/duration:,.2f}",
        "duration": f"{duration} month"
    }
    return render(request, "landlord/contract.html", context=context)


def add_lease_contract(request):
    if request.method == "POST":
        room_id = request.POST.get("lease_room")
        room = Room.objects.get(pk=room_id)
        room.status = "occupied"
        room.save()
        tenant_id = request.POST.get("lease_tenant")
        tenant = Tenant.objects.get(pk=tenant_id)
        lease_start = request.POST.get("lease_start")
        lease_end = request.POST.get("lease_end")
        LeaseContract.objects.create(room=room, tenant=tenant, lease_start=lease_start, lease_end=lease_end)
        return redirect("landlord:lease_contract")
    return redirect("landlord:lease_contract")


def delete_lease_contract(request, contract_id):
    landlord = request.user
    try:
        contract = LeaseContract.objects.get(room__apartment__landlord=landlord, pk=contract_id)
    except(LeaseContract.DoesNotExist):
        return redirect("landlord:lease_contract")
    room = contract.room
    room.status = "available"
    contract.delete()
    return redirect("landlord:lease_contract")


def edit_lease_contract(request, contract_id):
    landlord = request.user
    try:
        contract = LeaseContract.objects.get(room__apartment__landlord=landlord, pk=contract_id)
    except(LeaseContract.DoesNotExist):
        return redirect("landlord:lease_contract")
    room_id = request.POST.get("new_room")
    tenant_id = request.POST.get("new_tenant")
    lease_start = request.POST.get("new_start")
    lease_end = request.POST.get("new_end")
    if room_id:
        room = Room.objects.get(pk=room_id)
        contract.room = room
        if datetime.strptime(lease_end, "%Y-%m-%d").date() > timezone.now().date():
            room.status = "occupied"
        else:
            room.status = "available"
        room.save()
    if tenant_id:
        tenant = Tenant.objects.get(pk=tenant_id)
        contract.tenant = tenant
    if lease_start:
        contract.lease_start = lease_start
    if lease_end:
        contract.lease_end = lease_end
    contract.save()

    return redirect("landlord:lease_contract")


def check_room_status():
    rooms = Room.objects.filter(status="occupied")
    for room in rooms:
        contracts = LeaseContract.objects.filter(room=room, lease_end__lt=timezone.now())
        if not contracts:
            continue
        print(room.number, contracts, timezone.now())
        room.status = 'available'
        room.save()


@login_required
def apartment_page(request):
    apartment = Apartment.objects.get(landlord=request.user)
    location = ApartmentLocation.objects.get(apartment=apartment)
    employee = Employee.objects.filter(apartment=apartment)
    rooms = Room.objects.filter(apartment=apartment)
    contracts = LeaseContract.objects.filter(room__in=rooms)
    outcome_per_month = sum(emp.salary for emp in employee)
    total_income = sum(contract.room.price * math.ceil((contract.lease_end - contract.lease_start).days / 30) for contract in contracts)
    duration = 1
    if contracts.count() >= 2:
        lease_start_order = contracts.order_by("lease_start")
        lease_end_order = contracts.order_by("lease_end")
        duration = math.ceil((lease_end_order[lease_end_order.count() - 1].lease_end - lease_start_order[0].lease_start).days / 30)
    income_per_month = total_income/duration
    context = {
        "outcome": outcome_per_month,
        "income": income_per_month,
        "available_count": rooms.filter(status="available").count(),
        "occupied_count": rooms.filter(status="occupied").count(),
        "total_employee": employee.count(),
        "total_salary": f"{outcome_per_month:,.2f}",
        "total_room": rooms.count(),
        "total_contract": contracts.count(),
        "active_count": contracts.filter(lease_end__date__gt=timezone.now()).count(),
        "expired_count": contracts.filter(lease_end__date__lt=timezone.now()).count(),
        "total_income": f"{total_income:,.2f}",
        "avg_income": f"{income_per_month:,.2f}",
        "apartment": apartment,
        "location": location,
    }

    return render(request, "landlord/apartment.html", context=context)