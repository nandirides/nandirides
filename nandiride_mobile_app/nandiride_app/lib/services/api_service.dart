import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiService {
  // Android Emulator ke liye localhost ki jagah 10.0.2.2 use karein.
  // Chrome/Windows par local Django backend ke liye 127.0.0.1 use karein.
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';

  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> data,
  ) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode(data),
    );

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

    throw Exception(
      responseData['message'] ??
          responseData['detail'] ??
          'Request failed: HTTP ${response.statusCode}',
    );
  }
}
