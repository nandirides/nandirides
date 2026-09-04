from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from user.forms import UserForm, LoginForm, Profile, ForgetPassword, ResetPassword, Booking, Payment, MyRide, Driver
from user.models import User
#from django.contrib.auth import authenticate, login, logout


SIDEBAR_MENU = [
    {
        'icon': 'fa fa-dashboard',
        'name': 'Dashboard',
        'url': 'user-dashboard',
    },
    {
        'icon': 'fa fa-user',
        'name': 'Profile',
        'url': 'profile',
    },
    {
        'icon': 'fa fa-calendar',
        'name': 'Bookings',
        'url': 'booking',
    },
    {
        'icon': 'fa fa-motorcycle',
        'name': 'My Rides',
        'url': 'myride',
    },
    {
        'icon': 'fa fa-credit-card',
        'name': 'Payments',
        'url': 'payment',
    },
    {
        'icon': 'fa fa-map-marker',
        'name': 'Track Ride',
        'url': 'track',
    },
]


SOCIAL_LINKS = [
    {
        'name': 'Google',
        'icon': 'fa-brands fa-google',
        'url': '#',
    },
    {
        'name': 'Facebook',
        'icon': 'fa-brands fa-facebook-f',
        'url': '#',
    },
    {
        'name': 'Instagram',
        'icon': 'fa-brands fa-instagram',
        'url': '#',
    },
    {
        'name': 'LinkedIn',
        'icon': 'fa-brands fa-linkedin-in',
        'url': '#',
    },
]


