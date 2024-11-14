from django.urls import path, include
from .views import (detail_page, employee_page, add_employee, delete_employee, edit_employee,
                    tenant_page, add_tenant, delete_tenant, edit_tenant,
                    room_page, add_room, delete_room, edit_room,
                    parking_page, add_parking, delete_parking, edit_parking)

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
    path("room/", room_page, name="room"),
    path("add_room/", add_room, name="add_room"),
    path("delete_room/<int:room_id>", delete_room, name="delete_room"),
    path("edit_room/<int:room_id>", edit_room, name="edit_room"),
    path("parking/", parking_page, name="parking"),
    path("add_parking/", add_parking, name="add_parking"),
    path("delete_parking/<int:parking_id>", delete_parking, name="delete_parking"),
    path("edit_parking/<int:parking_id>", edit_parking, name="edit_parking"),
]