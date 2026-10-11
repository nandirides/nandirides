import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../app/app_theme.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NandiRide'),
        actions: [
          IconButton(
            tooltip: 'Profile',
            onPressed: () {
              Navigator.pushNamed(context, AppRoutes.profile);
            },
            icon: const Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Namaste! 👋',
            style: TextStyle(fontSize: 16, color: Colors.black54),
          ),
          const SizedBox(height: 6),
          const Text(
            'Where would you like to go?',
            style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 22),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.black12),
            ),
            child: const Column(
              children: [
                Row(
                  children: [
                    Icon(Icons.my_location, color: AppTheme.primary),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('PICKUP LOCATION'),
                          SizedBox(height: 4),
                          Text(
                            'Choose your pickup point',
                            style: TextStyle(color: Colors.black54),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                Padding(
                  padding: EdgeInsets.symmetric(vertical: 14),
                  child: Divider(),
                ),
                Row(
                  children: [
                    Icon(Icons.location_on, color: Colors.red),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('DROP LOCATION'),
                          SizedBox(height: 4),
                          Text(
                            'Where are you going?',
                            style: TextStyle(color: Colors.black54),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 18),

          SizedBox(
            height: 52,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.pushNamed(context, AppRoutes.booking);
              },
              icon: const Icon(Icons.directions_car),
              label: const Text('Book a Ride'),
            ),
          ),

          const SizedBox(height: 22),
          const Text(
            'Your rides',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),

          _HomeTile(
            icon: Icons.route,
            title: 'Track current ride',
            onTap: () => Navigator.pushNamed(context, AppRoutes.tracking),
          ),
          _HomeTile(
            icon: Icons.history,
            title: 'Ride history',
            onTap: () => Navigator.pushNamed(context, AppRoutes.history),
          ),
          _HomeTile(
            icon: Icons.person_outline,
            title: 'My profile',
            onTap: () => Navigator.pushNamed(context, AppRoutes.profile),
          ),

          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pushReplacementNamed(context, AppRoutes.driverHome);
            },
            icon: const Icon(Icons.drive_eta),
            label: const Text('Open Driver Demo'),
          ),
        ],
      ),
    );
  }
}

class _HomeTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _HomeTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
