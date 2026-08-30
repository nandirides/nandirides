from datetime import datetime
from django.urls import reverse

def site_data(request):
    return {
        'site_name': 'NandiRide',
        'site_tagline': 'Thank you for choosing NandiRide. Let\'s travel together!',
        'phone': '+91 9410554430',
        'phone2': '+91 2144-554430',
        'email': 'support@nandidride.com',
        'email2': 'nandidride@gmail.com',
        'location': 'Haridwar, India',
        'current_year': datetime.now().year,
        'button_login':'Login',
        'url_login': reverse('login'),
        'button_reg':'Register',
        'url_signup': reverse('signup'),

        'nav_links': [
                    {
                        'name': 'Home',
                        'icon': 'fa-brands fa-facebook-f',
                        'url': reverse('home'),
                    },
                    {
                        'name': 'About',
                        'icon': 'fa-brands fa-instagram',
                        'url': reverse('about'),
                    },
                    {
                        'name': 'Services',
                        'icon': 'fa-brands fa-twitter',
                        'url': reverse('underconstruction'),
                    },
                    {
                        'name': 'Contact',
                        'icon': 'fa-brands fa-linkedin-in',
                        'url': reverse('contact'),
                    },

                ],

        'support_links': [
                    {
                        'name': 'Help Center',
                        'url': 'underconstruction',
                    },
                    {
                        'name': 'Safety',
                        'url': 'underconstructiont',
                    },
                    {
                        'name': 'Terms & Condition',
                        'url': 'underconstruction',
                    },
                    {
                        'name': 'Privacy Policy',
                        'url': 'underconstruction',
                    },

                ],

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
    }