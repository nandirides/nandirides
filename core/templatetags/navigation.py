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
            "url": "user_profile",
            "permission": 'auth.user_profile',
    },

    {
            "title": "Admin Setting",
            "icon": "bi-gear",
            "url": "user_setting",
            "permission": 'auth.user_setting',
    },

    {
            "title": "User Ride Status",
            "icon": "bi-scooter",
            "url": "user_ridestatus",
            "permission": 'auth.user_ridestatus',
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
            "title": "Gallery",
            "icon": "bi-images",
            "url": "ride_gallery",
            "permission": "auth.ride_gallery",
        },

    {
        "title": "Administration",
        "icon": "bi-gear",
        "url": "admin:index",
        "staff_only": True,
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

        children = item.get("children", [])

        visible_children = []

        for child in children:

            if not item_is_visible(user, child):
                continue

            child = child.copy()

            child["active"] = (
                child.get("url") == current_url_name
            )

            visible_children.append(child)

        item = item.copy()

        item["children"] = visible_children

        item["active"] = (
            item.get("url") == current_url_name
            or any(
                child["active"]
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
        current_url_name = (
            request.resolver_match.url_name
        )

    return build_navigation(
        request.user,
        current_url_name,
    )