
import 'package:flutter/material.dart';
import '../../app/app_routes.dart';
import '../../services/driver_service.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});
  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  bool isOnline = false;
  bool isLoadingProfile = true;
  bool isUpdatingOnline = false;
  String verificationStatus = 'pending';
  String driverStatus = 'pending';
  static const Color navy = Color(0xFF102A43);
  static const Color darkNavy = Color(0xFF0B1F3A);
  static const Color gold = Color(0xFFFFC857);
  static const Color background = Color(0xFFF4F7FB);
  static const Color mutedText = Color(0xFF68778D);

  @override
  void initState() {
    super.initState();
    _loadDriverProfile();
  }

  Future<void> _loadDriverProfile() async {
    try {
      final profile = await DriverService.getMyProfile();
      if (!mounted) return;
      setState(() {
        verificationStatus = profile['verification_status']?.toString() ?? 'pending';
        driverStatus = profile['status']?.toString() ?? 'pending';
        isOnline = profile['is_online'] == true;
        isLoadingProfile = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        isLoadingProfile = false;
      });
      _showStatusMessage('Could not load driver profile: ${_errorMessage(e)}');
    }
  }

  String _errorMessage(Object error) {
    return error.toString().replaceFirst('Exception: ', '');
  }

  void _showStatusMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: navy,
          behavior: SnackBarBehavior.floating,
        ),
      );
  }

  Future<void> _changeOnlineStatus(bool value) async {
    if (isUpdatingOnline || isLoadingProfile) return;
    if (value &&
        (driverStatus.toLowerCase() != 'active' ||
            verificationStatus.toLowerCase() != 'verified')) {
      _showStatusMessage('Your driver account must be active and verified to go online.');
      return;
    }
    setState(() {
      isUpdatingOnline = true;
    });
    try {
      final response = await DriverService.updateOnlineStatus(isOnline: value);
      if (!mounted) return;
      setState(() {
        isOnline = response['is_online'] == true;
      });
      _showStatusMessage(
        response['message']?.toString() ??
            (isOnline ? 'You are now online.' : 'You are now offline.'),
      );
    } catch (e) {
      if (!mounted) return;
      _showStatusMessage(_errorMessage(e));
    } finally {
      if (mounted) {
        setState(() {
          isUpdatingOnline = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: navy,
        foregroundColor: Colors.white,
        titleSpacing: 20,
        title: const Row(
          children: [
            Icon(Icons.electric_bike_rounded, color: gold, size: 28),
            SizedBox(width: 10),
            Text(
              'NandiRide Driver',
              style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 0.2),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Driver Profile',
            onPressed: () {
              Navigator.pushNamed(context, AppRoutes.driverProfile);
            },
            icon: const Icon(Icons.account_circle_rounded),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 20, 18, 28),
        children: [
          _buildWelcomeHeader(),
          const SizedBox(height: 22),
          _buildVerificationCard(),
          const SizedBox(height: 16),
          _buildOnlineCard(),
          const SizedBox(height: 16),
          _buildEarningsCard(),
          const SizedBox(height: 26),
          _sectionHeading('Driver Services', 'Manage your rides and account'),
          const SizedBox(height: 14),
          _menuTile(
            icon: Icons.notifications_active_rounded,
            title: 'Ride Requests',
            subtitle: 'View available ride requests',
            route: AppRoutes.rideRequests,
          ),
          _menuTile(
            icon: Icons.route_rounded,
            title: 'Trip Details',
            subtitle: 'View your trip information',
            route: AppRoutes.tripDetails,
          ),
          _menuTile(
            icon: Icons.account_circle_rounded,
            title: 'Driver Profile',
            subtitle: 'Personal and licence information',
            route: AppRoutes.driverProfile,
          ),
          const SizedBox(height: 18),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            },
            style: OutlinedButton.styleFrom(
              foregroundColor: navy,
              side: const BorderSide(color: navy, width: 1.3),
              minimumSize: const Size.fromHeight(52),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            icon: const Icon(Icons.person_rounded),
            label: const Text(
              'Switch to Customer',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
          ),
          const SizedBox(height: 12),
          const Center(
            child: Text(
              'NandiRide • Your Ride, Your Way',
              style: TextStyle(
                color: mutedText,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [navy, darkNavy],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.16),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'NAMASTE, DRIVER!',
                  style: TextStyle(
                    color: gold,
                    fontSize: 11,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.4,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Ready to ride?',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 25,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 7),
                Text(
                  'Welcome to your NandiRide dashboard.',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.82),
                    fontSize: 12,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: gold,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'DRIVER PARTNER',
                    style: TextStyle(
                      color: navy,
                      fontSize: 10,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 0.8,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Container(
            height: 82,
            width: 76,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.09),
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: gold.withValues(alpha: 0.55)),
            ),
            child: const Icon(Icons.electric_bike_rounded, color: gold, size: 48),
          ),
        ],
      ),
    );
  }

  Widget _buildVerificationCard() {
    final bool isVerified = verificationStatus.toLowerCase() == 'verified';
    final String displayStatus = verificationStatus.isEmpty
        ? 'Pending'
        : '${verificationStatus[0].toUpperCase()}${verificationStatus.substring(1).toLowerCase()}';
    return _card(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _iconBox(
            Icons.verified_user_rounded,
            isVerified ? const Color(0xFFDDF5E8) : const Color(0xFFFFF1CE),
            isVerified ? const Color(0xFF16794B) : const Color(0xFF956500),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Account Verification',
                  style: TextStyle(color: navy, fontSize: 15, fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: isVerified ? const Color(0xFFDDF5E8) : const Color(0xFFFFF1CE),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    isLoadingProfile ? 'Loading...' : displayStatus,
                    style: TextStyle(
                      color: isVerified ? const Color(0xFF16794B) : const Color(0xFF956500),
                      fontSize: 11,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Your account must be approved before accepting rides.',
                  style: TextStyle(color: mutedText, fontSize: 12, height: 1.45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOnlineCard() {
    return _card(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(14),
        clipBehavior: Clip.antiAlias,
        child: SwitchListTile(
          contentPadding: EdgeInsets.zero,
          secondary: _iconBox(
            isOnline ? Icons.wifi_rounded : Icons.wifi_off_rounded,
            isOnline ? const Color(0xFFDDF5E8) : const Color(0xFFE9EDF4),
            isOnline ? const Color(0xFF16794B) : mutedText,
          ),
          title: Text(
            isLoadingProfile
                ? 'Loading driver status...'
                : isUpdatingOnline
                    ? 'Updating status...'
                    : isOnline
                        ? 'You are Online'
                        : 'You are Offline',
            style: const TextStyle(color: navy, fontSize: 15, fontWeight: FontWeight.w900),
          ),
          subtitle: Text(
            isOnline
                ? 'You can check available ride requests.'
                : 'Turn on to receive available ride requests.',
            style: const TextStyle(color: mutedText, fontSize: 11, height: 1.5),
          ),
          value: isOnline,
          activeThumbColor: navy,
          activeTrackColor: gold,
          onChanged: isLoadingProfile || isUpdatingOnline ? null : _changeOnlineStatus,
        ),
      ),
    );
  }

  Widget _buildEarningsCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: navy,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.12),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  "Today's Earnings",
                  style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w800),
                ),
              ),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: gold, borderRadius: BorderRadius.circular(12)),
                child: const Icon(Icons.account_balance_wallet_rounded, color: navy, size: 23),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Text(
            '₹0.00',
            style: TextStyle(color: gold, fontSize: 34, fontWeight: FontWeight.w900, letterSpacing: -0.6),
          ),
          const SizedBox(height: 4),
          Text(
            'Earnings API not connected',
            style: TextStyle(color: Colors.white.withValues(alpha: 0.75), fontSize: 11),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            height: 46,
            child: FilledButton(
              onPressed: () {
                Navigator.pushNamed(context, AppRoutes.earnings);
              },
              style: FilledButton.styleFrom(
                backgroundColor: gold,
                foregroundColor: navy,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('View Earnings', style: TextStyle(fontWeight: FontWeight.w900)),
                  SizedBox(width: 8),
                  Icon(Icons.arrow_forward_rounded, size: 18),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionHeading(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(color: navy, fontSize: 19, fontWeight: FontWeight.w900)),
        const SizedBox(height: 4),
        Text(subtitle, style: const TextStyle(color: mutedText, fontSize: 12)),
      ],
    );
  }

  Widget _menuTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required String route,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: _card(
        padding: EdgeInsets.zero,
        child: Material(
          color: Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          clipBehavior: Clip.antiAlias,
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
            leading: _iconBox(icon, gold, navy),
            title: Text(
              title,
              style: const TextStyle(color: navy, fontSize: 14, fontWeight: FontWeight.w900),
            ),
            subtitle: Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(subtitle, style: const TextStyle(color: mutedText, fontSize: 11)),
            ),
            trailing: const Icon(Icons.arrow_forward_ios_rounded, color: navy, size: 16),
            onTap: () {
              Navigator.pushNamed(context, route);
            },
          ),
        ),
      ),
    );
  }

  Widget _iconBox(IconData icon, Color backgroundColor, Color iconColor) {
    return Container(
      width: 46,
      height: 46,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Icon(icon, color: iconColor, size: 25),
    );
  }

  Widget _card({
    required Widget child,
    EdgeInsetsGeometry padding = const EdgeInsets.all(18),
  }) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE7ECF3)),
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.035),
            blurRadius: 16,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: child,
    );
  }
}
