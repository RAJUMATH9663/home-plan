from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import re, random

from .models import *
from .forms import *


def get_razorpay_client():
    import razorpay
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def send_otp_email(email, otp, subject=None, body=None):
    try:
        send_mail(
            subject=subject or 'Your HomeServices OTP',
            message=body or f'Your OTP is: {otp}\n\nValid for 10 minutes.\n\n- HomeServices',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error for {email}: {e}")
        return False

def store_otp_preview(request, email, otp, delivered):
    request.session['otp_preview'] = {
        'email': email,
        'otp': otp,
        'delivered': delivered,
    }

def is_admin(user):
    return user.is_staff or user.is_superuser

def is_employee(user):
    return hasattr(user, 'employee')


# ════════════════════════════════════════════════════════
#  HOME
# ════════════════════════════════════════════════════════
def home(request):
    services   = Service.objects.filter(is_active=True)[:8]
    categories = ServiceCategory.objects.all()
    return render(request, 'home.html', {'services': services, 'categories': categories})


# ════════════════════════════════════════════════════════
#  REGISTER
# ════════════════════════════════════════════════════════
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    errors = {}

    if request.method == 'POST':
        first_name   = request.POST.get('first_name',   '').strip()
        last_name    = request.POST.get('last_name',    '').strip()
        email        = request.POST.get('email',        '').strip()
        phone        = request.POST.get('phone',        '').strip()
        password     = request.POST.get('password',     '')
        confirm_pass = request.POST.get('confirm_pass', '')

        if not first_name:
            errors['first_name'] = 'First name is required.'
        elif not re.match(r'^[a-zA-Z]+$', first_name):
            errors['first_name'] = 'First name must contain letters only.'

        if not last_name:
            errors['last_name'] = 'Last name is required.'
        elif not re.match(r'^[a-zA-Z]+$', last_name):
            errors['last_name'] = 'Last name must contain letters only.'

        if not email:
            errors['email'] = 'Email is required.'
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = 'Enter a valid email address.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'This email is already registered. Please login.'

        if not phone:
            errors['phone'] = 'Phone number is required.'
        elif not phone.isdigit():
            errors['phone'] = 'Phone number must contain digits only.'
        elif len(phone) != 10:
            errors['phone'] = f'Phone must be exactly 10 digits.'
        elif phone[0] not in ('6', '7', '8', '9'):
            errors['phone'] = 'Invalid Indian number. Must start with 6, 7, 8, or 9.'

        if not password:
            errors['password'] = 'Password is required.'
        else:
            pwd_errors = []
            if len(password) < 8:
                pwd_errors.append('minimum 8 characters')
            if not re.search(r'[A-Z]', password):
                pwd_errors.append('1 uppercase letter (A-Z)')
            if not re.search(r'[a-z]', password):
                pwd_errors.append('1 lowercase letter (a-z)')
            if not re.search(r'[0-9]', password):
                pwd_errors.append('1 number (0-9)')
            if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', password):
                pwd_errors.append('1 special character like !@#$%')
            if pwd_errors:
                errors['password'] = 'Password needs: ' + ' | '.join(pwd_errors)

        if not confirm_pass:
            errors['confirm_pass'] = 'Please confirm your password.'
        elif password and not errors.get('password') and password != confirm_pass:
            errors['confirm_pass'] = 'Passwords do not match.'

        if not errors:
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name':  last_name,
                'email':      email,
                'phone':      phone,
                'password':   password,
            }
            otp_obj = OTPVerification.generate_otp(email)
            sent    = send_otp_email(email, otp_obj.otp)
            store_otp_preview(request, email, otp_obj.otp, sent)
            if sent:
                messages.success(request, f'OTP sent to {email}')
            else:
                messages.info(request, f'[TEST MODE] OTP: {otp_obj.otp}')
            return redirect('verify_otp')

        return render(request, 'register.html', {'errors': errors, 'post': request.POST})

    return render(request, 'register.html', {'errors': {}, 'post': {}})


