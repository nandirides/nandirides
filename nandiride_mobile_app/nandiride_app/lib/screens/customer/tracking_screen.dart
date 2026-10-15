
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../app/app_routes.dart';
import '../../services/booking_service.dart';

class TrackingScreen extends StatefulWidget {
  const TrackingScreen({super.key});
  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  int? _requestId;
  int? _rideId;
  Timer? _timer;
  bool _initialized = false;
  bool _loading = true;
  bool _refreshing = false;
  String? _error;
  Map<String, dynamic> _ride = {};
  Map<String, dynamic> _request = {};
  Map<String, dynamic> _tracking = {};
  Map<String, dynamic> _payment = {};
  static const Color navy = Color(0xFF101B3F);
  static const Color gold = Color(0xFFFFC928);
  static const Color muted = Color(0xFF68728A);
  static const Color green = Color(0xFF179B72);
  static const Color pageBackground = Color(0xFFF5F7FC);
  static const String mapUrl = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_3wf8_1_477b9c969e22fe3e205f303d';
  final MapController _mapController = MapController();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_initialized) return;
    _initialized = true;
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map) {
      _requestId = _parseId(args['requestId'] ?? args['request_id'] ?? args['id']);
      _rideId = _parseId(args['rideId'] ?? args['ride_id']);
      final initialRide = _asMap(args['ride']);
      final initialRequest = _asMap(args['request']);
      if (initialRide != null) _ride = initialRide;
      if (initialRequest != null) _request = initialRequest;
      if (_requestId == null) {
        _requestId = _parseId(_request['id'] ?? _request['request_id']);
      }
      if (_rideId == null) {
        _rideId = _parseId(_ride['id'] ?? _ride['ride_id']);
      }
    }
    if (_requestId == null) {
      _loading = false;
      _error = 'Booking request ID nahi mila. My Rides se tracking open karein.';
      return;
    }
    _refresh();
    _timer = Timer.periodic(const Duration(seconds: 5), (_) => _refresh());
  }

  int? _parseId(dynamic value) {
    if (value is int) return value;
    return int.tryParse(value?.toString() ?? '');
  }

  double? _number(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    final cleaned = value.toString().replaceAll(',', '').replaceAll('₹', '').trim();
    return double.tryParse(cleaned);
  }

  String _money(dynamic value) {
    final parsed = _number(value);
    if (parsed == null) return 'Not available';
    return '₹${parsed.toStringAsFixed(2)}';
  }

  Map<String, dynamic>? _asMap(dynamic value) {
    if (value is Map<String, dynamic>) return value;
    if (value is Map) return Map<String, dynamic>.from(value);
    return null;
  }

  dynamic _firstValue(List<dynamic> values) {
    for (final value in values) {
      if (value != null && value.toString().trim().isNotEmpty) return value;
    }
    return null;
  }

  dynamic _findNestedValue(dynamic source, List<String> keys, {int depth = 0}) {
    if (source is! Map || depth > 6) return null;
    for (final key in keys) {
      if (source.containsKey(key) && source[key] != null) return source[key];
    }
    for (final value in source.values) {
      if (value is Map) {
        final result = _findNestedValue(value, keys, depth: depth + 1);
        if (result != null) return result;
      }
    }
    return null;
  }

  dynamic _field(List<String> keys) {
    final sources = [_ride, _request, _payment];
    for (final source in sources) {
      final value = _firstValue(keys.map((key) => source[key]).toList());
      if (value != null) return value;
    }
    for (final source in sources) {
      final value = _findNestedValue(source, keys);
      if (value != null) return value;
    }
    return null;
  }

  Future<void> _refresh() async {
    if (!mounted || _refreshing || _requestId == null) return;
    _refreshing = true;
    try {
      final response = await BookingService.getRideRequestTracking(_requestId!);
      if (!mounted) return;
      final root = _asMap(response['data']) ?? response;
      final requestData = _asMap(root['request']) ??
          _asMap(root['ride_request']) ??
          _asMap(root['booking']) ??
          _asMap(root['rideRequest']);
      final rideData = _asMap(root['ride']) ??
          _asMap(root['active_ride']) ??
          _asMap(root['trip']);
      final trackingData = _asMap(root['latest_tracking']) ??
          _asMap(root['tracking']) ??
          _asMap(root['location']) ??
          _asMap(rideData?['latest_tracking']) ??
          _asMap(rideData?['tracking']);
      final paymentData = _asMap(root['payment']) ??
          _asMap(root['payment_details']) ??
          _asMap(root['payment_detail']) ??
          _asMap(rideData?['payment']);
      setState(() {
        if (requestData != null) {
          _request = {..._request, ...requestData};
        } else {
          _request = {..._request, ...root};
        }
        if (rideData != null) {
          _ride = {..._ride, ...rideData};
        }
        if (trackingData != null) {
          _tracking = {..._tracking, ...trackingData};
        } else {
          final nested = _asMap(_ride['latest_tracking']) ?? _asMap(_ride['tracking']);
          if (nested != null) _tracking = {..._tracking, ...nested};
        }
        if (paymentData != null) {
          _payment = {..._payment, ...paymentData};
        }
        _rideId = _parseId(_ride['id'] ?? _ride['ride_id'] ?? _ride['rideId']) ?? _rideId;
        _requestId = _parseId(_request['id'] ?? _request['request_id']) ?? _requestId;
        _error = null;
        _loading = false;
      });
      if (_isFinished) _timer?.cancel();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    } finally {
      _refreshing = false;
    }
  }

  String get _rawStatus => (_field(['status', 'ride_status', 'booking_status']) ?? 'requested').toString().toLowerCase().trim();

  String get _status {
    switch (_rawStatus) {
      case 'requested':
      case 'searching_driver':
      case 'finding_driver':
      case 'pending':
        return 'Finding your driver';
      case 'driver_assigned':
      case 'accepted':
        return 'Driver assigned';
      case 'driver_arriving':
        return 'Driver on the way';
      case 'driver_arrived':
        return 'Driver waiting at pickup';
      case 'started':
      case 'in_progress':
        return 'Ride in progress';
      case 'completed':
        return 'Ride completed';
      case 'cancelled':
        return 'Ride cancelled';
      case 'expired':
        return 'Booking expired';
      default:
        return 'Booking submitted';
    }
  }

  bool get _isFinished => ['completed', 'cancelled', 'expired'].contains(_rawStatus);
  Map<String, dynamic> get _driver => _asMap(_ride['driver']) ?? _asMap(_request['driver']) ?? {};
  Map<String, dynamic> get _vehicle => _asMap(_ride['vehicle']) ?? _asMap(_ride['vehicle_type']) ?? _asMap(_request['vehicle_type']) ?? {};
  bool get _hasDriver {
    return _ride['driver_id'] != null ||
        _ride['driverId'] != null ||
        _driver['id'] != null ||
        _ride['driver_name'] != null ||
        _ride['driverName'] != null ||
        _ride['driver'] is Map;
  }

  String _value(dynamic value, [String fallback = 'Not available']) {
    if (value == null || value.toString().trim().isEmpty) return fallback;
    return value.toString();
  }

  String _location(dynamic value) {
    if (value is Map) {
      return _value(value['address'] ?? value['name'] ?? value['title'] ?? value['location_name'] ?? value['formatted_address']);
    }
    return _value(value);
  }

  dynamic get _pickup => _ride['pickup_location'] ?? _request['pickup_location'] ?? _request['pickup'] ?? _ride['pickup'];
  dynamic get _drop => _ride['drop_location'] ?? _request['drop_location'] ?? _request['drop'] ?? _ride['drop'];

  dynamic get _estimatedFare => _field([
    'estimated_fare', 'estimate_fare', 'estimated_amount', 'base_fare',
    'original_fare', 'fare_before_discount', 'original_amount', 'subtotal'
  ]);

  dynamic get _discount => _field([
    'discount_amount', 'coupon_discount', 'discount', 'coupon_savings',
    'discount_value', 'coupon_amount'
  ]);

  dynamic get _couponCode => _field([
    'coupon_code', 'applied_coupon', 'coupon', 'promo_code'
  ]);

  dynamic get _couponFare => _field([
    'coupon_applied_fare', 'discounted_fare', 'fare_after_discount',
    'fare_after_coupon', 'subtotal_after_discount'
  ]);

  dynamic get _finalFare => _field([
    'final_fare', 'final_amount', 'payable_amount',
    'amount_after_discount', 'fare_after_coupon'
  ]);

  dynamic get _totalFare => _field([
    'total_fare', 'total_amount', 'grand_total', 'total_payable',
    'amount_due', 'payable_amount'
  ]);

  double? get _calculatedDiscountedFare {
    final explicit = _number(_couponFare);
    if (explicit != null) return explicit;
    final estimated = _number(_estimatedFare);
    final discount = _number(_discount);
    if (estimated != null && discount != null) return (estimated - discount).clamp(0, double.infinity).toDouble();
    return null;
  }

  dynamic get _displayFinalFare => _firstValue([
    _finalFare,
    _calculatedDiscountedFare,
    _totalFare,
    _field(['fare', 'amount', 'price'])
  ]);

  dynamic get _displayTotalFare => _firstValue([
    _totalFare,
    _finalFare,
    _calculatedDiscountedFare,
    _field(['fare', 'amount', 'price'])
  ]);

  String get _driverName => _value(
    _ride['driver_name'] ?? _ride['driverName'] ??
    _driver['full_name'] ?? _driver['name'] ??
    _driver['username'] ?? _driver['user_name'],
    _hasDriver ? 'Driver assigned' : 'Waiting for assignment',
  );

  String get _vehicleName {
    final value = _ride['vehicle_type_name'] ??
        _ride['vehicleTypeName'] ??
        _vehicle['vehicle_type_name'] ??
        _vehicle['name'] ??
        _vehicle['model'] ??
        _ride['vehicle_type'] ??
        _request['vehicle_type_name'];
    if (value is Map) return _value(value['name'] ?? value['code']);
    return _value(value);
  }

  String get _vehicleNumber => _value(
    _ride['vehicle_number'] ?? _ride['vehicleNumber'] ??
    _vehicle['registration_number'] ?? _vehicle['registration_number_plate'] ??
    _vehicle['plate_number'] ?? _vehicle['number_plate'],
  );

  String get _driverPhone => _value(
    _ride['driver_phone'] ?? _ride['driverPhone'] ??
    _driver['phone'] ?? _driver['mobile'] ?? _driver['phone_number'],
  );

  LatLng? _coordinates(dynamic source) {
    if (source is! Map) return null;
    final lat = _number(source['latitude'] ?? source['lat'] ??
        source['pickup_latitude'] ?? source['drop_latitude'] ?? source['driver_latitude']);
    final lng = _number(source['longitude'] ?? source['lng'] ?? source['lon'] ??
        source['pickup_longitude'] ?? source['drop_longitude'] ?? source['driver_longitude']);
    if (lat == null || lng == null || lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
    return LatLng(lat, lng);
  }

  LatLng? get _driverPoint {
    final sources = [_tracking, _asMap(_tracking['location']), _asMap(_ride['latest_tracking']), _asMap(_ride['tracking']), _ride, _driver];
    for (final source in sources) {
      final point = _coordinates(source);
      if (point != null) return point;
    }
    return null;
  }

  LatLng? get _pickupPoint => _coordinates(_asMap(_pickup)) ?? _coordinates(_request) ?? _coordinates(_ride['pickup']);
  LatLng? get _dropPoint => _coordinates(_asMap(_drop)) ?? _coordinates(_request['drop']) ?? _coordinates(_ride['drop']);
  LatLng get _mapCenter => _driverPoint ?? _pickupPoint ?? _dropPoint ?? const LatLng(29.9457, 78.1642);

  List<Marker> get _mapMarkers {
    final markers = <Marker>[];
    final pickup = _pickupPoint;
    final drop = _dropPoint;
    final driver = _driverPoint;
    if (pickup != null) {
      markers.add(Marker(point: pickup, width: 42, height: 48, child: const Icon(Icons.location_on, color: green, size: 42)));
    }
    if (drop != null) {
      markers.add(Marker(point: drop, width: 42, height: 48, child: const Icon(Icons.location_on, color: Colors.red, size: 42)));
    }
    if (driver != null) {
      markers.add(Marker(
        point: driver,
        width: 54,
        height: 54,
        child: Container(
          decoration: BoxDecoration(color: navy, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 3), boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)]),
          child: const Icon(Icons.directions_car_rounded, color: gold, size: 28),
        ),
      ));
    }
    return markers;
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final requestNumber = _field(['request_number', 'booking_number', 'booking_id']);
    final rideNumber = _field(['ride_number', 'rideNumber']);
    return Scaffold(
      backgroundColor: pageBackground,
      appBar: AppBar(
        title: const Text('Track Your Ride', style: TextStyle(fontWeight: FontWeight.w800)),
        backgroundColor: navy,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: 'Refresh tracking',
            onPressed: _refreshing ? null : _refresh,
            icon: _refreshing
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.refresh_rounded),
          ),
          IconButton(
            tooltip: 'My profile',
            onPressed: () => Navigator.pushNamed(context, AppRoutes.profile),
            icon: const Icon(Icons.person_outline_rounded, color: gold),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
              CircularProgressIndicator(color: navy),
              SizedBox(height: 16),
              Text('Loading your ride...', style: TextStyle(color: navy, fontWeight: FontWeight.w700)),
            ]))
          : RefreshIndicator(
              onRefresh: _refresh,
              color: navy,
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(18),
                children: [
                  _statusCard(rideNumber: rideNumber, requestNumber: requestNumber),
                  const SizedBox(height: 16),
                  if (_error != null) ...[_errorCard(), const SizedBox(height: 14)],
                  _mapCard(),
                  const SizedBox(height: 16),
                  if (_hasDriver) ...[_driverCard(), const SizedBox(height: 14)]
                  else if (!_isFinished) ...[_searchingCard(), const SizedBox(height: 14)],
                  _journeyCard(pickup: _pickup, drop: _drop),
                  const SizedBox(height: 16),
                  _fareCard(),
                  const SizedBox(height: 16),
                  _progressCard(),
                  const SizedBox(height: 20),
                  if (_isFinished)
                    ElevatedButton.icon(
                      onPressed: () => Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false),
                      icon: const Icon(Icons.home_rounded),
                      label: const Text('Back to Home'),
                      style: _primaryButtonStyle(),
                    )
                  else
                    OutlinedButton.icon(
                      onPressed: _refreshing ? null : _refresh,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Refresh Ride Status'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: navy,
                        side: const BorderSide(color: navy),
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                    ),
                  const SizedBox(height: 16),
                  const Text(
                    'Ride status refreshes every 5 seconds. Driver marker moves when the backend returns updated driver coordinates.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: muted, fontSize: 12, height: 1.5),
                  ),
                  const SizedBox(height: 20),
                ],
              ),
            ),
    );
  }

  Widget _statusCard({dynamic rideNumber, dynamic requestNumber}) {
    final Color statusColor = _rawStatus == 'completed'
        ? green
        : _rawStatus == 'cancelled' || _rawStatus == 'expired'
            ? Colors.red
            : gold;
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [navy, Color(0xFF263B70)], begin: Alignment.topLeft, end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.14), blurRadius: 18, offset: const Offset(0, 8))],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            padding: const EdgeInsets.all(11),
            decoration: BoxDecoration(color: gold.withValues(alpha: 0.16), borderRadius: BorderRadius.circular(14)),
            child: const Icon(Icons.route_rounded, color: gold, size: 30),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
            decoration: BoxDecoration(color: statusColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(30)),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Container(width: 7, height: 7, decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle)),
              const SizedBox(width: 7),
              Text(_isFinished ? 'Updated' : 'Live status', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
            ]),
          ),
        ]),
        const SizedBox(height: 18),
        const Text('YOUR RIDE STATUS', style: TextStyle(color: Colors.white70, fontSize: 11, letterSpacing: 1.2, fontWeight: FontWeight.w700)),
        const SizedBox(height: 7),
        Text(_status, style: const TextStyle(color: Colors.white, fontSize: 23, height: 1.2, fontWeight: FontWeight.w900)),
        const SizedBox(height: 12),
        Text(
          rideNumber != null ? 'Ride #$rideNumber' : requestNumber != null ? 'Request #$requestNumber' : 'Request ID: ${_requestId ?? '—'}',
          style: const TextStyle(color: gold, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        Text('Booking date: ${_value(_field(['created_at', 'booking_date', 'requested_at', 'date']))}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
      ]),
    );
  }

  Widget _mapCard() {
    final driver = _driverPoint;
    final pickup = _pickupPoint;
    final drop = _dropPoint;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration(),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Row(children: [
          Icon(Icons.location_on_rounded, color: navy, size: 22),
          SizedBox(width: 9),
          Expanded(child: Text('Live driver map', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900))),
        ]),
        const SizedBox(height: 12),
        ClipRRect(
          borderRadius: BorderRadius.circular(15),
          child: SizedBox(
            height: 300,
            width: double.infinity,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(initialCenter: _mapCenter, initialZoom: 13, minZoom: 3, maxZoom: 19),
              children: [
                TileLayer(
                  urlTemplate: mapUrl,
                  subdomains: const ['a', 'b', 'c', 'd'],
                  maxZoom: 20,
                  userAgentPackageName: 'com.nandiride.app',
                ),
                MarkerLayer(markers: _mapMarkers),
                RichAttributionWidget(attributions: [TextSourceAttribution('© OpenStreetMap contributors © CARTO')]),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Wrap(spacing: 14, runSpacing: 8, children: [
          _mapLegend(green, 'Pickup'),
          _mapLegend(Colors.red, 'Drop'),
          _mapLegend(navy, 'Driver'),
        ]),
        const SizedBox(height: 10),
        Text(
          driver != null
              ? 'Driver location: ${driver.latitude.toStringAsFixed(6)}, ${driver.longitude.toStringAsFixed(6)}'
              : 'Driver ki live location abhi API se nahi mili. Driver marker ke liye backend se latitude aur longitude aana zaroori hai.',
          style: const TextStyle(color: muted, fontSize: 12, height: 1.5),
        ),
        if (pickup == null || drop == null) ...[
          const SizedBox(height: 5),
          const Text('Pickup/drop markers ke liye response mein latitude aur longitude fields honi chahiye.', style: TextStyle(color: muted, fontSize: 11, height: 1.4)),
        ],
      ]),
    );
  }

  Widget _mapLegend(Color color, String label) {
    return Row(mainAxisSize: MainAxisSize.min, children: [
      Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
      const SizedBox(width: 5),
      Text(label, style: const TextStyle(color: muted, fontSize: 11, fontWeight: FontWeight.w700)),
    ]);
  }

  Widget _searchingCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: const Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SizedBox(width: 28, height: 28, child: CircularProgressIndicator(strokeWidth: 3, color: gold)),
        SizedBox(width: 14),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Finding your driver', style: TextStyle(color: navy, fontSize: 16, fontWeight: FontWeight.w900)),
          SizedBox(height: 5),
          Text('Your booking request is being checked. Driver details will appear here after assignment.', style: TextStyle(color: muted, fontSize: 12, height: 1.5)),
        ])),
      ]),
    );
  }

  Widget _driverCard() {
    final rating = _value(_ride['driver_rating'] ?? _driver['rating']);
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Driver details', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900)),
        const SizedBox(height: 16),
        Row(children: [
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(color: gold.withValues(alpha: 0.20), shape: BoxShape.circle),
            child: const Icon(Icons.person_rounded, color: navy, size: 30),
          ),
          const SizedBox(width: 13),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(_driverName, style: const TextStyle(color: navy, fontSize: 16, fontWeight: FontWeight.w900)),
            const SizedBox(height: 4),
            Text('Vehicle: $_vehicleName', style: const TextStyle(color: muted, fontSize: 12)),
          ])),
          if (rating != 'Not available')
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(color: const Color(0xFFFFF6D8), borderRadius: BorderRadius.circular(10)),
              child: Text('★ $rating', style: const TextStyle(color: navy, fontWeight: FontWeight.w800, fontSize: 12)),
            ),
        ]),
        const Divider(height: 26),
        _detailRow(Icons.phone_outlined, 'Phone', _driverPhone),
        const SizedBox(height: 12),
        _detailRow(Icons.directions_car_outlined, 'Registration', _vehicleNumber),
      ]),
    );
  }

  Widget _journeyCard({required dynamic pickup, required dynamic drop}) {
    final vehicleType = _vehicleName == 'Not available'
        ? _value(_request['vehicle_type_name'] ?? _request['vehicle_type'])
        : _vehicleName;
    final paymentStatus = _value(_field(['payment_status', 'status_payment']));
    final paymentMethod = _value(_field(['payment_method', 'method']));
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Booking details', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900)),
        const SizedBox(height: 18),
        _locationRow(green, 'PICKUP LOCATION', _location(pickup)),
        const SizedBox(height: 18),
        _locationRow(Colors.red, 'DROP LOCATION', _location(drop)),
        const Divider(height: 30),
        _detailRow(Icons.confirmation_number_outlined, 'Request number', _value(_field(['request_number', 'booking_number']))),
        const SizedBox(height: 12),
        _detailRow(Icons.directions_car_outlined, 'Ride number', _value(_field(['ride_number', 'rideNumber']))),
        const SizedBox(height: 12),
        _detailRow(Icons.directions_car_filled_outlined, 'Vehicle type', vehicleType),
        const SizedBox(height: 12),
        _detailRow(Icons.event_outlined, 'Booking date', _value(_field(['created_at', 'booking_date', 'requested_at', 'date']))),
        const SizedBox(height: 12),
        _detailRow(Icons.payments_outlined, 'Payment method', paymentMethod),
        const SizedBox(height: 12),
        _detailRow(Icons.receipt_long_outlined, 'Payment status', paymentStatus),
      ]),
    );
  }

  Widget _fareCard() {
    final estimated = _number(_estimatedFare);
    final discount = _number(_discount);
    final couponFare = _calculatedDiscountedFare;
    final finalFare = _number(_displayFinalFare);
    final totalFare = _number(_displayTotalFare);
    final coupon = _couponCode;
    final hasCoupon = coupon != null && coupon.toString().trim().isNotEmpty;
    final hasFare = estimated != null || discount != null || couponFare != null || finalFare != null || totalFare != null;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Row(children: [
          Icon(Icons.receipt_long_rounded, color: navy, size: 22),
          SizedBox(width: 9),
          Expanded(child: Text('Fare breakdown', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900))),
        ]),
        const SizedBox(height: 16),
        if (!hasFare)
          const Text('Fare details API response mein available nahi hain.', style: TextStyle(color: muted, fontSize: 12))
        else ...[
          _fareRow('Estimated fare', _money(estimated)),
          if (hasCoupon) _fareRow('Coupon applied', coupon.toString()),
          if (discount != null) _fareRow('Coupon discount', '- ${_money(discount)}', valueColor: green),
          if (couponFare != null) _fareRow('Fare after coupon', _money(couponFare)),
          const Divider(height: 24),
          _fareRow('Final fare', _money(finalFare ?? couponFare ?? estimated), bold: true),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: const Color(0xFFEAF8F1), borderRadius: BorderRadius.circular(13)),
            child: Row(children: [
              const Expanded(child: Text('Total fare', style: TextStyle(color: navy, fontWeight: FontWeight.w900, fontSize: 15))),
              Text(_money(totalFare ?? finalFare ?? couponFare ?? estimated), style: const TextStyle(color: green, fontSize: 20, fontWeight: FontWeight.w900)),
            ]),
          ),
        ],
        const SizedBox(height: 10),
        const Text('Fare values backend response ke according dikhaye jaate hain. Final billed amount server ke calculated amount se confirm karein.', style: TextStyle(color: muted, fontSize: 11, height: 1.45)),
      ]),
    );
  }

  Widget _fareRow(String label, String value, {Color valueColor = navy, bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(children: [
        Expanded(child: Text(label, style: TextStyle(color: muted, fontSize: 13, fontWeight: bold ? FontWeight.w800 : FontWeight.w500))),
        const SizedBox(width: 12),
        Flexible(child: Text(value, textAlign: TextAlign.end, style: TextStyle(color: valueColor, fontSize: 13, fontWeight: bold ? FontWeight.w900 : FontWeight.w700))),
      ]),
    );
  }

  Widget _locationRow(Color color, String title, String address) {
    return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Icon(Icons.location_on_rounded, color: color, size: 22),
      const SizedBox(width: 10),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(color: muted, fontSize: 10, letterSpacing: 0.8, fontWeight: FontWeight.w800)),
        const SizedBox(height: 4),
        Text(address, style: const TextStyle(color: navy, fontWeight: FontWeight.w700, height: 1.4)),
      ])),
    ]);
  }

  Widget _progressCard() {
    final steps = <(String, IconData, bool)>[
      ('Booking submitted', Icons.check_circle_rounded, true),
      ('Driver assigned', Icons.person_pin_circle_rounded, _hasDriver || ['driver_assigned', 'accepted', 'driver_arriving', 'driver_arrived', 'started', 'completed'].contains(_rawStatus)),
      ('Driver arrived', Icons.directions_car_rounded, ['driver_arrived', 'started', 'in_progress', 'completed'].contains(_rawStatus)),
      ('Ride in progress', Icons.route_rounded, ['started', 'in_progress', 'completed'].contains(_rawStatus)),
      ('Ride completed', Icons.flag_rounded, _rawStatus == 'completed'),
    ];
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Ride progress', style: TextStyle(color: navy, fontSize: 17, fontWeight: FontWeight.w900)),
        const SizedBox(height: 16),
        for (int i = 0; i < steps.length; i++) ...[
          Row(children: [
            Icon(steps[i].$2, color: steps[i].$3 ? green : const Color(0xFFB8C0D0), size: 22),
            const SizedBox(width: 12),
            Expanded(child: Text(steps[i].$1, style: TextStyle(color: steps[i].$3 ? navy : muted, fontWeight: steps[i].$3 ? FontWeight.w800 : FontWeight.w500))),
            if (steps[i].$3) const Icon(Icons.check_rounded, color: green, size: 20),
          ]),
          if (i != steps.length - 1)
            const Padding(padding: EdgeInsets.only(left: 10, top: 3, bottom: 3), child: SizedBox(height: 20, child: VerticalDivider(color: Color(0xFFD5DCE9), thickness: 2, width: 2))),
        ],
        if (_rawStatus == 'cancelled' || _rawStatus == 'expired') ...[
          const SizedBox(height: 14),
          Text(_status, style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w800)),
        ],
      ]),
    );
  }

  Widget _errorCard() {
    return Container(
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(13), border: Border.all(color: Colors.red.withValues(alpha: 0.18))),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Icon(Icons.info_outline_rounded, color: Colors.red),
        const SizedBox(width: 10),
        Expanded(child: Text('Tracking update nahi ho paya: $_error', style: const TextStyle(color: Colors.red, fontSize: 12, height: 1.5))),
      ]),
    );
  }

  Widget _detailRow(IconData icon, String label, String value) {
    return Row(children: [
      Icon(icon, color: muted, size: 19),
      const SizedBox(width: 10),
      Expanded(child: Text(label, style: const TextStyle(color: muted, fontSize: 12))),
      const SizedBox(width: 12),
      Flexible(child: Text(value, textAlign: TextAlign.end, style: const TextStyle(color: navy, fontSize: 12, fontWeight: FontWeight.w700))),
    ]);
  }

  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: const Color(0xFFE5E9F1)),
      boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.035), blurRadius: 12, offset: const Offset(0, 4))],
    );
  }

  ButtonStyle _primaryButtonStyle() {
    return ElevatedButton.styleFrom(
      backgroundColor: navy,
      foregroundColor: Colors.white,
      padding: const EdgeInsets.symmetric(vertical: 15),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      textStyle: const TextStyle(fontWeight: FontWeight.w800),
    );
  }
}
