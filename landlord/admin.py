from django.contrib import admin
from .models import Apartment, ApartmentLocation, Tenant, Employee,  Room, RoomType, Parking, LeaseContract

admin.site.register(Apartment)
admin.site.register(ApartmentLocation)
admin.site.register(Tenant)
admin.site.register(Employee)
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(Parking)
admin.site.register(LeaseContract)


# class CustomUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('first_name', 'last_name')}),
#     )
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#
# # Register the User model with the custom admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)