def verify_otp(request):
    reg_data = request.session.get('reg_data')
    if not reg_data:
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        email       = reg_data['email']
        try:
            otp_obj = OTPVerification.objects.filter(
                email=email, otp=entered_otp, is_used=False
            ).latest('created_at')
            if otp_obj.is_valid():
                otp_obj.is_used = True
                otp_obj.save()
                username = email.split('@')[0]
                base = username; i = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base}{i}"; i += 1
                user = User.objects.create_user(
                    username=username, email=email,
                    password=reg_data['password'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                )
                UserProfile.objects.create(
                    user=user, phone=reg_data['phone'], is_verified=True
                )
                del request.session['reg_data']
                request.session.pop('otp_preview', None)
                login(request, user)
                messages.success(request, f"Welcome {user.first_name}! Account created.")
                return redirect('dashboard')
            else:
                messages.error(request, 'OTP expired. Please register again.')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_otp.html', {
        'email': reg_data.get('email', ''),
        'otp_preview': request.session.get('otp_preview'),
    })


def resend_otp(request):
    reg_data = request.session.get('reg_data')
    if reg_data:
        otp_obj = OTPVerification.generate_otp(reg_data['email'])
        sent    = send_otp_email(reg_data['email'], otp_obj.otp)
        store_otp_preview(request, reg_data['email'], otp_obj.otp, sent)
        if sent:
            messages.success(request, 'New OTP sent.')
        else:
            messages.info(request, f'[TEST MODE] New OTP: {otp_obj.otp}')
    return redirect('verify_otp')


# ════════════════════════════════════════════════════════
#  LOGIN / LOGOUT
# ════════════════════════════════════════════════════════
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username'].strip()
            pwd   = form.cleaned_data['password']
            if '@' in uname:
                try:
                    uname = User.objects.get(email=uname).username
                except User.DoesNotExist:
                    pass
            user = authenticate(request, username=uname, password=pwd)
            if user:
                login(request, user)
                if is_admin(user):    return redirect('admin_dashboard')
                if is_employee(user): return redirect('employee_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


# ════════════════════════════════════════════════════════
#  FORGOT PASSWORD
# ════════════════════════════════════════════════════════
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'forgot_password.html')
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No account found with this email.')
            return render(request, 'forgot_password.html')
        otp = str(random.randint(100000, 999999))
        request.session['reset_email']    = email
        request.session['reset_otp']      = otp
        request.session['reset_verified'] = False
        sent = send_otp_email(email, otp,
            subject='HomeServices — Password Reset OTP',
            body=f'Your password reset OTP is: {otp}\n\nValid for 10 minutes.')
        store_otp_preview(request, email, otp, sent)
        if sent:
            messages.success(request, f'OTP sent to {email}')
        else:
            messages.info(request, f'[TEST MODE] Reset OTP: {otp}')
        return redirect('forgot_password_otp')
    return render(request, 'forgot_password.html')


def forgot_password_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    if request.method == 'POST':
        entered = request.POST.get('otp', '').strip()
        saved   = request.session.get('reset_otp', '')
        if entered == saved:
            request.session['reset_verified'] = True
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'forgot_password_otp.html', {'email': email})


def reset_password(request):
    email    = request.session.get('reset_email')
    verified = request.session.get('reset_verified', False)
    if not email or not verified:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('forgot_password')
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_pass', '')
        pwd_errors = []
        if len(password) < 8:           pwd_errors.append('minimum 8 characters')
        if not re.search(r'[A-Z]', password): pwd_errors.append('1 uppercase')
        if not re.search(r'[a-z]', password): pwd_errors.append('1 lowercase')
        if not re.search(r'[0-9]', password): pwd_errors.append('1 number')
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', password):
            pwd_errors.append('1 special character')
        if pwd_errors:
            messages.error(request, 'Password needs: ' + ' | '.join(pwd_errors))
            return render(request, 'reset_password.html')
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        request.session.pop('otp_preview', None)
        for k in ('reset_email', 'reset_otp', 'reset_verified'):
            request.session.pop(k, None)
        messages.success(request, 'Password reset successful! Login with your new password.')
        return redirect('login')
    return render(request, 'reset_password.html')


def resend_reset_otp(request):
    email = request.session.get('reset_email')
    if email:
        otp = str(random.randint(100000, 999999))
        request.session['reset_otp'] = otp
        sent = send_otp_email(email, otp,
            subject='HomeServices — New Reset OTP',
            body=f'Your new OTP is: {otp}\n\nValid for 10 minutes.')
        if sent:
            messages.success(request, 'New OTP sent.')
        else:
            messages.info(request, f'[TEST MODE] New OTP: {otp}')
    return redirect('forgot_password_otp')


