# 🏠 HomeServices – Integrated Home Services Platform

> **BCA Final Year Project** | Django + MySQL + Razorpay Test Mode

---

## 📋 Project Features

| Feature | Status |
|---------|--------|
| Email OTP Verification | ✅ |
| User / Employee / Admin Roles | ✅ |
| Service Booking with Slot Selection (10AM–5PM) | ✅ |
| Razorpay Payment – **TEST MODE** | ✅ |
| Photo Proof Verification | ✅ |
| Digital Invoice with PDF Print | ✅ |
| Star Rating & Review System | ✅ |
| Civic Complaint Submission | ✅ |
| Admin Dashboard | ✅ |
| Employee Job Management | ✅ |
| MySQL Database | ✅ |
| Modern Glassmorphism UI | ✅ |

---

## 🚀 STEP-BY-STEP SETUP

### Step 1 – Install Python packages
```bash
pip install -r requirements.txt
```
This project now uses `PyMySQL` by default so Windows setup does not depend on compiling `mysqlclient`.

If you are using Python 3.13, the dependency versions in `requirements.txt` are already adjusted for it.

---

### Step 2 – Create MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE homeservices_db CHARACTER SET utf8mb4;
```
Or run the provided file from PowerShell:
```bash
Get-Content .\setup.sql | mysql -u root -p
```

If you are using Command Prompt instead of PowerShell, this also works:
```bash
mysql -u root -p < setup.sql
```

---

### Step 3 – Configure Settings
Open `homeservices/settings.py` and change:

```python
# MySQL Password
'PASSWORD': 'your_mysql_password',   # ← your MySQL root password

# Email (for OTP)
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'

# Razorpay TEST Keys (from https://dashboard.razorpay.com)
RAZORPAY_KEY_ID = 'rzp_test_XXXXXXXXXX'
RAZORPAY_KEY_SECRET = 'XXXXXXXXXX'
```

> 💡 **If email is not configured**, OTP will be shown on-screen in test mode banner.

---

### Step 4 – Run Django Migrations
```bash
cd homeservices
python manage.py makemigrations
python manage.py migrate
```

---

### Step 5 – Create Admin User
```bash
python manage.py createsuperuser
```
Enter username, email, password when prompted.

---

### Step 6 – Seed Sample Data (Services)
```bash
python manage.py seed_data
```

---

### Step 7 – Run the Server
```bash
python manage.py runserver
```

Open browser: **http://127.0.0.1:8000**

---

## 🔑 Default Login URLs

| Role | URL | Credentials |
|------|-----|-------------|
| Home | http://127.0.0.1:8000 | — |
| Register | http://127.0.0.1:8000/register/ | Email OTP |
| Login | http://127.0.0.1:8000/login/ | — |
| Admin Panel | http://127.0.0.1:8000/admin-panel/ | Superuser |
| Django Admin | http://127.0.0.1:8000/admin/ | Superuser |

---

## 👷 Creating an Employee Account

1. Go to **http://127.0.0.1:8000/admin/**
2. Click **Users → Add User** → create username + password
3. Go to **Services → Employees → Add Employee**
4. Link the user you just created
5. Employee can now login at http://127.0.0.1:8000/login/

---

## 💳 Razorpay Test Mode Payment

### Test Card Details:
```
Card Number : 4111 1111 1111 1111
Expiry      : Any future date (e.g. 12/27)
CVV         : Any 3 digits (e.g. 123)
OTP         : 1234
```

### Where to get Test Keys:
1. Go to https://dashboard.razorpay.com
2. Register / Login
3. Switch to **Test Mode** (toggle in top bar)
4. Go to Settings → API Keys → Generate Key
5. Copy **Key ID** and **Key Secret** to settings.py

---

## 🗄️ Database Tables (20 Tables)

| # | Table | Purpose |
|---|-------|---------|
| 1 | Users (Django built-in) | Authentication |
| 2 | UserProfile | Extended user info |
| 3 | OTPVerification | Email OTP |
| 4 | ServiceCategory | Service categories |
| 5 | Service | Available services |
| 6 | Employee | Worker profiles |
| 7 | Slot | Time slot management |
| 8 | Booking | Service bookings |
| 9 | Payment | Razorpay transactions |
| 10 | Invoice | Generated invoices |
| 11 | Review | Star ratings |
| 12 | CivicComplaint | Municipal complaints |
| 13 | Notification | User notifications |
| 14 | AdminLog | Admin activity log |

---

## 📁 Project Structure

```
homeservices/
├── homeservices/
│   ├── settings.py       ← Config (DB, Razorpay, Email)
│   ├── urls.py
│   └── wsgi.py
├── services/
│   ├── models.py         ← All database models
│   ├── views.py          ← All page logic
│   ├── urls.py           ← URL routes
│   ├── forms.py          ← All forms
│   ├── admin.py          ← Django admin config
│   └── management/commands/seed_data.py
├── templates/            ← All HTML pages
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── dashboard.html
│   ├── service_list.html
│   ├── book_service.html
│   ├── payment.html      ← Razorpay Test Mode
│   ├── invoice.html
│   ├── my_bookings.html
│   ├── rate_employee.html
│   ├── civic_complaint.html
│   ├── my_complaints.html
│   ├── profile.html
│   ├── employee_dashboard.html
│   ├── admin_dashboard.html
│   └── assign_employee.html
├── static/
│   ├── css/style.css     ← Modern Glassmorphism CSS
│   └── js/main.js
├── media/                ← Uploaded photos
├── setup.sql             ← MySQL database creation
├── requirements.txt
└── manage.py
```

---

## 🎓 For Viva – Key Points

1. **SDLC Model Used**: Waterfall Model
2. **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
3. **Backend**: Python Django 4.2
4. **Database**: MySQL (20 tables)
5. **Payment**: Razorpay API – Test Mode (no real money)
6. **Authentication**: Email OTP via Gmail SMTP
7. **Architecture**: MVC (Model-View-Template in Django)
8. **Time Slots**: Fixed 10 AM – 5 PM (7 slots per day)
9. **Roles**: User, Employee, Admin (3 interfaces)
10. **Invoice**: Auto-generated with GST after payment

---

*Built with ❤️ using Django + MySQL + Razorpay Test Mode*
