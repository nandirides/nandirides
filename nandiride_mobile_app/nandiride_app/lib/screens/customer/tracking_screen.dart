import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../app/app_theme.dart';

class TrackingScreen extends StatelessWidget {
  const TrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Track Your Ride')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            height: 200,
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.location_searching,
                  size: 64,
                  color: AppTheme.primary,
                ),
                SizedBox(height: 12),
                Text('Map will appear here'),
                Text(
                  'Google Maps integration pending',
                  style: TextStyle(color: Colors.black54),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Ride Status',
            style: TextStyle(fontSize: 23, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const ListTile(
            leading: Icon(Icons.check_circle, color: Colors.green),
            title: Text('Booking submitted'),
            subtitle: Text('Demo status'),
          ),
          const ListTile(
            leading: Icon(Icons.hourglass_empty, color: Colors.orange),
            title: Text('Finding a driver'),
            subtitle: Text('Driver matching is not connected'),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            },
            child: const Text('Back to Home'),
          ),
        ],
      ),
    );
  }
}
