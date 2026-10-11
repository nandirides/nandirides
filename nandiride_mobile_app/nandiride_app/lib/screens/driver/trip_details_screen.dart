import 'package:flutter/material.dart';

import '../../app/app_theme.dart';

class TripDetailsScreen extends StatefulWidget {
  const TripDetailsScreen({super.key});

  @override
  State<TripDetailsScreen> createState() => _TripDetailsScreenState();
}

class _TripDetailsScreenState extends State<TripDetailsScreen> {
  String status = 'Demo Trip — Not Accepted';

  void updateStatus(String newStatus) {
    setState(() {
      status = newStatus;
    });

    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('Demo status: $newStatus')));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Trip Details'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Icon(Icons.route, size: 64),
          const SizedBox(height: 12),
          const Text(
            'Demo Trip',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Pickup Location',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  const Text('Haridwar Railway Station (Demo)'),
                  const Divider(height: 28),
                  const Text(
                    'Drop Location',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  const Text('Har Ki Pauri, Haridwar (Demo)'),
                  const Divider(height: 28),
                  const Text(
                    'Estimated Fare',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '₹100.00 (Sample only)',
                    style: TextStyle(fontSize: 22),
                  ),
                  const Divider(height: 28),
                  const Text(
                    'Current Status',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  Text(status),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => updateStatus('Accepted — Demo Only'),
            icon: const Icon(Icons.check_circle),
            label: const Text('Accept Demo Trip'),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () => updateStatus('Completed — Demo Only'),
            icon: const Icon(Icons.flag),
            label: const Text('Complete Demo Trip'),
          ),
          const SizedBox(height: 12),
          const Text(
            'These buttons only change the screen status. '
            'They do not accept or complete a real ride.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }
}
