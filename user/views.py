import math
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from user.forms import UserForm, LoginForm, Profile, ForgetPassword, ResetPassword, Booking, Payment as PaymentForm, MyRide, Driver, UserProfileForm, UserAddressForm, CustomerCreateForm
from django.contrib.auth import get_user_model
from user.models import Feedback
from dashboard.models import UserProfile
User = get_user_model()
from drivers.forms import DriverForm, DriverDocumentForm, DriverBankAccountForm
from locations.models import Location
from rides.models import RideRequest, Ride, RideTracking
from payments.models import Payment as PaymentModel
from promotions.models import Coupon, CouponUsage
from django.http import Http404

SIDEBAR_MENU = [
    {"icon": "fa fa-dashboard", "name": "Dashboard", "url": "user-dashboard"},
    {"icon": "fa fa-user", "name": "Profile", "url": "profile"},
    {"icon": "fa fa-calendar", "name": "Bookings", "url": "booking"},
    {"icon": "fa fa-motorcycle", "name": "My Rides", "url": "myride"},
    {"icon": "fa fa-credit-card", "name": "Payments", "url": "payment"},
    {"icon": "fa fa-map-marker", "name": "Track Ride", "url": "track"},
]
SOCIAL_LINKS = [
    {"name": "Google", "icon": "fa-brands fa-google", "url": "#"},
    {"name": "Facebook", "icon": "fa-brands fa-facebook-f", "url": "#"},
    {"name": "Instagram", "icon": "fa-brands fa-instagram", "url": "#"},
    {"name": "LinkedIn", "icon": "fa-brands fa-linkedin-in", "url": "#"},
]

def build_number(prefix="NR"):
    return f"{prefix}{timezone.localtime().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

def get_user_requests(user):
    return RideRequest.objects.filter(passenger=user).select_related(
        "pickup_location", "drop_location", "vehicle_type"
    ).order_by("-requested_at")

def calculate_distance_km(lat1, lon1, lat2, lon2):
    radius = 6371
    lat1, lon1, lat2, lon2 = map(
        math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)]
    )
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(max(0, 1 - value)))