class HomeView(TemplateView):
    template_name = "user/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "site_tagline": "Safe, comfortable and reliable rides for every journey.",
            "carousel_interval": 4000,
            "carousel_height": 430,
            "hero_slides": [
                {
                    "badge": "FAST • SAFE • RELIABLE",
                    "title": "Your Journey, <br>Our Responsibility",
                    "description": "Book comfortable and reliable rides with NandiRide and travel with confidence.",
                    "button_text": "Book Your Ride",
                    "button_url": reverse("booking"),
                    "button_class": "btn-light text-danger",
                    "button_icon": "fa-solid fa-calendar-check",
                    "icon": "🚕",
                    "heading": "Ride With NandiRide",
                    "image_class": "bg-img1",
                },
                {
                    "badge": "COMFORTABLE RIDES",
                    "title": "Travel Your Way",
                    "description": "From daily rides to long journeys, choose the ride that fits your needs.",
                    "button_text": "Explore Rides",
                    "button_url": reverse("booking"),
                    "button_class": "btn-light text-danger",
                    "button_icon": "fa-solid fa-car",
                    "icon": "🚗",
                    "heading": "Comfort At Every Step",
                    "image_class": "bg-img2",
                },
                {
                    "badge": "TRUSTED SERVICE",
                    "title": "SAFE RIDES, <br>HAPPY JOURNEYS",
                    "description": "Experience dependable transportation with professional service and transparent booking.",
                    "button_text": "Get Started",
                    "button_url": reverse("booking"),
                    "button_class": "btn-light text-danger",
                    "button_icon": "fa-solid fa-arrow-right",
                    "icon": "🛡️",
                    "heading": "Your Safety<br>Matters",
                    "image_class": "bg-img3",
                },
            ],
            "ride_title": "Book Your Ride",
            "page_subtitle": "Enter your pickup and destination to get started.",
            "pickup_label": "Pickup Location",
            "pickup_placeholder": "Enter pickup location",
            "drop_label": "Drop Location",
            "drop_placeholder": "Enter destination",
            "booking_button": {
                "text": "Book Now",
                "icon": "fa-solid fa-calendar-check",
            },
            "booking_url": reverse("booking"),
            "book_title": "Need A Ride?",
            "title": "Your journey starts here.",
            "description": "Choose your preferred ride and book quickly with NandiRide. We make everyday travel simple, comfortable and reliable.",
            "track_ride": {
                "title": "Track Your Ride",
                "subtitle": "Know where your ride is in real time.",
                "placeholder": "Enter Booking ID",
                "button": "Track Ride",
                "button_icon": "fa-solid fa-location-crosshairs",
                "url": reverse("myride"),
                "icon": "fa-solid fa-map-location-dot",
            },
            "ride_section_title": "Choose Your Ride",
            "ride_section_subtitle": "Select the ride that suits your journey.",
            "ride_types": [
                {
                    "name": "Bike Ride",
                    "icon": "fa-solid fa-motorcycle",
                    "description": "Quick, affordable and convenient rides for your everyday travel.",
                    "button": "Book Bike",
                    "url": reverse("booking"),
                },
                {
                    "name": "Car Ride",
                    "icon": "fa-solid fa-car",
                    "description": "Comfortable rides for individuals, families and business travel.",
                    "button": "Book Car",
                    "url": reverse("booking"),
                },
                {
                    "name": "Premium Ride",
                    "icon": "fa-solid fa-car-side",
                    "description": "Enjoy a premium travel experience with extra comfort and convenience.",
                    "button": "Book Premium",
                    "url": reverse("booking"),
                },
            ],
            "why_section": {
                "title": "Why Choose NandiRide?",
                "subtitle": "Everything you need for a smooth, safe and comfortable journey.",
            },
            "why_choose": [
                {
                    "title": "Safe & Secure",
                    "description": "Your safety is our first priority on every journey.",
                    "icon": "fa-solid fa-shield-halved",
                },
                {
                    "title": "Easy Booking",
                    "description": "Book your ride quickly with a simple and convenient process.",
                    "icon": "fa-solid fa-calendar-check",
                },
                {
                    "title": "Reliable Service",
                    "description": "Count on NandiRide for dependable transportation whenever you need it.",
                    "icon": "fa-solid fa-circle-check",
                },
                {
                    "title": "Affordable Price",
                    "description": "Enjoy comfortable rides at competitive and transparent prices.",
                    "icon": "fa-solid fa-wallet",
                },
            ],
            "home_stats": [
                {
                    "value": "24/7",
                    "label": "Ride Availability",
                    "icon": "fa-solid fa-clock",
                },
                {
                    "value": "100%",
                    "label": "Customer Focus",
                    "icon": "fa-solid fa-heart",
                },
                {
                    "value": "Fast",
                    "label": "Booking Process",
                    "icon": "fa-solid fa-bolt",
                },
                {
                    "value": "Safe",
                    "label": "Travel Experience",
                    "icon": "fa-solid fa-shield-halved",
                },
            ],
            "home_cta": {
                "title": "Ready To Start Your Journey?",
                "description": "Book your next ride with NandiRide and experience travel made simple.",
                "url": reverse("booking"),
                "icon": "fa-solid fa-car",
                "button_text": "Book Your Ride",
                "button_icon": "fa-solid fa-calendar-check",
            },
            "current_year": datetime.now().year,
        })
        return context



class UnderConstruction(TemplateView):
    template_name = 'user/underconstruction.html'


