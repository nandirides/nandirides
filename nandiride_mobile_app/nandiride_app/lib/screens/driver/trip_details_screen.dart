
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../../app/app_theme.dart';
import '../../services/driver_service.dart';

class TripDetailsScreen extends StatefulWidget {
  final int? rideId;

  const TripDetailsScreen({super.key, this.rideId});

  @override
  State<TripDetailsScreen> createState() => _TripDetailsScreenState();
}

class _TripDetailsScreenState extends State<TripDetailsScreen> {
  Map<String, dynamic>? _ride;
  Map<String, dynamic>? _pickup;
  Map<String, dynamic>? _drop;
  bool _isLoading = true;
  bool _isUpdating = false;
  String? _error;
  int? _rideId;
  bool _argumentsResolved = false;
  final TextEditingController _otpController = TextEditingController();

  String get _status => (_ride?['status'] ?? '').toString().toLowerCase();

  String get _statusLabel {
    switch (_status) {
      case 'driver_assigned':
        return 'Ride Assigned';
      case 'driver_arriving':
        return 'Driver Arriving';
      case 'driver_arrived':
        return 'Driver Arrived';
      case 'started':
        return 'Trip In Progress';
      case 'completed':
        return 'Trip Completed';
      case 'cancelled':
        return 'Trip Cancelled';
      default:
        return _status.isEmpty
            ? 'Status unavailable'
            : _status.replaceAll('_', ' ').toUpperCase();
    }
  }

  int? _parseId(dynamic value) {
    if (value is int) return value > 0 ? value : null;
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

  Map<String, dynamic>? _asMap(dynamic value) {
    if (value is Map) return Map<String, dynamic>.from(value);
    return null;
  }

  int? _readRideId(dynamic value, {int depth = 0}) {
    if (depth > 6 || value is! Map) return null;

    final map = Map<String, dynamic>.from(value);

    for (final key in [
      'ride_id',
      'rideId',
      'accepted_ride_id',
      'assigned_ride_id',
      'trip_id',
      'tripId',
    ]) {
      final id = _parseId(map[key]);
      if (id != null) return id;
    }

    for (final key in [
      'ride',
      'accepted_ride',
      'assigned_ride',
      'ride_details',
      'ride_detail',
      'trip',
      'assigned_trip',
    ]) {
      final nested = map[key];
      if (nested is Map) {
        final ride = Map<String, dynamic>.from(nested);
        final id = _parseId(
          ride['ride_id'] ?? ride['rideId'] ?? ride['id'],
        );
        if (id != null) return id;

        final nestedId = _readRideId(ride, depth: depth + 1);
        if (nestedId != null) return nestedId;
      }
    }

    for (final key in ['data', 'result', 'response', 'payload']) {
      final nested = map[key];
      if (nested is Map) {
        final id = _readRideId(nested, depth: depth + 1);
        if (id != null) return id;
      }
    }

    return null;
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_argumentsResolved) return;
    _argumentsResolved = true;

    final args = ModalRoute.of(context)?.settings.arguments;
    final argumentId = _readRideId(args);
    final directArgumentId = _parseId(args);

    _rideId = _parseId(widget.rideId) ?? directArgumentId ?? argumentId;

    debugPrint('TRIP DETAILS ROUTE ARGUMENTS: $args');
    debugPrint('TRIP DETAILS RIDE ID: $_rideId');

    if (_rideId != null) {
      _loadRide();
    } else {
      setState(() {
        _isLoading = false;
        _error =
            'Ride ID missing. Ride accept API se actual ride_id return hona chahiye.';
      });
    }
  }

