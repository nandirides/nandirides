import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'token_service.dart';
class ApiService {
  //static const String baseUrl = 'https://nandirides.onrender.com/api/v1';
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  // static const String baseUrl = 'http://10.233.65.201:8000/api/v1';
  static Future<Map<String, dynamic>> get(
    String endpoint, {
    bool authenticated = true,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);
    _logRequest('GET', uri, headers);
    final response = await http.get(uri, headers: headers);
    return _handleResponse(response, method: 'GET', uri: uri);
  }
  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> data, {
    bool authenticated = false,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);
    final body = jsonEncode(data);
    _logRequest('POST', uri, headers, body: body);
    final response = await http.post(
      uri,
      headers: headers,
      body: body,
    );
    return _handleResponse(response, method: 'POST', uri: uri);
  }
  static Future<Map<String, dynamic>> patch(
    String endpoint,
    Map<String, dynamic> data, {
    bool authenticated = true,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers(authenticated: authenticated);
    final body = jsonEncode(data);
    _logRequest('PATCH', uri, headers, body: body);
    final response = await http.patch(
      uri,
      headers: headers,
      body: body,
    );
    return _handleResponse(response, method: 'PATCH', uri: uri);
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
  static void _logRequest(
    String method,
    Uri uri,
    Map<String, String> headers, {
    String? body,
  }) {
    if (!kDebugMode) return;
    debugPrint('========== API REQUEST ==========');
    debugPrint('$method $uri');
    debugPrint('Content-Type: ${headers['Content-Type']}');
    debugPrint('Authenticated: ${headers.containsKey('Authorization')}');
    if (body != null) {
      debugPrint('Request body: $body');
    }
    debugPrint('=================================');
  }
  static Map<String, dynamic> _handleResponse(
    http.Response response, {
    required String method,
    required Uri uri,
  }) {
    dynamic decoded;
    try {
      decoded = jsonDecode(response.body);
    } catch (_) {
      decoded = response.body;
    }
    final Map<String, dynamic> responseData;
    if (decoded is Map<String, dynamic>) {
      responseData = decoded;
    } else if (decoded is Map) {
      responseData = Map<String, dynamic>.from(decoded);
    } else if (decoded is List) {
      responseData = {'data': decoded};
    } else {
      responseData = {
        'message': decoded.toString(),
      };
    }
    if (kDebugMode) {
      debugPrint('========== API RESPONSE ==========');
      debugPrint('$method $uri');
      debugPrint('Status code: ${response.statusCode}');
      debugPrint('Response body: ${response.body}');
      debugPrint('==================================');
    }
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return responseData;
    }
    final message = _extractErrorMessage(
      responseData,
      response.statusCode,
    );
    throw Exception(message);
  }
  static String _extractErrorMessage(
    Map<String, dynamic> data,
    int statusCode,
  ) {
    for (final key in ['detail', 'message', 'error']) {
      final value = data[key];
      if (value != null && value.toString().trim().isNotEmpty) {
        return 'HTTP $statusCode: ${value.toString()}';
      }
    }
    final errors = <String>[];
    data.forEach((key, value) {
      if (value == null) return;
      if (value is List) {
        errors.add('$key: ${value.map((item) => item.toString()).join(', ')}');
      } else if (value is Map) {
        errors.add('$key: ${_formatNestedError(value)}');
      } else {
        errors.add('$key: $value');
      }
    });
    if (errors.isNotEmpty) {
      return 'HTTP $statusCode: ${errors.join(' | ')}';
    }
    return 'Request failed: HTTP $statusCode';
  }
  static String _formatNestedError(Map<dynamic, dynamic> data) {
    return data.entries
        .map((entry) => '${entry.key}: ${entry.value}')
        .join(', ');
  }
}