import 'api_service.dart';

class BookingService {
  static Future<Map<String, dynamic>> getLocations({
    int? cityId,
  }) async {
    final query = cityId == null ? '' : '?city=$cityId';
    return ApiService.get(
      '/locations/list/$query',
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> getVehicleTypes() async {
    return ApiService.get(
      '/vehicles/types/',
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> estimateFare({
    required int pickupLocationId,
    required int dropLocationId,
    required int vehicleTypeId,
    String couponCode = '',
  }) async {
    final data = <String, dynamic>{
      'pickup_location': pickupLocationId,
      'drop_location': dropLocationId,
      'vehicle_type': vehicleTypeId,
      if (couponCode.trim().isNotEmpty)
        'coupon_code': couponCode.trim(),
    };

    return ApiService.post(
      '/rides/fare/estimate/',
      data,
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> createRideRequest({
    required int pickupLocationId,
    required int dropLocationId,
    required int vehicleTypeId,
    int? couponId,
  }) async {
    final data = <String, dynamic>{
      'pickup_location': pickupLocationId,
      'drop_location': dropLocationId,
      'vehicle_type': vehicleTypeId,
      if (couponId != null) 'coupon': couponId,
    };

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
  final data = <String, dynamic>{
    'address': address,
    'latitude': double.parse(latitude.toStringAsFixed(6)),
    'longitude': double.parse(longitude.toStringAsFixed(6)),
    if (cityId != null) 'city': cityId,
  };
  return ApiService.post(
    '/locations/map/select/',
    data,
    authenticated: true,
  );
}

  static Future<Map<String, dynamic>> getRideTracking(
    int rideId,
  ) async {
    return ApiService.get(
      '/rides/$rideId/tracking/',
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> getRideRequestTracking(
    int requestId,
  ) async {
    return ApiService.get(
      '/rides/requests/$requestId/tracking/',
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> updateDriverLocation({
    required int rideId,
    required double latitude,
    required double longitude,
    double? accuracy,
    double? speed,
    double? heading,
  }) async {
    final data = <String, dynamic>{
      'latitude': latitude,
      'longitude': longitude,
      if (accuracy != null) 'accuracy': accuracy,
      if (speed != null) 'speed': speed,
      if (heading != null) 'heading': heading,
    };

    return ApiService.post(
      '/rides/$rideId/tracking/update/',
      data,
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> updateRideStatus({
    required int rideId,
    required String action,
    String? otp,
  }) async {
    final data = <String, dynamic>{
      'action': action,
      if (otp != null && otp.trim().isNotEmpty)
        'otp': otp.trim(),
    };

    return ApiService.post(
      '/rides/$rideId/status/',
      data,
      authenticated: true,
    );
  }
}