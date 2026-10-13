import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../app/app_theme.dart';

class DriverHomeScreen extends StatelessWidget {
  const DriverHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NandiRide Driver'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            tooltip: 'Driver Profile',
            onPressed: () {
              Navigator.pushNamed(context, AppRoutes.driverProfile);
            },
            icon: const Icon(Icons.account_circle),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Namaste, Driver!',
            style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text('Welcome to your NandiRide dashboard.'),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Today\'s Earnings'),
                  const SizedBox(height: 8),
                  const Text(
                    '₹0.00',
                    style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                  ),
                  const Text('Demo amount — API not connected'),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.earnings);
                    },
                    child: const Text('View Earnings'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          _menuTile(
            context,
            icon: Icons.notifications_active,
            title: 'Ride Requests',
            subtitle: 'View available ride requests',
            route: AppRoutes.rideRequests,
          ),
          _menuTile(
            context,
            icon: Icons.route,
            title: 'Trip Details',
            subtitle: 'View trip information',
            route: AppRoutes.tripDetails,
          ),
          _menuTile(
            context,
            icon: Icons.account_circle,
            title: 'Driver Profile',
            subtitle: 'Profile and vehicle information',
            route: AppRoutes.driverProfile,
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            },
            icon: const Icon(Icons.person),
            label: const Text('Switch to Customer Demo'),
          ),
        ],
      ),
    );
  }

  Widget _menuTile(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required String route,
  }) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primary, size: 30),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: () => Navigator.pushNamed(context, route),
      ),
    );
  }
}