def calculate_fare(vehicle_type, distance):
    name = str(vehicle_type).lower()
    if "bike" in name or "motorcycle" in name:
        base, rate, fee = Decimal("30.00"), Decimal("8.00"), Decimal("10.00")
    elif "auto" in name or "rickshaw" in name:
        base, rate, fee = Decimal("40.00"), Decimal("12.00"), Decimal("10.00")
    else:
        base, rate, fee = Decimal("50.00"), Decimal("15.00"), Decimal("15.00")
    distance = Decimal(str(max(float(distance), 1))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    charge = (distance * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (base + charge + fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "base_fare": base,
        "ride_charge": charge,
        "platform_fee": fee,
        "distance": distance,
        "total_amount": total,
        "estimate_fare": total,
        "final_fare": total,
        "discount_amount": Decimal("0.00"),
        "coupon": None,
    }


def apply_coupon_to_fare(user, coupon_code, fare):
    result = dict(fare)
    result["coupon"] = None
    result["discount_amount"] = Decimal("0.00")
    result["final_fare"] = result["total_amount"]
    if not coupon_code:
        return result, None
    now = timezone.now()
    coupon = Coupon.objects.filter(code__iexact=coupon_code.strip(), is_active=True).first()
    if not coupon:
        return result, "Invalid or inactive coupon code."
    if coupon.valid_from and coupon.valid_from > now:
        return result, "This coupon is not active yet."
    if coupon.valid_to and coupon.valid_to < now:
        return result, "This coupon has expired."
    if result["total_amount"] < (coupon.minimum_fare or Decimal("0.00")):
        return result, "Your booking amount does not meet the minimum fare for this coupon."
    usage_count = CouponUsage.objects.filter(coupon=coupon, user=user).count()
    request_count = RideRequest.objects.filter(passenger=user, coupon=coupon).count()
    if coupon.per_user_limit and usage_count + request_count >= coupon.per_user_limit:
        return result, "You have already used this coupon the maximum allowed number of times."
    if coupon.usage_limit:
        total_usage = CouponUsage.objects.filter(coupon=coupon).count()
        total_requests = RideRequest.objects.filter(coupon=coupon).count()
        if total_usage + total_requests >= coupon.usage_limit:
            return result, "This coupon has reached its usage limit."
    if coupon.discount_type == "percentage":
        discount = result["total_amount"] * Decimal(str(coupon.discount_value)) / Decimal("100")
        if coupon.maximum_discount:
            discount = min(discount, coupon.maximum_discount)
    else:
        discount = Decimal(str(coupon.discount_value))
    discount = min(discount, result["total_amount"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    result["coupon"] = coupon
    result["discount_amount"] = discount
    result["final_fare"] = max(Decimal("0.00"), result["total_amount"] - discount)
    result["estimate_fare"] = result["final_fare"]
    return result, None

def get_request_payment(ride_request):
    return PaymentModel.objects.filter(ride_request=ride_request).first()

def get_request_data(ride_request):
    payment = get_request_payment(ride_request)
    ride = Ride.objects.filter(ride_request=ride_request).select_related("driver", "vehicle").first()
    scheduled = timezone.localtime(ride_request.scheduled_at) if ride_request.scheduled_at else None
    amount = ride_request.final_fare or ride_request.estimated_fare or Decimal("0.00")
    return {
        "phone": getattr(ride_request.passenger, "phone", "") or getattr(ride_request.passenger, "mobile_number", ""),
        "request_id": ride_request.pk,
        "booking_id": ride_request.request_number,
        "request_number": ride_request.request_number,
        "ride_request": ride_request,
        "ride": ride,
        "pickup_location": ride_request.pickup_location.address,
        "destination": ride_request.drop_location.address,
        "pickup": ride_request.pickup_location.address,
        "drop": ride_request.drop_location.address,
        "ride_type": str(ride_request.vehicle_type),
        "ride_date": scheduled.date() if scheduled else ride_request.requested_at.date(),
        "ride_time": scheduled.strftime("%H:%M") if scheduled else "",
        "status": ride_request.get_status_display(),
        "ride_status": ride_request.get_status_display(),
        "passengers": 1,
        "distance": str(ride_request.estimated_distance or 0),
        "base_fare": Decimal("0.00"),
        "ride_charge": Decimal("0.00"),
        "platform_fee": Decimal("0.00"),
        "total_amount": amount,
        "fare": amount,
        "estimate_fare": amount,
        "discount_amount": ride_request.discount_amount,
        "payment": payment,
        "payment_type": payment.payment_method if payment else "",
        "payment_status": payment.get_status_display() if payment else "Not initiated",
        "payment_id": payment.payment_number if payment else "",
        "payment_date": timezone.localtime(payment.paid_at).strftime("%d %b %Y") if payment and payment.paid_at else "",
        "payment_time": timezone.localtime(payment.paid_at).strftime("%I:%M %p") if payment and payment.paid_at else "",
        "driver_name": str(ride.driver) if ride else "",
        "driver_phone": getattr(ride.driver, "phone", "") if ride else "",
        "driver_rating": "",
        "vehicle": str(ride.vehicle) if ride else "",
        "vehicle_number": getattr(ride.vehicle, "registration_number", "") if ride else "",
        "eta": "",
        "remaining_distance": "",
    }

def booking_page(request, form=None, booking_data=None):
    return render(request, "user/profile/booking.html", {
        "form": form or Booking(),
        "sidebar_menu": SIDEBAR_MENU,
        "booking_data": booking_data or {},
        "site_name": "NandiRide",
    })

def payment_page(request, form=None, booking_data=None):
    booking_data = booking_data or {}
    if booking_data.get("request_id"):
        request.session["pending_ride_request_id"] = booking_data["request_id"]
    return render(request, "user/profile/payment.html", {
        "form": form or PaymentForm(),
        "sidebar_menu": SIDEBAR_MENU,
        "booking_data": booking_data,
        "request_id": booking_data.get("request_id", ""),
        "site_name": "NandiRide",
    })

def get_owned_request(request, request_id=None):
    if request_id:
        return get_object_or_404(
            RideRequest.objects.select_related("pickup_location", "drop_location", "vehicle_type"),
            pk=request_id,
            passenger=request.user,
        )
    return get_user_requests(request.user).first()

def get_booking_request_id(request):
    return (
        request.POST.get("request_id")
        or request.POST.get("ride_request_id")
        or request.GET.get("request_id")
        or request.session.get("pending_ride_request_id")
    )

# ==================== PUBLIC PAGES ====================

class HomeView(TemplateView):
    template_name = "user/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_tagline": "Safe, comfortable and reliable rides for every journey.",
            "carousel_interval": 4000,
            "carousel_height": 430,
            "hero_slides": [
                {"badge": "FAST • SAFE • RELIABLE", "title": "Your Journey, <br>Our Responsibility", "description": "Book comfortable and reliable rides with NandiRide and travel with confidence.", "button_text": "Book Your Ride", "button_url": reverse("booking"), "button_class": "btn-light text-danger", "button_icon": "fa-solid fa-calendar-check", "icon": "🚕", "heading": "Ride With NandiRide", "image_class": "bg-img1"},
                {"badge": "COMFORTABLE RIDES", "title": "Travel Your Way", "description": "From daily rides to long journeys, choose the ride that fits your needs.", "button_text": "Explore Rides", "button_url": reverse("booking"), "button_class": "btn-light text-danger", "button_icon": "fa-solid fa-car", "icon": "🚗", "heading": "Comfort At Every Step", "image_class": "bg-img2"},
                {"badge": "TRUSTED SERVICE", "title": "SAFE RIDES, <br>HAPPY JOURNEYS", "description": "Experience dependable transportation with professional service and transparent booking.", "button_text": "Get Started", "button_url": reverse("booking"), "button_class": "btn-light text-danger", "button_icon": "fa-solid fa-arrow-right", "icon": "🛡️", "heading": "Your Safety<br>Matters", "image_class": "bg-img3"},
            ],
            "ride_title": "Book Your Ride",
            "page_subtitle": "Enter your pickup and destination to get started.",
            "pickup_label": "Pickup Location",
            "pickup_placeholder": "Enter pickup location",
            "drop_label": "Drop Location",
            "drop_placeholder": "Enter destination",
            "booking_button": {"text": "Book Now", "icon": "fa-solid fa-calendar-check"},
            "booking_url": reverse("booking"),
            "book_title": "Need A Ride?",
            "title": "Your journey starts here.",
            "description": "Choose your preferred ride and book quickly with NandiRide. We make everyday travel simple, comfortable and reliable.",
            "track_ride": {"title": "Track Your Ride", "subtitle": "Know where your ride is in real time.", "placeholder": "Enter Booking ID", "button": "Track Ride", "button_icon": "fa-solid fa-location-crosshairs", "url": reverse("myride"), "icon": "fa-solid fa-map-location-dot"},
            "ride_section_title": "Choose Your Ride",
            "ride_section_subtitle": "Select the ride that suits your journey.",
            "ride_types": [
                {"name": "Bike Ride", "icon": "fa-solid fa-motorcycle", "description": "Quick, affordable and convenient rides for your everyday travel.", "button": "Book Bike", "url": reverse("booking")},
                {"name": "Car Ride", "icon": "fa-solid fa-car", "description": "Comfortable rides for individuals, families and business travel.", "button": "Book Car", "url": reverse("booking")},
                {"name": "Premium Ride", "icon": "fa-solid fa-car-side", "description": "Enjoy a premium travel experience with extra comfort and convenience.", "button": "Book Premium", "url": reverse("booking")},
            ],
            "why_section": {"title": "Why Choose NandiRide?", "subtitle": "Everything you need for a smooth, safe and comfortable journey."},
            "why_choose": [
                {"title": "Safe & Secure", "description": "Your safety is our first priority on every journey.", "icon": "fa-solid fa-shield-halved"},
                {"title": "Easy Booking", "description": "Book your ride quickly with a simple and convenient process.", "icon": "fa-solid fa-calendar-check"},
                {"title": "Reliable Service", "description": "Count on NandiRide for dependable transportation whenever you need it.", "icon": "fa-solid fa-circle-check"},
                {"title": "Affordable Price", "description": "Enjoy comfortable rides at competitive and transparent prices.", "icon": "fa-solid fa-wallet"},
            ],
            "home_stats": [
                {"value": "24/7", "label": "Ride Availability", "icon": "fa-solid fa-clock"},
                {"value": "100%", "label": "Customer Focus", "icon": "fa-solid fa-heart"},
                {"value": "Fast", "label": "Booking Process", "icon": "fa-solid fa-bolt"},
                {"value": "Safe", "label": "Travel Experience", "icon": "fa-solid fa-shield-halved"},
            ],
            "home_cta": {"title": "Ready To Start Your Journey?", "description": "Book your next ride with NandiRide and experience travel made simple.", "url": reverse("booking"), "icon": "fa-solid fa-car", "button_text": "Book Your Ride", "button_icon": "fa-solid fa-calendar-check"},
            "current_year": timezone.localdate().year,
        })
        return context

class UnderConstruction(TemplateView):
    template_name = "user/underconstruction.html"

class About(TemplateView):
    template_name = "user/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_name": "NandiRide",
            "about_hero": {"title": "Ride Smarter,", "highlight": "Travel Better", "description": "NandiRide makes everyday travel simple, reliable and convenient with safe rides and a smooth booking experience.", "button": "Book Your Ride", "button_icon": "fa-solid fa-car", "button_url": reverse("booking"), "secondary_button": "Contact Us", "secondary_button_icon": "fa-solid fa-headset", "secondary_button_url": reverse("user-contact")},
            "about_intro": {"small": "WHO WE ARE", "title": "Your Journey, Our Responsibility", "description": "NandiRide is built to provide a simple, comfortable and reliable ride booking experience for everyone. From booking to payment, we focus on making every step easy."},
            "about_features": [
                {"icon": "fa-solid fa-shield-halved", "title": "Safe & Reliable", "description": "We focus on providing dependable rides and a comfortable travel experience."},
                {"icon": "fa-solid fa-bolt", "title": "Fast & Convenient", "description": "Book your ride quickly with a simple and convenient booking experience."},
                {"icon": "fa-solid fa-mobile-screen-button", "title": "Technology Driven", "description": "Modern technology helps us deliver a smooth and connected ride experience."},
            ],
            "about_stats_heading": {"small": "OUR JOURNEY", "title": "NandiRide At A Glance", "description": "Everything we build is focused on making travel easier."},
            "about_stats": [
                {"icon": "fa-solid fa-car", "number": "1000+", "title": "Rides", "description": "Trips completed"},
                {"icon": "fa-solid fa-users", "number": "500+", "title": "Customers", "description": "Happy riders"},
                {"icon": "fa-solid fa-location-dot", "number": "50+", "title": "Locations", "description": "Service areas"},
                {"icon": "fa-solid fa-headset", "number": "24/7", "title": "Support", "description": "Customer assistance"},
            ],
            "about_values": {"small": "WHAT WE BELIEVE", "title": "Our Core Values", "description": "The principles that guide everything we do at NandiRide."},
            "about_value_cards": [
                {"icon": "fa-solid fa-shield-heart", "title": "Safety First", "description": "Safety and trust are at the heart of every journey we provide."},
                {"icon": "fa-solid fa-heart", "title": "Customer First", "description": "We listen to our customers and continuously improve their experience."},
                {"icon": "fa-solid fa-handshake", "title": "Trust & Respect", "description": "We believe in honest communication and respectful relationships."},
                {"icon": "fa-solid fa-lightbulb", "title": "Innovation", "description": "We use technology and fresh ideas to create better travel solutions."},
                {"icon": "fa-solid fa-users", "title": "Teamwork", "description": "Great experiences are created when people work together."},
                {"icon": "fa-solid fa-star", "title": "Quality", "description": "We continuously work to deliver a dependable and enjoyable service."},
            ],
            "about_highlights": [
                {"icon": "fa-solid fa-route", "title": "Easy Booking", "description": "Book your ride with a simple and user-friendly experience."},
                {"icon": "fa-solid fa-location-crosshairs", "title": "Live Ride Experience", "description": "Stay connected with your ride and journey information."},
                {"icon": "fa-solid fa-credit-card", "title": "Simple Payments", "description": "Enjoy convenient and secure payment options after your ride."},
            ],
            "about_mission": {"icon": "fa-solid fa-road", "badge": "OUR MISSION", "title": "Making Every Journey Better", "description": "Our mission is to make ride booking simple, convenient, reliable and accessible for everyone.", "primary_button": "Book a Ride", "secondary_button": "Contact Us"},
            "about_cta": {"badge": "START YOUR JOURNEY", "title": "Ready to Ride With NandiRide?", "description": "Experience a simple, comfortable and convenient way to travel.", "button": "Book Your Ride", "button_icon": "fa-solid fa-calendar-check", "button_url": reverse("booking")},
        })
        return context

