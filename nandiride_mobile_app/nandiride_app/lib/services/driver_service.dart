
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
      '/drivers/online-status/',
      {'is_online': isOnline},
      authenticated: true,
    );
  }

  // Get pending ride requests available to this driver.
  static Future<Map<String, dynamic>> getPendingRideRequests() async {
    return ApiService.get(
      '/rides/driver-requests/',
      authenticated: true,
    );
  }

  // Accept a ride request.
  static Future<Map<String, dynamic>> acceptRide(
    int requestId,
  ) async {
    return ApiService.post(
      '/rides/driver-requests/$requestId/accept/',
      {},
      authenticated: true,
    );
  }
}