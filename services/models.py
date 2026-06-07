from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

# ─── Service Category ─────────────────────────────────────────────────────────
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🔧')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"

# ─── Service ──────────────────────────────────────────────────────────────────
class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_hours = models.IntegerField(default=1)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ─── UserProfile ──────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

# ─── OTP Verification ─────────────────────────────────────────────────────────
class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)

    @classmethod
    def generate_otp(cls, email):
        cls.objects.filter(email=email, is_used=False).update(is_used=True)
        otp = str(random.randint(100000, 999999))
        return cls.objects.create(email=email, otp=otp)

    def __str__(self):
        return f"OTP for {self.email}"

# ─── Employee ─────────────────────────────────────────────────────────────────
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    phone = models.CharField(max_length=15)
    services = models.ManyToManyField(Service, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_jobs = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Employee: {self.user.get_full_name() or self.user.username}"

# ─── Slot ─────────────────────────────────────────────────────────────────────
class Slot(models.Model):
    SLOT_CHOICES = [
        ('10:00-11:00', '10:00 AM – 11:00 AM'),
        ('11:00-12:00', '11:00 AM – 12:00 PM'),
        ('12:00-13:00', '12:00 PM – 1:00 PM'),
        ('13:00-14:00', '1:00 PM – 2:00 PM'),
        ('14:00-15:00', '2:00 PM – 3:00 PM'),
        ('15:00-16:00', '3:00 PM – 4:00 PM'),
        ('16:00-17:00', '4:00 PM – 5:00 PM'),
    ]
    time_slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='slots')
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['time_slot', 'date', 'employee']

    def __str__(self):
        return f"{self.date} {self.time_slot} - {self.employee}"

# ─── Booking ──────────────────────────────────────────────────────────────────
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('confirmed',   'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service          = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee         = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date     = models.DateField()
    time_slot        = models.CharField(max_length=20)
    address          = models.TextField()
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    problem_description      = models.TextField(blank=True)
    problem_photo            = models.ImageField(upload_to='proofs/before/',  blank=True, null=True)
    completion_photo         = models.ImageField(upload_to='proofs/after/',   blank=True, null=True)

    # ── CHANGE 1: Two-way verification ────────────────────────────────────────
    user_verification_photo  = models.ImageField(upload_to='proofs/verify/',  blank=True, null=True)
    user_verified            = models.BooleanField(default=False)
    # ──────────────────────────────────────────────────────────────────────────

    total_amount     = models.DecimalField(max_digits=8, decimal_places=2)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.service.name}"

# ─── Payment ──────────────────────────────────────────────────────────────────
class Payment(models.Model):
    STATUS_CHOICES = [
        ('created',  'Created'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]
    booking              = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    razorpay_order_id    = models.CharField(max_length=100, blank=True)
    razorpay_payment_id  = models.CharField(max_length=100, blank=True)
    razorpay_signature   = models.CharField(max_length=200, blank=True)
    amount               = models.DecimalField(max_digits=8, decimal_places=2)
    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    is_test_mode         = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    paid_at              = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.status} - ₹{self.amount}"

# ─── Invoice ──────────────────────────────────────────────────────────────────
class Invoice(models.Model):
    booking        = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=20, unique=True)
    generated_at   = models.DateTimeField(auto_now_add=True)
    total_amount   = models.DecimalField(max_digits=8, decimal_places=2)
    gst_amount     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_amount   = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{self.booking.id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number

# ─── Rating & Review ──────────────────────────────────────────────────────────
class Review(models.Model):
    booking  = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews')
    rating   = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        reviews = Review.objects.filter(employee=self.employee)
        avg = sum(r.rating for r in reviews) / reviews.count()
        self.employee.rating = round(avg, 2)
        self.employee.save()

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating}★"

# ─── Civic Complaint ──────────────────────────────────────────────────────────
class CivicComplaint(models.Model):
    TYPE_CHOICES = [
        ('gas',         'Gas Booking'),
        ('water',       'Water Tanker Request'),
        ('garbage',     'Garbage Complaint'),
        ('streetlight', 'Streetlight Complaint'),
        ('electricity', 'Electricity Complaint'),
        ('other',       'Other'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('resolved',  'Resolved'),
        ('rejected',  'Rejected'),
    ]
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='civic_complaints')
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description    = models.TextField()
    address        = models.TextField()
    photo          = models.ImageField(upload_to='civic/', blank=True, null=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at     = models.DateTimeField(auto_now_add=True)
    resolved_at    = models.DateTimeField(null=True, blank=True)
    admin_note     = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_complaint_type_display()} by {self.user.username}"

# ─── Notification ─────────────────────────────────────────────────────────────
class Notification(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.title} → {self.user.username}"

# ─── Admin Log ────────────────────────────────────────────────────────────────
class AdminLog(models.Model):
    admin      = models.ForeignKey(User, on_delete=models.CASCADE)
    action     = models.CharField(max_length=200)
    details    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username}: {self.action}"