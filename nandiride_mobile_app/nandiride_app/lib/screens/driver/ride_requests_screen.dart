
import 'package:flutter/material.dart';
import '../../app/app_theme.dart';
import '../../app/app_routes.dart';
import '../../services/driver_service.dart';

class RideRequestsScreen extends StatefulWidget {
  const RideRequestsScreen({super.key});
  @override
  State<RideRequestsScreen> createState() => _RideRequestsScreenState();
}

class _RideRequestsScreenState extends State<RideRequestsScreen> {
  bool _isLoading = true;
  bool _isOffline = false;
  String? _error;
  List<Map<String, dynamic>> _requests = [];
  int? _acceptingRequestId;

  @override
  void initState() {
    super.initState();
    _loadRequests();
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

  String _errorMessage(Object error) {
    return error.toString().replaceFirst('Exception: ', '').trim();
  }

  int? _parseId(dynamic value) {
    if (value is int && value > 0) return value;
    if (value is num && value > 0) return value.toInt();
    final parsed = int.tryParse(value?.toString().trim() ?? '');
    return parsed != null && parsed > 0 ? parsed : null;
  }

  Map<String, dynamic>? _asMap(dynamic value) {
    if (value is Map) return Map<String, dynamic>.from(value);
    return null;
  }

  Map<String, dynamic> _unwrapResponse(Map<String, dynamic> response) {
    final data = response['data'];
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    return response;
  }

  int? _extractRideId(Map<String, dynamic> response) {
    final data = _unwrapResponse(response);
    final ride = _asMap(data['ride']) ??
        _asMap(data['accepted_ride']) ??
        _asMap(data['assigned_ride']);

    final candidates = [
      data['ride_id'],
      data['rideId'],
      data['accepted_ride_id'],
      data['assigned_ride_id'],
      ride?['id'],
      ride?['ride_id'],
    ];

    for (final candidate in candidates) {
      final id = _parseId(candidate);
      if (id != null) return id;
    }

    // A top-level id is only accepted when the response identifies
    // the returned object as a ride, not merely a ride request.
    final type = (data['type'] ??
            data['object_type'] ??
            data['resource'] ??
            '')
        .toString()
        .toLowerCase();

    if (type == 'ride' || type == 'accepted_ride') {
      return _parseId(data['id']);
    }

    return null;
  }

  Future<void> _loadRequests({bool showLoader = true}) async {
    if (showLoader && mounted) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final profile = await DriverService.getMyProfile();
      if (!mounted) return;

      if (profile['is_online'] != true) {
        setState(() {
          _requests = [];
          _isOffline = true;
          _isLoading = false;
          _error = null;
        });
        return;
      }

      final response = await DriverService.getPendingRideRequests();
      final dynamic rawResults =
          response['results'] ?? response['data'] ?? [];

      List<Map<String, dynamic>> requests = [];

      if (rawResults is List) {
        requests = rawResults
            .whereType<Map>()
            .map((item) => Map<String, dynamic>.from(item))
            .toList();
      } else if (rawResults is Map && rawResults['results'] is List) {
        requests = (rawResults['results'] as List)
            .whereType<Map>()
            .map((item) => Map<String, dynamic>.from(item))
            .toList();
      }

      if (!mounted) return;
      setState(() {
        _requests = requests;
        _isOffline = false;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = _errorMessage(e);
      });
    }
  }

  Future<void> _acceptRide(Map<String, dynamic> rideRequest) async {
    if (_acceptingRequestId != null) return;

    final requestId = _parseId(
      rideRequest['id'] ?? rideRequest['request_id'],
    );

    if (requestId == null) {
      _showMessage('Invalid ride request ID.', isError: true);
      return;
    }

    setState(() => _acceptingRequestId = requestId);

    try {
      final response = await DriverService.acceptRide(requestId);
      if (!mounted) return;

      final rideId = _extractRideId(response);

      setState(() {
        _requests.removeWhere(
          (item) =>
              _parseId(item['id'] ?? item['request_id']) == requestId,
        );
      });

      final message = response['message']?.toString() ??
          _unwrapResponse(response)['message']?.toString() ??
          'Ride accepted successfully.';

      _showMessage(message);

      if (rideId == null) {
        _showMessage(
          'Ride accepted, but the API did not return a Ride ID. '
          'Please check DriverService.acceptRide() response.',
          isError: true,
        );
        await _loadRequests(showLoader: false);
        return;
      }

      await Navigator.of(context).pushNamed(
        AppRoutes.tripDetails,
        arguments: {'rideId': rideId},
      );

      if (mounted) await _loadRequests(showLoader: false);
    } catch (e) {
      if (!mounted) return;
      _showMessage(_errorMessage(e), isError: true);
      await _loadRequests(showLoader: false);
    } finally {
      if (mounted) {
        setState(() => _acceptingRequestId = null);
      }
    }
  }

  String _locationText(dynamic value) {
    if (value is Map) {
      final address = (value['address'] ??
              value['pickup_address'] ??
              value['drop_address'] ??
              '')
          .toString()
          .trim();
      final city = (value['city'] ?? '').toString().trim();
      final combined = [address, city]
          .where((part) => part.isNotEmpty)
          .toSet()
          .join(', ');
      if (combined.isNotEmpty) return combined;
    }
    if (value != null && value.toString().trim().isNotEmpty) {
      return value.toString();
    }
    return 'Location unavailable';
  }

