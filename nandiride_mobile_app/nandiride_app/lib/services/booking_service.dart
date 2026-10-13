import 'api_service.dart';

class BookingService {
  // 1. Fetch pickup/drop locations.
  static Future<Map<String, dynamic>> getLocations({
    int? cityId,
  }) async {
    final query = cityId == null ? '' : '?city=$cityId';

    return ApiService.get(
      '/locations/locations/$query',
      authenticated: true,
    );
  }

  // 2. Fetch active vehicle types.
  static Future<Map<String, dynamic>> getVehicleTypes() async {
    return ApiService.get(
      '/vehicles/types/',
      authenticated: true,
    );
  }

  // 3. Calculate estimated fare.
  static Future<Map<String, dynamic>> estimateFare({
    required int pickupLocationId,
    required int dropLocationId,
    required int vehicleTypeId,
    String couponCode = '',
  }) async {
    final Map<String, dynamic> data = {
      'pickup_location': pickupLocationId,
      'drop_location': dropLocationId,
      'vehicle_type': vehicleTypeId,
    };

    if (couponCode.trim().isNotEmpty) {
      data['coupon_code'] = couponCode.trim();
    }

    return ApiService.post(
      '/rides/fare-estimate/',
      data,
      authenticated: true,
    );
  }

  // 4. Create a passenger ride request.
  static Future<Map<String, dynamic>> createRideRequest({
    required int pickupLocationId,
    required int dropLocationId,
    required int vehicleTypeId,
    int? couponId,
  }) async {
    final Map<String, dynamic> data = {
      'pickup_location': pickupLocationId,
      'drop_location': dropLocationId,
      'vehicle_type': vehicleTypeId,
    };

    if (couponId != null) {
      data['coupon'] = couponId;
    }

    return ApiService.post(
      '/rides/requests/',
      data,
      authenticated: true,
    );
  }
  
static Future<Map<String, dynamic>> saveMapLocation({
  required String address,
  required double latitude,
  required double longitude,
  int? cityId,
}) async {
  final Map<String, dynamic> data = {
    'address': address,
    'latitude': latitude.toStringAsFixed(6),
    'longitude': longitude.toStringAsFixed(6),
  };

  if (cityId != null) {
    data['city'] = cityId;
  }

  return ApiService.post(
    '/locations/locations/map-select/',
    data,
    authenticated: true,
  );
}

}
