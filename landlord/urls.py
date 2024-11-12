from django.urls import path
from .views import detail_page, employee_page, add_employee, delete_employee, edit_employee

app_name = "landlord"
urlpatterns = [
    path("home/", detail_page, name="home"),
    path("employee/", employee_page, name="employee"),
    path("add_employee/", add_employee, name="add_employee"),
    path("delete_employee/<int:employee_id>", delete_employee, name="delete_employee"),
    path("edit_employee/<int:employee_id>", edit_employee, name="edit_employee"),
]