  String _money(dynamic value) {
    final amount = double.tryParse(value?.toString() ?? '');
    if (amount == null) return 'N/A';
    return '₹${amount.toStringAsFixed(2)}';
  }

  String _distance(dynamic value) {
    final distance = double.tryParse(value?.toString() ?? '');
    if (distance == null) return 'N/A';
    return '${distance.toStringAsFixed(2)} km';
  }

  Widget _buildLocationRow({
    required IconData icon,
    required Color color,
    required String label,
    required String location,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: color, size: 21),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                location,
                style: const TextStyle(
                  color: AppTheme.primary,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRideCard(Map<String, dynamic> ride) {
    final id = _parseId(ride['id'] ?? ride['request_id']);
    final isAccepting = id != null && _acceptingRequestId == id;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const CircleAvatar(
                backgroundColor: AppTheme.secondary,
                child: Icon(
                  Icons.directions_car_rounded,
                  color: AppTheme.primary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Request ${ride['request_number'] ?? '#${ride['id'] ?? ride['request_id'] ?? ''}'}',
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        color: AppTheme.primary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      ride['vehicle_type_name']?.toString() ?? 'Ride request',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.notifications_active_outlined,
                color: AppTheme.primary,
              ),
            ],
          ),
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 18),
            child: Divider(height: 1),
          ),
          _buildLocationRow(
            icon: Icons.trip_origin_rounded,
            color: Colors.green,
            label: 'PICKUP',
            location: _locationText(ride['pickup_details']),
          ),
          const SizedBox(height: 18),
          _buildLocationRow(
            icon: Icons.location_on_rounded,
            color: Colors.redAccent,
            label: 'DROP',
            location: _locationText(ride['drop_details']),
          ),
          const SizedBox(height: 18),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.background,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Estimated fare',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        _money(
                          ride['final_fare'] ??
                              ride['estimated_fare'] ??
                              ride['fare'],
                        ),
                        style: const TextStyle(
                          color: AppTheme.primary,
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 1,
                  height: 40,
                  color: AppTheme.border,
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        'Distance',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        _distance(
                          ride['estimated_distance_km'] ??
                              ride['distance_km'],
                        ),
                        style: const TextStyle(
                          color: AppTheme.primary,
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton.icon(
              onPressed: _acceptingRequestId != null || id == null
                  ? null
                  : () => _acceptRide(ride),
              icon: isAccepting
                  ? const SizedBox(
                      width: 19,
                      height: 19,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.check_circle_outline_rounded),
              label: Text(isAccepting ? 'Accepting...' : 'Accept Ride'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primary,
                foregroundColor: Colors.white,
                disabledBackgroundColor: Colors.grey.shade400,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOfflineState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 112,
              height: 112,
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.wifi_off_rounded,
                size: 54,
                color: Colors.orange,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'You Are Offline',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.primary,
                fontSize: 22,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Please go online from the Driver Dashboard to view available ride requests.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 14,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 20),
            OutlinedButton.icon(
              onPressed: () => _loadRequests(),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Check Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 112,
              height: 112,
              decoration: BoxDecoration(
                color: AppTheme.secondary.withValues(alpha: 0.22),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.route_rounded,
                size: 58,
                color: AppTheme.primary,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'No Ride Requests Yet',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.primary,
                fontSize: 22,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'New ride requests will appear here when they are available for your driver account.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 14,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 20),
            OutlinedButton.icon(
              onPressed: () => _loadRequests(),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Refresh Requests'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.cloud_off_rounded,
              size: 58,
              color: Colors.redAccent,
            ),
            const SizedBox(height: 16),
            const Text(
              'Could Not Load Ride Requests',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: AppTheme.primary,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              _error ?? 'Something went wrong.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () => _loadRequests(),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Ride Requests'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: 'Refresh requests',
            onPressed: _isLoading ? null : () => _loadRequests(),
            icon: const Icon(Icons.refresh_rounded),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: const BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(24),
                ),
              ),
              child: Row(
                children: [
                  const CircleAvatar(
                    radius: 26,
                    backgroundColor: AppTheme.secondary,
                    child: Icon(
                      Icons.directions_car_rounded,
                      color: AppTheme.primary,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Incoming Rides',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 19,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        SizedBox(height: 5),
                        Text(
                          'Find your next trip with NandiRide',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.14),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '${_requests.length} rides',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? _buildErrorState()
                      : _isOffline
                          ? _buildOfflineState()
                          : _requests.isEmpty
                              ? _buildEmptyState()
                              : RefreshIndicator(
                                  onRefresh: () => _loadRequests(
                                    showLoader: false,
                                  ),
                                  child: ListView.builder(
                                    padding: const EdgeInsets.all(18),
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: _requests.length,
                                    itemBuilder: (context, index) =>
                                        _buildRideCard(_requests[index]),
                                  ),
                                ),
            ),
          ],
        ),
      ),
    );
  }
}
