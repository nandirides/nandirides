
from datetime import datetime
from django.urls import reverse

def site_data(request):
    return {
        # SITE
        'site_name': 'NandiRide',
        'site_tagline': "Thank you for choosing NandiRide. Let's travel together!",
        'phone': '+91 9410554430',
        'phone2': '+91 4421-554430',
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
                'url': reverse('services'),
                'icon': 'fa fa-cogs',
            },
            {
                'name': 'Blog',
                'url': reverse('blog'),
                'icon': 'fa fa-cogs',
            },
            {
                'name': 'Career',
                'url': reverse('career'),
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
    }