# ════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════
@login_required
def dashboard(request):
    if is_admin(request.user):    return redirect('admin_dashboard')
    if is_employee(request.user): return redirect('employee_dashboard')
    bookings      = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]
    complaints    = CivicComplaint.objects.filter(user=request.user).order_by('-created_at')[:3]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    services      = Service.objects.filter(is_active=True)[:6]
    return render(request, 'dashboard.html', {
        'bookings':           bookings,
        'complaints':         complaints,
        'notifications':      notifications,
        'services':           services,
        'total_bookings':     Booking.objects.filter(user=request.user).count(),
        'completed_bookings': Booking.objects.filter(user=request.user, status='completed').count(),
    })


def service_list(request):
    categories = ServiceCategory.objects.prefetch_related('services').all()
    return render(request, 'service_list.html', {'categories': categories})


# ════════════════════════════════════════════════════════
#  BOOK SERVICE
#  CHANGE 1: User uploads BEFORE photo of the problem
# ════════════════════════════════════════════════════════
ALL_SLOTS = [
    ('10:00-11:00', '10:00 AM - 11:00 AM', 10),
    ('11:00-12:00', '11:00 AM - 12:00 PM', 11),
    ('12:00-13:00', '12:00 PM - 1:00 PM',  12),
    ('13:00-14:00', '1:00 PM  - 2:00 PM',  13),
    ('14:00-15:00', '2:00 PM  - 3:00 PM',  14),
    ('15:00-16:00', '3:00 PM  - 4:00 PM',  15),
    ('16:00-17:00', '4:00 PM  - 5:00 PM',  16),
]

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)

    now          = timezone.localtime(timezone.now())
    today_str    = now.strftime('%Y-%m-%d')
    current_hour = now.hour

    def build_slots(selected_date_str):
        is_today = (selected_date_str == today_str)
        return [
            {
                'value':    v,
                'label':    l,
                'disabled': is_today and h <= current_hour,
            }
            for v, l, h in ALL_SLOTS
        ]

    if request.method == 'POST':
        chosen_date = request.POST.get('booking_date', today_str)
        chosen_slot = request.POST.get('time_slot', '')
        slots       = build_slots(chosen_date)

        # Block past slots server-side
        if chosen_date == today_str:
            slot_hour = next((h for v, l, h in ALL_SLOTS if v == chosen_slot), None)
            if slot_hour is not None and slot_hour <= current_hour:
                messages.error(request, f'The {chosen_slot} slot has already passed.')
                return render(request, 'book_service.html', {
                    'service': service, 'form': BookingForm(request.POST, request.FILES),
                    'slots': slots, 'today': today_str, 'current_hour': current_hour,
                })

        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking              = form.save(commit=False)
            booking.user         = request.user
            booking.service      = service
            booking.total_amount = service.price
            booking.status       = 'pending'
            booking.employee     = None
            booking.save()
            
            # Create Payment object for this booking
            Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_amount,
                    'status': 'created',
                    'is_test_mode': True
                }
            )

            # Notify USER
            Notification.objects.create(
                user=request.user,
                title="Booking Received",
                message=(
                    f"Your booking for {service.name} on {booking.booking_date} "
                    f"at {booking.time_slot} is received. "
                    f"Please complete payment. Admin will assign an expert employee."
                )
            )
            # Notify ALL ADMINS
            for admin_user in User.objects.filter(is_staff=True):
                Notification.objects.create(
                    user=admin_user,
                    title=f"New Booking — {service.name}",
                    message=(
                        f"New booking from {request.user.get_full_name() or request.user.username}. "
                        f"Service: {service.name} | Date: {booking.booking_date} | "
                        f"Slot: {booking.time_slot}. Please assign an expert employee."
                    )
                )
            messages.success(request, "Booking received! Please complete payment.")
            return redirect('payment', booking_id=booking.id)

    else:
        form  = BookingForm()
        slots = build_slots(today_str)

    return render(request, 'book_service.html', {
        'service':      service,
        'form':         form,
        'slots':        slots,
        'today':        today_str,
        'current_hour': current_hour,
    })


