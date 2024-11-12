from django.shortcuts import render, redirect
from django.db.models import Min, Max, Avg
from numpy.ma.extras import average
from socks import method

from .models import Employee, Apartment


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

    context = {
        'employee': employee,
        'num_employee': employee.count(),
        'current_occ': occupation_filter,
        'current_sal': current_sal,
        'occupations': occupations,
        'min_salary': str(min_salary),
        'max_salary': str(max_salary),
        'avg_this_salary': f"{average_this_salary:.2f}",
        'min_this_salary': f"{min_this_salary:.2f}",
        'max_this_salary': f"{max_this_salary:.2f}"
    }
    return render(request, "landlord/employee.html", context=context)


def add_employee(request):
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