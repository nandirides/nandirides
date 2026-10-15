import 'package:flutter/material.dart';
import '../../services/driver_service.dart';

class DriverProfileScreen extends StatefulWidget {
  const DriverProfileScreen({super.key});

  @override
  State<DriverProfileScreen> createState() =>
      _DriverProfileScreenState();
}

class _DriverProfileScreenState extends State<DriverProfileScreen>
    with SingleTickerProviderStateMixin {
  late Future<Map<String, dynamic>> _profileFuture;
  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  static const Color navy = Color(0xFF102A43);
  static const Color darkNavy = Color(0xFF0B1F3A);
  static const Color gold = Color(0xFFFFC857);
  static const Color background = Color(0xFFF4F7FB);
  static const Color mutedText = Color(0xFF68778D);

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeOutCubic,
      ),
    );

    _profileFuture = DriverService.getMyProfile();
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _reloadProfile() {
    setState(() {
      _profileFuture = DriverService.getMyProfile();
    });
    _animationController
      ..reset()
      ..forward();
  }

  String _value(dynamic value, [String fallback = 'Not added']) {
    if (value == null || value.toString().trim().isEmpty) {
      return fallback;
    }
    return value.toString();
  }

  String _formatStatus(String status) {
    if (status.isEmpty || status == 'Not added') {
      return status;
    }

    return status
        .replaceAll('_', ' ')
        .split(' ')
        .map(
          (word) => word.isEmpty
              ? word
              : '${word[0].toUpperCase()}${word.substring(1)}',
        )
        .join(' ');
  }

  Color _statusColor(String status) {
    switch (status.toLowerCase()) {
      case 'verified':
      case 'active':
      case 'approved':
        return const Color(0xFF16794B);
      case 'rejected':
      case 'suspended':
      case 'blocked':
      case 'inactive':
        return const Color(0xFFB42318);
      default:
        return const Color(0xFF956500);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: navy,
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Driver Profile',
          style: TextStyle(
            fontWeight: FontWeight.w800,
          ),
        ),
        actions: [
          IconButton(
            tooltip: 'Refresh profile',
            onPressed: _reloadProfile,
            icon: const Icon(Icons.refresh_rounded),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _profileFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return _buildLoading();
          }

          if (snapshot.hasError) {
            return _buildError(snapshot.error.toString());
          }

          final profile = snapshot.data ?? {};

          final firstName = _value(profile['first_name'], '');
          final lastName = _value(profile['last_name'], '');
          final fullName = '$firstName $lastName'.trim();

          final driverName = fullName.isEmpty
              ? _value(profile['driver_code'], 'Driver')
              : fullName;

          final verificationStatus = _formatStatus(
            _value(profile['verification_status']),
          );

          final accountStatus = _formatStatus(
            _value(profile['status']),
          );

          return RefreshIndicator(
            color: navy,
            backgroundColor: gold,
            onRefresh: () async {
              _reloadProfile();
              try {
                await _profileFuture;
              } catch (_) {
                // FutureBuilder displays the error state.
              }
            },
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: SlideTransition(
                position: _slideAnimation,
                child: ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(18, 20, 18, 28),
                  children: [
                    _buildProfileHeader(
                      driverName: driverName,
                      phone: _value(profile['phone']),
                      driverCode: _value(profile['driver_code']),
                    ),

                    const SizedBox(height: 22),

                    _sectionTitle(
                      'Driver Information',
                      'Your registered details',
                    ),

                    const SizedBox(height: 14),

                    _infoCard(
                      icon: Icons.verified_user_rounded,
                      title: 'Verification Status',
                      value: verificationStatus,
                      statusColor: _statusColor(
                        _value(profile['verification_status']),
                      ),
                    ),

                    _infoCard(
                      icon: Icons.badge_rounded,
                      title: 'Driving Licence',
                      value: _value(profile['license_number']),
                    ),

                    _infoCard(
                      icon: Icons.calendar_month_rounded,
                      title: 'Licence Expiry',
                      value: _value(profile['license_expiry']),
                    ),

                    _infoCard(
                      icon: Icons.work_history_rounded,
                      title: 'Driving Experience',
                      value:
                          '${_value(profile['experience_years'], '0')} years',
                    ),

                    _infoCard(
                      icon: Icons.toggle_on_rounded,
                      title: 'Account Status',
                      value: accountStatus,
                      statusColor: _statusColor(
                        _value(profile['status']),
                      ),
                    ),

                    const SizedBox(height: 20),

                    SizedBox(
                      height: 52,
                      child: FilledButton.icon(
                        onPressed: _reloadProfile,
                        style: FilledButton.styleFrom(
                          backgroundColor: gold,
                          foregroundColor: navy,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        icon: const Icon(Icons.refresh_rounded),
                        label: const Text(
                          'Refresh Profile',
                          style: TextStyle(
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 12),

                    SizedBox(
                      height: 50,
                      child: OutlinedButton.icon(
                        onPressed: () => Navigator.pop(context),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: navy,
                          side: const BorderSide(
                            color: navy,
                            width: 1.2,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        icon: const Icon(Icons.arrow_back_rounded),
                        label: const Text(
                          'Go Back',
                          style: TextStyle(
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 18),

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
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildProfileHeader({
    required String driverName,
    required String phone,
    required String driverCode,
  }) {
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
      child: Column(
        children: [
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.75, end: 1),
            duration: const Duration(milliseconds: 650),
            curve: Curves.easeOutBack,
            builder: (context, scale, child) {
              return Transform.scale(
                scale: scale,
                child: child,
              );
            },
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: gold,
                  width: 3,
                ),
              ),
              child: const CircleAvatar(
                radius: 43,
                backgroundColor: Colors.white,
                child: Icon(
                  Icons.person_rounded,
                  size: 52,
                  color: navy,
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),

          Text(
            driverName,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 23,
              fontWeight: FontWeight.w900,
            ),
          ),

          const SizedBox(height: 7),

          Text(
            phone,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.82),
              fontSize: 13,
            ),
          ),

          const SizedBox(height: 14),

          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 13,
              vertical: 8,
            ),
            decoration: BoxDecoration(
              color: gold,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'ID: $driverCode',
              style: const TextStyle(
                color: navy,
                fontSize: 11,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: navy,
            fontSize: 19,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: const TextStyle(
            color: mutedText,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _infoCard({
    required IconData icon,
    required String title,
    required String value,
    Color? statusColor,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.94, end: 1),
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOutCubic,
        builder: (context, scale, child) {
          return Transform.scale(
            scale: scale,
            child: child,
          );
        },
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: const Color(0xFFE7ECF3),
            ),
            boxShadow: [
              BoxShadow(
                color: navy.withValues(alpha: 0.035),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                height: 46,
                width: 46,
                decoration: BoxDecoration(
                  color: gold.withValues(alpha: 0.28),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  icon,
                  color: navy,
                  size: 25,
                ),
              ),

              const SizedBox(width: 14),

              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: mutedText,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      value,
                      style: TextStyle(
                        color: statusColor ?? navy,
                        fontSize: 14,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),

              if (statusColor != null)
                Icon(
                  value.toLowerCase() == 'verified' ||
                          value.toLowerCase() == 'active' ||
                          value.toLowerCase() == 'approved'
                      ? Icons.check_circle_rounded
                      : Icons.info_rounded,
                  color: statusColor,
                  size: 20,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoading() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            height: 48,
            width: 48,
            child: CircularProgressIndicator(
              color: navy,
              strokeWidth: 4,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Loading Driver Profile...',
            style: TextStyle(
              color: navy,
              fontSize: 15,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Please wait',
            style: TextStyle(
              color: mutedText.withValues(alpha: 0.9),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildError(String error) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              height: 84,
              width: 84,
              decoration: BoxDecoration(
                color: const Color(0xFFFFE9E7),
                borderRadius: BorderRadius.circular(26),
              ),
              child: const Icon(
                Icons.cloud_off_rounded,
                color: Color(0xFFB42318),
                size: 43,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Could not load driver profile',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: navy,
                fontSize: 19,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Check your login and backend connection, then try again.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: mutedText,
                fontSize: 13,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 12),
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: const Text(
                'Technical details',
                style: TextStyle(
                  color: navy,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
              children: [
                SelectableText(
                  error,
                  style: const TextStyle(
                    color: mutedText,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: FilledButton.icon(
                onPressed: _reloadProfile,
                style: FilledButton.styleFrom(
                  backgroundColor: gold,
                  foregroundColor: navy,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                icon: const Icon(Icons.refresh_rounded),
                label: const Text(
                  'Try Again',
                  style: TextStyle(
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