class ServicesView(TemplateView):
    template_name = "user/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_name": "NandiRide",
            "hero": {"badge": "NandiRide Services", "title": "Reliable Rides", "highlight": "Made For You", "description": "From everyday city rides to long-distance journeys, NandiRide makes every trip simple, comfortable and dependable.", "primary_button": "Book a Ride", "primary_icon": "fa-solid fa-car", "primary_url": "booking", "secondary_button": "Explore Services", "secondary_icon": "fa-solid fa-arrow-down", "card_icon": "fa-solid fa-route", "card_title": "Your Journey Matters", "card_description": "Safe rides, simple booking, convenient payments and reliable support in one place."},
            "services_heading": {"badge": "OUR SERVICES", "title": "Everything You Need To Ride", "description": "Explore our range of services designed to make every NandiRide journey easier."},
            "services": [
                {"icon": "fa-solid fa-car-side", "title": "Book a Ride", "description": "Book a comfortable and reliable ride whenever you need it.", "features": ["Quick booking", "Reliable drivers", "Easy pickup"], "button": "Book Now", "button_icon": "fa-solid fa-arrow-right", "url": "booking", "popular": True, "popular_text": "Popular"},
                {"icon": "fa-solid fa-location-dot", "title": "Track Your Ride", "description": "Track your ride in real time and stay updated throughout your journey.", "features": ["Live tracking", "Driver location", "Ride updates"], "button": "My Rides", "button_icon": "fa-solid fa-route", "url": "myride", "popular": False, "popular_text": "Popular"},
                {"icon": "fa-solid fa-calendar-check", "title": "Schedule a Ride", "description": "Plan your journey in advance and schedule your ride according to your time.", "features": ["Advance booking", "Flexible timing", "Easy planning"], "button": "Schedule", "button_icon": "fa-solid fa-calendar-days", "url": "booking", "popular": False, "popular_text": "Popular"},
                {"icon": "fa-solid fa-credit-card", "title": "Easy Payments", "description": "Enjoy a simple and convenient payment experience after every ride.", "features": ["Secure payment", "Multiple options", "Payment history"], "button": "View Payment", "button_icon": "fa-solid fa-wallet", "url": "payment", "popular": False, "popular_text": "Popular"},
                {"icon": "fa-solid fa-route", "title": "Long Distance Ride", "description": "Travel comfortably between cities with convenient long-distance rides.", "features": ["Comfortable travel", "Flexible routes", "Reliable service"], "button": "Book Ride", "button_icon": "fa-solid fa-arrow-right", "url": "booking", "popular": False, "popular_text": "Popular"},
                {"icon": "fa-solid fa-headset", "title": "24/7 Support", "description": "Our support team is available to help you whenever you need assistance.", "features": ["Quick assistance", "Ride support", "Customer care"], "button": "Contact Us", "button_icon": "fa-solid fa-headset", "url": "user-contact", "popular": False, "popular_text": "Popular"},
            ],
            "empty_services": {"title": "No Services Available", "description": "Services will be displayed here when they are available."},
            "cta": {"icon": "fa-solid fa-road", "badge": "START YOUR JOURNEY", "title": "Ready For Your Next Ride?", "description": "Book your journey with NandiRide today and enjoy a simple travel experience.", "button": "Book Now", "button_icon": "fa-solid fa-car", "url": "booking"},
        })
        return context

