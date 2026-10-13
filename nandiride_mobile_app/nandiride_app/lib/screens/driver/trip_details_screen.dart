import 'package:flutter/material.dart';

import '../../app/app_theme.dart';

class TripDetailsScreen extends StatefulWidget {
  const TripDetailsScreen({super.key});

  @override
  State<TripDetailsScreen> createState() =>
      _TripDetailsScreenState();
}

class _TripDetailsScreenState extends State<TripDetailsScreen> {
  String status = 'Demo Trip — Not Accepted';

  int _statusStep = 0;

  void updateStatus(String newStatus, int step) {
    if (_statusStep == 2) {
      _showMessage('This demo trip is already completed.');
      return;
    }

    if (step == 2 && _statusStep == 0) {
      _showMessage('Please accept the demo trip first.');
      return;
    }

    setState(() {
      status = newStatus;
      _statusStep = step;
    });

    _showMessage('Demo status: $newStatus');
  }

  void _showMessage(String message) {
    if (!mounted) return;

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: AppTheme.primary,
          behavior: SnackBarBehavior.floating,
        ),
      );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Trip Details'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          // Trip header
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              color: AppTheme.primary,
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              children: [
                Container(
                  width: 76,
                  height: 76,
                  decoration: const BoxDecoration(
                    color: AppTheme.secondary,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.route_rounded,
                    color: AppTheme.primary,
                    size: 40,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Demo Trip',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 25,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 7,
                  ),
                  decoration: BoxDecoration(
                    color: AppTheme.secondary,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'SAMPLE RIDE',
                    style: TextStyle(
                      color: AppTheme.primary,
                      fontSize: 10,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 22),

          const Text(
            'Journey Information',
            style: TextStyle(
              color: AppTheme.primary,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),

          const SizedBox(height: 14),

          // Pickup and drop
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.border),
            ),
            child: Column(
              children: [
                _LocationRow(
                  icon: Icons.my_location_rounded,
                  iconColor: AppTheme.success,
                  title: 'PICKUP LOCATION',
                  location: 'Haridwar Railway Station',
                ),
                Padding(
                  padding: const EdgeInsets.only(left: 11),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Container(
                      height: 28,
                      width: 2,
                      color: AppTheme.border,
                    ),
                  ),
                ),
                _LocationRow(
                  icon: Icons.location_on_rounded,
                  iconColor: AppTheme.error,
                  title: 'DROP LOCATION',
                  location: 'Har Ki Pauri, Haridwar',
                ),
                const SizedBox(height: 10),
                const Divider(color: AppTheme.border),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(
                      Icons.info_outline_rounded,
                      color: AppTheme.primary,
                      size: 18,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Locations are for demonstration only.',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Fare card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF8DF),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color: AppTheme.secondary.withValues(alpha: 0.7),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppTheme.secondary,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(
                    Icons.payments_rounded,
                    color: AppTheme.primary,
                    size: 26,
                  ),
                ),
                const SizedBox(width: 14),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Estimated Fare',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      SizedBox(height: 5),
                      Text(
                        '₹100.00',
                        style: TextStyle(
                          color: AppTheme.primary,
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ],
                  ),
                ),
                const Text(
                  'DEMO',
                  style: TextStyle(
                    color: AppTheme.primary,
                    fontWeight: FontWeight.w900,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 22),

          const Text(
            'Trip Status',
            style: TextStyle(
              color: AppTheme.primary,
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),

          const SizedBox(height: 12),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  _statusStep == 2
                      ? Icons.check_circle_rounded
                      : _statusStep == 1
                          ? Icons.directions_car_rounded
                          : Icons.hourglass_empty_rounded,
                  color: AppTheme.primary,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        status,
                        style: const TextStyle(
                          color: AppTheme.primary,
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        'Demo status only — not saved to the server.',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 22),

          // Accept trip
          SizedBox(
            height: 54,
            child: ElevatedButton.icon(
              onPressed: _statusStep != 0
                  ? null
                  : () => updateStatus(
                        'Accepted — Demo Only',
                        1,
                      ),
              icon: const Icon(Icons.check_circle_rounded),
              label: const Text('Accept Demo Trip'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primary,
                foregroundColor: Colors.white,
                disabledBackgroundColor: AppTheme.border,
                disabledForegroundColor: AppTheme.textSecondary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // Complete trip
          SizedBox(
            height: 54,
            child: OutlinedButton.icon(
              onPressed: _statusStep != 1
                  ? null
                  : () => updateStatus(
                        'Completed — Demo Only',
                        2,
                      ),
              icon: const Icon(Icons.flag_rounded),
              label: const Text('Complete Demo Trip'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.primary,
                side: const BorderSide(
                  color: AppTheme.primary,
                  width: 1.5,
                ),
                disabledForegroundColor: AppTheme.textSecondary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),

          const SizedBox(height: 18),

          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.secondary.withValues(alpha: 0.18),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: AppTheme.primary,
                  size: 22,
                ),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Demo screen: accepting or completing this trip '
                    'only changes its local display status. '
                    'Real ride operations require backend API integration.',
                    style: TextStyle(
                      color: AppTheme.primary,
                      fontSize: 12,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

class _LocationRow extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String location;

  const _LocationRow({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.location,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: iconColor, size: 24),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                location,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
