import 'package:flutter/material.dart';

import '../../app/app_theme.dart';

class EarningsScreen extends StatelessWidget {
  const EarningsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Earnings'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const Icon(Icons.account_balance_wallet, size: 55),
                  const SizedBox(height: 16),
                  const Text('Total Earnings'),
                  const SizedBox(height: 8),
                  const Text(
                    '₹0.00',
                    style: TextStyle(fontSize: 34, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text('Demo data — not actual earnings'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Earnings Summary',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          const Card(
            child: ListTile(
              leading: Icon(Icons.today),
              title: Text('Today'),
              trailing: Text('₹0.00'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.calendar_month),
              title: Text('This Month'),
              trailing: Text('₹0.00'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.directions_car),
              title: Text('Completed Trips'),
              trailing: Text('0'),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Real earnings will be loaded from the backend API later.',
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