class CareerView(TemplateView):
    template_name = "user/career.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_name": "NandiRide",
            "departments": ["Technology", "Operations", "Customer Support", "Marketing", "Business"],
            "benefits": [
                {"icon": "fa-solid fa-rocket", "title": "Growth & Learning", "description": "Learn new skills, take on meaningful challenges and grow your career with us."},
                {"icon": "fa-solid fa-people-group", "title": "Great Team", "description": "Work with passionate and supportive people who care about building something meaningful."},
                {"icon": "fa-solid fa-bullseye", "title": "Meaningful Impact", "description": "Your work helps improve everyday travel experiences for customers and drivers."},
                {"icon": "fa-solid fa-lightbulb", "title": "Innovation", "description": "Bring your ideas to the table and help us create better solutions for modern travel."},
                {"icon": "fa-solid fa-handshake", "title": "Collaborative Culture", "description": "We believe the best results come from teamwork, trust and open communication."},
                {"icon": "fa-solid fa-heart", "title": "People First", "description": "We care about our people and aim to create a positive and respectful workplace."},
            ],
            "jobs": [
                {"icon": "fa-solid fa-code", "title": "Django Backend Developer", "department": "Technology", "location": "India", "type": "Full Time", "experience": "1-3 Years", "salary": "Competitive", "description": "Build scalable backend services and APIs for the NandiRide ride booking platform.", "skills": ["Python", "Django", "DRF", "PostgreSQL"], "url": "user-contact", "featured": True},
                {"icon": "fa-solid fa-mobile-screen-button", "title": "React Native Developer", "department": "Technology", "location": "India", "type": "Full Time", "experience": "1-3 Years", "salary": "Competitive", "description": "Create smooth and reliable mobile experiences for NandiRide customers and drivers.", "skills": ["React Native", "JavaScript", "API", "Git"], "url": "user-contact", "featured": False},
                {"icon": "fa-solid fa-headset", "title": "Customer Support Executive", "department": "Customer Support", "location": "India", "type": "Full Time", "experience": "0-2 Years", "salary": "Competitive", "description": "Help customers with bookings, rides, payments and general NandiRide support.", "skills": ["Communication", "Customer Service", "Problem Solving"], "url": "user-contact", "featured": False},
                {"icon": "fa-solid fa-gears", "title": "Operations Executive", "department": "Operations", "location": "India", "type": "Full Time", "experience": "1-3 Years", "salary": "Competitive", "description": "Support daily ride operations and help maintain a reliable experience for customers and drivers.", "skills": ["Operations", "Management", "Communication"], "url": "user-contact", "featured": False},
            ],
        })
        return context