@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if already paid
    if hasattr(booking, 'payment') and booking.payment.status == 'paid':
        return redirect('invoice', booking_id=booking.id)
    
    # Ensure Payment object exists
    payment_obj, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_amount,
            'status': 'created',
            'is_test_mode': True
        }
    )

    # Development mode: bypass Razorpay for testing
    is_dev_mode = settings.DEBUG and request.GET.get('dev_bypass') == 'true'
    
    if is_dev_mode:
        print(f'[DEV MODE] Bypassing Razorpay for booking {booking_id}')
        return render(request, 'payment.html', {
            'booking': booking,
            'razorpay_order_id': f'dev_order_{booking.id}',
            'razorpay_key_id': 'dev_key',
            'amount': int(booking.total_amount * 100),
            'amount_display': booking.total_amount,
            'is_test_mode': True,
            'prefill_phone': '',
            'payment_ready': True,
            'payment_init_error': '',
            'is_dev_mode': True,
        })

    # Razorpay may hide UPI collect (UPI ID entry) when contact is missing.
    user_phone = ''
    if hasattr(request.user, 'profile') and request.user.profile.phone:
        digits_only = ''.join(ch for ch in request.user.profile.phone if ch.isdigit())
        if len(digits_only) >= 10:
            user_phone = digits_only[-10:]

    client       = get_razorpay_client()
    amount_paise = int(booking.total_amount * 100)
    
    print(f'=== RAZORPAY DEBUG INFO ===')
    print(f'Razorpay KEY_ID: {settings.RAZORPAY_KEY_ID}')
    print(f'Razorpay KEY_ID Length: {len(settings.RAZORPAY_KEY_ID)}')
    print(f'Razorpay KEY_SECRET Length: {len(settings.RAZORPAY_KEY_SECRET)}')
    print(f'Amount in paise: {amount_paise}')
    print(f'===========================')
    
    try:
        print(f'Creating Razorpay order for booking {booking.id}, amount: {amount_paise}')
        print(f'Razorpay KEY_ID: {settings.RAZORPAY_KEY_ID[:20]}...')
        
        order = client.order.create({
            'amount': amount_paise, 
            'currency': 'INR',
            'payment_capture': 1, 
            'notes': {'booking_id': str(booking.id)}
        })
        print(f'Razorpay order created successfully: {order["id"]}')
        
        # Update existing payment with Razorpay order ID
        payment_obj.razorpay_order_id = order['id']
        payment_obj.amount = booking.total_amount
        payment_obj.status = 'created'
        payment_obj.is_test_mode = True
        payment_obj.save()
        
        return render(request, 'payment.html', {
            'booking': booking, 'razorpay_order_id': order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount_paise, 'amount_display': booking.total_amount,
            'is_test_mode': settings.RAZORPAY_TEST_MODE,
            'prefill_phone': user_phone,
            'payment_ready': True,
            'payment_init_error': '',
            'is_dev_mode': False,
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f'ERROR creating Razorpay order: {error_msg}')
        print(f'Error type: {type(e).__name__}')
        traceback.print_exc()
        
        # Check if credentials are the issue
        if 'Invalid request' in error_msg or 'Unauthorized' in error_msg or 'authentication' in error_msg.lower():
            error_msg = '⚠️ Invalid Razorpay credentials. Please check your .env file. KEY_ID and KEY_SECRET must be valid.'
        elif 'connection' in error_msg.lower():
            error_msg = 'Cannot connect to Razorpay. Check your internet connection or Razorpay is down.'
        
        # Show a helpful error on the page while logging full details to console
        return render(request, 'payment.html', {
            'booking': booking,
            'razorpay_order_id': '',
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount_paise,
            'amount_display': booking.total_amount,
            'is_test_mode': settings.RAZORPAY_TEST_MODE,
            'prefill_phone': user_phone,
            'payment_ready': False,
            'payment_init_error': error_msg,
            'is_dev_mode': False,
        })


@csrf_exempt
@login_required
def payment_success(request):
    import razorpay
    if request.method == 'POST':
        data   = request.POST
        
        # Check if this is a demo mode payment
        is_demo_payment = (data.get('razorpay_payment_id', '').startswith('demo_payment_') and 
                          data.get('razorpay_signature', '').startswith('demo_'))
        
        if is_demo_payment:
            print(f'[DEMO MODE] Processing demo payment for booking {data.get("booking_id")}')
        
        client = get_razorpay_client()
        try:
            # Skip signature verification for demo payments
            if not is_demo_payment:
                client.utility.verify_payment_signature({
                    'razorpay_order_id':   data.get('razorpay_order_id'),
                    'razorpay_payment_id': data.get('razorpay_payment_id'),
                    'razorpay_signature':  data.get('razorpay_signature'),
                })
                print(f'Razorpay signature verified for payment {data.get("razorpay_payment_id")}')
            
            booking = get_object_or_404(Booking, id=data.get('booking_id'), user=request.user)
            
            # Ensure payment object exists
            pay, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_amount,
                    'status': 'created',
                    'is_test_mode': True
                }
            )
            
            pay.razorpay_payment_id = data.get('razorpay_payment_id', '')
            pay.razorpay_signature  = data.get('razorpay_signature', '')
            pay.razorpay_order_id   = data.get('razorpay_order_id', '')
            pay.status  = 'paid'
            pay.paid_at = timezone.now()
            pay.save()
            
            booking.status = 'pending'
            booking.save()
            
            total = booking.total_amount
            gst   = round(float(total) * 18 / 118, 2)
            base  = round(float(total) - gst, 2)
            
            Invoice.objects.get_or_create(
                booking=booking,
                defaults={'total_amount': base, 'gst_amount': gst, 'final_amount': total}
            )
            
            Notification.objects.create(
                user=request.user, title="Payment Successful",
                message=f"Payment of Rs.{total} received. Admin will assign your employee soon."
            )
            
            for admin_user in User.objects.filter(is_staff=True):
                Notification.objects.create(
                    user=admin_user,
                    title=f"Payment Done — Assign Employee Now",
                    message=(
                        f"{request.user.get_full_name() or request.user.username} "
                        f"paid Rs.{total} for {booking.service.name} on {booking.booking_date}. "
                        f"Please assign an expert employee."
                    )
                )
            
            mode_text = " (DEMO MODE)" if is_demo_payment else ""
            messages.success(request, f"Payment successful{mode_text}! Admin will assign your employee shortly.")
            return redirect('my_bookings')
            
        except razorpay.errors.SignatureVerificationError:
            print('Razorpay signature verification failed for data:', dict(data))
            messages.error(request, "Payment verification failed. Signature mismatch.")
            return redirect('dashboard')
        except Exception as e:
            import traceback
            print('Unexpected error in payment_success:', e)
            traceback.print_exc()
            messages.error(request, "Payment verification failed due to server error.")
            return redirect('dashboard')
    return redirect('dashboard')