class About(TemplateView):
    template_name = 'user/about.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'NandiRide'
        context['about_hero'] = {
            'title': 'Ride Smarter,',
            'highlight': 'Travel Better',
            'description': 'NandiRide makes everyday travel simple, reliable and convenient with safe rides and a smooth booking experience.',
            'button': 'Book Your Ride',
            'button_icon': 'fa-solid fa-car',
            'button_url': reverse('booking'),
            'secondary_button': 'Contact Us',
            'secondary_button_icon': 'fa-solid fa-headset',
            'secondary_button_url': reverse('contact'),
        }
        context['about_intro'] = {
            'small': 'WHO WE ARE',
            'title': 'Your Journey, Our Responsibility',
            'description': 'NandiRide is built to provide a simple, comfortable and reliable ride booking experience for everyone. From booking to payment, we focus on making every step easy.',
        }
        context['about_features'] = [
            {
                'icon': 'fa-solid fa-shield-halved',
                'title': 'Safe & Reliable',
                'description': 'We focus on providing dependable rides and a comfortable travel experience.',
            },
            {
                'icon': 'fa-solid fa-bolt',
                'title': 'Fast & Convenient',
                'description': 'Book your ride quickly with a simple and convenient booking experience.',
            },
            {
                'icon': 'fa-solid fa-mobile-screen-button',
                'title': 'Technology Driven',
                'description': 'Modern technology helps us deliver a smooth and connected ride experience.',
            },
        ]
        context['about_stats_heading'] = {
            'small': 'OUR JOURNEY',
            'title': 'NandiRide At A Glance',
            'description': 'Everything we build is focused on making travel easier.',
        }
        context['about_stats'] = [
            {
                'icon': 'fa-solid fa-car',
                'number': '1000+',
                'title': 'Rides',
                'description': 'Trips completed',
            },
            {
                'icon': 'fa-solid fa-users',
                'number': '500+',
                'title': 'Customers',
                'description': 'Happy riders',
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'number': '50+',
                'title': 'Locations',
                'description': 'Service areas',
            },
            {
                'icon': 'fa-solid fa-headset',
                'number': '24/7',
                'title': 'Support',
                'description': 'Customer assistance',
            },
        ]
        context['about_values'] = {
            'small': 'WHAT WE BELIEVE',
            'title': 'Our Core Values',
            'description': 'The principles that guide everything we do at NandiRide.',
        }
        context['about_value_cards'] = [
            {
                'icon': 'fa-solid fa-shield-heart',
                'title': 'Safety First',
                'description': 'Safety and trust are at the heart of every journey we provide.',
            },
            {
                'icon': 'fa-solid fa-heart',
                'title': 'Customer First',
                'description': 'We listen to our customers and continuously improve their experience.',
            },
            {
                'icon': 'fa-solid fa-handshake',
                'title': 'Trust & Respect',
                'description': 'We believe in honest communication and respectful relationships.',
            },
            {
                'icon': 'fa-solid fa-lightbulb',
                'title': 'Innovation',
                'description': 'We use technology and fresh ideas to create better travel solutions.',
            },
            {
                'icon': 'fa-solid fa-users',
                'title': 'Teamwork',
                'description': 'Great experiences are created when people work together.',
            },
            {
                'icon': 'fa-solid fa-star',
                'title': 'Quality',
                'description': 'We continuously work to deliver a dependable and enjoyable service.',
            },
        ]
        context['about_highlights'] = [
            {
                'icon': 'fa-solid fa-route',
                'title': 'Easy Booking',
                'description': 'Book your ride with a simple and user-friendly experience.',
            },
            {
                'icon': 'fa-solid fa-location-crosshairs',
                'title': 'Live Ride Experience',
                'description': 'Stay connected with your ride and journey information.',
            },
            {
                'icon': 'fa-solid fa-credit-card',
                'title': 'Simple Payments',
                'description': 'Enjoy convenient and secure payment options after your ride.',
            },
        ]
        context['about_mission'] = {
            'icon': 'fa-solid fa-road',
            'badge': 'OUR MISSION',
            'title': 'Making Every Journey Better',
            'description': 'Our mission is to make ride booking simple, convenient, reliable and accessible for everyone.',
            'primary_button': 'Book a Ride',
            'secondary_button': 'Contact Us',
        }
        context['about_cta'] = {
            'badge': 'START YOUR JOURNEY',
            'title': 'Ready to Ride With NandiRide?',
            'description': 'Experience a simple, comfortable and convenient way to travel.',
            'button': 'Book Your Ride',
            'button_icon': 'fa-solid fa-calendar-check',
            'button_url': reverse('booking'),
        }
        return context