class BlogView(TemplateView):
    template_name = "user/blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_name": "NandiRide",
            "categories": ["Ride Guide", "Travel Tips", "Safety", "NandiRide"],
            "featured_post": {"icon": "fa-solid fa-car-side", "title": "How to Book a Comfortable Ride with NandiRide", "category": "Ride Guide", "date": "02 Sep 2026", "read_time": "5 min read", "author": "NandiRide Team", "description": "Learn how to book your next ride quickly and enjoy a smooth, reliable and comfortable journey with NandiRide.", "image": "", "url": "booking"},
            "posts": [
                {"icon": "fa-solid fa-car-side", "title": "How to Book a Ride with NandiRide", "category": "Ride Guide", "date": "02 Sep 2026", "read_time": "5 min read", "description": "A simple guide to booking your next comfortable and reliable ride.", "image": "", "url": "booking", "featured": True},
                {"icon": "fa-solid fa-shield-heart", "title": "5 Simple Tips for a Safer Ride", "category": "Safety", "date": "01 Sep 2026", "read_time": "4 min read", "description": "Follow these simple practices to make every journey safer and more comfortable.", "image": "", "url": "", "featured": False},
                {"icon": "fa-solid fa-route", "title": "Planning the Perfect Long Distance Journey", "category": "Travel Tips", "date": "30 Aug 2026", "read_time": "6 min read", "description": "Useful ideas for planning a comfortable and stress-free long-distance journey.", "image": "", "url": "booking", "featured": False},
                {"icon": "fa-solid fa-location-dot", "title": "Why Real-Time Ride Tracking Matters", "category": "NandiRide", "date": "28 Aug 2026", "read_time": "4 min read", "description": "Understand how ride tracking helps you stay informed throughout your journey.", "image": "", "url": "myride", "featured": False},
                {"icon": "fa-solid fa-credit-card", "title": "Making Your Ride Payments Easy", "category": "NandiRide", "date": "25 Aug 2026", "read_time": "3 min read", "description": "Learn how to manage your ride payments and keep track of your payment history.", "image": "", "url": "payment", "featured": False},
                {"icon": "fa-solid fa-map-location-dot", "title": "Travel Better with NandiRide", "category": "Travel Tips", "date": "22 Aug 2026", "read_time": "5 min read", "description": "Explore useful travel ideas that can make your everyday journeys easier.", "image": "", "url": "", "featured": False},
            ],
        })
        return context

class ContactView(TemplateView):
    template_name = "user/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_name": "NandiRide",
            "contact_phone": "+91 9410554430",
            "contact_email": "support@nandiride.com",
            "contact_hours": "24 Hours / 7 Days",
            "contact_address": "Haridwar, Uttarakhand (India)",
            "contact_info": [
                {"icon": "fa-solid fa-phone", "title": "Call Us", "description": "Talk directly with our support team.", "value": "+91 9410554430", "link": "tel:+919410554430"},
                {"icon": "fa-solid fa-envelope", "title": "Email Us", "description": "Send us your questions anytime.", "value": "support@nandiride.com", "link": "mailto:support@nandiride.com"},
                {"icon": "fa-solid fa-clock", "title": "Support Hours", "description": "Our customer support is available.", "value": "24/7 Support", "link": ""},
                {"icon": "fa-solid fa-location-dot", "title": "Location", "description": "Serving customers across India.", "value": "Haridwar, Uttarakhand (India)", "link": ""},
            ],
            "contact_subjects": [
                {"value": value, "label": label}
                for value, label in Feedback.SUBJECT_CHOICES
            ],
            "faqs": [
                {"question": "How can I book a NandiRide?", "answer": "You can book a ride from the booking page by entering your pickup and destination details and confirming your ride."},
                {"question": "How can I get help with an existing ride?", "answer": "Contact our support team using the phone number, email address or contact form on this page."},
                {"question": "Can I contact NandiRide about a payment issue?", "answer": "Yes. Select Payment Issue from the contact form and provide the relevant details."},
                {"question": "How quickly will I receive a response?", "answer": "Our support team aims to respond to customer enquiries as quickly as possible."},
            ],
        })
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "feedback").strip().lower()
        message = request.POST.get("message", "").strip()
        valid_subjects = dict(Feedback.SUBJECT_CHOICES)
        if not name or not email or not message:
            messages.error(request, "Please fill in your name, email and message.")
            return self.render_to_response(self.get_context_data())
        if subject not in valid_subjects:
            messages.error(request, "Please select a valid contact subject.")
            return self.render_to_response(self.get_context_data())
        try:
            Feedback.objects.create(
                name=name,
                email=email,
                mobile_number=phone,
                subject=subject,
                message=message,
            )
            messages.success(request, "Thank you for contacting NandiRide. Your message has been submitted successfully.")
            return redirect("user-contact")
        except Exception:
            messages.error(request, "We could not submit your message. Please try again.")
            return self.render_to_response(self.get_context_data())


