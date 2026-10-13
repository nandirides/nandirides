import 'api_service.dart';

class AuthService {
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

  static Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    return ApiService.post('/auth/login/', {
      'username': username,
      'password': password,
    });
  }

  // Current logged-in user ka profile load karein.
  static Future<Map<String, dynamic>> getCurrentUser() async {
    return ApiService.get('/users/');
  }

  // Name, email aur phone Django mein save karein.
  static Future<Map<String, dynamic>> updateCurrentUser({
    required String firstName,
    required String lastName,
    required String email,
    required String phone,
  }) async {
    return ApiService.patch('/users/', {
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
    });
  }
}