@csrf_exempt
def payment_error(request):
    """Receive client-side Razorpay payment failure reports and log them to disk and console."""
    import json, datetime
    try:
        # Try to parse JSON body first
        body = request.body.decode('utf-8') if request.body else ''
        try:
            payload = json.loads(body) if body else dict(request.POST)
        except Exception:
            payload = dict(request.POST) if request.POST else body

        print('Payment error report received:', payload)
        # Append to a local log file under project BASE_DIR
        log_path = settings.BASE_DIR / 'payment_errors.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} - {payload}\n")
    except Exception as e:
        print('Failed to record payment error report:', e)
    return JsonResponse({'status': 'ok'})


@login_required
def invoice(request, booking_id):
    booking     = get_object_or_404(Booking, id=booking_id, user=request.user)
    invoice_obj = get_object_or_404(Invoice, booking=booking)
    return render(request, 'invoice.html', {'booking': booking, 'invoice': invoice_obj})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def rate_employee(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='completed')

    # Must verify work first before rating
    if not booking.user_verified:
        messages.error(request, "Please verify the completed work first before rating.")
        return redirect('user_verify_work', booking_id=booking.id)

    if hasattr(booking, 'review'):
        messages.info(request, "You have already submitted a review.")
        return redirect('my_bookings')

    if request.method == 'POST':
        rating  = request.POST.get('rating', '')
        comment = request.POST.get('comment', '').strip()

        if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
            messages.error(request, "Please select a star rating (1 to 5).")
            return render(request, 'rate_employee.html', {'booking': booking})

        review = Review.objects.create(
            booking  = booking,
            user     = request.user,
            employee = booking.employee,
            rating   = int(rating),
            comment  = comment,
        )

        # Notify ADMIN: work completed and verified + rated
        star_display = '★' * int(rating) + '☆' * (5 - int(rating))
        for admin_user in User.objects.filter(is_staff=True):
            Notification.objects.create(
                user=admin_user,
                title=f"Work Verified & Rated — {booking.service.name}",
                message=(
                    f"Booking #{booking.id} is fully complete. "
                    f"Employee: {booking.employee.user.get_full_name() or booking.employee.user.username} | "
                    f"Customer: {request.user.get_full_name() or request.user.username} | "
                    f"Rating: {star_display} ({rating}/5). "
                    f"Customer verified the work with a photo."
                )
            )

        # Notify EMPLOYEE: you got a rating
        Notification.objects.create(
            user=booking.employee.user,
            title=f"New Rating — {rating}/5 Stars",
            message=(
                f"{request.user.get_full_name() or request.user.username} "
                f"rated your work {star_display} for {booking.service.name}. "
                + (f'Comment: "{comment}"' if comment else "No comment added.")
            )
        )

        messages.success(request, f"Thank you! You rated {rating}/5 stars.")
        return redirect('my_bookings')

    return render(request, 'rate_employee.html', {'booking': booking})


