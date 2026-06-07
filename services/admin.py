from django.contrib import admin
from .models import *

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active']
    list_filter  = ['category', 'is_active']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'rating', 'total_jobs', 'is_available']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'service', 'booking_date', 'time_slot', 'status', 'total_amount']
    list_filter  = ['status', 'booking_date']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'status', 'is_test_mode', 'created_at']
    list_filter  = ['status', 'is_test_mode']

@admin.register(CivicComplaint)
class CivicComplaintAdmin(admin.ModelAdmin):
    list_display = ['user', 'complaint_type', 'status', 'created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee', 'rating', 'created_at']

admin.site.register(UserProfile)
admin.site.register(OTPVerification)
admin.site.register(Invoice)
admin.site.register(Notification)
admin.site.register(AdminLog)
