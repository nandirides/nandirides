
import 'api_service.dart';

class DriverService {
  // Get logged-in driver's profile.
  static Future<Map<String, dynamic>> getMyProfile() async {
    return ApiService.get(
      '/drivers/me/',
      authenticated: true,
    );
  }

  // Register the logged-in user as a driver.
  static Future<Map<String, dynamic>> registerDriver({
    required String firstName,
    required String lastName,
    required String email,
    required String phone,
    required String licenseNumber,
    String? licenseExpiry,
    int experienceYears = 0,
  }) async {
    return ApiService.post(
      '/drivers/register/',
      {
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'phone': phone,
        'license_number': licenseNumber,
        'license_expiry': licenseExpiry,
        'experience_years': experienceYears,
      },
      authenticated: true,
    );
  }

  // Register a driver, or return the existing profile.
  static Future<Map<String, dynamic>> registerOrGetExistingProfile({
    required String firstName,
    required String lastName,
    required String email,
    required String phone,
    required String licenseNumber,
    String? licenseExpiry,
    int experienceYears = 0,
  }) async {
    try {
      return await registerDriver(
        firstName: firstName,
        lastName: lastName,
        email: email,
        phone: phone,
        licenseNumber: licenseNumber,
        licenseExpiry: licenseExpiry,
        experienceYears: experienceYears,
      );
    } catch (registrationError) {
      try {
        final profile = await getMyProfile();
        if (profile.isNotEmpty) {
          return profile;
        }
      } catch (_) {
        // No accessible existing driver profile.
      }
      throw Exception(
        'Driver registration failed: $registrationError',
      );
    }
  }

  // Update driver's online/offline availability.
  static Future<Map<String, dynamic>> updateOnlineStatus({
    required bool isOnline,
  }) async {
    return ApiService.post(
      '/drivers/online/status/',
      {'is_online': isOnline},
      authenticated: true,
    );
  }

  // Get pending ride requests available to this driver.
  static Future<Map<String, dynamic>> getPendingRideRequests() async {
    return ApiService.get(
      '/rides/driver/requests/',
      authenticated: true,
    );
  }

  // Accept a ride request.
  // The request ID and the accepted ride ID may be different.
  static Future<Map<String, dynamic>> acceptRide(
    int requestId,
  ) async {
    if (requestId <= 0) {
      throw ArgumentError.value(
        requestId,
        'requestId',
        'Ride request ID must be greater than zero.',
      );
    }
    return ApiService.post(
      '/rides/driver/requests/$requestId/accept/',
      {},
      authenticated: true,
    );
  }

  // Extract the actual ride ID from an API response.
  // Does not assume that the request ID is the ride ID.
  static int? extractRideId(Map<String, dynamic> response) {
    final candidates = <dynamic>[
      response['ride_id'],
      response['rideId'],
      response['accepted_ride_id'],
      response['assigned_ride_id'],
      response['ride'],
      response['data'] is Map
          ? (response['data'] as Map)['ride_id']
          : null,
      response['data'] is Map
          ? (response['data'] as Map)['rideId']
          : null,
      response['data'] is Map
          ? (response['data'] as Map)['ride']
          : null,
      response['result'] is Map
          ? (response['result'] as Map)['ride_id']
          : null,
      response['result'] is Map
          ? (response['result'] as Map)['ride']
          : null,
    ];

    for (final candidate in candidates) {
      final id = _parseRideId(candidate);
      if (id != null && id > 0) {
        return id;
      }
    }

    // Accept a top-level ID only when the response identifies
    // the object as a ride, rather than a ride request.
    final objectType = (
      response['type'] ??
      response['object_type'] ??
      response['resource']
    )?.toString().toLowerCase();

    if (objectType == 'ride' || objectType == 'rides') {
      final id = _parseRideId(response['id']);
      if (id != null && id > 0) {
        return id;
      }
    }

    return null;
  }

  static int? _parseRideId(dynamic value) {
    if (value is Map) {
      return _parseRideId(
        value['ride_id'] ??
        value['rideId'] ??
        value['id'],
      );
    }
    if (value is int) {
      return value > 0 ? value : null;
    }
    if (value is num) {
      final id = value.toInt();
      return id > 0 ? id : null;
    }
    if (value is String) {
      final id = int.tryParse(value.trim());
      return id != null && id > 0 ? id : null;
    }
    return null;
  }

  // Get details for an accepted ride using its actual ride ID.
  static Future<Map<String, dynamic>> getRideDetails(
    int rideId,
  ) async {
    if (rideId <= 0) {
      throw ArgumentError.value(
        rideId,
        'rideId',
        'Ride ID must be greater than zero.',
      );
    }
    return ApiService.get(
      '/rides/driver/rides/$rideId/',
      authenticated: true,
    );
  }

  // Update the accepted ride's status.
  static Future<Map<String, dynamic>> updateRideStatus({
    required int rideId,
    required String action,
    String? otp,
  }) async {
    if (rideId <= 0) {
      throw ArgumentError.value(
        rideId,
        'rideId',
        'Ride ID must be greater than zero.',
      );
    }

    final normalizedAction = action.trim();
    if (normalizedAction.isEmpty) {
      throw ArgumentError.value(
        action,
        'action',
        'Ride status action cannot be empty.',
      );
    }

    final Map<String, dynamic> data = {
      'action': normalizedAction,
    };

    if (otp != null && otp.trim().isNotEmpty) {
      data['otp'] = otp.trim();
    }

    return ApiService.post(
      '/rides/$rideId/status/',
      data,
      authenticated: true,
    );
  }

  // Update the driver's current location for an active ride.
  static Future<Map<String, dynamic>> updateRideLocation({
    required int rideId,
    required double latitude,
    required double longitude,
  }) async {
    if (rideId <= 0) {
      throw ArgumentError.value(
        rideId,
        'rideId',
        'Ride ID must be greater than zero.',
      );
    }
    if (latitude < -90 || latitude > 90) {
      throw ArgumentError.value(
        latitude,
        'latitude',
        'Latitude must be between -90 and 90.',
      );
    }
    if (longitude < -180 || longitude > 180) {
      throw ArgumentError.value(
        longitude,
        'longitude',
        'Longitude must be between -180 and 180.',
      );
    }

    return ApiService.post(
      '/rides/$rideId/tracking/update/',
      {
        'latitude': latitude,
        'longitude': longitude,
      },
      authenticated: true,
    );
  }
}