class ServicesView(TemplateView):
    template_name = 'user/services.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'NandiRide'
        context['hero'] = {
            'badge': 'NandiRide Services',
            'title': 'Reliable Rides',
            'highlight': 'Made For You',
            'description': 'From everyday city rides to long-distance journeys, NandiRide makes every trip simple, comfortable and dependable.',
            'primary_button': 'Book a Ride',
            'primary_icon': 'fa-solid fa-car',
            'primary_url': 'booking',
            'secondary_button': 'Explore Services',
            'secondary_icon': 'fa-solid fa-arrow-down',
            'card_icon': 'fa-solid fa-route',
            'card_title': 'Your Journey Matters',
            'card_description': 'Safe rides, simple booking, convenient payments and reliable support in one place.',
        }
        context['services_heading'] = {
            'badge': 'OUR SERVICES',
            'title': 'Everything You Need To Ride',
            'description': 'Explore our range of services designed to make every NandiRide journey easier.',
        }
        context['services'] = [
            {
                'icon': 'fa-solid fa-car-side',
                'title': 'Book a Ride',
                'description': 'Book a comfortable and reliable ride whenever you need it.',
                'features': ['Quick booking', 'Reliable drivers', 'Easy pickup'],
                'button': 'Book Now',
                'button_icon': 'fa-solid fa-arrow-right',
                'url': 'booking',
                'popular': True,
                'popular_text': 'Popular',
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'title': 'Track Your Ride',
                'description': 'Track your ride in real time and stay updated throughout your journey.',
                'features': ['Live tracking', 'Driver location', 'Ride updates'],
                'button': 'My Rides',
                'button_icon': 'fa-solid fa-route',
                'url': 'myride',
                'popular': False,
                'popular_text': 'Popular',
            },
            {
                'icon': 'fa-solid fa-calendar-check',
                'title': 'Schedule a Ride',
                'description': 'Plan your journey in advance and schedule your ride according to your time.',
                'features': ['Advance booking', 'Flexible timing', 'Easy planning'],
                'button': 'Schedule',
                'button_icon': 'fa-solid fa-calendar-days',
                'url': 'booking',
                'popular': False,
                'popular_text': 'Popular',
            },
            {
                'icon': 'fa-solid fa-credit-card',
                'title': 'Easy Payments',
                'description': 'Enjoy a simple and convenient payment experience after every ride.',
                'features': ['Secure payment', 'Multiple options', 'Payment history'],
                'button': 'View Payment',
                'button_icon': 'fa-solid fa-wallet',
                'url': 'payment',
                'popular': False,
                'popular_text': 'Popular',
            },
            {
                'icon': 'fa-solid fa-route',
                'title': 'Long Distance Ride',
                'description': 'Travel comfortably between cities with convenient long-distance rides.',
                'features': ['Comfortable travel', 'Flexible routes', 'Reliable service'],
                'button': 'Book Ride',
                'button_icon': 'fa-solid fa-arrow-right',
                'url': 'booking',
                'popular': False,
                'popular_text': 'Popular',
            },
            {
                'icon': 'fa-solid fa-headset',
                'title': '24/7 Support',
                'description': 'Our support team is available to help you whenever you need assistance.',
                'features': ['Quick assistance', 'Ride support', 'Customer care'],
                'button': 'Contact Us',
                'button_icon': 'fa-solid fa-headset',
                'url': 'contact',
                'popular': False,
                'popular_text': 'Popular',
            },
        ]
        context['empty_services'] = {
            'title': 'No Services Available',
            'description': 'Services will be displayed here when they are available.',
        }
        context['cta'] = {
            'icon': 'fa-solid fa-road',
            'badge': 'START YOUR JOURNEY',
            'title': 'Ready For Your Next Ride?',
            'description': 'Book your journey with NandiRide today and enjoy a simple travel experience.',
            'button': 'Book Now',
            'button_icon': 'fa-solid fa-car',
            'url': 'booking',
        }
        return context


