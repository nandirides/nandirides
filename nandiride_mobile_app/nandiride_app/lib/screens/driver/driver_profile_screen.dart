import 'package:flutter/material.dart';

import '../../app/app_theme.dart';

class DriverProfileScreen extends StatelessWidget {
  const DriverProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Profile'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const CircleAvatar(radius: 45, child: Icon(Icons.person, size: 50)),
          const SizedBox(height: 14),
          const Text(
            'Driver Name',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text('Demo Driver Account', textAlign: TextAlign.center),
          const SizedBox(height: 24),
          const Card(
            child: ListTile(
              leading: Icon(Icons.verified_user),
              title: Text('Verification Status'),
              subtitle: Text('Pending — Demo Data'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.two_wheeler),
              title: Text('Vehicle Type'),
              subtitle: Text('Bike — Sample'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.confirmation_number),
              title: Text('Vehicle Number'),
              subtitle: Text('Not added'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.badge),
              title: Text('Driving Licence'),
              subtitle: Text('Not added'),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Real driver details and verification status will '
            'come from Django after API integration.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Go Back'),
          ),
        ],
      ),
    );
  }
}