# ==================== BOOKING ====================

class UserBookingView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in before booking a ride.")
            return redirect("user-login")
        return booking_page(request)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in before booking a ride.")
            return redirect("user-login")
        form = Booking(request.POST)
        if not form.is_valid():
            return booking_page(request, form)
        data = form.cleaned_data
        coords = [
            data.get("pickup_latitude"), data.get("pickup_longitude"),
            data.get("drop_latitude"), data.get("drop_longitude"),
        ]
        if any(value is None for value in coords):
            form.add_error(None, "Please select both pickup and destination from the map.")
            return booking_page(request, form)
        pickup_lat, pickup_lng, drop_lat, drop_lng = coords
        if not (-90 <= pickup_lat <= 90 and -90 <= drop_lat <= 90 and -180 <= pickup_lng <= 180 and -180 <= drop_lng <= 180):
            form.add_error(None, "Invalid pickup or destination coordinates.")
            return booking_page(request, form)
        if not data.get("pickup_location", "").strip() or not data.get("destination", "").strip():
            form.add_error(None, "Pickup and destination are required.")
            return booking_page(request, form)
        distance = calculate_distance_km(pickup_lat, pickup_lng, drop_lat, drop_lng)
        if distance < 0.05:
            form.add_error(None, "Pickup and destination must be different.")
            return booking_page(request, form)
        fare = calculate_fare(data["ride_type"], distance)
        coupon, coupon_error = None, None
        if data.get("coupon_code"):
            fare, coupon_error = apply_coupon_to_fare(request.user, data["coupon_code"], fare)
            coupon = fare.get("coupon")
        if coupon_error:
            form.add_error("coupon_code", coupon_error)
            return booking_page(request, form)
        scheduled_at = None
        if data.get("ride_date") and data.get("ride_time"):
            scheduled_at = datetime.combine(data["ride_date"], data["ride_time"])
            scheduled_at = timezone.make_aware(scheduled_at) if timezone.is_naive(scheduled_at) else scheduled_at
            if scheduled_at < timezone.now():
                form.add_error("ride_date", "Please select a future date and time.")
                return booking_page(request, form)
        elif data.get("ride_date") or data.get("ride_time"):
            form.add_error(None, "Please provide both ride date and ride time, or leave both empty.")
            return booking_page(request, form)
        try:
            with transaction.atomic():
                pickup = Location.objects.create(
                    address=data["pickup_location"].strip(),
                    latitude=pickup_lat,
                    longitude=pickup_lng,
                )
                drop = Location.objects.create(
                    address=data["destination"].strip(),
                    latitude=drop_lat,
                    longitude=drop_lng,
                )
                ride_request = RideRequest.objects.create(
                    request_number=build_number("NRQ"),
                    passenger=request.user,
                    pickup_location=pickup,
                    drop_location=drop,
                    vehicle_type=data["ride_type"],
                    scheduled_at=scheduled_at,
                    estimated_distance=fare["distance"],
                    estimated_duration=max(1, round(distance / 25 * 60)),
                    estimated_fare=fare["final_fare"],
                    final_fare=fare["final_fare"],
                    coupon=coupon,
                    discount_amount=fare.get("discount_amount", Decimal("0.00")),
                    status=RideRequest.Status.REQUESTED,
                )
            request.session["pending_ride_request_id"] = ride_request.pk
            booking_data = get_request_data(ride_request)
            booking_data.update(fare)
            booking_data["request_id"] = ride_request.pk
            booking_data["passengers"] = data.get("passengers") or 1
            booking_data["note"] = data.get("note") or ""
            messages.success(request, "Your ride request has been saved.")
            return payment_page(request, PaymentForm(), booking_data)
        except (ValidationError, ValueError, TypeError) as exc:
            form.add_error(None, f"Unable to create booking: {exc}")
            return booking_page(request, form)

# ==================== PAYMENT ====================

class UserPaymentView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view payments.")
            return redirect("user-login")
        request_id = get_booking_request_id(request)
        ride_request = get_owned_request(request, request_id)
        if not ride_request:
            messages.info(request, "Please book a ride first.")
            return redirect("booking")
        request.session["pending_ride_request_id"] = ride_request.pk
        return payment_page(request, PaymentForm(), get_request_data(ride_request))

    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to make a payment.")
            return redirect("user-login")
        request_id = get_booking_request_id(request)
        if not request_id:
            messages.error(request, "Booking reference is missing. Please select a booking.")
            return redirect("myride")
        ride_request = get_object_or_404(RideRequest, pk=request_id, passenger=request.user)
        form = PaymentForm(request.POST)
        if not form.is_valid():
            return payment_page(request, form, get_request_data(ride_request))
        method = form.cleaned_data.get("payment_type")
        if method not in dict(PaymentModel.Method.choices):
            form.add_error("payment_type", "Please select a valid payment method.")
            return payment_page(request, form, get_request_data(ride_request))
        amount = ride_request.final_fare or ride_request.estimated_fare or Decimal("0.00")
        if amount <= 0:
            form.add_error(None, "The booking amount is invalid. Please contact support.")
            return payment_page(request, form, get_request_data(ride_request))
        with transaction.atomic():
            payment = PaymentModel.objects.select_for_update().filter(ride_request=ride_request).first()
            if payment and payment.status == PaymentModel.Status.SUCCESS:
                messages.info(request, "This booking has already been paid.")
                return redirect(f"{reverse('myride')}?request_id={ride_request.pk}")
            if payment is None:
                PaymentModel.objects.create(
                    payment_number=build_number("PAY"),
                    ride_request=ride_request,
                    user=request.user,
                    amount=amount,
                    payment_method=method,
                    status=PaymentModel.Status.PENDING,
                    metadata={"source": "customer_web"},
                )
            else:
                payment.payment_method = method
                payment.amount = amount
                payment.status = PaymentModel.Status.PENDING
                payment.metadata = {**(payment.metadata or {}), "source": "customer_web"}
                payment.save(update_fields=["payment_method", "amount", "status", "metadata", "updated_at"])
        messages.info(request, "Payment method saved. Status remains Pending until payment is verified.")
        return redirect(f"{reverse('myride')}?request_id={ride_request.pk}")