# ════════════════════════════════════════════════════════
#  USER VERIFY WORK
#  CHANGE 1 (part 2): User uploads their OWN photo after
#  employee marks job done — two-way verification
# ════════════════════════════════════════════════════════
@login_required
def user_verify_work(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Only allow if employee already completed and uploaded their photo
    if booking.status != 'completed':
        messages.error(request, "Work is not yet completed by the employee.")
        return redirect('my_bookings')

    if booking.user_verification_photo:
        messages.info(request, "You have already verified this work.")
        return redirect('my_bookings')

    if request.method == 'POST':
        photo = request.FILES.get('user_verification_photo')
        if not photo:
            messages.error(request, "Please upload a photo of the completed work.")
            return render(request, 'user_verify_work.html', {'booking': booking})

        booking.user_verification_photo = photo
        booking.user_verified           = True
        booking.save()

        Notification.objects.create(
            user=booking.user,
            title="Work Verified",
            message=(
                f"You have verified the {booking.service.name} work. "
                f"Thank you! Please rate the employee."
            )
        )
        if booking.employee:
            Notification.objects.create(
                user=booking.employee.user,
                title="Work Verified by User",
                message=(
                    f"{booking.user.get_full_name() or booking.user.username} "
                    f"has verified your work for {booking.service.name}."
                )
            )
        messages.success(request, "Work verified! Please rate the employee.")
        return redirect('rate_employee', booking_id=booking.id)

    return render(request, 'user_verify_work.html', {'booking': booking})


@login_required
def civic_complaint(request):
    if request.method == 'POST':
        form = CivicComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.save()
            messages.success(request, "Complaint submitted!")
            return redirect('my_complaints')
    else:
        form = CivicComplaintForm()
    return render(request, 'civic_complaint.html', {'form': form})


@login_required
def my_complaints(request):
    complaints = CivicComplaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_complaints.html', {'complaints': complaints})


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name  = form.cleaned_data['last_name']
            request.user.email      = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name':  request.user.last_name,
            'email':      request.user.email,
        })
    return render(request, 'profile.html', {'form': form, 'profile': profile_obj})


# ════════════════════════════════════════════════════════
#  EMPLOYEE DASHBOARD
# ════════════════════════════════════════════════════════
@login_required
def employee_dashboard(request):
    if not is_employee(request.user):
        return redirect('dashboard')
    emp            = request.user.employee
    all_assigned   = Booking.objects.filter(employee=emp).order_by('-created_at')
    pending_jobs   = all_assigned.filter(status__in=['confirmed', 'in_progress'])
    completed_jobs = all_assigned.filter(status='completed')
    return render(request, 'employee_dashboard.html', {
        'employee':       emp,
        'pending_jobs':   pending_jobs,
        'completed_jobs': completed_jobs,
        'total_jobs':     all_assigned.count(),
        'pending_count':  pending_jobs.count(),
        'done_count':     completed_jobs.count(),
    })


@login_required
def update_job_status(request, booking_id):
    if not is_employee(request.user):
        return redirect('dashboard')
    booking = get_object_or_404(Booking, id=booking_id, employee=request.user.employee)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        photo      = request.FILES.get('completion_photo')

        if new_status == 'in_progress' and booking.status == 'confirmed':
            booking.status = 'in_progress'
            booking.save()
            Notification.objects.create(
                user=booking.user, title="Service Started",
                message=f"Your {booking.service.name} service has started."
            )
            messages.success(request, "Job marked as In Progress.")

        elif new_status == 'completed' and booking.status == 'in_progress':
            if not photo:
                messages.error(request, "Please upload your completion photo.")
                return redirect('employee_dashboard')
            booking.status           = 'completed'
            booking.completion_photo = photo
            booking.save()
            emp = request.user.employee
            emp.total_jobs += 1
            emp.save()
            # Ask user to upload their verification photo too
            Notification.objects.create(
                user=booking.user,
                title="Work Done — Please Verify",
                message=(
                    f"Your {booking.service.name} service is done by "
                    f"{emp.user.get_full_name() or emp.user.username}. "
                    f"Please upload your own photo of the completed work to verify, "
                    f"then rate the service."
                )
            )
            messages.success(request, "Job completed! User has been asked to verify.")

    return redirect('employee_dashboard')


