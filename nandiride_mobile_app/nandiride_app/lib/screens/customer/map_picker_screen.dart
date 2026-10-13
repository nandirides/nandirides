
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
  static const navy = Color(0xFF101B3F);
  static const gold = Color(0xFFFFC928);

  late final MapController _mapController;
  late LatLng _selected;
  final TextEditingController _address = TextEditingController();

  bool _loadingAddress = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _selected = LatLng(
      widget.initialLatitude ?? 30.7333,
      widget.initialLongitude ?? 76.7794,
    );
    _address.text = _coordinatesAddress(_selected);
    if (widget.initialLatitude != null && widget.initialLongitude != null) {
      _reverseGeocode(_selected);
    }
  }

  String _coordinatesAddress(LatLng point) =>
      'Map location (${point.latitude.toStringAsFixed(6)}, ${point.longitude.toStringAsFixed(6)})';

  Future<void> _selectPoint(LatLng point) async {
    setState(() {
      _selected = point;
      _loadingAddress = true;
      _error = null;
      _address.text = _coordinatesAddress(point);
    });
    await _reverseGeocode(point);
  }

  Future<void> _reverseGeocode(LatLng point) async {
    if (mounted) {
      setState(() {
        _loadingAddress = true;
        _error = null;
      });
    }

    try {
      final uri = Uri.https(
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

      final response = await http.get(
        uri,
        headers: const {
          'User-Agent': 'NandiRideFlutterApp/1.0',
          'Accept-Language': 'en',
        },
      ).timeout(const Duration(seconds: 12));

      if (response.statusCode != 200) {
        throw Exception('Address lookup failed. You can enter the address manually.');
      }

      final body = jsonDecode(response.body) as Map<String, dynamic>;
      final displayName = body['display_name']?.toString();

      if (!mounted) return;
      setState(() {
        if (displayName != null && displayName.isNotEmpty) {
          _address.text = displayName.length > 500
              ? displayName.substring(0, 500)
              : displayName;
        }
        _loadingAddress = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loadingAddress = false;
        _error = 'Address lookup unavailable. Enter the address below.';
      });
    }
  }

  @override
  void dispose() {
    _address.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        backgroundColor: navy,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: _selected,
                initialZoom: 14,
                onTap: (_, point) => _selectPoint(point),
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.nandiride.app',
                ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: _selected,
                      width: 52,
                      height: 52,
                      child: const Icon(
                        Icons.location_pin,
                        size: 48,
                        color: Color(0xFFE24B58),
                      ),
                    ),
                  ],
                ),
                RichAttributionWidget(
                  attributions: [
                    TextSourceAttribution(
                      'OpenStreetMap contributors',
                      onTap: () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
            ),
            child: SafeArea(
              top: false,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Selected address',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: navy,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _address,
                    maxLines: 2,
                    maxLength: 500,
                    decoration: InputDecoration(
                      hintText: 'Enter house, street or landmark',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                  if (_loadingAddress)
                    const LinearProgressIndicator(color: gold),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 6, bottom: 8),
                      child: Text(
                        _error!,
                        style: const TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                  Text(
                    'Lat: ${_selected.latitude.toStringAsFixed(6)}  '
                    'Lng: ${_selected.longitude.toStringAsFixed(6)}',
                    style: const TextStyle(fontSize: 12, color: Colors.black54),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: gold,
                        foregroundColor: navy,
                      ),
                      onPressed: () {
                        final address = _address.text.trim();
                        if (address.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Please enter an address.')),
                          );
                          return;
                        }
                        Navigator.pop(context, {
                          'address': address,
                          'latitude': _selected.latitude,
                          'longitude': _selected.longitude,
                        });
                      },
                      child: const Text(
                        'Confirm location',
                        style: TextStyle(fontWeight: FontWeight.w900),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
