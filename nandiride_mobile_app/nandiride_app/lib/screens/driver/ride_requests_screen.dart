import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../app/app_theme.dart';

class RideRequestsScreen extends StatelessWidget {
  const RideRequestsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ride Requests'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.directions_car_outlined,
                size: 80,
                color: AppTheme.primary,
              ),
              const SizedBox(height: 20),
              const Text(
                'No Ride Requests Yet',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 10),
              const Text(
                'Live ride requests will appear here after '
                'the Django API is connected.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: () {
                  Navigator.pushNamed(context, AppRoutes.tripDetails);
                },
                child: const Text('Open Demo Trip'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