# ==================== MY RIDES ====================

class UserMyRideView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view your rides.")
            return redirect("user-login")
        requests = get_user_requests(request.user)
        request_id = request.GET.get("request_id")
        selected = get_object_or_404(requests, pk=request_id) if request_id else requests.first()
        return render(request, "user/profile/myride.html", {
            "sidebar_menu": SIDEBAR_MENU,
            "booking_data": get_request_data(selected) if selected else {},
            "ride_requests": requests,
            "rides": [get_request_data(item) for item in requests],
            "ride_count": requests.count(),
            "site_name": "NandiRide",
        })

# ==================== DASHBOARD ====================

class UserDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view your dashboard.")
            return redirect("user-login")
        requests = get_user_requests(request.user)
        payments = PaymentModel.objects.filter(user=request.user, status=PaymentModel.Status.SUCCESS)
        total_spent = payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        recent_rides = []
        for item in requests[:5]:
            data = get_request_data(item)
            recent_rides.append({
                "pickup": data["pickup"],
                "destination": data["destination"],
                "booking_id": data["booking_id"],
                "date": data["ride_date"],
                "time": data["ride_time"],
                "vehicle": data["ride_type"],
                "fare": data["total_amount"],
                "status": data["status"],
                "driver_name": data["driver_name"],
                "payment_status": data["payment_status"],
            })
        return render(request, "user/dashboard.html", {
            "sidebar_menu": SIDEBAR_MENU,
            "site_name": "NandiRide",
            "dashboard_stats": {
                "total_rides": requests.count(),
                "completed": requests.filter(status=RideRequest.Status.COMPLETED).count(),
                "total_spent": total_spent,
                "rating": "",
            },
            "recent_rides": recent_rides,
            "ride_requests": requests,
        })

# ==================== TRACK RIDE ====================

class TrackRideView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to track a ride.")
            return redirect("user-login")
        request_id = request.GET.get("request_id")
        ride_request = get_owned_request(request, request_id)
        if not ride_request:
            messages.info(request, "You do not have a booking to track yet.")
            return redirect("booking")
        data = get_request_data(ride_request)
        actual_ride = data["ride"]
        latest = RideTracking.objects.filter(ride=actual_ride).order_by("-recorded_at").first() if actual_ride else None
        ride_data = {
            "booking_id": ride_request.request_number,
            "pickup": data["pickup"],
            "destination": data["destination"],
            "ride_type": data["ride_type"],
            "date": data["ride_date"],
            "time": data["ride_time"],
            "passengers": 1,
            "distance": f"{ride_request.estimated_distance or 0} km",
            "fare": data["total_amount"],
            "status": data["status"],
            "driver_name": data["driver_name"],
            "driver_rating": data["driver_rating"],
            "driver_phone": data["driver_phone"],
            "vehicle": data["vehicle"],
            "vehicle_number": data["vehicle_number"],
            "eta": "",
            "remaining_distance": "",
            "latitude": latest.latitude if latest else None,
            "longitude": latest.longitude if latest else None,
            "last_location_update": latest.recorded_at if latest else None,
        }
        return render(request, "user/profile/track.html", {
            "sidebar_menu": SIDEBAR_MENU,
            "booking_data": data,
            "ride": ride_data,
            "site_name": "NandiRide",
        })

# ==================== PROFILE AND AUTHENTICATION ====================

class UserEditProfileView(TemplateView):
    template_name = "user/profile/editprofile.html"

    def get(self, request):
        return render(request, self.template_name, {"form": Profile(), "sidebar_menu": SIDEBAR_MENU})

class UserLoginView(TemplateView):
    template_name = "user/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm(), "social_links": SOCIAL_LINKS})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username") or form.cleaned_data.get("email") or form.cleaned_data.get("mobilenumber")
            user = authenticate(request, username=username, password=form.cleaned_data.get("password"))
            if user:
                login(request, user)
                messages.success(request, "Login successful.")
                next_url = request.GET.get("next")
                if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                    return redirect(next_url)
                return redirect("user-dashboard")
            messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form, "social_links": SOCIAL_LINKS})

class UserSignupView(TemplateView):
    template_name = "user/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": UserForm(), "social_links": SOCIAL_LINKS})

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.save()
                    form.save_profile(user)
                messages.success(request, "Account created. Please log in.")
                return redirect("user-login")
            except (AttributeError, TypeError, ValidationError) as exc:
                messages.error(request, f"Unable to create account: {exc}")
        return render(request, self.template_name, {"form": form, "social_links": SOCIAL_LINKS})

