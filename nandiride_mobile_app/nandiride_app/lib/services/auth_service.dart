import 'api_service.dart';

class AuthService {
  /// Register a new customer.
  static Future<Map<String, dynamic>> register({
    required String firstName,
    required String lastName,
    required String username,
    required String email,
    required String phone,
    required String password,
    required String password2,
  }) async {
    return ApiService.post('/auth/register/', {
      'first_name': firstName,
      'last_name': lastName,
      'username': username,
      'email': email,
      'phone': phone,
      'password': password,
      'password2': password2,
    });
  }

  /// Login using username and password.
  static Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    return ApiService.post('/auth/login/', {
      'username': username,
      'password': password,
    });
  }
}
