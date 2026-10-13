import 'dart:convert';

import 'package:http/http.dart' as http;

import 'token_service.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  //static const String baseUrl = 'http://10.233.65.201:8000/api/v1';

  static Future<Map<String, dynamic>> get(
    String endpoint, {
    bool authenticated = true,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);

    final response = await http.get(uri, headers: headers);

    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> data, {
    bool authenticated = false,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);

    final response = await http.post(
      uri,
      headers: headers,
      body: jsonEncode(data),
    );

    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> patch(
    String endpoint,
    Map<String, dynamic> data, {
    bool authenticated = true,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);

    final response = await http.patch(
      uri,
      headers: headers,
      body: jsonEncode(data),
    );

    return _handleResponse(response);
  }

  static Future<Map<String, String>> _headers({
    required bool authenticated,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (authenticated) {
      final token = await TokenService.getToken();

      if (token == null || token.isEmpty) {
        throw Exception('Login expired. Please login again.');
      }

      headers['Authorization'] = 'Token $token';
    }

    return headers;
  }

  static Map<String, dynamic> _handleResponse(
    http.Response response,
  ) {
    Map<String, dynamic> responseData;

    try {
      final decoded = jsonDecode(response.body);

      responseData = decoded is Map<String, dynamic>
          ? decoded
          : {'data': decoded};
    } catch (_) {
      responseData = {'message': response.body};
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return responseData;
    }

    final message = responseData['detail'] ??
        responseData['message'] ??
        responseData['error'] ??
        'Request failed: HTTP ${response.statusCode}';

    throw Exception(message.toString());
  }
}