class CareerView(TemplateView):
    template_name = 'user/career.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'NandiRide'
        context['departments'] = [
            'Technology',
            'Operations',
            'Customer Support',
            'Marketing',
            'Business',
        ]
        context['benefits'] = [
            {
                'icon': 'fa-solid fa-rocket',
                'title': 'Growth & Learning',
                'description': 'Learn new skills, take on meaningful challenges and grow your career with us.',
            },
            {
                'icon': 'fa-solid fa-people-group',
                'title': 'Great Team',
                'description': 'Work with passionate and supportive people who care about building something meaningful.',
            },
            {
                'icon': 'fa-solid fa-bullseye',
                'title': 'Meaningful Impact',
                'description': 'Your work helps improve everyday travel experiences for customers and drivers.',
            },
            {
                'icon': 'fa-solid fa-lightbulb',
                'title': 'Innovation',
                'description': 'Bring your ideas to the table and help us create better solutions for modern travel.',
            },
            {
                'icon': 'fa-solid fa-handshake',
                'title': 'Collaborative Culture',
                'description': 'We believe the best results come from teamwork, trust and open communication.',
            },
            {
                'icon': 'fa-solid fa-heart',
                'title': 'People First',
                'description': 'We care about our people and aim to create a positive and respectful workplace.',
            },
        ]
        context['jobs'] = [
            {
                'icon': 'fa-solid fa-code',
                'title': 'Django Backend Developer',
                'department': 'Technology',
                'location': 'India',
                'type': 'Full Time',
                'experience': '1-3 Years',
                'salary': 'Competitive',
                'description': 'Build scalable backend services and APIs for the NandiRide ride booking platform.',
                'skills': ['Python', 'Django', 'DRF', 'PostgreSQL'],
                'url': 'contact',
                'featured': True,
            },
            {
                'icon': 'fa-solid fa-mobile-screen-button',
                'title': 'React Native Developer',
                'department': 'Technology',
                'location': 'India',
                'type': 'Full Time',
                'experience': '1-3 Years',
                'salary': 'Competitive',
                'description': 'Create smooth and reliable mobile experiences for NandiRide customers and drivers.',
                'skills': ['React Native', 'JavaScript', 'API', 'Git'],
                'url': 'contact',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-headset',
                'title': 'Customer Support Executive',
                'department': 'Customer Support',
                'location': 'India',
                'type': 'Full Time',
                'experience': '0-2 Years',
                'salary': 'Competitive',
                'description': 'Help customers with bookings, rides, payments and general NandiRide support.',
                'skills': ['Communication', 'Customer Service', 'Problem Solving'],
                'url': 'contact',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-gears',
                'title': 'Operations Executive',
                'department': 'Operations',
                'location': 'India',
                'type': 'Full Time',
                'experience': '1-3 Years',
                'salary': 'Competitive',
                'description': 'Support daily ride operations and help maintain a reliable experience for customers and drivers.',
                'skills': ['Operations', 'Management', 'Communication'],
                'url': 'contact',
                'featured': False,
            },
        ]
        return context


class BlogView(TemplateView):
    template_name = 'user/blog.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'NandiRide'
        context['categories'] = [
            'Ride Guide',
            'Travel Tips',
            'Safety',
            'NandiRide',
        ]
        context['featured_post'] = {
            'icon': 'fa-solid fa-car-side',
            'title': 'How to Book a Comfortable Ride with NandiRide',
            'category': 'Ride Guide',
            'date': '02 Sep 2026',
            'read_time': '5 min read',
            'author': 'NandiRide Team',
            'description': 'Learn how to book your next ride quickly and enjoy a smooth, reliable and comfortable journey with NandiRide.',
            'image': '',
            'url': 'booking',
        }
        context['posts'] = [
            {
                'icon': 'fa-solid fa-car-side',
                'title': 'How to Book a Ride with NandiRide',
                'category': 'Ride Guide',
                'date': '02 Sep 2026',
                'read_time': '5 min read',
                'description': 'A simple guide to booking your next comfortable and reliable ride.',
                'image': '',
                'url': 'booking',
                'featured': True,
            },
            {
                'icon': 'fa-solid fa-shield-heart',
                'title': '5 Simple Tips for a Safer Ride',
                'category': 'Safety',
                'date': '01 Sep 2026',
                'read_time': '4 min read',
                'description': 'Follow these simple practices to make every journey safer and more comfortable.',
                'image': '',
                'url': '',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-route',
                'title': 'Planning the Perfect Long Distance Journey',
                'category': 'Travel Tips',
                'date': '30 Aug 2026',
                'read_time': '6 min read',
                'description': 'Useful ideas for planning a comfortable and stress-free long-distance journey.',
                'image': '',
                'url': 'booking',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'title': 'Why Real-Time Ride Tracking Matters',
                'category': 'NandiRide',
                'date': '28 Aug 2026',
                'read_time': '4 min read',
                'description': 'Understand how ride tracking helps you stay informed throughout your journey.',
                'image': '',
                'url': 'myride',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-credit-card',
                'title': 'Making Your Ride Payments Easy',
                'category': 'NandiRide',
                'date': '25 Aug 2026',
                'read_time': '3 min read',
                'description': 'Learn how to manage your ride payments and keep track of your payment history.',
                'image': '',
                'url': 'payment',
                'featured': False,
            },
            {
                'icon': 'fa-solid fa-map-location-dot',
                'title': 'Travel Better with NandiRide',
                'category': 'Travel Tips',
                'date': '22 Aug 2026',
                'read_time': '5 min read',
                'description': 'Explore useful travel ideas that can make your everyday journeys easier.',
                'image': '',
                'url': '',
                'featured': False,
            },
        ]
        return context


