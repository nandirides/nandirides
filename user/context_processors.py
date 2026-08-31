
from datetime import datetime
from django.urls import reverse

def site_data(request):
    return {
        # SITE
        'site_name': 'NandiRide',
        'site_tagline': "Thank you for choosing NandiRide. Let's travel together!",
        'phone': '+91 9410554430',
        'phone2': '+91 2144-554430',
        'email': 'support@nandidride.com',
        'email2': 'nandidride@gmail.com',
        'location': 'Haridwar, India',
        'current_year': datetime.now().year,
        'footer_tag': 'All Rights Reserved',

        # NAVBAR
        'nav_links': [
            {
                'name': 'Home',
                'url': reverse('home'),
                'icon': 'fa fa-home',
            },
            {
                'name': 'About',
                'url': reverse('about'),
                'icon': 'fa fa-info-circle',
            },
            {
                'name': 'Services',
                'url': reverse('underconstruction'),
                'icon': 'fa fa-cogs',
            },
            {
                'name': 'Career',
                'url': reverse('underconstruction'),
                'icon': 'fa fa-briefcase',
            },
            {
                'name': 'Contact',
                'url': reverse('contact'),
                'icon': 'fa fa-phone',
            },
        ],

        # LOGIN
        'button_login': 'Login',
        'url_login': reverse('login'),
        'button_reg': 'Register',
        'url_signup': reverse('signup'),

        # SUPPORT
        'support_links': [
            {
                'name': 'Help Center',
                'url': reverse('contact'),
            },
            {
                'name': 'Safety',
                'url': reverse('underconstruction'),
            },
            {
                'name': 'Terms & Conditions',
                'url': reverse('underconstruction'),
            },
            {
                'name': 'Privacy Policy',
                'url': reverse('underconstruction'),
            },
        ],

        # SOCIAL
        'social_links': [
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
                'name': 'Twitter',
                'icon': 'fa-brands fa-twitter',
                'url': '#',
            },
            {
                'name': 'LinkedIn',
                'icon': 'fa-brands fa-linkedin-in',
                'url': '#',
            },
        ],

        # HOME PAGE
        'hero_slides': [
            {
                'badge': 'Fast & Reliable',
                'title': 'Your Ride, Your Way',
                'description': 'Book a bike, auto or cab with Nandi Ride.',
                'button_text': '🚕 Book Now',
                'button_url': reverse('underconstruction'),
                'button_class': 'btn-light',
                'image_class': 'bg-img1',
                'icon': '🛵',
                'heading': 'Ride with Nandi',
            },
            {
                'badge': 'Affordable Rides',
                'title': 'Travel More, Pay Less',
                'description': 'Affordable rides at your fingertips.',
                'button_text': '🏍️ Start Riding',
                'button_url': reverse('underconstruction'),
                'button_class': 'btn-warning',
                'image_class': 'bg-img2 bg-dark',
                'icon': '💰',
                'heading': 'Best Ride Experience',
            },
            {
                'badge': 'Safe & Secure',
                'title': 'Ride Safely With Nandi',
                'description': 'Your safety is our priority.',
                'button_text': '📍 Book Your Ride',
                'button_url': reverse('underconstruction'),
                'button_class': 'btn-light',
                'image_class': 'bg-img3 bg-secondary',
                'icon': '🔒',
                'heading': 'Safe Journey',
            },
        ],

        # BOOKING
        'ride_title': 'Book Your Ride',
        'page_subtitle': 'Enter your pickup and destination',
        'booking_url': reverse('login'),
        'pickup_label': 'Pickup Location',
        'pickup_placeholder': 'Enter pickup location',
        'drop_label': 'Drop Location',
        'drop_placeholder': 'Enter destination',
        'booking_button': 'Book',

        # SECOND BOX
        'book_title': 'Nandi Ride',
        'title': 'Your Journey Starts Here',
        'description': 'Choose your preferred ride and enjoy a safe, comfortable and affordable journey.',

        # RIDE TYPES
        'ride_types': [
            {
                'icon': 'fa-solid fa-motorcycle',
                'name': 'Nandi Bike',
                'description': 'Quick and affordable bike rides.',
                'button': 'Choose Bike',
                'url': reverse('underconstruction'),
            },
            {
                'icon': 'fa-solid fa-car-side',
                'name': 'Nandi Auto',
                'description': 'Comfortable auto rides.',
                'button': 'Choose Auto',
                'url': reverse('underconstruction'),
            },
            {
                'icon': 'fa-solid fa-taxi',
                'name': 'Nandi Cab',
                'description': 'Comfortable rides for everyone.',
                'button': 'Choose Cab',
                'url': reverse('underconstruction'),
            },
            {
                'icon': 'fa-solid fa-van-shuttle',
                'name': 'Nandi Mini',
                'description': 'Comfortable rides for small groups.',
                'button': 'Choose Mini',
                'url': reverse('underconstruction'),
            },
            {
                'icon': 'fa-solid fa-bicycle',
                'name': 'Nandi Cycle',
                'description': 'Simple and eco-friendly cycle rides.',
                'button': 'Choose Cycle',
                'url': reverse('underconstruction'),
            },
        ],
        'ride_section_title': 'Choose Your Ride',
        'ride_section_subtitle': 'Select the ride that suits your journey',

        # WHY NANDI
        'why_choose': [
            {
                'icon': 'fa-solid fa-shield-halved',
                'title': 'Safe & Secure',
                'description': 'Your safety is our top priority.',
            },
            {
                'icon': 'fa-solid fa-wallet',
                'title': 'Affordable Fare',
                'description': 'Enjoy transparent and affordable fares.',
            },
            {
                'icon': 'fa-solid fa-bolt',
                'title': 'Quick Booking',
                'description': 'Book your ride quickly and easily.',
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'title': 'Live Tracking',
                'description': 'Track your ride in real time.',
            },
            {
                'icon': 'fa-solid fa-headset',
                'title': '24/7 Support',
                'description': 'We are always here to help you.',
            },
        ],

        # ABOUT PAGE
        'about_hero': {
            'title': 'Your Ride,',
            'highlight': 'Our Commitment',
            'description': 'NandiRide is here to make your travel easy, safe, and comfortable. We connect you with reliable rides anytime, anywhere.',
            'button': 'Ride with NandiRide',
            'button_url': reverse('login'),
            'button_icon': 'fa-solid fa-arrow-right',
        },

        'about_intro': {
            'small': 'WHO WE ARE',
            'title': 'Driven by Trust, Focused on You',
            'description': 'NandiRide was created with a simple vision — to provide dependable, affordable and convenient transportation while maintaining the highest standards of safety and customer satisfaction.',
        },

        # ABOUT FEATURES
        'about_features': [
            {
                'icon': 'fa-solid fa-users',
                'title': 'Customer First',
                'description': 'We put our customers at the heart of everything we do.',
            },
            {
                'icon': 'fa-solid fa-shield-halved',
                'title': 'Safety Always',
                'description': 'Verified drivers, real-time tracking and reliable support.',
            },
            {
                'icon': 'fa-solid fa-car',
                'title': 'Reliable Rides',
                'description': 'From daily commutes to long trips, we are always here.',
            },
        ],

        # ABOUT STATS
        'about_stats': [
            {
                'icon': 'fa-solid fa-users',
                'number': '10K+',
                'title': 'Happy Customers',
            },
            {
                'icon': 'fa-solid fa-car',
                'number': '25K+',
                'title': 'Rides Completed',
            },
            {
                'icon': 'fa-solid fa-location-dot',
                'number': '50+',
                'title': 'Cities Covered',
            },
            {
                'icon': 'fa-solid fa-star',
                'number': '4.8/5',
                'title': 'Customer Rating',
            },
        ],

        # ABOUT VALUES
        'about_values': {
            'small': 'OUR VALUES',
            'title': 'The Principles That Drive Us',
        },

        # ABOUT VALUE CARDS
        'about_value_cards': [
            {
                'icon': 'fa-solid fa-bullseye',
                'title': 'Our Mission',
                'description': 'To provide safe, affordable and convenient rides while building a transportation ecosystem people can truly rely on.',
            },
            {
                'icon': 'fa-solid fa-eye',
                'title': 'Our Vision',
                'description': 'To become a trusted ride-hailing platform, connecting people with convenient transportation every day.',
            },
            {
                'icon': 'fa-regular fa-heart',
                'title': 'Our Promise',
                'description': 'We promise transparency, reliability and respect for every customer and driver who travels with NandiRide.',
            },
        ],

        # CONTACT PAGE
        'contact_hero': {
            'badge': 'Nandi Ride Support',
            'title': "We're Here to",
            'highlight': 'Help You',
            'description': 'Have a question, complaint or feedback? Our Nandi Ride support team is ready to help you.',
            'icon': '📞',
        },

        'contact_info': [
            {
                'icon': '📞',
                'icon_class': 'bg-danger-subtle text-danger',
                'title': 'Call Us',
                'description': 'Available 24/7 for ride support',
                'value': '+91 9410554430',
                'url': 'tel:+919410554430',
                'link_class': 'text-danger',
            },
            {
                'icon': '✉️',
                'icon_class': 'bg-primary-subtle text-primary',
                'title': 'Email Us',
                'description': 'Send us your questions anytime',
                'value': 'support@nandidride.com',
                'url': 'mailto:support@nandidride.com',
                'link_class': 'text-primary',
            },
            {
                'icon': '📍',
                'icon_class': 'bg-success-subtle text-success',
                'title': 'Our Office',
                'description': 'Nandi Ride Headquarters',
                'value': 'Haridwar, India',
                'url': '#',
                'link_class': 'text-success',
            },
        ],

        'contact_form': {
            'small': 'GET IN TOUCH',
            'title': 'Have Something',
            'highlight': 'To Say?',
            'description': 'Whether you need help with your booking, want to report an issue, or simply want to share your feedback, send us a message.',
            'button': 'Send Message',
            'button_icon': '➜',
        },

        'contact_support_points': [
            {
                'icon': '✓',
                'text': 'Quick customer support',
            },
            {
                'icon': '✓',
                'text': 'Booking assistance',
            },
            {
                'icon': '✓',
                'text': 'Feedback & complaints',
            },
        ],

        'contact_subjects': [
            {
                'value': 'booking',
                'name': 'Booking Issue',
            },
            {
                'value': 'payment',
                'name': 'Payment Issue',
            },
            {
                'value': 'driver',
                'name': 'Driver Related',
            },
            {
                'value': 'complaint',
                'name': 'Complaint',
            },
            {
                'value': 'feedback',
                'name': 'Feedback',
            },
            {
                'value': 'other',
                'name': 'Other',
            },
        ],

        'contact_faq': [
            {
                'id': 'faqOne',
                'question': 'How can I book a Nandi Ride?',
                'answer': 'You can book your ride through the Nandi Ride booking page by entering your pickup and destination.',
                'show': True,
            },
            {
                'id': 'faqTwo',
                'question': 'How can I track my ride?',
                'answer': 'After booking, you can view your ride status and driver information from the My Rides section.',
                'show': False,
            },
            {
                'id': 'faqThree',
                'question': 'How can I report a complaint?',
                'answer': 'You can submit your complaint using the contact form or the Complaints section of your dashboard.',
                'show': False,
            },
        ],

        'contact_cta': {
            'title': 'Ready to Ride with Nandi?',
            'description': 'Book your ride today and enjoy a safe journey.',
            'button': '🚕 Book Your Ride',
            'url': reverse('signup'),
        },

    }
