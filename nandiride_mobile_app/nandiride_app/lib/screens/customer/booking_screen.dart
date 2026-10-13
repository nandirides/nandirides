
import 'package:flutter/material.dart';
import '../../services/booking_service.dart';

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

  final _pickupAddress = TextEditingController();
  final _dropAddress = TextEditingController();
  final _coupon = TextEditingController();

  bool _loading = true;
  bool _estimating = false;
  bool _booking = false;
  bool _manualPickup = false;
  bool _manualDrop = false;
  bool _couponApplied = false;

  String? _error;
  String? _couponMessage;
  String _paymentMethod = 'cash';

  List<Map<String, dynamic>> _locations = [];
  List<Map<String, dynamic>> _vehicles = [];

  int? _pickupId;
  int? _dropId;
  int? _vehicleId;

  Map<String, dynamic>? _fare;
  Map<String, dynamic>? _bookingResult;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _pickupAddress.dispose();
    _dropAddress.dispose();
    _coupon.dispose();
    super.dispose();
  }

  List<Map<String, dynamic>> _list(Map<String, dynamic> response) {
    dynamic data = response['results'] ?? response['data'] ?? [];
    if (data is Map) {
      data = data['results'] ?? data['data'] ?? [];
    }
    if (data is! List) return [];
    return data.whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e)).toList();
  }

  int? _int(dynamic value) {
    if (value is int) return value;
    return int.tryParse(value?.toString() ?? '');
  }

  String _locationName(Map<String, dynamic> item) {
    final address = item['address']?.toString() ?? '';
    final city = item['city_name']?.toString() ??
        (item['city'] is Map
            ? item['city']['name']?.toString() ?? ''
            : '');
    if (address.isNotEmpty && city.isNotEmpty) return '$address, $city';
    if (address.isNotEmpty) return address;
    return 'Location #${item['id']}';
  }

  String _money(dynamic value) {
    final amount = double.tryParse(value?.toString() ?? '');
    return amount == null ? '—' : '₹${amount.toStringAsFixed(2)}';
  }

  dynamic _total(Map<String, dynamic> fare) =>
      fare['final_fare'] ??
      fare['subtotal'] ??
      fare['estimated_fare'] ??
      fare['total_fare'];

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
    _bookingResult = null;
    _couponApplied = false;
    _couponMessage = null;
  }

  Future<void> _loadData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final responses = await Future.wait([
        BookingService.getLocations(),
        BookingService.getVehicleTypes(),
      ]);
      final locations = _list(responses[0]);
      final vehicles = _list(responses[1]);

      if (!mounted) return;

      final args = ModalRoute.of(context)?.settings.arguments;
      final arguments = args is Map ? args : <dynamic, dynamic>{};
      final pickup = arguments['pickup']?.toString().toLowerCase() ?? '';
      final drop = arguments['drop']?.toString().toLowerCase() ?? '';
      final rideType = arguments['rideType']?.toString().toLowerCase() ?? '';

      int? pickupId;
      int? dropId;
      int? vehicleId;

      for (final item in locations) {
        final id = _int(item['id']);
        final name = _locationName(item).toLowerCase();

        if (id != null && pickup.isNotEmpty &&
            (name.contains(pickup) || pickup.contains(name))) {
          pickupId = id;
        }
        if (id != null && drop.isNotEmpty &&
            (name.contains(drop) || drop.contains(name))) {
          dropId = id;
        }
      }

      for (final item in vehicles) {
        final id = _int(item['id']);
        final name =
            '${item['name'] ?? ''} ${item['code'] ?? ''}'.toLowerCase();
        if (id != null && rideType.isNotEmpty && name.contains(rideType)) {
          vehicleId = id;
          break;
        }
      }

      setState(() {
        _locations = locations;
        _vehicles = vehicles;
        _pickupId = pickupId;
        _dropId = dropId;
        _vehicleId = vehicleId;
        _loading = false;

        if (locations.isEmpty) {
          _error = 'No saved locations found. Check your Django API.';
        } else if (vehicles.isEmpty) {
          _error = 'No active vehicle types found.';
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> _estimateFare({bool coupon = false}) async {
    FocusScope.of(context).unfocus();

    if (_manualPickup || _manualDrop) {
      _message(
        'Your current Django API requires saved location IDs. '
        'Manual addresses cannot be estimated until the backend is updated.',
        error: true,
      );
      return;
    }

    if (_pickupId == null || _dropId == null || _vehicleId == null) {
      _message('Please select pickup, drop and vehicle.', error: true);
      return;
    }

    if (_pickupId == _dropId) {
      _message('Pickup and drop must be different.', error: true);
      return;
    }

    setState(() {
      _estimating = true;
      _bookingResult = null;
      if (!coupon) {
        _fare = null;
        _couponApplied = false;
        _couponMessage = null;
      }
    });

    try {
      final result = await BookingService.estimateFare(
        pickupLocationId: _pickupId!,
        dropLocationId: _dropId!,
        vehicleTypeId: _vehicleId!,
        couponCode: _coupon.text.trim(),
      );

      if (!mounted) return;
      setState(() {
        _fare = result;
        _estimating = false;
        _couponApplied = coupon && _coupon.text.trim().isNotEmpty;
        _couponMessage = _couponApplied
            ? (result['coupon_message']?.toString() ??
                'Coupon checked by server.')
            : null;
      });

      _message('Fare estimate updated.');
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _estimating = false;
        if (coupon) {
          _couponApplied = false;
          _couponMessage = e.toString().replaceFirst('Exception: ', '');
        }
      });
      _message(e.toString().replaceFirst('Exception: ', ''), error: true);
    }
  }

  Future<void> _bookRide() async {
    if (_manualPickup || _manualDrop) {
      _message(
        'Manual addresses cannot be saved by the current ride API. '
        'Select saved locations to continue.',
        error: true,
      );
      return;
    }

    if (_pickupId == null || _dropId == null || _vehicleId == null) {
      _message('Please select all booking details.', error: true);
      return;
    }

    if (_pickupId == _dropId) {
      _message('Pickup and drop must be different.', error: true);
      return;
    }

    if (_fare == null) {
      _message('Estimate the fare first.', error: true);
      return;
    }

    final confirmed = await _paymentDialog();
    if (confirmed != true || !mounted) return;

    setState(() {
      _booking = true;
      _bookingResult = null;
    });

    try {
      final result = await BookingService.createRideRequest(
        pickupLocationId: _pickupId!,
        dropLocationId: _dropId!,
        vehicleTypeId: _vehicleId!,
        couponId: _int(_fare?['coupon_id'] ?? _fare?['coupon']),
      );

      if (!mounted) return;
      setState(() {
        _booking = false;
        _bookingResult = result;
      });
      _successDialog(result);
    } catch (e) {
      if (!mounted) return;
      setState(() => _booking = false);
      _message(e.toString().replaceFirst('Exception: ', ''), error: true);
    }
  }

  Future<bool?> _paymentDialog() {
    String selected = _paymentMethod;

    return showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
          ),
          title: const Text(
            'Choose payment method',
            style: TextStyle(color: navy, fontWeight: FontWeight.w900),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _paymentOption('cash', 'Cash', Icons.payments_rounded,
                  selected, (v) => setDialogState(() => selected = v)),
              _paymentOption('upi', 'UPI', Icons.qr_code_rounded,
                  selected, (v) => setDialogState(() => selected = v)),
              _paymentOption('card', 'Credit / Debit Card',
                  Icons.credit_card_rounded, selected,
                  (v) => setDialogState(() => selected = v)),
              _paymentOption('netbanking', 'Net Banking',
                  Icons.account_balance_rounded, selected,
                  (v) => setDialogState(() => selected = v)),
              const SizedBox(height: 8),
              const Text(
                'Payment selection is not yet sent to Django. '
                'Real payments require backend integration.',
                style: TextStyle(color: muted, fontSize: 11),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: gold,
                foregroundColor: navy,
              ),
              onPressed: () {
                setState(() => _paymentMethod = selected);
                Navigator.pop(dialogContext, true);
              },
              child: const Text('Confirm ride'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _paymentOption(
    String value,
    String label,
    IconData icon,
    String selected,
    ValueChanged<String> onChanged,
  ) {
    final active = value == selected;

    return InkWell(
      onTap: () => onChanged(value),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        margin: const EdgeInsets.only(bottom: 7),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: active ? const Color(0xFFFFF7D9) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: active ? gold : const Color(0xFFE5E9F1),
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: navy),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                  color: navy,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            Icon(
              active
                  ? Icons.radio_button_checked
                  : Icons.radio_button_off,
              color: active ? navy : muted,
            ),
          ],
        ),
      ),
    );
  }

  String _paymentLabel() {
    switch (_paymentMethod) {
      case 'upi':
        return 'UPI';
      case 'card':
        return 'Card';
      case 'netbanking':
        return 'Net Banking';
      default:
        return 'Cash';
    }
  }

  void _successDialog(Map<String, dynamic> result) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        icon: const Icon(
          Icons.check_circle_rounded,
          color: green,
          size: 56,
        ),
        title: const Text(
          'Ride Request Sent!',
          textAlign: TextAlign.center,
          style: TextStyle(color: navy, fontWeight: FontWeight.w900),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Your ride request has been submitted.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            _resultRow(
              'Request number',
              result['request_number']?.toString() ?? '—',
            ),
            _resultRow('Status', result['status']?.toString() ?? '—'),
            _resultRow('Estimated fare', _money(
              result['final_fare'] ??
                  result['estimated_fare'] ??
                  _total(_fare ?? {}),
            )),
            _resultRow('Selected payment', _paymentLabel()),
          ],
        ),
        actions: [
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: navy,
                foregroundColor: gold,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              onPressed: () {
                Navigator.pop(dialogContext);
                if (Navigator.canPop(context)) Navigator.pop(context);
              },
              child: const Text(
                'Done',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _resultRow(String label, String value) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Row(
          children: [
            Expanded(
              child: Text(label,
                  style: const TextStyle(color: muted, fontSize: 12)),
            ),
            Flexible(
              child: Text(
                value,
                textAlign: TextAlign.end,
                style: const TextStyle(
                  color: navy,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),
      );

  Widget _sectionTitle(String title, String subtitle) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: navy,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 4),
          Text(subtitle,
              style: const TextStyle(color: muted, fontSize: 12)),
        ],
      );

  Widget _header() => Container(
        padding: const EdgeInsets.fromLTRB(20, 14, 16, 22),
        decoration: const BoxDecoration(
          color: navy,
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
        ),
        child: SafeArea(
          bottom: false,
          child: Row(
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: gold,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Icon(
                  Icons.electric_bike_rounded,
                  color: navy,
                  size: 28,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'NandiRide',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'YOUR RIDE, YOUR WAY',
                      style: TextStyle(
                        color: gold,
                        fontSize: 9,
                        letterSpacing: 1.7,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: _loading ? null : _loadData,
                icon: const Icon(Icons.refresh_rounded, color: Colors.white),
              ),
            ],
          ),
        ),
      );

  Widget _locationDropdown({
    required String label,
    required String hint,
    required IconData icon,
    required Color iconColor,
    required int? value,
    required ValueChanged<int?> onChanged,
  }) {
    final validId =
        _locations.any((e) => _int(e['id']) == value) ? value : null;

    return Row(
      children: [
        Icon(icon, color: iconColor, size: 23),
        const SizedBox(width: 12),
        Expanded(
          child: DropdownButtonFormField<int>(
            value: validId,
            isExpanded: true,
            decoration: InputDecoration(
              labelText: label,
              hintText: hint,
              labelStyle: const TextStyle(
                color: muted,
                fontSize: 10,
                fontWeight: FontWeight.w800,
              ),
              border: InputBorder.none,
            ),
            items: _locations.map((item) {
              final id = _int(item['id']);
              return DropdownMenuItem<int>(
                value: id,
                child: Text(
                  _locationName(item),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: navy,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              );
            }).where((item) => item.value != null).toList(),
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  Widget _manualAddress({
    required String label,
    required bool value,
    required TextEditingController controller,
    required ValueChanged<bool> onChanged,
  }) =>
      Column(
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: () => onChanged(!value),
              icon: Icon(
                value
                    ? Icons.list_alt_rounded
                    : Icons.edit_location_alt_rounded,
                size: 17,
              ),
              label: Text(
                value ? 'Choose saved location instead' : label,
                style: const TextStyle(fontSize: 11),
              ),
              style: TextButton.styleFrom(foregroundColor: navy),
            ),
          ),
          if (value)
            TextField(
              controller: controller,
              textCapitalization: TextCapitalization.words,
              maxLines: 2,
              decoration: InputDecoration(
                hintText: 'House, street, landmark and city',
                prefixIcon: const Icon(Icons.location_on_outlined),
                filled: true,
                fillColor: background,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(13),
                  borderSide: BorderSide.none,
                ),
              ),
              onChanged: (_) => setState(_invalidateFare),
            ),
        ],
      );

  Widget _locationCard() => Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: const Color(0xFFE8ECF4)),
          boxShadow: [
            BoxShadow(
              color: navy.withValues(alpha: 0.04),
              blurRadius: 18,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          children: [
            _locationDropdown(
              label: 'PICKUP LOCATION',
              hint: 'Where should we pick you up?',
              icon: Icons.my_location_rounded,
              iconColor: green,
              value: _pickupId,
              onChanged: (v) => setState(() {
                _pickupId = v;
                _manualPickup = false;
                _invalidateFare();
              }),
            ),
            _manualAddress(
              label: 'Enter pickup address manually',
              value: _manualPickup,
              controller: _pickupAddress,
              onChanged: (v) => setState(() {
                _manualPickup = v;
                if (v) _pickupId = null;
                _invalidateFare();
              }),
            ),
            Row(
              children: [
                const Expanded(child: Divider()),
                IconButton(
                  tooltip: 'Swap pickup and drop',
                  onPressed: () => setState(() {
                    final oldId = _pickupId;
                    _pickupId = _dropId;
                    _dropId = oldId;

                    final oldText = _pickupAddress.text;
                    _pickupAddress.text = _dropAddress.text;
                    _dropAddress.text = oldText;

                    final oldManual = _manualPickup;
                    _manualPickup = _manualDrop;
                    _manualDrop = oldManual;
                    _invalidateFare();
                  }),
                  icon: const Icon(Icons.swap_vert_rounded, color: navy),
                ),
                const Expanded(child: Divider()),
              ],
            ),
            _locationDropdown(
              label: 'DROP LOCATION',
              hint: 'Where do you want to go?',
              icon: Icons.location_on_rounded,
              iconColor: red,
              value: _dropId,
              onChanged: (v) => setState(() {
                _dropId = v;
                _manualDrop = false;
                _invalidateFare();
              }),
            ),
            _manualAddress(
              label: 'Enter drop address manually',
              value: _manualDrop,
              controller: _dropAddress,
              onChanged: (v) => setState(() {
                _manualDrop = v;
                if (v) _dropId = null;
                _invalidateFare();
              }),
            ),
            const SizedBox(height: 8),
            const Text(
              'Note: manual addresses need backend support before they can be booked.',
              style: TextStyle(color: muted, fontSize: 11),
            ),
          ],
        ),
      );

  IconData _vehicleIcon(Map<String, dynamic> vehicle) {
    final name =
        '${vehicle['name'] ?? ''} ${vehicle['code'] ?? ''}'.toLowerCase();
    if (name.contains('bike') || name.contains('scooter')) {
      return Icons.two_wheeler_rounded;
    }
    if (name.contains('auto') || name.contains('rickshaw')) {
      return Icons.electric_rickshaw_rounded;
    }
    if (name.contains('cab') || name.contains('car')) {
      return Icons.local_taxi_rounded;
    }
    return Icons.directions_car_rounded;
  }

  Widget _vehiclesSection() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle('Choose your ride', 'Select a vehicle for your journey'),
          const SizedBox(height: 14),
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
                      borderRadius: BorderRadius.circular(18),
                      onTap: () => setState(() {
                        _vehicleId = id;
                        _invalidateFare();
                      }),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 180),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 5,
                          vertical: 15,
                        ),
                        decoration: BoxDecoration(
                          color: selected ? navy : Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(
                            color: selected ? gold : const Color(0xFFE4E9F2),
                            width: selected ? 2 : 1,
                          ),
                        ),
                        child: Column(
                          children: [
                            Icon(
                              _vehicleIcon(vehicle),
                              size: 30,
                              color: selected ? gold : navy,
                            ),
                            const SizedBox(height: 9),
                            Text(
                              vehicle['name']?.toString() ?? 'Vehicle',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: selected ? Colors.white : navy,
                                fontSize: 12,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 7),
                            Text(
                              _money(vehicle['base_fare']),
                              style: TextStyle(
                                color: selected ? gold : navy,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            const SizedBox(height: 7),
                            Icon(
                              selected
                                  ? Icons.check_circle
                                  : Icons.circle_outlined,
                              size: 17,
                              color: selected ? gold : muted,
                            ),
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

  Widget _couponCard() => Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFE8ECF4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.local_offer_rounded, color: green),
                SizedBox(width: 8),
                Text(
                  'Apply coupon',
                  style: TextStyle(
                    color: navy,
                    fontSize: 15,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _coupon,
                    enabled: !_couponApplied,
                    textCapitalization: TextCapitalization.characters,
                    decoration: InputDecoration(
                      hintText: 'Enter coupon code',
                      filled: true,
                      fillColor: background,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (_) => setState(() {
                      _fare = null;
                      _couponApplied = false;
                      _couponMessage = null;
                    }),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _estimating
                      ? null
                      : () {
                          if (_couponApplied) {
                            setState(() {
                              _coupon.clear();
                              _couponApplied = false;
                              _couponMessage = null;
                              _fare = null;
                            });
                          } else {
                            _estimateFare(coupon: true);
                          }
                        },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _couponApplied ? red : navy,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 15,
                    ),
                  ),
                  child: Text(_couponApplied ? 'Remove' : 'Apply'),
                ),
              ],
            ),
            if (_couponMessage != null) ...[
              const SizedBox(height: 8),
              Text(
                _couponMessage!,
                style: TextStyle(
                  color: _couponApplied ? green : red,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
      );

  Widget _fareCard() {
    final fare = _fare;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE8ECF4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.receipt_long_rounded, color: navy, size: 27),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Fare summary',
                  style: TextStyle(
                    color: navy,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (_estimating)
            const Center(
              child: CircularProgressIndicator(color: navy),
            )
          else if (fare == null)
            const Text(
              'Select your locations and vehicle, then estimate your fare.',
              style: TextStyle(color: muted, fontSize: 12),
            )
          else ...[
            _fareRow('Base fare', fare['base_fare']),
            _fareRow('Distance fare', fare['distance_fare']),
            _fareRow('Time fare', fare['time_fare']),
            _fareRow('Discount', fare['discount']),
            const Divider(height: 24),
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Estimated total',
                    style: TextStyle(
                      color: navy,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Text(
                  _money(_total(fare)),
                  style: const TextStyle(
                    color: navy,
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              'Distance: ${fare['distance_km'] ?? '—'} km   '
              'Duration: ${fare['duration_minutes'] ?? '—'} min',
              style: const TextStyle(color: muted, fontSize: 11),
            ),
          ],
        ],
      ),
    );
  }

  Widget _fareRow(String label, dynamic value) {
    if (value == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Expanded(
            child: Text(label, style: const TextStyle(color: muted)),
          ),
          Text(
            _money(value),
            style: const TextStyle(
              color: navy,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _errorView() => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline_rounded, size: 48, color: navy),
              const SizedBox(height: 14),
              Text(
                _error ?? 'Unable to load booking details.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh),
                label: const Text('Try again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: navy,
                  foregroundColor: gold,
                ),
              ),
            ],
          ),
        ),
      );

  Widget _bottomButton() => SafeArea(
        top: false,
        child: Container(
          padding: const EdgeInsets.fromLTRB(18, 12, 18, 14),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: navy.withValues(alpha: 0.08),
                blurRadius: 18,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ESTIMATED FARE',
                      style: TextStyle(
                        color: muted,
                        fontSize: 9,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _fare == null ? '—' : _money(_total(_fare!)),
                      style: const TextStyle(
                        color: navy,
                        fontSize: 19,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                flex: 2,
                child: SizedBox(
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _booking || _estimating
                        ? null
                        : _fare == null
                            ? _estimateFare
                            : _bookRide,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: gold,
                      foregroundColor: navy,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: _booking || _estimating
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: navy,
                            ),
                          )
                        : Text(
                            _fare == null ? 'Estimate Fare' : 'Confirm Ride',
                            style: const TextStyle(
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                  ),
                ),
              ),
            ],
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: navy))
          : _error != null
              ? _errorView()
              : SafeArea(
                  bottom: false,
                  child: CustomScrollView(
                    physics: const BouncingScrollPhysics(),
                    slivers: [
                      SliverToBoxAdapter(child: _header()),
                      SliverPadding(
                        padding: const EdgeInsets.fromLTRB(18, 20, 18, 24),
                        sliver: SliverList(
                          delegate: SliverChildListDelegate([
                            const Text(
                              'Almost there! 👋',
                              style: TextStyle(
                                color: muted,
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Plan your journey',
                              style: TextStyle(
                                color: navy,
                                fontSize: 26,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            const SizedBox(height: 5),
                            const Text(
                              'Choose locations, vehicle and fare.',
                              style: TextStyle(color: muted, fontSize: 13),
                            ),
                            const SizedBox(height: 20),
                            _locationCard(),
                            const SizedBox(height: 24),
                            _vehiclesSection(),
                            const SizedBox(height: 22),
                            _couponCard(),
                            const SizedBox(height: 18),
                            _fareCard(),
                            const SizedBox(height: 24),
                          ]),
                        ),
                      ),
                    ],
                  ),
                ),
      bottomNavigationBar: _loading || _error != null ? null : _bottomButton(),
    );
  }
}