# ════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ════════════════════════════════════════════════════════
@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    import json, calendar
    today = timezone.localtime(timezone.now()).date()
    total_revenue = Payment.objects.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0

    month_labels = []
    month_revenue = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12; y -= 1
        rev = Payment.objects.filter(
            status='paid', paid_at__year=y, paid_at__month=m
        ).aggregate(t=Sum('amount'))['t'] or 0
        month_labels.append(calendar.month_abbr[m])
        month_revenue.append(float(rev))

    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:10]

    return render(request, 'admin_dashboard.html', {
        'total_users':         User.objects.filter(is_staff=False).count(),
        'total_bookings':      Booking.objects.count(),
        'total_revenue':       total_revenue,
        'unassigned_bookings': Booking.objects.filter(
            employee__isnull=True
        ).exclude(status='cancelled').order_by('-created_at'),
        'unassigned_count':    Booking.objects.filter(
            employee__isnull=True
        ).exclude(status='cancelled').count(),
        'recent_bookings':     Booking.objects.select_related(
            'user', 'service', 'employee', 'employee__user'
        ).order_by('-created_at')[:15],
        'complaints':          CivicComplaint.objects.filter(
            status='submitted'
        ).order_by('-created_at')[:5],
        'admin_notifications': notifications,
        'month_labels':        json.dumps(month_labels),
        'month_revenue':       json.dumps(month_revenue),
    })


# ════════════════════════════════════════════════════════
#  ADMIN ASSIGN EMPLOYEE
#  CHANGE 2: Show ONLY employees expert in that service
#            Separate section for others (not experts)
# ════════════════════════════════════════════════════════
@login_required
def admin_assign_employee(request, booking_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    booking = get_object_or_404(Booking, id=booking_id)

    # ── CHANGE 2: Expert employees ONLY for this service ─────────────────────
    expert_employees = Employee.objects.filter(
        is_available=True,
        services=booking.service          # linked to THIS service
    ).order_by('user__first_name')

    # Other available employees (NOT expert in this service)
    other_employees = Employee.objects.filter(
        is_available=True
    ).exclude(
        services=booking.service
    ).order_by('user__first_name')

    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        emp    = get_object_or_404(Employee, id=emp_id)

        booking.employee = emp
        booking.status   = 'confirmed'
        booking.save()

        # Notify USER
        Notification.objects.create(
            user=booking.user,
            title="Employee Assigned — Booking Confirmed!",
            message=(
                f"{emp.user.get_full_name() or emp.user.username} "
                f"(expert in {booking.service.name}) has been assigned. "
                f"Date: {booking.booking_date} | Slot: {booking.time_slot}. "
                f"Your booking is confirmed."
            )
        )
        # Notify EMPLOYEE
        Notification.objects.create(
            user=emp.user,
            title=f"New Job — {booking.service.name}",
            message=(
                f"Admin assigned you a job. "
                f"Service: {booking.service.name} | "
                f"Customer: {booking.user.get_full_name() or booking.user.username} | "
                f"Date: {booking.booking_date} | Slot: {booking.time_slot} | "
                f"Address: {booking.address}"
            )
        )
        messages.success(
            request,
            f"{emp.user.get_full_name() or emp.user.username} assigned. Employee notified."
        )
        return redirect('admin_dashboard')

    return render(request, 'assign_employee.html', {
        'booking':          booking,
        'expert_employees': expert_employees,
        'other_employees':  other_employees,
    })


@login_required
def admin_resolve_complaint(request, complaint_id):
    if not is_admin(request.user):
        return redirect('dashboard')
    complaint = get_object_or_404(CivicComplaint, id=complaint_id)
    if request.method == 'POST':
        complaint.status     = request.POST.get('status', 'resolved')
        complaint.admin_note = request.POST.get('note', '')
        if complaint.status == 'resolved':
            complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, "Complaint updated.")
    return redirect('admin_dashboard')


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})