class UserProfileView(TemplateView):
    template_name = "user/profile/profile.html"

    def get(self, request):
        return render(request, self.template_name, {
            "CustomerForm": CustomerCreateForm(),
            "UserProfile": UserProfileForm(),
            "UserAddress": UserAddressForm(),
            "Driver": DriverForm(),
            "DriverDocument": DriverDocumentForm(),
            "DriverBankAccount": DriverBankAccountForm(),
            "sidebar_menu": SIDEBAR_MENU,
        })

class ForgetPasswordView(TemplateView):
    template_name = "user/profile/forgetpassword.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ForgetPassword(), "sidebar_menu": SIDEBAR_MENU})

class ResetPasswordView(TemplateView):
    template_name = "user/profile/resetpassword.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ResetPassword(), "sidebar_menu": SIDEBAR_MENU})

# ==================== PAYMENT DETAILS AND RECEIPT ====================

class PaymentDetailsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view payments.")
            return redirect("user-login")
        payment_id = request.GET.get("payment_id")
        if payment_id:
            payment_query = PaymentModel.objects.filter(user=request.user)
            if str(payment_id).isdigit():
                payment = payment_query.filter(pk=int(payment_id)).first()
            else:
                payment = payment_query.filter(payment_number=payment_id).first()
            if payment is None:
                raise Http404("Payment not found.")
        else:
            payment = PaymentModel.objects.filter(user=request.user).order_by("-created_at").first()
        return render(request, "user/profile/paymentdetails.html", {
            "sidebar_menu": SIDEBAR_MENU,
            "form": PaymentForm(),
            "payment": payment,
            "payments": PaymentModel.objects.filter(user=request.user).order_by("-created_at"),
            "booking_data": get_request_data(payment.ride_request) if payment and payment.ride_request else {},
            "site_name": "NandiRide",
        })

class PaymentReceiptView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view receipts.")
            return redirect("user-login")
        payment_id = request.GET.get("payment_id")
        payment = get_object_or_404(PaymentModel, pk=payment_id, user=request.user) if payment_id else PaymentModel.objects.filter(user=request.user).order_by("-created_at").first()
        return render(request, "user/profile/paymentreceipt.html", {
            "sidebar_menu": SIDEBAR_MENU,
            "form": PaymentForm(),
            "payment": payment,
            "booking_data": get_request_data(payment.ride_request) if payment and payment.ride_request else {},
            "site_name": "NandiRide",
        })

# ==================== CANCEL RIDE ====================

class CancelRideView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to cancel a ride.")
            return redirect("user-login")
        request_id = get_booking_request_id(request)
        if not request_id:
            messages.error(request, "Booking reference is missing.")
            return redirect("myride")
        ride_request = get_object_or_404(RideRequest, pk=request_id, passenger=request.user)
        cancellable = [
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
            RideRequest.Status.ASSIGNED,
            RideRequest.Status.ACCEPTED,
        ]
        if ride_request.status not in cancellable:
            messages.error(request, "This ride cannot be cancelled from the customer page.")
            return redirect(f"{reverse('myride')}?request_id={ride_request.pk}")
        with transaction.atomic():
            ride_request.status = RideRequest.Status.CANCELLED
            ride_request.save(update_fields=["status", "updated_at"])
            actual_ride = Ride.objects.filter(ride_request=ride_request).first()
            if actual_ride and actual_ride.status != Ride.Status.COMPLETED:
                actual_ride.status = Ride.Status.CANCELLED
                actual_ride.save(update_fields=["status", "updated_at"])
            payment = PaymentModel.objects.filter(ride_request=ride_request).first()
            if payment and payment.status == PaymentModel.Status.PENDING:
                payment.metadata = {
                    **(payment.metadata or {}),
                    "cancellation_note": "Ride cancelled before payment confirmation",
                }
                payment.save(update_fields=["metadata", "updated_at"])
        messages.success(request, "Ride cancelled successfully.")
        return redirect(f"{reverse('myride')}?request_id={ride_request.pk}")

# ==================== HELP CHATBOT ====================

class HelpChatbotView(View):
    def post(self, request):
        message = request.POST.get("message", "").strip().lower()
        if not message:
            return JsonResponse({"reply": "Please type your question so I can help you."})
        booking_data = {}
        if request.user.is_authenticated:
            request_id = request.POST.get("request_id")
            ride_request = get_owned_request(request, request_id)
            if ride_request:
                booking_data = get_request_data(ride_request)
        if any(word in message for word in ["hello", "hi", "hey"]):
            reply = "Hello! 👋 Welcome to NandiRide Help. How can I help you today?"
        elif "book" in message or "booking" in message:
            reply = "Open Booking, enter pickup and destination, select your ride type, and confirm your booking."
        elif "payment" in message or "pay" in message:
            reply = f"Your latest payment status is {booking_data.get('payment_status', 'not available')}." if booking_data else "Your payment status is available on the Payment page. Pending payments are not treated as successful."
        elif any(word in message for word in ["track", "where", "location"]):
            reply = f"Your latest booking status is {booking_data.get('status', 'Unknown')}." if booking_data else "No booking was found for your account. Please log in and book a ride."
        elif "cancel" in message:
            reply = "Open My Rides and use the cancellation option if your ride is eligible."
        elif "booking id" in message or message == "id":
            reply = f"Your booking ID is {booking_data.get('booking_id')}." if booking_data else "No booking was found for your account."
        elif any(word in message for word in ["user-contact", "support", "help"]):
            reply = "Contact NandiRide support at support@nandiride.com or use the Contact page."
        else:
            reply = "You can ask about booking, payment, tracking, cancellation, booking ID, or support."
        return JsonResponse({"reply": reply})