from django import template
import math

register = template.Library()

@register.filter
def calculate_price(contract):
    lease_duration_days = (contract.lease_end - contract.lease_start).days
    return f"{contract.room.price * math.ceil(lease_duration_days/30):,.2f}"
