from django.urls import path
from .views import (detail_page, employee_page, add_employee, delete_employee, edit_employee,
                    tenant_page, add_tenant, delete_tenant, edit_tenant)

app_name = "landlord"
urlpatterns = [
    path("home/", detail_page, name="home"),
    path("employee/", employee_page, name="employee"),
    path("add_employee/", add_employee, name="add_employee"),
    path("delete_employee/<int:employee_id>", delete_employee, name="delete_employee"),
    path("edit_employee/<int:employee_id>", edit_employee, name="edit_employee"),
    path("tenant/", tenant_page, name="tenant"),
    path("add_tenant/", add_tenant, name="add_tenant"),
    path("delete_tenant/<int:tenant_id>", delete_tenant, name="delete_tenant"),
    path("edit_tenant/<int:tenant_id>", edit_tenant, name="edit_tenant"),

]