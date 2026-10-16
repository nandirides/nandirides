
import 'package:flutter/foundation.dart';
import 'api_service.dart';

class DriverService {
  static Future<Map<String, dynamic>> getMyProfile() async {
    return ApiService.get(
      '/drivers/me/',
      authenticated: true,
    );
  }

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
      throw Exception('Driver registration failed: $registrationError');
    }
  }

  static Future<Map<String, dynamic>> updateOnlineStatus({
    required bool isOnline,
  }) async {
    return ApiService.post(
      '/drivers/online/status/',
      {'is_online': isOnline},
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> getPendingRideRequests() async {
    return ApiService.get(
      '/rides/driver/requests/',
      authenticated: true,
    );
  }

  static Future<Map<String, dynamic>> acceptRide(int requestId) async {
    if (requestId <= 0) {
      throw ArgumentError.value(
        requestId,
        'requestId',
        'Ride request ID must be greater than zero.',
      );
    }

    final response = await ApiService.post(
      '/rides/driver/requests/$requestId/accept/',
      {},
      authenticated: true,
    );

    debugPrint('ACCEPT RIDE API RESPONSE: $response');
    debugPrint('EXTRACTED RIDE ID: ${extractRideId(response)}');

    return response;
  }

  static int? extractRideId(Map<String, dynamic> response) {
    return _findRideId(response);
  }

  static int? _findRideId(dynamic value, {int depth = 0}) {
    if (depth > 8 || value is! Map) return null;

    final map = Map<String, dynamic>.from(value);

    // Check explicitly named ride ID fields first.
    for (final key in [
      'ride_id',
      'rideId',
      'accepted_ride_id',
      'assigned_ride_id',
      'trip_id',
      'tripId',
    ]) {
      final id = _parseRideId(map[key]);
      if (id != null) return id;
    }

    // A generic "id" is trusted only inside an explicit ride object.
    const rideObjectKeys = [
      'ride',
      'accepted_ride',
      'assigned_ride',
      'ride_details',
      'ride_detail',
      'trip',
      'assigned_trip',
    ];

    for (final key in rideObjectKeys) {
      final nested = map[key];

      if (nested is Map) {
        final nestedMap = Map<String, dynamic>.from(nested);

        final id = _parseRideId(
          nestedMap['ride_id'] ??
              nestedMap['rideId'] ??
              nestedMap['id'],
        );

        if (id != null) return id;

        final deeperId = _findRideId(
          nestedMap,
          depth: depth + 1,
        );

        if (deeperId != null) return deeperId;
      }
    }

    // Support wrapped API responses.
    for (final key in [
      'data',
      'result',
      'response',
      'payload',
    ]) {
      final nested = map[key];

      if (nested is Map) {
        final nestedId = _findRideId(
          nested,
          depth: depth + 1,
        );

        if (nestedId != null) return nestedId;
      }
    }

    final objectType = (map['type'] ??
            map['object_type'] ??
            map['resource'] ??
            '')
        .toString()
        .trim()
        .toLowerCase();

    if ([
      'ride',
      'rides',
      'accepted_ride',
      'trip',
    ].contains(objectType)) {
      return _parseRideId(map['id']);
    }

    return null;
  }

  static int? _parseRideId(dynamic value) {
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

  static Future<Map<String, dynamic>> getRideDetails(int rideId) async {
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
