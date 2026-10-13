from decimal import Decimal, ROUND_HALF_UP
from math import radians, sin, cos, sqrt, atan2
from django.utils import timezone
from promotions.models import Coupon
from vehicles.models import VehicleType

def calculate_distance_km(pickup, drop):
    lat1 = radians(float(pickup.latitude))
    lon1 = radians(float(pickup.longitude))
    lat2 = radians(float(drop.latitude))
    lon2 = radians(float(drop.longitude))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return Decimal(str(6371 * c)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

def calculate_duration_minutes(distance_km):
    if distance_km <= 0:
        return 0
    average_speed = Decimal("30")
    duration = (distance_km / average_speed) * Decimal("60")
    return int(duration.quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    ))

def calculate_coupon_discount(coupon, user, subtotal):
    if not coupon:
        return Decimal("0.00"), ""

    now = timezone.now()

    if not coupon.is_active:
        return Decimal("0.00"), "Coupon is inactive."

    if now < coupon.valid_from:
        return Decimal("0.00"), "Coupon is not active yet."

    if now > coupon.valid_to:
        return Decimal("0.00"), "Coupon has expired."

    if subtotal < coupon.minimum_fare:
        return (
            Decimal("0.00"),
            f"Minimum fare for this coupon is ₹{coupon.minimum_fare}."
        )

    if coupon.usage_limit is not None:
        total_usage = coupon.usages.count()
        if total_usage >= coupon.usage_limit:
            return Decimal("0.00"), "Coupon usage limit has been reached."

    user_usage = coupon.usages.filter(user=user).count()

    if user_usage >= coupon.per_user_limit:
        return (
            Decimal("0.00"),
            "You have already reached the usage limit for this coupon."
        )

    if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
        discount = (
            subtotal * coupon.discount_value
        ) / Decimal("100")
        if coupon.maximum_discount is not None:
            discount = min(
                discount,
                coupon.maximum_discount
            )
    else:
        discount = coupon.discount_value

    discount = min(discount, subtotal)

    return (
        discount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        ),
        "Coupon applied successfully."
    )

def calculate_fare(
    pickup,
    drop,
    vehicle_type,
    user,
    coupon_code=""
):
    distance_km = calculate_distance_km(
        pickup,
        drop
    )

    duration_minutes = calculate_duration_minutes(
        distance_km
    )

    base_fare = vehicle_type.base_fare

    distance_fare = (
        distance_km * vehicle_type.per_km_rate
    )

    time_fare = (
        Decimal(duration_minutes)
        * vehicle_type.per_minute_rate
    )

    subtotal = (
        base_fare
        + distance_fare
        + time_fare
    )

    coupon = None
    discount = Decimal("0.00")
    coupon_message = ""

    if coupon_code:
        try:
            coupon = Coupon.objects.get(
                code__iexact=coupon_code.strip()
            )
        except Coupon.DoesNotExist:
            coupon_message = "Invalid coupon code."
        else:
            discount, coupon_message = calculate_coupon_discount(
                coupon,
                user,
                subtotal
            )

    final_fare = max(
        subtotal - discount,
        Decimal("0.00")
    )

    return {
        "distance_km": distance_km,
        "duration_minutes": duration_minutes,
        "base_fare": base_fare,
        "distance_fare": distance_fare,
        "time_fare": time_fare,
        "subtotal": subtotal,
        "coupon_code": coupon.code if coupon and discount > 0 else None,
        "discount": discount,
        "final_fare": final_fare,
        "coupon_message": coupon_message,
    }