import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';

class MapPickerScreen extends StatefulWidget {
  final String title;
  final double? initialLatitude;
  final double? initialLongitude;

  const MapPickerScreen({
    super.key,
    required this.title,
    this.initialLatitude,
    this.initialLongitude,
  });

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  static const Color navy = Color(0xFF101B3F);
  static const Color gold = Color(0xFFFFC928);
  static const Color red = Color(0xFFE24B58);
  static const Color pageBackground = Color(0xFFF6F7FB);

  late final MapController _mapController;
  late LatLng _selected;
  final TextEditingController _address = TextEditingController();

  bool _mapReady = false;
  bool _loadingAddress = false;
  String? _error;
  int _requestId = 0;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _selected = LatLng(
      widget.initialLatitude ?? 30.7333,
      widget.initialLongitude ?? 76.7794,
    );
    _address.text = _coordinatesAddress(_selected);

    if (widget.initialLatitude != null &&
        widget.initialLongitude != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _reverseGeocode(_selected);
        }
      });
    }
  }

  String _coordinatesAddress(LatLng point) {
    return 'Map location (${point.latitude.toStringAsFixed(6)}, ${point.longitude.toStringAsFixed(6)})';
  }

  Future<void> _selectPoint(LatLng point) async {
    if (!mounted) return;

    setState(() {
      _selected = point;
      _address.text = _coordinatesAddress(point);
      _loadingAddress = true;
      _error = null;
    });

    await _reverseGeocode(point);
  }

  Future<void> _reverseGeocode(LatLng point) async {
    final int requestId = ++_requestId;

    if (!mounted) return;

    setState(() {
      _loadingAddress = true;
      _error = null;
    });

    try {
      final Uri uri = Uri.https(
        'nominatim.openstreetmap.org',
        '/reverse',
        {
          'format': 'jsonv2',
          'lat': point.latitude.toString(),
          'lon': point.longitude.toString(),
          'zoom': '18',
          'addressdetails': '1',
        },
      );

      final http.Response response = await http
          .get(
            uri,
            headers: const {
              'User-Agent': 'NandiRideFlutterApp/1.0',
              'Accept-Language': 'en',
            },
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode != 200) {
        throw Exception('Address lookup failed.');
      }

      final dynamic decoded = jsonDecode(response.body);

      if (decoded is! Map<String, dynamic>) {
        throw Exception('Invalid address response.');
      }

      final String? displayName = decoded['display_name']?.toString();

      if (!mounted || requestId != _requestId) return;

      setState(() {
        if (displayName != null && displayName.trim().isNotEmpty) {
          _address.text = displayName.length > 500
              ? displayName.substring(0, 500)
              : displayName;
        } else {
          _address.text = _coordinatesAddress(point);
          _error = 'Address not found. You can enter it manually.';
        }
        _loadingAddress = false;
      });
    } on TimeoutException {
      if (!mounted || requestId != _requestId) return;
      setState(() {
        _loadingAddress = false;
        _error = 'Address lookup timed out. You can enter the address manually.';
      });
    } catch (_) {
      if (!mounted || requestId != _requestId) return;
      setState(() {
        _loadingAddress = false;
        _error = 'Address lookup unavailable. You can enter the address manually.';
      });
    }
  }

  void _moveToSelected() {
    if (!_mapReady || !mounted) return;
    _mapController.move(_selected, 16);
  }

  void _confirmLocation() {
    final String selectedAddress = _address.text.trim();

    if (selectedAddress.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter an address.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    Navigator.of(context).pop({
      'address': selectedAddress,
      'latitude': _selected.latitude,
      'longitude': _selected.longitude,
    });
  }

  @override
  void dispose() {
    _requestId++;
    _address.dispose();
    _mapController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final double screenHeight = MediaQuery.sizeOf(context).height;

    return Scaffold(
      backgroundColor: pageBackground,
      appBar: AppBar(
        title: Text(
          widget.title,
          style: const TextStyle(
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        backgroundColor: navy,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: 'Center selected location',
            onPressed: _moveToSelected,
            icon: const Icon(Icons.my_location_rounded),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: _selected,
                    initialZoom: 15,
                    minZoom: 3,
                    maxZoom: 20,
                    onMapReady: () {
                      if (mounted) {
                        setState(() {
                          _mapReady = true;
                        });
                      }
                    },
                    onTap: (tapPosition, point) {
                      FocusManager.instance.primaryFocus?.unfocus();
                      _selectPoint(point);
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_3wf8_1_477b9c969e22fe3e205f303d',
                      subdomains: const ['a', 'b', 'c', 'd'],
                      maxZoom: 20,
                      userAgentPackageName: 'com.nandiride.app',
                    ),
                    MarkerLayer(
                      markers: [
                        Marker(
                          point: _selected,
                          width: 56,
                          height: 60,
                          alignment: Alignment.topCenter,
                          child: const Icon(
                            Icons.location_pin,
                            size: 52,
                            color: red,
                          ),
                        ),
                      ],
                    ),
                    RichAttributionWidget(
                      attributions: [
                        TextSourceAttribution(
                          '© OpenStreetMap contributors',
                        ),
                        TextSourceAttribution('© CARTO'),
                      ],
                    ),
                  ],
                ),
                Positioned(
                  top: 14,
                  left: 14,
                  right: 14,
                  child: IgnorePointer(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 11,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.96),
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x18000000),
                            blurRadius: 12,
                            offset: Offset(0, 3),
                          ),
                        ],
                      ),
                      child: const Row(
                        children: [
                          Icon(
                            Icons.touch_app_rounded,
                            color: navy,
                            size: 22,
                          ),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Tap on the map to select your location',
                              style: TextStyle(
                                color: navy,
                                fontWeight: FontWeight.w700,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                Positioned(
                  right: 14,
                  bottom: 14,
                  child: Material(
                    color: Colors.white,
                    elevation: 3,
                    borderRadius: BorderRadius.circular(14),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(14),
                      onTap: _moveToSelected,
                      child: const Padding(
                        padding: EdgeInsets.all(13),
                        child: Icon(
                          Icons.center_focus_strong_rounded,
                          color: navy,
                          size: 24,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            constraints: BoxConstraints(
              maxHeight: screenHeight * 0.48,
            ),
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(
                top: Radius.circular(22),
              ),
              boxShadow: [
                BoxShadow(
                  color: Color(0x18000000),
                  blurRadius: 16,
                  offset: Offset(0, -4),
                ),
              ],
            ),
            child: SafeArea(
              top: false,
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 42,
                          height: 42,
                          decoration: BoxDecoration(
                            color: gold.withValues(alpha: 0.22),
                            borderRadius: BorderRadius.circular(13),
                          ),
                          child: const Icon(
                            Icons.location_on_rounded,
                            color: navy,
                            size: 24,
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Select your location',
                                style: TextStyle(
                                  fontSize: 17,
                                  fontWeight: FontWeight.w900,
                                  color: navy,
                                ),
                              ),
                              SizedBox(height: 3),
                              Text(
                                'Move the pin by tapping anywhere on the map.',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.black54,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: _address,
                      maxLines: 2,
                      minLines: 2,
                      maxLength: 500,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: InputDecoration(
                        hintText: 'Enter house, street or landmark',
                        prefixIcon: const Icon(
                          Icons.edit_location_alt_rounded,
                          color: navy,
                        ),
                        filled: true,
                        fillColor: const Color(0xFFF7F8FC),
                        counterText: '',
                        contentPadding: const EdgeInsets.all(14),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(13),
                          borderSide: const BorderSide(
                            color: Color(0xFFE0E4ED),
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(13),
                          borderSide: const BorderSide(
                            color: Color(0xFFE0E4ED),
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(13),
                          borderSide: const BorderSide(
                            color: gold,
                            width: 1.8,
                          ),
                        ),
                      ),
                    ),
                    if (_loadingAddress) ...[
                      const SizedBox(height: 6),
                      const LinearProgressIndicator(
                        color: gold,
                        minHeight: 3,
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Finding address...',
                        style: TextStyle(
                          color: Colors.black54,
                          fontSize: 12,
                        ),
                      ),
                    ],
                    if (_error != null) ...[
                      const SizedBox(height: 6),
                      Text(
                        _error!,
                        style: const TextStyle(
                          color: Colors.red,
                          fontSize: 12,
                        ),
                      ),
                    ],
                    const SizedBox(height: 10),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF7F8FC),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.my_location_rounded,
                            size: 18,
                            color: navy,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Lat: ${_selected.latitude.toStringAsFixed(6)}\nLng: ${_selected.longitude.toStringAsFixed(6)}',
                              style: const TextStyle(
                                fontSize: 11,
                                height: 1.5,
                                color: Colors.black87,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          IconButton(
                            tooltip: 'Center selected location',
                            onPressed: _moveToSelected,
                            icon: const Icon(
                              Icons.center_focus_strong_rounded,
                              color: navy,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: gold,
                          foregroundColor: navy,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(13),
                          ),
                        ),
                        onPressed: _confirmLocation,
                        icon: const Icon(Icons.check_circle_rounded),
                        label: const Text(
                          'Confirm location',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}