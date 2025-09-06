from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'quantity', 'customer_name', 'customer_email', 'status', 'created_at')
