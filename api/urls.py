from django.urls import include, path


urlpatterns = [

    path(
        "auth/",
        include("api.authentication.urls"),
    ),

    path(
        "users/",
        include("api.users.urls"),
    ),

    path(
        "rides/",
        include("api.rides.urls"),
    ),

    # path(
    #     "drivers/",
    #     include("api.drivers.urls"),
    # ),

    # path(
    #     "vehicles/",
    #     include("api.vehicles.urls"),
    # ),

    # path(
    #     "payments/",
    #     include("api.payments.urls"),
    # ),

    # path(
    #     "notifications/",
    #     include("api.notifications.urls"),
    # ),
]