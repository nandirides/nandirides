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
        "url": "vehicle_dashboard",
        "permission": "vehicles.view_vehicle",
        "active_urls": [
            "vehicle_dashboard",
            "vehicle_list",
            "vehicle_detail",
            "vehicle_edit",
            "vehicle_add",
            "vehicle_type_list",
            "vehicle_type_add",
            "vehicle_type_form_edit",
            "assignment_list",
            "assignment_add",
            "assignment_edit",
            "assignment_end",
            "document_list",
            "document_add",
            "document_edit",
        ],
    },
    {
        "title": "Locations",
        "icon": "bi-geo-alt",
        "url": "location_dashboard",
        "permission": "locations.view_location",
        "active_urls": [
            "location_dashboard",
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
        "icon": "bi-tags",
        "url": "pricing_dashboard",
        "permission": "pricing.view_farerule",
        "active_urls": [
            "pricing_dashboard",
            "fare_rule_list",
            "fare_rule_create",
            "fare_rule_detail",
            "fare_rule_edit",
            "fare_rule_toggle",
            "surge_list",
            "surge_create",
            "surge_detail",
            "surge_edit",
            "surge_toggle",
            "fare_breakdown_list",
            "fare_breakdown_detail",
        ],
    },
    {
        "title": "Promotions",
        "icon": "bi-megaphone",
        "url": "promotions_dashboard",
        "permission": "promotions.view_coupon",
        "active_urls": [
            "promotions_dashboard",
            "coupon_list",
            "coupon_create",
            "coupon_detail",
            "coupon_edit",
            "coupon_toggle",
            "coupon_usage_list",
            "coupon_usage_detail",
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
        "url": "support_dashboard",
        "permission": "support.view_supportticket",
        "active_urls": [
            "support_dashboard",
            "ticket_list",
            "ticket_add",
            "ticket_edit",
            "ticket_detail",
            "category_list",
            "category_add",
            "category_edit",
            "notification_list",
            "notification_read",
            "notification_read_all",
        ],
    },
    {
        "title": "Permissions",
        "icon": "bi-gear",
        "permission": "drivers.view_driver",
        "children": [
            {
                "title": "Groups",
                "icon": "bi-circle",
                "url": "group_list",
                "permission": None,
            },
            {
                "title": "Administration",
                "icon": "bi-circle",
                "url": "admin:index",
                "staff_only": True,
                "active_urls": [
                    "index",
                ],
            },
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