class ContactView(TemplateView):
    template_name = 'user/contact.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_phone'] = '+91 9410554430'
        context['contact_email'] = 'support@nandiride.com'
        context['contact_hours'] = '24 Hours / 7 Days'
        context['contact_address'] = 'Haridwar, Uttrakhand (India)'
        context['contact_info'] = [
            {
                'icon': 'fa-solid fa-phone',
                'title': 'Call Us',
                'description': 'Talk directly with our support team.',
                'value': '+91 9410554430',
                'link': 'tel:+919876543210',
            },
            {
                'icon': 'fa-solid fa-envelope',
                'title': 'Email Us',
                'description': 'Send us your questions anytime.',
                'value': 'support@nandiride.com',
                'link': 'mailto:support@nandiride.com',
            },
            {
                'icon': 'fa-solid fa-clock',
                'title': 'Support Hours',
                'description': 'Our customer support is available.',
                'value': '24/7 Support',
                'link': '',
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'title': 'Location',
                'description': 'Serving customers across India.',
                'value': 'Haridwar, Uttrakhand (India)',
                'link': '',
            },
        ]
        context['contact_subjects'] = ['Ride Support', 'Booking Issue', 'Payment Issue', 'Account Support',
                                    'Driver Support', 'General Enquiry', 'Feedback', 'Other',
        ]
        context['faqs'] = [
            {
                'question': 'How can I book a NandiRide?',
                'answer': 'You can book a ride from the booking page by entering your pickup and destination details and confirming your ride.',
            },
            {
                'question': 'How can I get help with an existing ride?',
                'answer': 'You can contact our support team using the phone number, email address or contact form available on this page.',
            },
            {
                'question': 'Can I contact NandiRide about a payment issue?',
                'answer': 'Yes. Select Payment Issue from the contact form and provide your transaction details so our team can assist you.',
            },
            {
                'question': 'How quickly will I receive a response?',
                'answer': 'Our support team aims to respond to customer enquiries as quickly as possible.',
            },
        ]
        return context


