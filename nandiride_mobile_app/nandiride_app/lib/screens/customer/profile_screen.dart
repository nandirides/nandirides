import 'package:flutter/material.dart';

import '../../app/app_routes.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const CircleAvatar(radius: 48, child: Icon(Icons.person, size: 55)),
          const SizedBox(height: 16),
          const Text(
            'NandiRide User',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 23, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 5),
          const Text('Demo account', textAlign: TextAlign.center),
          const SizedBox(height: 28),
          Card(
            child: ListTile(
              leading: const Icon(Icons.edit_outlined),
              title: const Text('Edit Profile'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.pushNamed(context, AppRoutes.editProfile);
              },
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.history),
              title: const Text('Ride History'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.pushNamed(context, AppRoutes.history);
              },
            ),
          ),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pushNamedAndRemoveUntil(
                context,
                AppRoutes.login,
                (route) => false,
              );
            },
            icon: const Icon(Icons.logout),
            label: const Text('Logout Demo'),
          ),
          const SizedBox(height: 10),
          const Text(
            'Demo only: logout does not revoke a server token.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.black54, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
