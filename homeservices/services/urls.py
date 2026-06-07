from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',          views.home,         name='home'),
    path('services/', views.service_list, name='service_list'),

    # Registration
    path('register/',    views.register,    name='register'),
    path('verify-otp/',  views.verify_otp,  name='verify_otp'),
    path('resend-otp/',  views.resend_otp,  name='resend_otp'),

    # Login / Logout
    path('login/',  views.user_login,  name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Forgot Password (3 steps)
    path('forgot-password/',        views.forgot_password,     name='forgot_password'),
    path('forgot-password/otp/',    views.forgot_password_otp, name='forgot_password_otp'),
    path('forgot-password/reset/',  views.reset_password,      name='reset_password'),
    path('forgot-password/resend/', views.resend_reset_otp,    name='resend_reset_otp'),

    # User pages
    path('dashboard/',   views.dashboard,   name='dashboard'),
    path('profile/',     views.profile,     name='profile'),
    path('bookings/',    views.my_bookings, name='my_bookings'),
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('payment/<int:booking_id>/',        views.payment,         name='payment'),
    path('payment/success/',                 views.payment_success, name='payment_success'),
    path('payment/error/',                   views.payment_error,   name='payment_error'),
    path('invoice/<int:booking_id>/',        views.invoice,         name='invoice'),
    path('rate/<int:booking_id>/',           views.rate_employee,   name='rate_employee'),
    path('verify-work/<int:booking_id>/',    views.user_verify_work, name='user_verify_work'),

    # Civic
    path('civic/',     views.civic_complaint, name='civic_complaint'),
    path('civic/my/',  views.my_complaints,   name='my_complaints'),

    # Employee
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/job/<int:booking_id>/update/', views.update_job_status, name='update_job_status'),

    # Admin
    path('admin-panel/',                              views.admin_dashboard,        name='admin_dashboard'),
    path('admin-panel/assign/<int:booking_id>/',      views.admin_assign_employee,  name='admin_assign_employee'),
    path('admin-panel/complaint/<int:complaint_id>/resolve/', views.admin_resolve_complaint, name='admin_resolve_complaint'),

    # API
    path('api/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]