class UserBookingView(View):

    def get(self, request):
        form = Booking()
        return render(
            request,
            'user/profile/booking.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )

    def post(self, request):
        form = Booking(request.POST)

        if form.is_valid():
            booking_data = {
                'booking_id': form.cleaned_data.get('booking_id'),
                'pickup_location': form.cleaned_data.get('pickup_location'),
                'destination': form.cleaned_data.get('destination'),
                'ride_type': form.cleaned_data.get('ride_type'),
                'ride_date': form.cleaned_data.get('ride_date'),
                'ride_time': form.cleaned_data.get('ride_time'),
                'ride_status': 'Pending',
                'passengers': form.cleaned_data.get('passengers'),
                'note': form.cleaned_data.get('note'),
                'base_fare': 50,
                'ride_charge': 180,
                'distance': form.cleaned_data.get('distance'),
                'platform_fee': 20,
                'total_amount': 250,
                'completed_ride': 0,
                'total_ride': 0,
                'total_spent': 0,
                'fare': 250,
                'estimate_fare': 250,
                'your_rating': '',
                'driver_name': 'Raj Kumar',
                'driver_phone': '9876543210',
                'vehicle_number': 'DL 01 AB 1234',
                'payment_type': 'Cash',
                'payment_status': 'Pending',
            }

            request.session['booking_data'] = booking_data
            request.session.modified = True

            return redirect('payment')

        return render(
            request,
            'user/profile/booking.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )


class UserPaymentView(View):

    def get(self, request):
        form = Payment()
        booking_data = request.session.get('booking_data', {})

        return render(
            request,
            'user/profile/payment.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
                'booking_data': booking_data,
            }
        )

    def post(self, request):
        form = Payment(request.POST)
        booking_data = request.session.get('booking_data', {})

        if form.is_valid():
            booking_data['payment_id'] = form.cleaned_data.get('payment_id')
            booking_data['payment_date'] = form.cleaned_data.get('payment_date')
            booking_data['payment_time'] = form.cleaned_data.get('payment_time')
            booking_data['payment_type'] = form.cleaned_data.get('payment_type')
            booking_data['payment_receipt'] = form.cleaned_data.get('payment_receipt')
            booking_data['payment_status'] = 'Paid'
            booking_data['ride_status'] = 'Confirmed'

            request.session['booking_data'] = booking_data
            request.session.modified = True

            messages.success(
                request,
                'Payment complete successfully!'
            )

            return redirect('myride')

        return render(
            request,
            'user/profile/payment.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
                'booking_data': booking_data,
            }
        )


class UserMyRideView(View):

    def get(self, request):
        booking_data = request.session.get('booking_data', {})

        return render(
            request,
            'user/profile/myride.html',
            {
                'sidebar_menu': SIDEBAR_MENU,
                'booking_data': booking_data,
            }
        )


class UserDashboardView(View):

    def get(self, request):
        booking_data = request.session.get('booking_data', {})

        return render(
            request,
            'user/dashboard.html',
            {
                'sidebar_menu': SIDEBAR_MENU,
                'booking_data': booking_data,
            }
        )


class TrackRideView(View):

    def get(self, request):
        booking_data = request.session.get('booking_data', {})

        return render(
            request,
            'user/profile/track.html',
            {
                'sidebar_menu': SIDEBAR_MENU,
                'booking_data': booking_data,
            }
        )

class UserEditProfileView(TemplateView):
    def get(self, request):
        form = Profile()
        return render(
            request,
            'user/profile/editprofile.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )


class UserLoginView(TemplateView):
    def get(self, request):
        form = LoginForm()
        return render(
            request,
            'user/login.html',
            {
                'form': form,
                'social_links': SOCIAL_LINKS,
            }
        )


class UserSignupView(TemplateView):
    def get(self, request):
        form = UserForm()
        return render(
            request,
            'user/signup.html',
            {
                'form': form,
                'social_links': SOCIAL_LINKS,
            }
        )


class UserProfileView(TemplateView):
    def get(self, request):
        form = Profile()
        return render(
            request,
            'user/profile/profile.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )


class ForgetPasswordView(TemplateView):
    def get(self, request):
        form = ForgetPassword()
        return render(
            request,
            'user/profile/forgetpassword.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )


class ResetPasswordView(TemplateView):
    def get(self, request):
        form = ResetPassword()
        return render(
            request,
            'user/profile/resetpassword.html',
            {
                'form': form,
                'sidebar_menu': SIDEBAR_MENU,
            }
        )

class PaymentDetailsView(TemplateView):
    def get(self, request):
        form = Payment()
        return render(
            request,
            'user/profile/paymentdetails.html',
            {
                'sidebar_menu': SIDEBAR_MENU,
                'form': form,
            }
        )
    
class PaymentReceiptView(TemplateView):
    def get(self, request):
        form = Payment()
        return render(
            request,
            'user/profile/paymentreceipt.html',
            {
                'sidebar_menu': SIDEBAR_MENU,
                'form': form,
            }
        )

class CancelRideView(View):
    def post(self, request):
        request.session.pop('booking_data', None)

        messages.success(
            request,
            'Ride cancelled successfully.'
        )

        return redirect('myride')