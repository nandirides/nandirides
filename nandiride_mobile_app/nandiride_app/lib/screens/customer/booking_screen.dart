
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart' as geo;
import '../../services/booking_service.dart';
import '../../app/app_routes.dart';

class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key});
  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  static const navy = Color(0xFF101B3F);
  static const gold = Color(0xFFFFC928);
  static const background = Color(0xFFF5F7FC);
  static const muted = Color(0xFF68728A);
  static const green = Color(0xFF179B72);
  static const red = Color(0xFFE24B58);
  static const LatLng _defaultCenter = LatLng(29.9457, 78.1642);
  static const String _userAgent = 'NandiRide/1.0 (location search)';
  final _pickupController = TextEditingController();
  final _dropController = TextEditingController();
  final _couponController = TextEditingController();
  final _mapController = MapController();
  List<Map<String, dynamic>> _vehicles = [];
  List<Map<String, dynamic>> _pickupSuggestions = [];
  List<Map<String, dynamic>> _dropSuggestions = [];
  List<LatLng> _routePoints = [];
  int? _pickupId;
  int? _dropId;
  int? _vehicleId;
  LatLng? _pickupPoint;
  LatLng? _dropPoint;
  Map<String, dynamic>? _fare;
  double? _routeDistanceKm;
  double? _routeDurationMinutes;
  Timer? _pickupDebounce;
  Timer? _dropDebounce;
  Timer? _autoRouteDebounce;
  bool _loading = true;
  bool _savingPickup = false;
  bool _savingDrop = false;
  bool _estimating = false;
  bool _booking = false;
  bool _loadingRoute = false;
  bool _gettingCurrentLocation = false;
  bool _choosingPickupOnMap = true;
  bool _showPickupSuggestions = false;
  bool _showDropSuggestions = false;
  bool _couponApplied = false;
  String? _error;
  String? _couponMessage;
  String? _routeError;
  String _paymentMethod = 'cash';
  int _routeRequestToken = 0;
  int _addressResolveToken = 0;

  @override
  void initState() {
    super.initState();
    _pickupController.addListener(_onPickupChanged);
    _dropController.addListener(_onDropChanged);
    _loadData();
  }

  @override
  void dispose() {
    _pickupDebounce?.cancel();
    _dropDebounce?.cancel();
    _autoRouteDebounce?.cancel();
    _pickupController.removeListener(_onPickupChanged);
    _dropController.removeListener(_onDropChanged);
    _pickupController.dispose();
    _dropController.dispose();
    _couponController.dispose();
    _mapController.dispose();
    super.dispose();
  }

  int? _int(dynamic value) {
    if (value is int) return value;
    return int.tryParse(value?.toString() ?? '');
  }

  double? _number(dynamic value) {
    if (value is num) return value.toDouble();
    return double.tryParse(value?.toString() ?? '');
  }

  List<Map<String, dynamic>> _list(Map<String, dynamic> response) {
    dynamic data = response['results'] ?? response['data'] ?? [];
    if (data is Map) data = data['results'] ?? data['data'] ?? [];
    if (data is! List) return [];
    return data.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
  }

  String _cleanError(Object error) => error.toString().replaceFirst('Exception: ', '');

  void _message(String message, {bool error = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(
        content: Text(message),
        backgroundColor: error ? red : navy,
        behavior: SnackBarBehavior.floating,
      ));
  }

  void _invalidateFare() {
    _fare = null;
    _couponApplied = false;
    _couponMessage = null;
  }

  void _clearRoute() {
    _routeRequestToken++;
    _routePoints = [];
    _routeDistanceKm = null;
    _routeDurationMinutes = null;
    _loadingRoute = false;
    _routeError = null;
  }

  Future<void> _loadData() async {
    if (mounted) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }
    try {
      final response = await BookingService.getVehicleTypes();
      if (!mounted) return;
      final vehicles = _list(response);
      setState(() {
        _vehicles = vehicles;
        _loading = false;
        if (_vehicleId != null && !vehicles.any((v) => _int(v['id']) == _vehicleId)) {
          _vehicleId = null;
          _invalidateFare();
        }
        if (vehicles.isEmpty) _error = 'No active vehicle types found. Check the vehicle API.';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = _cleanError(e);
      });
    }
  }

  void _onPickupChanged() {
    _pickupDebounce?.cancel();
    _autoRouteDebounce?.cancel();
    final query = _pickupController.text.trim();
    setState(() {
      _pickupId = null;
      _pickupPoint = null;
      _clearRoute();
      _invalidateFare();
      _showPickupSuggestions = query.length >= 3;
      _pickupSuggestions = [];
    });
    if (query.length >= 3) {
      _pickupDebounce = Timer(const Duration(milliseconds: 900), () => _searchPlaces(query, pickup: true));
      _scheduleAutoRoute();
    }
  }

  void _onDropChanged() {
    _dropDebounce?.cancel();
    _autoRouteDebounce?.cancel();
    final query = _dropController.text.trim();
    setState(() {
      _dropId = null;
      _dropPoint = null;
      _clearRoute();
      _invalidateFare();
      _showDropSuggestions = query.length >= 3;
      _dropSuggestions = [];
    });
    if (query.length >= 3) {
      _dropDebounce = Timer(const Duration(milliseconds: 900), () => _searchPlaces(query, pickup: false));
      _scheduleAutoRoute();
    }
  }

  void _scheduleAutoRoute() {
    _autoRouteDebounce?.cancel();
    _autoRouteDebounce = Timer(const Duration(seconds: 3), () async {
      if (!mounted || _savingPickup || _savingDrop) return;
      if (_pickupController.text.trim().length < 3 || _dropController.text.trim().length < 3) return;
      try {
        await _ensureLocationSelected(pickup: true, refreshRoute: false);
        if (!mounted) return;
        await _ensureLocationSelected(pickup: false, refreshRoute: false);
        if (!mounted) return;
        await _refreshRoute();
      } catch (e) {
        if (!mounted) return;
        setState(() {
          _routeError = _cleanError(e);
          _loadingRoute = false;
        });
      }
    });
  }

  Future<List<Map<String, dynamic>>> _geocode(String query) async {
    final uri = Uri.https('nominatim.openstreetmap.org', '/search', {
      'q': query,
      'format': 'jsonv2',
      'addressdetails': '1',
      'limit': '5',
      'countrycodes': 'in',
    });
    final response = await http.get(uri, headers: {
      'User-Agent': _userAgent,
      'Accept-Language': 'en-IN,en;q=0.9',
    }).timeout(const Duration(seconds: 20));
    if (response.statusCode != 200) throw Exception('Address search failed (${response.statusCode}).');
    final decoded = jsonDecode(response.body);
    if (decoded is! List) return [];
    return decoded.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
  }

  Future<void> _searchPlaces(String query, {required bool pickup}) async {
    try {
      final suggestions = await _geocode(query);
      if (!mounted) return;
      final currentText = (pickup ? _pickupController : _dropController).text.trim();
      if (currentText != query) return;
      setState(() {
        if (pickup) {
          _pickupSuggestions = suggestions;
          _showPickupSuggestions = true;
        } else {
          _dropSuggestions = suggestions;
          _showDropSuggestions = true;
        }
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        if (pickup) {
          _pickupSuggestions = [];
        } else {
          _dropSuggestions = [];
        }
      });
    }
  }

  String _placeName(Map<String, dynamic> place) {
    final name = place['display_name']?.toString().trim() ?? '';
    return name.isEmpty ? 'Selected location' : name;
  }

  LatLng? _coordinates(Map<String, dynamic> place) {
    final lat = double.tryParse(place['lat']?.toString() ?? '');
    final lon = double.tryParse(place['lon']?.toString() ?? '');
    if (lat == null || lon == null || lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;
    return LatLng(lat, lon);
  }

  void _setAddressText({required bool pickup, required String text}) {
    final controller = pickup ? _pickupController : _dropController;
    final listener = pickup ? _onPickupChanged : _onDropChanged;
    controller.removeListener(listener);
    controller.value = TextEditingValue(text: text, selection: TextSelection.collapsed(offset: text.length));
    controller.addListener(listener);
  }

  Future<void> _selectSuggestion(Map<String, dynamic> place, {required bool pickup}) async {
    final point = _coordinates(place);
    if (point == null) {
      _message('Location coordinates were not found.', error: true);
      return;
    }
    FocusScope.of(context).unfocus();
    final address = _placeName(place);
    setState(() {
      _setAddressText(pickup: pickup, text: address);
      if (pickup) {
        _pickupPoint = point;
        _pickupId = null;
        _showPickupSuggestions = false;
        _savingPickup = true;
      } else {
        _dropPoint = point;
        _dropId = null;
        _showDropSuggestions = false;
        _savingDrop = true;
      }
      _clearRoute();
      _invalidateFare();
    });
    await _savePoint(address, point, pickup: pickup);
  }

  Future<int> _persistPoint(String address, LatLng point) async {
    final response = await BookingService.saveMapLocation(
      address: address,
      latitude: point.latitude,
      longitude: point.longitude,
    );
    final dynamic data = response['data'] ?? response['location'] ?? response;
    final dynamic idValue = data is Map ? (data['id'] ?? data['location_id']) : null;
    final id = _int(idValue);
    if (id == null) throw Exception('Location API returned no saved location ID. Check the Django location endpoint.');
    return id;
  }

  Future<void> _savePoint(String address, LatLng point, {required bool pickup}) async {
    try {
      final id = await _persistPoint(address, point);
      if (!mounted) return;
      setState(() {
        if (pickup) {
          _pickupId = id;
          _savingPickup = false;
        } else {
          _dropId = id;
          _savingDrop = false;
        }
      });
      try {
        _mapController.move(point, 14);
      } catch (_) {}
      await _refreshRoute();
      if (mounted) _message(pickup ? 'Pickup location saved.' : 'Drop location saved.');
    } catch (e) {
      if (!mounted) return;
      setState(() {
        if (pickup) {
          _pickupId = null;
          _savingPickup = false;
        } else {
          _dropId = null;
          _savingDrop = false;
        }
      });
      _message(_cleanError(e), error: true);
    }
  }

  Future<void> _getCurrentLocation() async {
    if (_gettingCurrentLocation || _savingPickup) return;
    setState(() => _gettingCurrentLocation = true);
    try {
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are off. Please enable GPS.');
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied) {
        throw Exception('Location permission denied.');
      }
      if (permission == LocationPermission.deniedForever) {
        throw Exception('Location permission permanently denied. Enable it in app settings.');
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, timeLimit: Duration(seconds: 20)),
      );
      final point = LatLng(position.latitude, position.longitude);
      var address = 'Current location (${position.latitude.toStringAsFixed(6)}, ${position.longitude.toStringAsFixed(6)})';
      try {
        final geo.Geocoding geocoding = geo.Geocoding();
        final List<geo.Placemark> placemarks = await geocoding.placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );
        if (placemarks.isNotEmpty) {
          final p = placemarks.first;
          final parts = [
            p.name,
            p.street,
            p.subLocality,
            p.locality,
            p.administrativeArea,
            p.postalCode,
          ].whereType<String>().map((s) => s.trim()).where((s) => s.isNotEmpty).toSet().toList();
          if (parts.isNotEmpty) address = parts.join(', ');
        }
      } catch (_) {}
      if (!mounted) return;
      _pickupDebounce?.cancel();
      _autoRouteDebounce?.cancel();
      setState(() {
        _setAddressText(pickup: true, text: address);
        _pickupPoint = point;
        _pickupId = null;
        _savingPickup = true;
        _showPickupSuggestions = false;
        _pickupSuggestions = [];
        _choosingPickupOnMap = true;
        _clearRoute();
        _invalidateFare();
      });
      _mapController.move(point, 15);
      await _savePoint(address, point, pickup: true);
    } catch (e) {
      if (mounted) _message(_cleanError(e), error: true);
    } finally {
      if (mounted) setState(() => _gettingCurrentLocation = false);
    }
  }

  Future<void> _selectMapPoint(LatLng point) async {
    FocusScope.of(context).unfocus();
    final pickup = _choosingPickupOnMap;
    final address = 'Map location (${point.latitude.toStringAsFixed(6)}, ${point.longitude.toStringAsFixed(6)})';
    setState(() {
      if (pickup) {
        _pickupPoint = point;
        _pickupId = null;
        _setAddressText(pickup: true, text: address);
        _savingPickup = true;
        _showPickupSuggestions = false;
      } else {
        _dropPoint = point;
        _dropId = null;
        _setAddressText(pickup: false, text: address);
        _savingDrop = true;
        _showDropSuggestions = false;
      }
      _clearRoute();
      _invalidateFare();
    });
    var resolvedAddress = address;
    try {
      final uri = Uri.https('nominatim.openstreetmap.org', '/reverse', {
        'lat': point.latitude.toString(),
        'lon': point.longitude.toString(),
        'format': 'jsonv2',
        'addressdetails': '1',
      });
      final response = await http.get(uri, headers: {
        'User-Agent': _userAgent,
        'Accept-Language': 'en-IN,en;q=0.9',
      }).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded['display_name'] != null) resolvedAddress = decoded['display_name'].toString();
      }
      if (!mounted) return;
      setState(() => _setAddressText(pickup: pickup, text: resolvedAddress));
      await _savePoint(resolvedAddress, point, pickup: pickup);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        if (pickup) {
          _savingPickup = false;
        } else {
          _savingDrop = false;
        }
      });
      _message('Could not save map location. ${_cleanError(e)}', error: true);
    }
  }

  Future<void> _ensureLocationSelected({required bool pickup, bool refreshRoute = true}) async {
    final controller = pickup ? _pickupController : _dropController;
    final existingId = pickup ? _pickupId : _dropId;
    final existingPoint = pickup ? _pickupPoint : _dropPoint;
    if (existingId != null && existingPoint != null) return;
    final query = controller.text.trim();
    if (query.length < 3) throw Exception('Enter a complete ${pickup ? 'pickup' : 'drop'} address.');
    final token = ++_addressResolveToken;
    final suggestions = await _geocode(query);
    if (!mounted) throw Exception('Screen closed.');
    if (controller.text.trim() != query) throw Exception('Address changed while searching. Please try again.');
    if (suggestions.isEmpty) throw Exception('Address not found: "$query". Enter a more specific address.');
    Map<String, dynamic>? match;
    for (final place in suggestions) {
      if (_coordinates(place) != null) {
        match = place;
        break;
      }
    }
    if (match == null) throw Exception('Could not find coordinates for "$query".');
    final point = _coordinates(match)!;
    final address = _placeName(match);
    setState(() {
      if (pickup) {
        _pickupPoint = point;
        _pickupId = null;
        _savingPickup = true;
        _setAddressText(pickup: true, text: address);
      } else {
        _dropPoint = point;
        _dropId = null;
        _savingDrop = true;
        _setAddressText(pickup: false, text: address);
      }
      _clearRoute();
    });
    try {
      final id = await _persistPoint(address, point);
      if (!mounted || token != _addressResolveToken) return;
      setState(() {
        if (pickup) {
          _pickupId = id;
          _savingPickup = false;
        } else {
          _dropId = id;
          _savingDrop = false;
        }
      });
      if (refreshRoute && _pickupPoint != null && _dropPoint != null) await _refreshRoute();
    } catch (e) {
      if (mounted) {
        setState(() {
          if (pickup) {
            _savingPickup = false;
            _pickupId = null;
          } else {
            _savingDrop = false;
            _dropId = null;
          }
        });
      }
      rethrow;
    }
  }

  Future<void> _refreshRoute() async {
    final pickup = _pickupPoint;
    final drop = _dropPoint;
    final token = ++_routeRequestToken;
    if (pickup == null || drop == null) {
      if (!mounted) return;
      setState(() {
        _routePoints = [];
        _routeDistanceKm = null;
        _routeDurationMinutes = null;
        _loadingRoute = false;
        _routeError = null;
      });
      return;
    }
    if ((pickup.latitude - drop.latitude).abs() < 0.000001 && (pickup.longitude - drop.longitude).abs() < 0.000001) {
      if (!mounted) return;
      setState(() {
        _routePoints = [];
        _routeDistanceKm = null;
        _routeDurationMinutes = null;
        _loadingRoute = false;
        _routeError = 'Pickup and drop must be different.';
      });
      return;
    }
    if (!mounted) return;
    setState(() {
      _loadingRoute = true;
      _routeError = null;
    });
    try {
      final uri = Uri.https('router.project-osrm.org', '/route/v1/driving/${pickup.longitude},${pickup.latitude};${drop.longitude},${drop.latitude}', {
        'overview': 'full',
        'geometries': 'geojson',
        'steps': 'false',
      });
      final response = await http.get(uri).timeout(const Duration(seconds: 25));
      if (response.statusCode != 200) throw Exception('Route service returned ${response.statusCode}.');
      final decoded = jsonDecode(response.body);
      if (decoded is! Map || decoded['code'] != 'Ok') throw Exception('No driving route found between these locations.');
      final routes = decoded['routes'];
      if (routes is! List || routes.isEmpty || routes.first is! Map) throw Exception('No driving route is available.');
      final route = Map<String, dynamic>.from(routes.first as Map);
      final geometry = route['geometry'];
      final coordinates = geometry is Map ? geometry['coordinates'] : null;
      if (coordinates is! List || coordinates.length < 2) throw Exception('Route geometry is unavailable.');
      final points = <LatLng>[];
      for (final coordinate in coordinates) {
        if (coordinate is List && coordinate.length >= 2) {
          final lon = double.tryParse(coordinate[0].toString());
          final lat = double.tryParse(coordinate[1].toString());
          if (lat != null && lon != null && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) points.add(LatLng(lat, lon));
        }
      }
      if (points.length < 2) throw Exception('Route geometry contains insufficient coordinates.');
      if (!mounted || token != _routeRequestToken) return;
      setState(() {
        _routePoints = points;
        _routeDistanceKm = (_number(route['distance']) ?? 0) / 1000;
        _routeDurationMinutes = (_number(route['duration']) ?? 0) / 60;
        _loadingRoute = false;
        _routeError = null;
      });
      try {
        _mapController.fitCamera(CameraFit.bounds(bounds: LatLngBounds.fromPoints(points), padding: const EdgeInsets.all(42)));
      } catch (_) {
        try {
          _mapController.move(pickup, 13);
        } catch (_) {}
      }
    } catch (e) {
      if (!mounted || token != _routeRequestToken) return;
      setState(() {
        _routePoints = [];
        _routeDistanceKm = null;
        _routeDurationMinutes = null;
        _loadingRoute = false;
        _routeError = _cleanError(e);
      });
    }
  }

  Map<String, dynamic> _unwrapResponse(Map<String, dynamic> response) {
    dynamic value = response;
    for (var i = 0; i < 3; i++) {
      if (value is Map && value['data'] is Map) {
        value = value['data'];
      } else if (value is Map && value['result'] is Map) {
        value = value['result'];
      } else {
        break;
      }
    }
    return value is Map ? Map<String, dynamic>.from(value) : <String, dynamic>{};
  }

  dynamic _firstValue(Map<String, dynamic> data, List<String> keys) {
    for (final key in keys) {
      final value = data[key];
      if (value != null && _number(value) != null) return value;
    }
    return null;
  }

  dynamic _extractFare(Map<String, dynamic> response) {
    final data = _unwrapResponse(response);
    return _firstValue(data, [
      'final_fare', 'final_amount', 'payable_amount', 'total_fare', 'total_amount',
      'grand_total', 'total_payable', 'estimated_fare', 'estimated_amount',
      'fare', 'amount', 'price', 'subtotal',
    ]);
  }

  double? _fareValue(List<String> keys) => _fare == null ? null : _number(_firstValue(_fare!, keys));

  double? get _estimatedFare {
    final explicit = _fareValue([
      'estimated_fare', 'estimate_fare', 'estimated_amount', 'original_fare',
      'original_amount', 'base_fare', 'fare_before_discount', 'subtotal', 'fare', 'price',
    ]);
    if (explicit != null) return explicit;
    final finalFare = _finalFare;
    final discount = _discountAmount;
    if (finalFare != null && discount != null) return finalFare + discount;
    return finalFare;
  }

  double? get _discountAmount => _fareValue([
    'discount_amount', 'coupon_discount', 'discount', 'coupon_savings', 'discount_value',
  ]);

  double? get _couponAppliedFare {
    final explicit = _fareValue([
      'coupon_applied_fare', 'discounted_fare', 'fare_after_discount',
      'fare_after_coupon', 'subtotal_after_discount', 'amount_after_discount',
    ]);
    if (explicit != null) return explicit;
    final estimated = _estimatedFare;
    final discount = _discountAmount;
    if (estimated != null && discount != null) return (estimated - discount).clamp(0.0, double.infinity).toDouble();
    return _finalFare;
  }

  double? get _finalFare => _fareValue([
    'final_fare', 'final_amount', 'payable_amount', 'amount_after_discount',
    'total_fare', 'total_amount', 'grand_total', 'total_payable', 'fare',
    'amount', 'price', 'estimated_fare', 'estimated_amount', 'subtotal',
  ]);

  double? get _totalFare => _fareValue([
    'total_fare', 'total_amount', 'grand_total', 'total_payable', 'payable_amount',
    'final_fare', 'final_amount', 'amount', 'fare', 'estimated_fare', 'estimated_amount', 'subtotal',
  ]) ?? _finalFare;

  dynamic _fareTotal() => _fare == null ? null : _finalFare;

  String _money(dynamic value) {
    final amount = _number(value);
    return amount == null ? '—' : '₹${amount.toStringAsFixed(2)}';
  }

  Future<void> _estimateFare() async {
    FocusScope.of(context).unfocus();
    if (_estimating || _booking) return;
    if (_vehicleId == null) {
      _message('Please select a vehicle.', error: true);
      return;
    }
    if (_savingPickup || _savingDrop) {
      _message('Please wait while locations are being saved.', error: true);
      return;
    }
    _autoRouteDebounce?.cancel();
    setState(() {
      _estimating = true;
      _fare = null;
      _couponApplied = false;
      _couponMessage = null;
      _error = null;
    });
    try {
      await _ensureLocationSelected(pickup: true, refreshRoute: false);
      await _ensureLocationSelected(pickup: false, refreshRoute: false);
      if (!mounted) return;
      if (_pickupId == null || _dropId == null) throw Exception('Pickup and drop location IDs are missing. Please retry.');
      if (_pickupId == _dropId) throw Exception('Pickup and drop must be different locations.');
      final pickup = _pickupPoint;
      final drop = _dropPoint;
      if (pickup == null || drop == null) throw Exception('Pickup/drop coordinates are missing. Enter both addresses again.');
      if ((pickup.latitude - drop.latitude).abs() < 0.000001 && (pickup.longitude - drop.longitude).abs() < 0.000001) {
        throw Exception('Pickup and drop coordinates must be different.');
      }
      unawaited(_refreshRoute());
      final couponCode = _couponController.text.trim().toUpperCase();
      final result = await BookingService.estimateFare(
        pickupLocationId: _pickupId!,
        dropLocationId: _dropId!,
        vehicleTypeId: _vehicleId!,
        couponCode: couponCode,
      );
      if (!mounted) return;
      final data = _unwrapResponse(result);
      final fareValue = _extractFare(result);
      final apiMessage = data['detail'] ?? data['message'] ?? data['error'] ?? result['detail'] ?? result['message'] ?? result['error'];
      final couponError = data['coupon_error'] ?? result['coupon_error'];
      if (_number(fareValue) == null) {
        throw Exception(apiMessage?.toString() ?? 'Fare API returned no valid fare. Check the Django response.');
      }
      final normalized = Map<String, dynamic>.from(data);
      normalized.addAll({
        'final_fare': data['final_fare'] ?? data['final_amount'] ?? data['payable_amount'] ?? fareValue,
      });
      if (couponError != null) normalized['coupon_error'] = couponError;
      final responseCouponMessage = data['coupon_message'] ?? data['message'] ?? result['coupon_message'];
      if (responseCouponMessage != null) normalized['coupon_message'] = responseCouponMessage;
      setState(() {
        _fare = normalized;
        _couponApplied = couponCode.isNotEmpty && couponError == null &&
            _number(_firstValue(normalized, ['discount_amount', 'coupon_discount', 'discount', 'coupon_savings', 'discount_value'])) != null;
        _couponMessage = couponCode.isEmpty ? null : couponError?.toString() ??
            responseCouponMessage?.toString() ??
            (_couponApplied ? 'Coupon $couponCode applied successfully.' : 'Fare calculated. Coupon was not confirmed by the API.');
      });
      _message(_couponApplied ? 'Coupon applied and fare calculated successfully.' : 'Fare calculated successfully.');
    } catch (e) {
      if (mounted) _message(_cleanError(e), error: true);
    } finally {
      if (mounted) setState(() => _estimating = false);
    }
  }

  Future<void> _bookRide() async {
    if (_booking || _estimating) return;
    if (_vehicleId == null) {
      _message('Select a vehicle first.', error: true);
      return;
    }
    if (_fare == null || _number(_fareTotal()) == null) {
      _message('Please calculate a valid fare first.', error: true);
      return;
    }
    if (_savingPickup || _savingDrop) {
      _message('Please wait while locations are being saved.', error: true);
      return;
    }
    final confirmed = await _confirmBooking();
    if (confirmed != true || !mounted) return;
    setState(() => _booking = true);
    try {
      await _ensureLocationSelected(pickup: true, refreshRoute: false);
      await _ensureLocationSelected(pickup: false, refreshRoute: false);
      if (!mounted) return;
      if (_pickupId == null || _dropId == null || _pickupId == _dropId) throw Exception('Please check your pickup and drop locations.');
      if (_pickupPoint == null || _dropPoint == null) throw Exception('Pickup and drop coordinates are required.');
      final samePoint = (_pickupPoint!.latitude - _dropPoint!.latitude).abs() < 0.000001 &&
          (_pickupPoint!.longitude - _dropPoint!.longitude).abs() < 0.000001;
      if (samePoint) throw Exception('Pickup and drop must be different.');
      final result = await BookingService.createRideRequest(
        pickupLocationId: _pickupId!,
        dropLocationId: _dropId!,
        vehicleTypeId: _vehicleId!,
        couponId: _int(_fare?['coupon_id'] ?? _fare?['coupon']),
      );
      if (!mounted) return;
      final data = _unwrapResponse(result);
      final rawId = result['id'] ?? result['request_id'] ?? result['ride_request_id'] ??
          data['id'] ?? data['request_id'] ?? data['ride_request_id'];
      final requestId = _int(rawId);
      if (requestId == null) throw Exception('Booking response did not contain a request ID.');
      _message('Ride request created successfully. Payment selected: ${_paymentMethod.toUpperCase()}.');
      Navigator.pushReplacementNamed(context, AppRoutes.tracking, arguments: {'requestId': requestId});
    } catch (e) {
      if (mounted) _message(_cleanError(e), error: true);
    } finally {
      if (mounted) setState(() => _booking = false);
    }
  }

  Future<bool?> _confirmBooking() {
    String selected = _paymentMethod;
    String otherMethod = 'netbanking';
    String bank = 'SBI';
    final cardName = TextEditingController();
    final cardNumber = TextEditingController();
    final expiry = TextEditingController();
    final cvv = TextEditingController();
    final banks = ['SBI', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Punjab National Bank', 'Bank of Baroda', 'Kotak Mahindra Bank', 'Canara Bank'];
    return showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Confirm your ride', style: TextStyle(color: navy, fontWeight: FontWeight.w900)),
          content: SingleChildScrollView(
            child: SizedBox(
              width: 420,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Final fare: ${_money(_finalFare)}', style: const TextStyle(color: navy, fontWeight: FontWeight.w800, fontSize: 18)),
                  if (_couponApplied && _discountAmount != null) ...[
                    const SizedBox(height: 5),
                    Text('Coupon savings: ${_money(_discountAmount)}', style: const TextStyle(color: green, fontSize: 12)),
                  ],
                  const SizedBox(height: 12),
                  RadioGroup<String>(
                    groupValue: selected,
                    onChanged: (value) {
                      if (value != null) setDialogState(() => selected = value);
                    },
                    child: const Column(
                      children: [
                        RadioListTile<String>(value: 'cash', title: Text('Cash'), secondary: Icon(Icons.payments_outlined), activeColor: navy, contentPadding: EdgeInsets.zero),
                        RadioListTile<String>(value: 'upi', title: Text('UPI / Scan QR'), secondary: Icon(Icons.qr_code_2_rounded), activeColor: navy, contentPadding: EdgeInsets.zero),
                        RadioListTile<String>(value: 'card', title: Text('Credit / Debit Card'), secondary: Icon(Icons.credit_card_rounded), activeColor: navy, contentPadding: EdgeInsets.zero),
                        RadioListTile<String>(value: 'other', title: Text('Other payment options'), secondary: Icon(Icons.account_balance_rounded), activeColor: navy, contentPadding: EdgeInsets.zero),
                      ],
                    ),
                  ),
                  if (selected == 'upi') ...[
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFE4E9F2))),
                      child: Column(
                        children: [
                          const Icon(Icons.qr_code_2_rounded, size: 100, color: navy),
                          const Text('NandiRide UPI Demo', style: TextStyle(fontWeight: FontWeight.w900, color: navy)),
                          const SizedBox(height: 5),
                          const Text('Demo only — this is not a scannable payment QR.', textAlign: TextAlign.center, style: TextStyle(color: red, fontSize: 11)),
                          const SizedBox(height: 5),
                          Text('Amount: ${_money(_finalFare)}', style: const TextStyle(fontWeight: FontWeight.w800, color: navy)),
                        ],
                      ),
                    ),
                  ],
                  if (selected == 'card') ...[
                    const SizedBox(height: 8),
                    const Text('Card payment demo', style: TextStyle(color: navy, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 5),
                    const Text('Use a payment gateway for real card transactions. Do not collect or store CVV in your app backend.', style: TextStyle(color: muted, fontSize: 11)),
                  ],
                  if (selected == 'other') ...[
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      value: otherMethod,
                      decoration: InputDecoration(labelText: 'Payment type', filled: true, fillColor: background, border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                      items: const [
                        DropdownMenuItem(value: 'netbanking', child: Text('Net Banking')),
                        DropdownMenuItem(value: 'card', child: Text('Card details')),
                      ],
                      onChanged: (value) => setDialogState(() => otherMethod = value ?? 'netbanking'),
                    ),
                    if (otherMethod == 'netbanking') ...[
                      const SizedBox(height: 10),
                      DropdownButtonFormField<String>(
                        value: bank,
                        isExpanded: true,
                        decoration: InputDecoration(labelText: 'Select bank', filled: true, fillColor: background, border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                        items: banks.map((b) => DropdownMenuItem(value: b, child: Text(b))).toList(),
                        onChanged: (value) => setDialogState(() => bank = value ?? banks.first),
                      ),
                      const SizedBox(height: 8),
                      const Text('Demo selection only. Bank authentication is not connected.', style: TextStyle(color: muted, fontSize: 11)),
                    ],
                    if (otherMethod == 'card') ...[
                      const SizedBox(height: 10),
                      TextField(controller: cardName, textCapitalization: TextCapitalization.words, decoration: const InputDecoration(labelText: 'Name on card', border: OutlineInputBorder())),
                      const SizedBox(height: 9),
                      TextField(controller: cardNumber, keyboardType: TextInputType.number, maxLength: 19, decoration: const InputDecoration(labelText: 'Card number (demo)', counterText: '', border: OutlineInputBorder())),
                      const SizedBox(height: 9),
                      Row(
                        children: [
                          Expanded(child: TextField(controller: expiry, keyboardType: TextInputType.datetime, decoration: const InputDecoration(labelText: 'MM/YY', border: OutlineInputBorder()))),
                          const SizedBox(width: 9),
                          Expanded(child: TextField(controller: cvv, keyboardType: TextInputType.number, obscureText: true, maxLength: 4, decoration: const InputDecoration(labelText: 'CVV (demo)', counterText: '', border: OutlineInputBorder()))),
                        ],
                      ),
                      const SizedBox(height: 6),
                      const Text('Demo fields only. Never send or save card number/CVV to your Django API.', style: TextStyle(color: red, fontSize: 11)),
                    ],
                  ],
                  const SizedBox(height: 10),
                  const Text('Payment is not charged or verified by this demo popup.', style: TextStyle(color: muted, fontSize: 11)),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: navy, foregroundColor: Colors.white),
              onPressed: () {
                if (selected == 'other' && otherMethod == 'card') {
                  final digits = cardNumber.text.replaceAll(RegExp(r'\D'), '');
                  if (cardName.text.trim().isEmpty || digits.length < 12 || expiry.text.trim().isEmpty || cvv.text.trim().length < 3) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter demo card fields to continue.'), backgroundColor: red));
                    return;
                  }
                }
                _paymentMethod = selected == 'other' ? otherMethod : selected;
                Navigator.pop(dialogContext, true);
              },
              child: const Text('Confirm ride'),
            ),
          ],
        ),
      ),
    ).whenComplete(() {
      cardName.dispose();
      cardNumber.dispose();
      expiry.dispose();
      cvv.dispose();
    });
  }

  Future<void> _swapLocations() async {
    if (_savingPickup || _savingDrop) return;
    final pickupText = _pickupController.text.trim();
    final dropText = _dropController.text.trim();
    if (pickupText.isEmpty || dropText.isEmpty) {
      _message('Enter both pickup and drop addresses first.', error: true);
      return;
    }
    _pickupDebounce?.cancel();
    _dropDebounce?.cancel();
    _autoRouteDebounce?.cancel();
    final oldPickupPoint = _pickupPoint;
    final oldDropPoint = _dropPoint;
    final oldPickupId = _pickupId;
    final oldDropId = _dropId;
    setState(() {
      _setAddressText(pickup: true, text: dropText);
      _setAddressText(pickup: false, text: pickupText);
      _pickupPoint = oldDropPoint;
      _dropPoint = oldPickupPoint;
      _pickupId = oldDropId;
      _dropId = oldPickupId;
      _pickupSuggestions = [];
      _dropSuggestions = [];
      _showPickupSuggestions = false;
      _showDropSuggestions = false;
      _clearRoute();
      _invalidateFare();
    });
    try {
      await _ensureLocationSelected(pickup: true, refreshRoute: false);
      await _ensureLocationSelected(pickup: false, refreshRoute: false);
      if (mounted) await _refreshRoute();
    } catch (e) {
      if (mounted) _message(_cleanError(e), error: true);
    }
  }

  Widget _suggestions({required List<Map<String, dynamic>> places, required bool pickup}) {
    if (places.isEmpty) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(top: 5),
      constraints: const BoxConstraints(maxHeight: 210),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFE1E6F0)), boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.08), blurRadius: 12)]),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        clipBehavior: Clip.antiAlias,
        child: ListView.separated(
          shrinkWrap: true,
          padding: EdgeInsets.zero,
          itemCount: places.length,
          separatorBuilder: (_, __) => const Divider(height: 1, color: Color(0xFFE9EDF4)),
          itemBuilder: (context, index) {
            final place = places[index];
            return ListTile(
              dense: true,
              leading: Icon(pickup ? Icons.trip_origin_rounded : Icons.location_on_rounded, color: pickup ? green : red),
              title: Text(_placeName(place), maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(color: navy, fontSize: 12, fontWeight: FontWeight.w600)),
              onTap: () => _selectSuggestion(place, pickup: pickup),
            );
          },
        ),
      ),
    );
  }

  Widget _addressField({required bool pickup}) {
    final controller = pickup ? _pickupController : _dropController;
    final suggestions = pickup ? _pickupSuggestions : _dropSuggestions;
    final showSuggestions = pickup ? _showPickupSuggestions : _showDropSuggestions;
    final saving = pickup ? _savingPickup : _savingDrop;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: controller,
          textCapitalization: TextCapitalization.words,
          maxLines: 2,
          textInputAction: TextInputAction.search,
          onSubmitted: (_) async {
            try {
              await _ensureLocationSelected(pickup: pickup, refreshRoute: false);
              if (!mounted) return;
              final otherText = (pickup ? _dropController : _pickupController).text.trim();
              if (otherText.length >= 3) await _ensureLocationSelected(pickup: !pickup, refreshRoute: false);
              if (mounted) await _refreshRoute();
            } catch (e) {
              if (mounted) _message(_cleanError(e), error: true);
            }
          },
          decoration: InputDecoration(
            labelText: pickup ? 'Pickup location' : 'Drop location',
            hintText: pickup ? 'Type pickup address' : 'Type your destination',
            prefixIcon: Icon(pickup ? Icons.trip_origin_rounded : Icons.location_on_rounded, color: pickup ? green : red),
            suffixIcon: saving
                ? const Padding(padding: EdgeInsets.all(14), child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)))
                : IconButton(
                    tooltip: 'Choose on map',
                    icon: const Icon(Icons.map_outlined, color: navy),
                    onPressed: () {
                      FocusScope.of(context).unfocus();
                      setState(() => _choosingPickupOnMap = pickup);
                      _mapController.move(pickup ? (_pickupPoint ?? _defaultCenter) : (_dropPoint ?? _defaultCenter), 14);
                    },
                  ),
            filled: true,
            fillColor: background,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
          ),
        ),
        if (showSuggestions) _suggestions(places: suggestions, pickup: pickup),
        const SizedBox(height: 5),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            if (pickup)
              TextButton.icon(
                onPressed: _gettingCurrentLocation ? null : _getCurrentLocation,
                icon: _gettingCurrentLocation
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.my_location_rounded, size: 17),
                label: Text(_gettingCurrentLocation ? 'Getting location...' : 'Current Location'),
                style: TextButton.styleFrom(foregroundColor: green),
              ),
            TextButton.icon(
              onPressed: () {
                FocusScope.of(context).unfocus();
                setState(() => _choosingPickupOnMap = pickup);
                _mapController.move(pickup ? (_pickupPoint ?? _defaultCenter) : (_dropPoint ?? _defaultCenter), 14);
              },
              icon: const Icon(Icons.map_rounded, size: 17),
              label: const Text('Select on map'),
              style: TextButton.styleFrom(foregroundColor: navy),
            ),
          ],
        ),
      ],
    );
  }

  Widget _mapCard() {
    final center = _pickupPoint ?? _dropPoint ?? _defaultCenter;
    final markers = <Marker>[
      if (_pickupPoint != null) Marker(point: _pickupPoint!, width: 42, height: 42, child: const Icon(Icons.location_pin, color: green, size: 42)),
      if (_dropPoint != null) Marker(point: _dropPoint!, width: 42, height: 42, child: const Icon(Icons.location_pin, color: red, size: 42)),
    ];
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: _cardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Choose location on map', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900)),
          const SizedBox(height: 7),
          const Text('Select Pickup or Drop, then tap the map.', style: TextStyle(color: muted, fontSize: 12)),
          const SizedBox(height: 12),
          SegmentedButton<bool>(
            segments: const [
              ButtonSegment(value: true, label: Text('Pickup'), icon: Icon(Icons.trip_origin_rounded)),
              ButtonSegment(value: false, label: Text('Drop'), icon: Icon(Icons.location_on_rounded)),
            ],
            selected: {_choosingPickupOnMap},
            onSelectionChanged: (selection) => setState(() => _choosingPickupOnMap = selection.first),
            style: SegmentedButton.styleFrom(foregroundColor: navy, selectedForegroundColor: navy, selectedBackgroundColor: Color(0xFFFFF0B8)),
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(15),
            child: SizedBox(
              height: 285,
              child: FlutterMap(
                mapController: _mapController,
                options: MapOptions(initialCenter: center, initialZoom: 12, onTap: (_, point) => _selectMapPoint(point)),
                children: [
                  TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', userAgentPackageName: 'com.nandiride.app'),
                  if (_routePoints.length >= 2)
                    PolylineLayer(polylines: [
                      Polyline(points: _routePoints, strokeWidth: 6, color: navy),
                      Polyline(points: _routePoints, strokeWidth: 3, color: gold),
                    ]),
                  MarkerLayer(markers: markers),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          const Text('Map data © OpenStreetMap contributors', style: TextStyle(color: muted, fontSize: 10)),
          if (_loadingRoute) ...[
            const SizedBox(height: 8),
            const LinearProgressIndicator(color: gold, backgroundColor: background),
            const SizedBox(height: 5),
            const Text('Finding driving route...', style: TextStyle(color: muted, fontSize: 11)),
          ],
          if (_routePoints.length >= 2)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.route_rounded, color: green, size: 19),
                  const SizedBox(width: 7),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Driving route ready', style: TextStyle(color: green, fontSize: 12, fontWeight: FontWeight.w800)),
                        if (_routeDistanceKm != null && _routeDurationMinutes != null)
                          Text('${_routeDistanceKm!.toStringAsFixed(2)} km · ${_routeDurationMinutes!.round()} min estimated driving time', style: const TextStyle(color: muted, fontSize: 12)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          if (_routeError != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(_routeError!, style: const TextStyle(color: red, fontSize: 11))),
          if (_pickupPoint != null) Text('Pickup: ${_pickupPoint!.latitude.toStringAsFixed(5)}, ${_pickupPoint!.longitude.toStringAsFixed(5)}', style: const TextStyle(color: green, fontSize: 11)),
          if (_dropPoint != null) Text('Drop: ${_dropPoint!.latitude.toStringAsFixed(5)}, ${_dropPoint!.longitude.toStringAsFixed(5)}', style: const TextStyle(color: red, fontSize: 11)),
        ],
      ),
    );
  }

  IconData _vehicleIcon(Map<String, dynamic> vehicle) {
    final name = '${vehicle['name'] ?? ''} ${vehicle['code'] ?? ''}'.toLowerCase();
    if (name.contains('bike') || name.contains('scooter')) return Icons.two_wheeler_rounded;
    if (name.contains('auto') || name.contains('rickshaw')) return Icons.electric_rickshaw_rounded;
    if (name.contains('cab') || name.contains('car')) return Icons.local_taxi_rounded;
    return Icons.directions_car_rounded;
  }

  Widget _vehicleSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Choose your ride', style: TextStyle(color: navy, fontSize: 18, fontWeight: FontWeight.w900)),
        const SizedBox(height: 12),
        LayoutBuilder(
          builder: (context, constraints) {
            final width = (constraints.maxWidth - 20) / 3;
            return Wrap(
              spacing: 10,
              runSpacing: 10,
              children: _vehicles.map((vehicle) {
                final id = _int(vehicle['id']);
                if (id == null) return const SizedBox.shrink();
                final selected = id == _vehicleId;
                return SizedBox(
                  width: width,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(17),
                    onTap: () => setState(() {
                      _vehicleId = id;
                      _invalidateFare();
                    }),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 15),
                      decoration: BoxDecoration(
                        color: selected ? navy : Colors.white,
                        borderRadius: BorderRadius.circular(17),
                        border: Border.all(color: selected ? gold : const Color(0xFFE4E9F2), width: selected ? 2 : 1),
                      ),
                      child: Column(
                        children: [
                          Icon(_vehicleIcon(vehicle), color: selected ? gold : navy, size: 30),
                          const SizedBox(height: 8),
                          Text(vehicle['name']?.toString() ?? 'Vehicle', textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: selected ? Colors.white : navy, fontSize: 12, fontWeight: FontWeight.w800)),
                          const SizedBox(height: 7),
                          Text(_money(vehicle['base_fare']), style: TextStyle(color: selected ? gold : navy, fontWeight: FontWeight.w900)),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }

  Widget _cardDecorationWrapper(Widget child) => Container(padding: const EdgeInsets.all(16), decoration: _cardDecoration(), child: child);

  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: const Color(0xFFE7EBF3)),
      boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.04), blurRadius: 16, offset: const Offset(0, 5))],
    );
  }

  Widget _fareRow(String label, dynamic amount, {IconData? icon, Color valueColor = navy, bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 17, color: muted),
            const SizedBox(width: 8),
          ],
          Expanded(child: Text(label, style: TextStyle(color: muted, fontSize: 13, fontWeight: bold ? FontWeight.w800 : FontWeight.w600))),
          const SizedBox(width: 10),
          Text(_money(amount), textAlign: TextAlign.end, style: TextStyle(color: valueColor, fontSize: bold ? 17 : 13, fontWeight: bold ? FontWeight.w900 : FontWeight.w700)),
        ],
      ),
    );
  }

  Widget _fareCard() {
    final hasFare = _fare != null;
    final discount = _discountAmount ?? 0;
    final estimated = _estimatedFare;
    final appliedFare = _couponAppliedFare;
    final finalFare = _finalFare;
    final totalFare = _totalFare;
    final couponCode = _couponController.text.trim().toUpperCase();
    return _cardDecorationWrapper(
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.receipt_long_rounded, color: navy, size: 22),
              SizedBox(width: 9),
              Expanded(child: Text('Fare estimate & breakdown', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900))),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _couponController,
            textCapitalization: TextCapitalization.characters,
            decoration: InputDecoration(
              hintText: 'Coupon code (optional)',
              prefixIcon: const Icon(Icons.local_offer_outlined),
              suffixIcon: IconButton(
                tooltip: 'Clear coupon',
                onPressed: () {
                  _couponController.clear();
                  setState(() {
                    _couponApplied = false;
                    _couponMessage = null;
                    _fare = null;
                  });
                },
                icon: const Icon(Icons.close_rounded),
              ),
              filled: true,
              fillColor: background,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
            onChanged: (_) => setState(() {
              _couponApplied = false;
              _couponMessage = null;
              _fare = null;
            }),
          ),
          if (_couponMessage != null) ...[
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: (_couponApplied ? green : red).withValues(alpha: 0.08), borderRadius: BorderRadius.circular(10)),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(_couponApplied ? Icons.check_circle_rounded : Icons.info_outline_rounded, color: _couponApplied ? green : red, size: 17),
                  const SizedBox(width: 7),
                  Expanded(child: Text(_couponMessage!, style: TextStyle(color: _couponApplied ? green : red, fontSize: 12, fontWeight: FontWeight.w700))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _estimating || _booking || _savingPickup || _savingDrop ? null : _estimateFare,
              icon: _estimating ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.calculate_outlined),
              label: Text(_estimating ? 'Calculating fare...' : couponCode.isNotEmpty ? 'Apply coupon & calculate' : 'Calculate fare'),
              style: ElevatedButton.styleFrom(backgroundColor: navy, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13))),
            ),
          ),
          if (hasFare) ...[
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(15), border: Border.all(color: const Color(0xFFE5EAF3))),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.receipt_rounded, color: navy, size: 19),
                      SizedBox(width: 8),
                      Expanded(child: Text('Your fare details', style: TextStyle(color: navy, fontSize: 15, fontWeight: FontWeight.w900))),
                    ],
                  ),
                  const SizedBox(height: 9),
                  _fareRow('Estimated fare', estimated, icon: Icons.route_rounded),
                  if (couponCode.isNotEmpty) _fareRow('Coupon code', _couponApplied ? couponCode : 'Not applied', icon: Icons.local_offer_outlined, valueColor: _couponApplied ? green : red),
                  _fareRow('Coupon discount', _couponApplied ? discount : 0, icon: Icons.savings_outlined, valueColor: _couponApplied ? green : muted),
                  _fareRow('Coupon applied fare', _couponApplied ? appliedFare : estimated, icon: Icons.price_check_rounded),
                  const Divider(height: 20),
                  _fareRow('Final fare', finalFare, icon: Icons.payments_outlined, bold: true),
                  _fareRow('Total fare', totalFare, icon: Icons.account_balance_wallet_outlined, bold: true, valueColor: green),
                  if (_couponApplied && discount > 0) ...[
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(11),
                      decoration: BoxDecoration(color: green.withValues(alpha: 0.09), borderRadius: BorderRadius.circular(11)),
                      child: Row(
                        children: [
                          const Icon(Icons.celebration_rounded, color: green, size: 20),
                          const SizedBox(width: 8),
                          Expanded(child: Text('You saved ${_money(discount)} with $couponCode!', style: const TextStyle(color: green, fontSize: 12, fontWeight: FontWeight.w800))),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: navy))
          : SafeArea(
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.fromLTRB(18, 14, 18, 20),
                    decoration: const BoxDecoration(color: navy, borderRadius: BorderRadius.vertical(bottom: Radius.circular(25))),
                    child: Row(
                      children: [
                        Container(
                          width: 46,
                          height: 46,
                          decoration: BoxDecoration(color: gold, borderRadius: BorderRadius.circular(14)),
                          child: const Icon(Icons.electric_bike_rounded, color: navy, size: 27),
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('NandiRide', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900)),
                              SizedBox(height: 3),
                              Text('BOOK YOUR RIDE', style: TextStyle(color: gold, fontSize: 10, letterSpacing: 1.4, fontWeight: FontWeight.w800)),
                            ],
                          ),
                        ),
                        IconButton(onPressed: _loadData, icon: const Icon(Icons.refresh_rounded, color: Colors.white)),
                      ],
                    ),
                  ),
                  if (_error != null) Padding(padding: const EdgeInsets.all(12), child: Text(_error!, style: const TextStyle(color: red))),
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.all(16),
                      children: [
                        const Text('Where are you going?', style: TextStyle(color: navy, fontSize: 21, fontWeight: FontWeight.w900)),
                        const SizedBox(height: 5),
                        const Text('Enter pickup and destination. The route will load automatically after both addresses are resolved.', style: TextStyle(color: muted, fontSize: 12)),
                        const SizedBox(height: 16),
                        _cardDecorationWrapper(
                          Column(
                            children: [
                              _addressField(pickup: true),
                              const Divider(height: 16),
                              _addressField(pickup: false),
                              const SizedBox(height: 8),
                              Align(
                                alignment: Alignment.centerLeft,
                                child: TextButton.icon(
                                  onPressed: _swapLocations,
                                  icon: const Icon(Icons.swap_vert_rounded),
                                  label: const Text('Swap pickup and drop'),
                                  style: TextButton.styleFrom(foregroundColor: navy),
                                ),
                              ),
                              if (_savingPickup || _savingDrop) const Padding(padding: EdgeInsets.all(8), child: LinearProgressIndicator(color: gold, backgroundColor: background)),
                              if (_pickupId != null && _dropId != null)
                                const Row(
                                  children: [
                                    Icon(Icons.check_circle_rounded, color: green, size: 17),
                                    SizedBox(width: 7),
                                    Expanded(child: Text('Pickup and drop are saved.', style: TextStyle(color: green, fontSize: 12, fontWeight: FontWeight.w700))),
                                  ],
                                ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        _mapCard(),
                        const SizedBox(height: 20),
                        _vehicleSection(),
                        const SizedBox(height: 20),
                        _fareCard(),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _booking || _estimating || _savingPickup || _savingDrop ? null : _bookRide,
                            icon: _booking
                                ? const SizedBox(width: 19, height: 19, child: CircularProgressIndicator(strokeWidth: 2, color: navy))
                                : const Icon(Icons.arrow_forward_rounded),
                            label: Text(_booking ? 'Submitting ride...' : 'Book my ride'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: gold,
                              foregroundColor: navy,
                              disabledBackgroundColor: gold.withValues(alpha: 0.5),
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                              textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text('Address search and map data © OpenStreetMap contributors.', textAlign: TextAlign.center, style: TextStyle(color: muted, fontSize: 10)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
