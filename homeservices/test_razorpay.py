#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservices.settings')
import django
django.setup()

from django.conf import settings

print("="*50)
print("RAZORPAY CREDENTIALS")
print("="*50)
print(f"KEY_ID: {settings.RAZORPAY_KEY_ID}")
print(f"KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:10]}...")
print(f"TEST_MODE: {settings.RAZORPAY_TEST_MODE}")
print()

# Try to create a Razorpay order
try:
    import razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({'amount': 39900, 'currency': 'INR', 'payment_capture': 1})
    print("✅ Razorpay Order Created Successfully!")
    print(f"Order ID: {order['id']}")
except Exception as e:
    print(f"❌ Razorpay Error: {str(e)}")
    import traceback
    traceback.print_exc()