  @override
  void dispose() {
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _loadRide() async {
    final id = _rideId;
    if (id == null) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = 'Ride ID missing. Please reopen Trip Details from Ride Requests.';
      });
      return;
    }

    if (mounted) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final response = await DriverService.getRideDetails(id);
      debugPrint('TRIP DETAILS API RESPONSE: $response');

      dynamic current = response;
      Map<String, dynamic>? rideData;
      Map<String, dynamic>? pickupData;
      Map<String, dynamic>? dropData;

      for (var depth = 0; depth < 6; depth++) {
        final map = _asMap(current);
        if (map == null) break;

        rideData ??= _asMap(map['ride']);
        pickupData ??= _asMap(map['pickup_details']);
        dropData ??= _asMap(map['drop_details']);

        if (rideData == null &&
            (map.containsKey('ride_number') ||
                map.containsKey('ride_id') ||
                map.containsKey('status'))) {
          rideData = map;
        }

        if (rideData != null && pickupData != null && dropData != null) {
          break;
        }

        final next = map['data'] ?? map['result'] ?? map['response'];
        if (next is! Map) break;
        current = next;
      }

      if (rideData == null) {
        throw Exception(
          'Ride details API did not return a ride object. Check the server response.',
        );
      }

      if (!mounted) return;

      setState(() {
        _ride = rideData;
        _pickup = pickupData;
        _drop = dropData;
        _isLoading = false;
        _error = null;
      });
    } catch (e, stackTrace) {
      debugPrint('TRIP DETAILS LOAD ERROR: $e');
      debugPrintStack(stackTrace: stackTrace);
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = _cleanError(e);
      });
    }
  }

  String _cleanError(Object error) {
    return error.toString().replaceFirst('Exception: ', '').trim();
  }

  void _showMessage(String message, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: isError ? AppTheme.error : AppTheme.primary,
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(16),
        ),
      );
  }

  Future<void> _updateStatus(String action, {String? otp}) async {
    final id = _rideId;
    if (id == null || _isUpdating) return;

    setState(() => _isUpdating = true);

    try {
      final response = await DriverService.updateRideStatus(
        rideId: id,
        action: action,
        otp: otp,
      );

      if (response['success'] == false) {
        throw Exception(
          response['detail'] ??
              response['message'] ??
              'Ride status update failed.',
        );
      }

      _otpController.clear();
      await _loadRide();

      if (!mounted) return;

      _showMessage(
        (response['status_label'] ??
                response['message'] ??
                'Ride status updated successfully.')
            .toString(),
      );
    } catch (e) {
      _showMessage(_cleanError(e), isError: true);
    } finally {
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  String _locationText(Map<String, dynamic>? location) {
    if (location == null) return 'Location unavailable';
    final address = (location['address'] ?? '').toString().trim();
    final city = (location['city'] ?? '').toString().trim();
    final combined = [address, city]
        .where((s) => s.isNotEmpty)
        .toSet()
        .join(', ');
    return combined.isEmpty ? 'Location unavailable' : combined;
  }

  String _money(dynamic value) {
    if (value == null || value.toString().isEmpty) return 'Not available';
    final amount = double.tryParse(value.toString());
    return amount == null ? 'Not available' : '₹${amount.toStringAsFixed(2)}';
  }

  String _value(dynamic value, {String fallback = 'Not available'}) {
    if (value == null || value.toString().trim().isEmpty) return fallback;
    return value.toString();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text(
          'Trip Details',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: _isLoading ? null : _loadRide,
            tooltip: 'Refresh ride',
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(
                child: CircularProgressIndicator(color: AppTheme.primary),
              )
            : _error != null
                ? _buildError()
                : _ride == null
                    ? _buildError(message: 'Ride details are unavailable.')
                    : RefreshIndicator(
                        color: AppTheme.primary,
                        onRefresh: _loadRide,
                        child: ListView(
                          physics: const AlwaysScrollableScrollPhysics(),
                          padding: const EdgeInsets.all(16),
                          children: [
                            _buildHeader(),
                            const SizedBox(height: 22),
                            _sectionTitle('Journey Information'),
                            const SizedBox(height: 12),
                            _buildLocationsCard(),
                            const SizedBox(height: 16),
                            _buildFareCard(),
                            const SizedBox(height: 22),
                            _sectionTitle('Trip Status'),
                            const SizedBox(height: 12),
                            _buildStatusCard(),
                            const SizedBox(height: 16),
                            _buildProgress(),
                            const SizedBox(height: 22),
                            _buildActions(),
                            const SizedBox(height: 20),
                          ],
                        ),
                      ),
      ),
    );
  }

  Widget _buildError({String? message}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 54, color: AppTheme.error),
            const SizedBox(height: 14),
            Text(
              message ?? _error ?? 'Unable to load ride.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 18),
            ElevatedButton.icon(
              onPressed: _rideId == null
                  ? () => Navigator.of(context).maybePop()
                  : _loadRide,
              icon: const Icon(Icons.refresh_rounded),
              label: Text(_rideId == null ? 'Go Back' : 'Try Again'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primary,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final rideNumber = _value(
      _ride?['ride_number'],
      fallback: 'Ride #$_rideId',
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primary, Color(0xFF17386F)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primary.withValues(alpha: 0.16),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 68,
            height: 68,
            decoration: const BoxDecoration(
              color: AppTheme.secondary,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.route_rounded,
              color: AppTheme.primary,
              size: 34,
            ),
          ),
          const SizedBox(height: 14),
          Text(
            rideNumber,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 23,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 7),
            decoration: BoxDecoration(
              color: AppTheme.secondary,
              borderRadius: BorderRadius.circular(30),
            ),
            child: Text(
              _statusLabel.toUpperCase(),
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppTheme.primary,
                fontSize: 10,
                fontWeight: FontWeight.w900,
                letterSpacing: 0.8,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            'Ride ID: $_rideId',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.8),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: AppTheme.primary,
        fontSize: 19,
        fontWeight: FontWeight.w900,
      ),
    );
  }

  Widget _buildLocationsCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _LocationRow(
            icon: Icons.my_location_rounded,
            iconColor: AppTheme.success,
            title: 'PICKUP LOCATION',
            location: _locationText(_pickup),
          ),
          Padding(
            padding: const EdgeInsets.only(left: 11, top: 5, bottom: 5),
            child: Row(
              children: [
                Container(width: 2, height: 28, color: AppTheme.border),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Pickup point',
                    style: TextStyle(
                      color: AppTheme.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
          _LocationRow(
            icon: Icons.location_on_rounded,
            iconColor: AppTheme.error,
            title: 'DROP LOCATION',
            location: _locationText(_drop),
          ),
          const SizedBox(height: 14),
          const Divider(color: AppTheme.border),
          const SizedBox(height: 8),
          _InfoRow(
            label: 'Passenger',
            value: _value(_ride?['passenger_name']),
          ),
          const SizedBox(height: 8),
          _InfoRow(
            label: 'Vehicle',
            value: _value(_ride?['vehicle_type']),
          ),
          const SizedBox(height: 8),
          _InfoRow(
            label: 'Vehicle number',
            value: _value(_ride?['vehicle_number']),
          ),
        ],
      ),
    );
  }

  Widget _buildFareCard() {
    final fare = _ride?['fare'];
    final distance = _ride?['distance_km'];
    final duration = _ride?['duration_minutes'];
    final discount = _ride?['discount_amount'];

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF8DF),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppTheme.secondary.withValues(alpha: 0.7),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppTheme.secondary,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(
                  Icons.payments_rounded,
                  color: AppTheme.primary,
                  size: 25,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Estimated Fare',
                      style: TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: Alignment.centerLeft,
                      child: Text(
                        _money(fare),
                        style: const TextStyle(
                          color: AppTheme.primary,
                          fontSize: 27,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(color: AppTheme.border),
          const SizedBox(height: 8),
          _InfoRow(
            label: 'Distance',
            value: distance == null
                ? 'Not available'
                : '${_value(distance)} km',
          ),
          const SizedBox(height: 8),
          _InfoRow(
            label: 'Estimated duration',
            value: duration == null ? 'Not available' : '$duration min',
          ),
          const SizedBox(height: 8),
          _InfoRow(label: 'Discount', value: _money(discount)),
        ],
      ),
    );
  }

  Widget _buildStatusCard() {
    final description = switch (_status) {
      'driver_assigned' =>
        'Ride assigned to you. Start by heading toward the pickup point.',
      'driver_arriving' => 'You are on your way to the pickup location.',
      'driver_arrived' =>
        'You have arrived. Ask the passenger for the pickup OTP.',
      'started' =>
        'The trip is in progress. Complete it after reaching the drop location.',
      'completed' => 'This trip has been completed.',
      'cancelled' => 'This ride has been cancelled.',
      _ => 'Current ride status received from the server.',
    };

    final icon = switch (_status) {
      'completed' => Icons.check_circle_rounded,
      'started' => Icons.directions_car_rounded,
      'driver_arrived' => Icons.location_on_rounded,
      'cancelled' => Icons.cancel_rounded,
      _ => Icons.hourglass_top_rounded,
    };

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: AppTheme.secondary.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: AppTheme.primary, size: 25),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _statusLabel,
                  style: const TextStyle(
                    color: AppTheme.primary,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  description,
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 12,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgress() {
    const labels = [
      'Assigned',
      'Arriving',
      'Arrived',
      'Started',
      'Completed',
    ];
    const states = [
      'driver_assigned',
      'driver_arriving',
      'driver_arrived',
      'started',
      'completed',
    ];

    final currentIndex = states.indexOf(_status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        children: List.generate(labels.length, (index) {
          final done = currentIndex >= index && currentIndex >= 0;

          return Expanded(
            child: Column(
              children: [
                Row(
                  children: [
                    if (index > 0)
                      Expanded(
                        child: Container(
                          height: 3,
                          color: currentIndex >= index
                              ? AppTheme.primary
                              : AppTheme.border,
                        ),
                      ),
                    Container(
                      width: 27,
                      height: 27,
                      decoration: BoxDecoration(
                        color: done ? AppTheme.primary : AppTheme.background,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: done ? AppTheme.primary : AppTheme.border,
                        ),
                      ),
                      child: Icon(
                        done ? Icons.check_rounded : Icons.circle_outlined,
                        size: 15,
                        color: done ? AppTheme.secondary : AppTheme.textSecondary,
                      ),
                    ),
                    if (index < labels.length - 1)
                      Expanded(
                        child: Container(
                          height: 3,
                          color: currentIndex > index
                              ? AppTheme.primary
                              : AppTheme.border,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  labels[index],
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: done ? AppTheme.primary : AppTheme.textSecondary,
                    fontSize: 9,
                    fontWeight: done ? FontWeight.w800 : FontWeight.w600,
                  ),
                ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildActions() {
    final List<Widget> buttons = [];

    if (_status == 'driver_assigned') {
      buttons.add(
        _primaryButton(
          label: 'Start Heading to Pickup',
          icon: Icons.navigation_rounded,
          onPressed: () => _updateStatus('arriving'),
        ),
      );
    } else if (_status == 'driver_arriving') {
      buttons.add(
        _primaryButton(
          label: 'I Have Arrived',
          icon: Icons.location_on_rounded,
          onPressed: () => _updateStatus('arrived'),
        ),
      );
    } else if (_status == 'driver_arrived') {
      buttons.add(
        TextField(
          controller: _otpController,
          keyboardType: TextInputType.number,
          maxLength: 6,
          decoration: InputDecoration(
            labelText: 'Passenger pickup OTP',
            hintText: 'Enter 6-digit OTP',
            prefixIcon: const Icon(Icons.lock_outline_rounded),
            counterText: '',
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
            ),
          ),
        ),
      );
      buttons.add(const SizedBox(height: 12));
      buttons.add(
        _primaryButton(
          label: 'Verify OTP & Start Trip',
          icon: Icons.play_arrow_rounded,
          onPressed: () {
            final otp = _otpController.text.trim();
            if (otp.length != 6 || int.tryParse(otp) == null) {
              _showMessage(
                'Enter the valid 6-digit passenger OTP.',
                isError: true,
              );
              return;
            }
            _updateStatus('start', otp: otp);
          },
        ),
      );
    } else if (_status == 'started') {
      buttons.add(
        _primaryButton(
          label: 'Complete Trip',
          icon: Icons.flag_rounded,
          onPressed: _confirmComplete,
        ),
      );
    } else if (_status == 'completed' || _status == 'cancelled') {
      buttons.add(
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppTheme.background,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppTheme.border),
          ),
          child: Text(
            _status == 'completed'
                ? 'This ride is completed.'
                : 'This ride is cancelled.',
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      );
    } else {
      buttons.add(
        const Text(
          'No action is available for this ride status.',
          textAlign: TextAlign.center,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ...buttons,
        if (_isUpdating) ...[
          const SizedBox(height: 14),
          const Center(
            child: CircularProgressIndicator(color: AppTheme.primary),
          ),
        ],
      ],
    );
  }

  Widget _primaryButton({
    required String label,
    required IconData icon,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      height: 54,
      child: ElevatedButton.icon(
        onPressed: _isUpdating ? null : onPressed,
        icon: Icon(icon),
        label: Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primary,
          foregroundColor: Colors.white,
          disabledBackgroundColor: AppTheme.border,
          disabledForegroundColor: AppTheme.textSecondary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  Future<void> _confirmComplete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Complete Trip?'),
        content: const Text(
          'Confirm that the passenger has reached the drop location.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primary,
              foregroundColor: Colors.white,
            ),
            child: const Text('Complete Trip'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _updateStatus('complete');
    }
  }
}

class _LocationRow extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String location;

  const _LocationRow({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.location,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: iconColor, size: 24),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                location,
                softWrap: true,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 120,
          child: Text(
            label,
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            textAlign: TextAlign.end,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}
