from django import template


register = template.Library()


NAVIGATION = [
    {
        "title": "Dashboard",
        "icon": "bi-speedometer2",
        "url": "dashboard",
        "permission": None,
    },
    {
        "title": "Admin Profile",
        "icon": "bi-person",
        "url": "admin_profile",
        "permission": "auth.user_profile",
    },
    {
        "title": "Admin Setting",
        "icon": "bi-gear",
        "url": "user_setting",
        "permission": "auth.user_setting",
    },
    {
        "title": "Ride Status",
        "icon": "bi-scooter",
        "url": "ride_list",
        "permission": "rides.view_ride",
        "active_urls": [
            "ride_list",
            "ride_details",
            "ride_add",
            "ride_edit",
            "ride_status_update",
        ],
    },
    {
        "title": "Users",
        "icon": "bi-people",
        "permission": "auth.view_user",
        "children": [
            {
                "title": "All Users",
                "icon": "bi-circle",
                "url": "user_list",
                "permission": "auth.view_user",
            },
            {
                "title": "Add User",
                "icon": "bi-circle",
                "url": "user_create",
                "permission": "auth.add_user",
            },
        ],
    },
    {
        "title": "Drivers",
        "icon": "bi-person-badge",
        "permission": "drivers.view_driver",
        "children": [
            {
                "title": "All Drivers",
                "icon": "bi-circle",
                "url": "driver_list",
                "permission": "drivers.view_driver",
            },
            {
                "title": "Add Driver",
                "icon": "bi-circle",
                "url": "driver_create",
                "permission": "drivers.add_driver",
            },
        ],
    },
    {
        "title": "Vehicles",
        "icon": "bi-car-front",
        "permission": "vehicle.view_vehicle",
        "children": [
            {
                "title": "Vehicle Dashboard",
                "icon": "bi-speedometer2",
                "url": "vehicle_dashboard",
                "permission": "vehicle.view_vehicle",
                "active_urls": [
                    "vehicle_dashboard",
                ],
            },
            {
                "title": "All Vehicles",
                "icon": "bi-car-front",
                "url": "vehicle_list",
                "permission": "vehicle.view_vehicle",
                "active_urls": [
                    "vehicle_list",
                    "vehicle_detail",
                    "vehicle_edit",
                ],
            },
            {
                "title": "Add Vehicle",
                "icon": "bi-plus-circle",
                "url": "vehicle_add",
                "permission": "vehicle.add_vehicle",
            },
            {
                "title": "Vehicle Types",
                "icon": "bi-grid-3x3-gap",
                "url": "vehicle_type_list",
                "permission": "vehicle.view_vehicletype",
                "active_urls": [
                    "vehicle_type_list",
                    "vehicle_type_edit",
                ],
            },
            {
                "title": "Add Vehicle Type",
                "icon": "bi-plus-circle",
                "url": "vehicle_type_add",
                "permission": "vehicle.add_vehicletype",
            },
            {
                "title": "Driver Assignments",
                "icon": "bi-person-vcard",
                "url": "assignment_list",
                "permission": "vehicle.view_drivervehicle",
                "active_urls": [
                    "assignment_list",
                    "assignment_edit",
                ],
            },
            {
                "title": "Assign Vehicle",
                "icon": "bi-person-plus",
                "url": "assignment_add",
                "permission": "vehicle.add_drivervehicle",
            },
            {
                "title": "Vehicle Documents",
                "icon": "bi-file-earmark-text",
                "url": "document_list",
                "permission": "vehicle.view_vehicledocument",
                "active_urls": [
                    "document_list",
                    "document_edit",
                ],
            },
            {
                "title": "Upload Document",
                "icon": "bi-file-earmark-plus",
                "url": "document_add",
                "permission": "vehicle.add_vehicledocument",
            },
        ],
    },
    {
        "title": "Payments",
        "icon": "bi-credit-card",
        "url": "payment_list",
        "permission": "payments.view_payment",
    },
    {
        "title": "Pricing",
        "icon": "bi-cash-coin",
        "permission": "pricing.view_farerule",
        "children": [
            {
                "title": "Fare Rules",
                "icon": "bi-calculator",
                "url": "fare_rule_list",
                "permission": "pricing.view_farerule",
            },
            {
                "title": "Add Fare Rule",
                "icon": "bi-plus-circle",
                "url": "fare_rule_create",
                "permission": "pricing.add_farerule",
            },
            {
                "title": "Surge Pricing",
                "icon": "bi-lightning-charge",
                "url": "surge_list",
                "permission": "pricing.view_surgepricing",
            },
            {
                "title": "Add Surge Pricing",
                "icon": "bi-plus-circle",
                "url": "surge_create",
                "permission": "pricing.add_surgepricing",
            },
            {
                "title": "Fare Breakdowns",
                "icon": "bi-receipt",
                "url": "fare_breakdown_list",
                "permission": "pricing.view_farebreakdown",
            },
        ],
    },
    {
        "title": "Promotions",
        "icon": "bi-ticket-perforated",
        "permission": None,
        "children": [
            {
                "title": "Coupons",
                "icon": "bi-ticket",
                "url": "coupon_list",
                "permission": "promotions.view_coupon",
            },
            {
                "title": "Add Coupon",
                "icon": "bi-plus-circle",
                "url": "coupon_create",
                "permission": "promotions.add_coupon",
            },
            {
                "title": "Coupon Usage",
                "icon": "bi-receipt",
                "url": "coupon_usage_list",
                "permission": "promotions.view_couponusage",
            },
        ],
    },
    {
        "title": "Gallery",
        "icon": "bi-images",
        "url": "ride_gallery",
        "permission": "auth.ride_gallery",
    },
    {
        "title": "Support",
        "icon": "bi-headset",
        "permission": "support.view_supportticket",
        "children": [
            {
                "title": "Support Dashboard",
                "icon": "bi-speedometer2",
                "url": "support_dashboard",
                "permission": "support.view_supportticket",
            },
            {
                "title": "Tickets",
                "icon": "bi-ticket-detailed",
                "url": "ticket_list",
                "permission": "support.view_supportticket",
            },
            {
                "title": "Add Ticket",
                "icon": "bi-plus-circle",
                "url": "ticket_add",
                "permission": "support.add_supportticket",
            },
            {
                "title": "Categories",
                "icon": "bi-folder2-open",
                "url": "category_list",
                "permission": "support.view_supportcategory",
            },
            {
                "title": "Add Category",
                "icon": "bi-folder-plus",
                "url": "category_add",
                "permission": "support.add_supportcategory",
            },
            {
                "title": "Notifications",
                "icon": "bi-bell",
                "url": "notification_list",
                "permission": "support.view_notification",
            },
        ],
    },
    {
        "title": "Administration",
        "icon": "bi-gear",
        "url": "admin:index",
        "staff_only": True,
        "active_urls": [
            "index",
        ],
    },
]


