from pyexpat.errors import messages

from django.shortcuts import render, redirect
from django.db.models import Min, Max, Avg, Sum
from matplotlib.style.core import context
from numpy.ma.extras import average
from socks import method

from .models import Employee, Apartment, Room, Tenant


def detail_page(request):
    return render(request, "landlord/home.html")


def employee_page(request):
    condition = {}
    name_filter = request.GET.get('filter')
    occupation_filter = request.GET.get('occupation')
    salary_filter = request.GET.get('salary')

    if name_filter:
        condition["name__icontains"] = name_filter
    if occupation_filter:
        condition["occupation"] = occupation_filter
    if salary_filter:
        condition["salary__lt"] = salary_filter

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
        'employee': employee,
        'num_employee': employee.count(),
        'current_occ': occupation_filter,
        'current_sal': current_sal,
        'occupations': occupations,
        'min_salary': str(min_salary),
        'max_salary': str(max_salary),
        'avg_this_salary': f"{average_this_salary:,.2f}",
        'sum_this_salary': f"{sum_this_salary:,.2f}",
        'min_this_salary': f"{min_this_salary:,.2f}",
        'max_this_salary': f"{max_this_salary:,.2f}"
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
    if name_filter:
        condition["name__icontains"] = name_filter
    tenants = Tenant.objects.filter(**condition)
    context = {
        "tenants": tenants,
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
    room = Room.objects.all()
    return render(request, "landlord/room.html")