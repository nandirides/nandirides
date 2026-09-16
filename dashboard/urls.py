from django.urls import path
from dashboard import views
from drivers import views as driver_views
from payments import views as payment_views
from pricing import views as pricing_views
from promotions import views as promotion_views
from support import views as support_views
from vehicles import views as vehicle_views
from rides import views as rides_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("account/profile/", views.admin_profile, name="admin_profile"),
    path("account/editprofile/", views.edit_admin_profile, name="edit_admin_profile"),
    path("account/setting/", views.user_setting, name="user_setting"),
    path("users/<int:user_id>/profile/", views.user_profile, name="user_profile"),

    # Ride Management
    path("rides/", rides_views.ride_list, name="ride_list"),
    path("rides/add/", rides_views.ride_create_edit, name="ride_add"),
    path("rides/<int:pk>/edit/", rides_views.ride_create_edit, name="ride_edit"),
    path("rides/<int:pk>/status/", rides_views.ride_status_update, name="ride_status_update"),
    path("rides/<int:pk>/delete/", rides_views.ride_delete, name="ride_delete"),
    path("rides/<int:pk>/", rides_views.ride_details, name="ride_details"),

    # Ride Driver Assignment
    path("rides/<int:ride_pk>/assignments/", rides_views.ride_assignment_list, name="ride_assignment_list"),
    path("rides/<int:ride_pk>/assignments/add/", rides_views.ride_assignment_create, name="ride_assignment_add"),
    path("rides/assignments/<int:pk>/edit/", rides_views.ride_assignment_edit, name="ride_assignment_edit"),
    path("rides/assignments/<int:pk>/delete/", rides_views.ride_assignment_delete, name="ride_assignment_delete"),

    # Ride Tracking
    path("rides/<int:ride_pk>/tracking/", rides_views.ride_tracking_list, name="ride_tracking_list"),
    path("rides/<int:ride_pk>/tracking/add/", rides_views.ride_tracking_create, name="ride_tracking_add"),
    path("rides/tracking/<int:pk>/delete/", rides_views.ride_tracking_delete, name="ride_tracking_delete"),

    # Ride Cancellation
    path("rides/<int:ride_pk>/cancel/", rides_views.ride_cancellation_create, name="ride_cancellation_add"),

    # Ride Rating
    path("rides/<int:ride_pk>/rating/add/", rides_views.ride_rating_create, name="ride_rating_add"),

    # Ride Stops
    path("rides/<int:ride_pk>/stops/", rides_views.ride_stop_list, name="ride_stop_list"),
    path("rides/<int:ride_pk>/stops/add/", rides_views.ride_stop_create, name="ride_stop_add"),
    path("rides/stops/<int:pk>/edit/", rides_views.ride_stop_edit, name="ride_stop_edit"),
    path("rides/stops/<int:pk>/delete/", rides_views.ride_stop_delete, name="ride_stop_delete"),

    # Gallery Management
    path("gallery/", views.ride_gallery, name="ride_gallery"),
    path("gallery/<int:pk>/delete/", views.gallery_delete, name="gallery_delete"),

    # User Management
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_create, name="user_create"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("users/<int:pk>/edit/", views.user_create, name="user_update"),

    # Driver Management
    path("drivers/", driver_views.driver_list, name="driver_list"),
    path("drivers/add/", driver_views.driver_form, name="driver_create"),
    path("drivers/<int:pk>/edit/", driver_views.driver_form, name="driver_edit"),
    path("drivers/<int:driver_pk>/documents/add/", driver_views.driver_document_form, name="driver_document_create"),
    path("drivers/<int:driver_pk>/documents/<int:pk>/edit/", driver_views.driver_document_form, name="driver_document_edit"),
    path("drivers/<int:pk>/", driver_views.driver_detail, name="driver_detail"),

    # Payment Management
    path("payments/", payment_views.payment_list, name="payment_list"),
    path("payments/<int:pk>/", payment_views.payment_detail, name="payment_detail"),
    path("payments/<int:payment_pk>/refund/add/", payment_views.refund_form, name="refund_create"),
    path("payments/<int:payment_pk>/refund/<int:pk>/edit/", payment_views.refund_form, name="refund_edit"),

    # Pricing Management
    path("pricing/fare-rules/", pricing_views.fare_rule_list, name="fare_rule_list"),
    path("pricing/fare-rules/add/", pricing_views.fare_rule_create, name="fare_rule_create"),
    path("pricing/fare-rules/<int:pk>/", pricing_views.fare_rule_detail, name="fare_rule_detail"),
    path("pricing/fare-rules/<int:pk>/edit/", pricing_views.fare_rule_edit, name="fare_rule_edit"),
    path("pricing/fare-rules/<int:pk>/toggle/", pricing_views.fare_rule_toggle, name="fare_rule_toggle"),
    path("pricing/surge-pricing/", pricing_views.surge_list, name="surge_list"),
    path("pricing/surge-pricing/add/", pricing_views.surge_create, name="surge_create"),
    path("pricing/surge-pricing/<int:pk>/", pricing_views.surge_detail, name="surge_detail"),
    path("pricing/surge-pricing/<int:pk>/edit/", pricing_views.surge_edit, name="surge_edit"),
    path("pricing/surge-pricing/<int:pk>/toggle/", pricing_views.surge_toggle, name="surge_toggle"),
    path("pricing/fare-breakdowns/", pricing_views.fare_breakdown_list, name="fare_breakdown_list"),
    path("pricing/fare-breakdowns/<int:pk>/", pricing_views.fare_breakdown_detail, name="fare_breakdown_detail"),

    # Promotion Management
    path("promotions/coupons/", promotion_views.coupon_list, name="coupon_list"),
    path("promotions/coupons/add/", promotion_views.coupon_create, name="coupon_create"),
    path("promotions/coupons/<int:pk>/", promotion_views.coupon_detail, name="coupon_detail"),
    path("promotions/coupons/<int:pk>/edit/", promotion_views.coupon_edit, name="coupon_edit"),
    path("promotions/coupons/<int:pk>/toggle/", promotion_views.coupon_toggle, name="coupon_toggle"),
    path("promotions/coupon-usage/", promotion_views.coupon_usage_list, name="coupon_usage_list"),
    path("promotions/coupon-usage/<int:pk>/", promotion_views.coupon_usage_detail, name="coupon_usage_detail"),

    # Support Management
    path("support/", support_views.support_dashboard, name="support_dashboard"),
    path("support/tickets/", support_views.ticket_list, name="ticket_list"),
    path("support/tickets/add/", support_views.ticket_form, name="ticket_add"),
    path("support/tickets/<int:pk>/edit/", support_views.ticket_form, name="ticket_edit"),
    path("support/tickets/<int:pk>/", support_views.ticket_detail, name="ticket_detail"),
    path("support/categories/", support_views.category_list, name="category_list"),
    path("support/categories/add/", support_views.category_form, name="category_add"),
    path("support/categories/<int:pk>/edit/", support_views.category_form, name="category_edit"),
    path("support/categories/<int:pk>/delete/", support_views.category_delete, name="category_delete"),
    path("support/notifications/", support_views.notification_list, name="notification_list"),
    path("support/notifications/<int:pk>/read/", support_views.notification_read, name="notification_read"),
    path("support/notifications/read-all/", support_views.notification_read_all, name="notification_read_all"),

    # Vehicle Management
    path("vehicles/", vehicle_views.vehicle_dashboard, name="vehicle_dashboard"),
    path("vehicles/list/", vehicle_views.vehicle_list, name="vehicle_list"),
    path("vehicles/add/", vehicle_views.vehicle_form, name="vehicle_add"),
    path("vehicles/<int:pk>/edit/", vehicle_views.vehicle_form, name="vehicle_edit"),
    path("vehicles/<int:pk>/delete/", vehicle_views.vehicle_delete, name="vehicle_delete"),
    path("vehicles/<int:pk>/", vehicle_views.vehicle_detail, name="vehicle_detail"),

    # Vehicle Types
    path("vehicles/types/", vehicle_views.vehicle_type_list, name="vehicle_type_list"),
    path("vehicles/types/add/", vehicle_views.vehicle_type_form, name="vehicle_type_add"),
    path("vehicles/types/<int:pk>/edit/", vehicle_views.vehicle_type_form, name="vehicle_type_form_edit"),
    path("vehicles/types/<int:pk>/delete/", vehicle_views.vehicle_type_delete, name="vehicle_type_delete"),

    # Driver Assignments
    path("vehicles/assignments/", vehicle_views.assignment_list, name="assignment_list"),
    path("vehicles/assignments/add/", vehicle_views.assignment_form, name="assignment_add"),
    path("vehicles/assignments/<int:pk>/edit/", vehicle_views.assignment_form, name="assignment_edit"),
    path("vehicles/assignments/<int:pk>/end/", vehicle_views.assignment_end, name="assignment_end"),

    # Vehicle Documents
    path("vehicles/documents/", vehicle_views.document_list, name="document_list"),
    path("vehicles/documents/add/", vehicle_views.document_form, name="document_add"),
    path("vehicles/documents/<int:pk>/edit/", vehicle_views.document_form, name="document_edit"),
    path("vehicles/documents/<int:pk>/delete/", vehicle_views.document_delete, name="document_delete"),
]