def user_has_permission(user, permission):
    if not permission:
        return True

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.has_perm(permission)


def item_is_visible(user, item):
    if item.get("staff_only") and not user.is_staff:
        return False

    permission = item.get("permission")

    if not user_has_permission(user, permission):
        return False

    return True


def build_navigation(user, current_url_name):
    navigation = []

    for item in NAVIGATION:
        if not item_is_visible(user, item):
            continue

        item = item.copy()
        children = item.get("children", [])
        visible_children = []

        for child in children:
            if not item_is_visible(user, child):
                continue

            child = child.copy()
            active_urls = child.get("active_urls", [])

            child["active"] = (
                child.get("url") == current_url_name
                or current_url_name in active_urls
            )

            visible_children.append(child)

        if children and not visible_children:
            continue

        item["children"] = visible_children

        item["active"] = (
            item.get("url") == current_url_name
            or any(
                child.get("active", False)
                for child in visible_children
            )
        )

        item["open"] = (
            item["active"]
            and bool(visible_children)
        )

        navigation.append(item)

    return navigation


@register.simple_tag(takes_context=True)
def get_navigation(context):
    request = context["request"]
    current_url_name = ""

    if request.resolver_match:
        current_url_name = request.resolver_match.url_name

    return build_navigation(
        request.user,
        current_url_name,
    )