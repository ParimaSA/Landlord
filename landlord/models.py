from django.db import models
from django.contrib.auth.models import User


class Apartment(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class ApartmentLocation(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)


class Employee(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    salary = models.IntegerField()
    occupation = models.CharField(max_length=255)


class RoomType(models.Model):
    name = models.CharField(max_length=255, default="")
    room_size = models.CharField(max_length=255)
    bedroom_amount = models.IntegerField()
    bathroom_amount = models.IntegerField()
    kitchen_amount = models.IntegerField()
    furnishing_level = models.CharField(max_length=255)


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, null=True, blank=True)


class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
    ]
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    number = models.CharField(max_length=255, default="")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    price = models.IntegerField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='available')


class LeaseContract(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    lease_start = models.DateTimeField()
    lease_end = models.DateTimeField()


class Parking(models.Model):
    zone = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    plate_number = models.IntegerField()
