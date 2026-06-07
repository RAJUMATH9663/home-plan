import re
from django import forms
from django.contrib.auth.models import User
from .models import Booking, Review, CivicComplaint, UserProfile
from django.utils import timezone


class RegisterForm(forms.Form):

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name (letters only)',
            'class': 'form-control',
        })
    )

    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name (letters only)',
            'class': 'form-control',
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-control',
        })
    )

    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Mobile Number (10 digits, starts with 6/7/8/9)',
            'class': 'form-control',
            'maxlength': '10',
            'inputmode': 'numeric',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password (min 8, A-Z, a-z, 0-9, special)',
            'class': 'form-control',
        })
    )

    confirm_pass = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        })
    )

    def clean_first_name(self):
        value = self.cleaned_data.get('first_name', '').strip()
        if not re.match(r'^[a-zA-Z]+$', value):
            raise forms.ValidationError(
                'First name must contain letters only. No numbers or special characters.'
            )
        return value

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name', '').strip()
        if not re.match(r'^[a-zA-Z]+$', value):
            raise forms.ValidationError(
                'Last name must contain letters only. No numbers or special characters.'
            )
        return value

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email is already registered. Please login.'
            )
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain digits only.')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        if phone[0] not in ('6', '7', '8', '9'):
            raise forms.ValidationError(
                'Invalid Indian mobile number. Must start with 6, 7, 8, or 9.'
            )
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        errors = []
        if len(password) < 8:
            errors.append('minimum 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('1 uppercase letter (A-Z)')
        if not re.search(r'[a-z]', password):
            errors.append('1 lowercase letter (a-z)')
        if not re.search(r'[0-9]', password):
            errors.append('1 number (0-9)')
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append('1 special character (!@#$%)')
        if errors:
            raise forms.ValidationError('Password needs: ' + ' | '.join(errors))
        return password

    def clean(self):
        cleaned = super().clean()
        pwd  = cleaned.get('password')
        cpwd = cleaned.get('confirm_pass')
        if pwd and cpwd and pwd != cpwd:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'class': 'form-control otp-input',
            'maxlength': '6',
            'autocomplete': 'off',
            'inputmode': 'numeric',
        })
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
        })
    )


class BookingForm(forms.ModelForm):
    SLOT_CHOICES = [
        ('', 'Select Time Slot'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        ('11:00-12:00', '11:00 AM - 12:00 PM'),
        ('12:00-13:00', '12:00 PM - 1:00 PM'),
        ('13:00-14:00', '1:00 PM - 2:00 PM'),
        ('14:00-15:00', '2:00 PM - 3:00 PM'),
        ('15:00-16:00', '3:00 PM - 4:00 PM'),
        ('16:00-17:00', '4:00 PM - 5:00 PM'),
    ]
    time_slot = forms.ChoiceField(
        choices=SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model  = Booking
        fields = ['booking_date', 'time_slot', 'address',
                  'problem_description', 'problem_photo']
        widgets = {
            'booking_date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control',
                'min': str(timezone.now().date())
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Full service address'
            }),
            'problem_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Describe the issue'
            }),
            'problem_photo': forms.FileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model  = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }


class CivicComplaintForm(forms.ModelForm):
    class Meta:
        model  = CivicComplaint
        fields = ['complaint_type', 'description', 'address', 'photo']
        widgets = {
            'complaint_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Describe the issue in detail'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Location / Address'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model  = UserProfile
        fields = ['phone', 'address', 'city', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'maxlength': '10',
                'placeholder': '10-digit mobile number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2
            }),
            'city':          forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError('Phone must contain digits only.')
            if len(phone) != 10:
                raise forms.ValidationError('Phone must be exactly 10 digits.')
            if phone[0] not in ('6', '7', '8', '9'):
                raise forms.ValidationError('Must start with 6, 7, 8, or 9.')
        return phone


class CompletionPhotoForm(forms.Form):
    completion_photo = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control', 'accept': 'image/*'
        })
    )