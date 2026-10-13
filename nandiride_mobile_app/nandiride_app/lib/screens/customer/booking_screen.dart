import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../widgets/app_button.dart';

class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _pickupController = TextEditingController();
  final _dropController = TextEditingController();

  String _vehicle = 'Bike';

  @override
  void dispose() {
    _pickupController.dispose();
    _dropController.dispose();
    super.dispose();
  }

  void _confirmBooking() {
    if (!_formKey.currentState!.validate()) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Demo booking submitted. Backend is not connected yet.'),
      ),
    );

    Navigator.pushNamed(context, AppRoutes.tracking);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Book a Ride')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Text(
              'Enter your route',
              style: TextStyle(fontSize: 23, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 18),

            TextFormField(
              controller: _pickupController,
              decoration: const InputDecoration(
                labelText: 'Pickup location',
                hintText: 'Example: Haridwar Railway Station',
                prefixIcon: Icon(Icons.my_location),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Enter pickup location';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _dropController,
              decoration: const InputDecoration(
                labelText: 'Drop location',
                hintText: 'Example: Har Ki Pauri',
                prefixIcon: Icon(Icons.location_on_outlined),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Enter drop location';
                }
                if (value.trim().toLowerCase() ==
                    _pickupController.text.trim().toLowerCase()) {
                  return 'Pickup and drop must be different';
                }
                return null;
              },
            ),
            const SizedBox(height: 24),

            const Text(
              'Choose your vehicle',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),

            RadioListTile<String>(
              value: 'Bike',
              groupValue: _vehicle,
              title: const Text('Bike'),
              subtitle: const Text('Two-wheeler ride'),
              secondary: const Icon(Icons.two_wheeler),
              onChanged: (value) {
                setState(() => _vehicle = value!);
              },
            ),
            RadioListTile<String>(
              value: 'Auto',
              groupValue: _vehicle,
              title: const Text('Auto'),
              subtitle: const Text('Auto-rickshaw ride'),
              secondary: const Icon(Icons.electric_rickshaw),
              onChanged: (value) {
                setState(() => _vehicle = value!);
              },
            ),
            RadioListTile<String>(
              value: 'Cab',
              groupValue: _vehicle,
              title: const Text('Cab'),
              subtitle: const Text('Car ride'),
              secondary: const Icon(Icons.local_taxi),
              onChanged: (value) {
                setState(() => _vehicle = value!);
              },
            ),

            const SizedBox(height: 22),

            AppButton(
              label: 'Confirm Demo Booking',
              icon: Icons.check_circle_outline,
              onPressed: _confirmBooking,
            ),

            const SizedBox(height: 12),
            const Text(
              'Demo only: no driver will be assigned and no real ride will be booked.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.black54, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}
