import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/token_service.dart';
import '../../services/driver_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  static const Color navy = Color(0xFF0B1F4D);
  static const Color gold = Color(0xFFF5B400);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  static const Color navy = Color(0xFF102A43);
  static const Color gold = Color(0xFFFFC857);
  static const Color pageBg = Color(0xFFF4F7FB);

  String _name = 'NandiRide User';
  String _phone = '';
  String _email = '';

  bool _isLoading = true;
  bool _isSaving = false;

  // Driver registration status
  bool _isDriverStatusLoading = true;
  bool _isDriverRegistered = false;
  String? _driverStatusError;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  // Load customer profile and driver registration status.
  Future<void> _loadProfile() async {
    if (mounted) {
      setState(() => _isLoading = true);
    }

    try {
      final user = await AuthService.getCurrentUser();

      if (!mounted) return;

      final firstName = user['first_name']?.toString().trim() ?? '';
      final lastName = user['last_name']?.toString().trim() ?? '';
      final fullName = '$firstName $lastName'.trim();

      setState(() {
        _name = fullName.isEmpty
            ? (user['username']?.toString() ?? 'NandiRide User')
            : fullName;

        _phone = user['phone']?.toString() ?? '';
        _email = user['email']?.toString() ?? '';
      });
    } catch (error) {
      if (!mounted) return;

      _showMessage('Profile load failed: $error');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }

    // Check driver status separately so a driver API error
    // does not prevent the customer profile from opening.
    if (mounted) {
      await _checkDriverRegistration();
    }
  }

  // Check whether the logged-in user already has a driver profile.
  Future<void> _checkDriverRegistration() async {
    if (_isDriverStatusLoading && _driverStatusError == null) {
      // The initial check may already be running.
      // Continue with the check below.
    }

    if (!mounted) return;

    setState(() {
      _isDriverStatusLoading = true;
      _driverStatusError = null;
    });

    try {
      final response = await DriverService.getMyProfile();

      if (!mounted) return;

      final registered = _hasDriverProfile(response);

      setState(() {
        _isDriverRegistered = registered;
        _driverStatusError = null;
      });
    } catch (error) {
      if (!mounted) return;

      final errorText = error.toString().toLowerCase();

      // Treat a clear "no driver profile" response as not registered.
      // Other errors should not be mistaken for missing registration.
      final definitelyNotRegistered =
          errorText.contains('driver profile not found') ||
          errorText.contains('driver not found') ||
          errorText.contains('no driver profile') ||
          errorText.contains('not registered') ||
          errorText.contains('404');

      setState(() {
        if (definitelyNotRegistered) {
          _isDriverRegistered = false;
          _driverStatusError = null;
        } else {
          _driverStatusError =
              'Could not check driver registration. Please retry.';
        }
      });
    } finally {
      if (mounted) {
        setState(() => _isDriverStatusLoading = false);
      }
    }
  }

  // Detect a real driver profile from the API response.
  bool _hasDriverProfile(Map<String, dynamic> response) {
    if (response['is_registered'] == false ||
        response['registered'] == false) {
      return false;
    }

    if (response['is_registered'] == true ||
        response['registered'] == true) {
      return true;
    }

    final detail = response['detail']?.toString().toLowerCase() ?? '';

    if (detail.contains('not found') ||
        detail.contains('not registered') ||
        detail.contains('no driver')) {
      return false;
    }

    // Some APIs wrap the driver profile inside "driver" or "data".
    final nested = response['driver'] ?? response['data'];

    if (nested is Map) {
      return _hasDriverProfile(
        Map<String, dynamic>.from(nested),
      );
    }

    // Empty response means no profile was returned.
    if (response.isEmpty) return false;

    // Recognize common fields in a driver profile.
    const profileKeys = [
      'id',
      'driver_code',
      'license_number',
      'license_expiry',
      'verification_status',
      'user_id',
    ];

    return profileKeys.any(
      (key) => response[key] != null,
    );
  }

  Future<void> _handleDriverAction() async {
    if (_isDriverStatusLoading) return;

    // If status could not be checked, retry instead of
    // incorrectly sending an existing driver to registration.
    if (_driverStatusError != null) {
      await _checkDriverRegistration();
      return;
    }

    if (_isDriverRegistered) {
      // Existing driver goes straight to Driver Home.
      if (!mounted) return;

      Navigator.pushNamed(
        context,
        AppRoutes.driverHome,
      );
      return;
    }

    // No driver profile: open the registration form.
    final result = await Navigator.pushNamed<dynamic>(
      context,
      AppRoutes.driverRegistration,
    );

    if (!mounted) return;

    // If registration screen returns, refresh the status.
    // This also supports registration screens that pop with a result.
    if (result != null) {
      await _checkDriverRegistration();
    }
  }

  Future<void> _openEditProfile() async {
    if (_isSaving || _isLoading) return;

    final result = await Navigator.pushNamed<dynamic>(
      context,
      AppRoutes.editProfile,
      arguments: {
        'name': _name,
        'phone': _phone,
        'email': _email,
      },
    );

    if (!mounted || result is! Map) return;

    final updatedName = result['name']?.toString().trim() ?? '';
    final updatedPhone = result['phone']?.toString().trim() ?? _phone;
    final updatedEmail = result['email']?.toString().trim() ?? _email;

    if (updatedName.isEmpty) {
      _showMessage('Please enter your name.');
      return;
    }

    final nameParts = updatedName.split(RegExp(r'\s+'));
    final firstName = nameParts.first;
    final lastName =
        nameParts.length > 1 ? nameParts.skip(1).join(' ') : '';

    setState(() => _isSaving = true);

    try {
      final updatedUser = await AuthService.updateCurrentUser(
        firstName: firstName,
        lastName: lastName,
        email: updatedEmail,
        phone: updatedPhone,
      );

      if (!mounted) return;

      final savedFirstName =
          updatedUser['first_name']?.toString().trim() ?? firstName;
      final savedLastName =
          updatedUser['last_name']?.toString().trim() ?? lastName;

      final savedName = '$savedFirstName $savedLastName'.trim();

      setState(() {
        _name = savedName.isEmpty ? updatedName : savedName;
        _phone = updatedUser['phone']?.toString() ?? updatedPhone;
        _email = updatedUser['email']?.toString() ?? updatedEmail;
      });

      _showMessage('Profile updated successfully.');
    } catch (error) {
      if (!mounted) return;

      _showMessage('Could not update profile: $error');
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Future<void> _logout() async {
    if (_isSaving) return;

    final shouldLogout = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          icon: Container(
            height: 64,
            width: 64,
            decoration: BoxDecoration(
              color: const Color(0xFFFFF3D6),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.logout_rounded,
              color: Color(0xFF102A43),
              size: 32,
            ),
          ),
          title: const Text(
            'Confirm Logout',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Color(0xFF102A43),
              fontWeight: FontWeight.bold,
              fontSize: 21,
            ),
          ),
          content: const Text(
            'Are you sure you want to logout from your NandiRide account?',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Color(0xFF66788A),
              fontSize: 14,
              height: 1.5,
            ),
          ),
          actionsAlignment: MainAxisAlignment.center,
          actionsPadding: const EdgeInsets.fromLTRB(20, 0, 20, 22),
          actions: [
            SizedBox(
              width: 110,
              child: OutlinedButton(
                onPressed: () {
                  Navigator.pop(dialogContext, false);
                },
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF102A43),
                  side: const BorderSide(
                    color: Color(0xFFCBD5E1),
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: const Text('Cancel'),
              ),
            ),
            const SizedBox(width: 10),
            SizedBox(
              width: 130,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(dialogContext, true);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF102A43),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: const Text(
                  'Yes, Logout',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        );
      },
    );

    if (shouldLogout != true || !mounted) return;

    try {
      await TokenService.clearToken();

      if (!mounted) return;

      Navigator.pushNamedAndRemoveUntil(
        context,
        AppRoutes.login,
        (route) => false,
      );
    } catch (error) {
      if (!mounted) return;

      _showMessage('Logout failed: $error');
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  String get _initials {
    final parts = _name.trim().split(RegExp(r'\s+'));

    if (parts.isEmpty || parts.first.isEmpty) return 'N';
    if (parts.length == 1) return parts.first[0].toUpperCase();

    return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
  }

  // Driver section changes according to registration status.
  Widget _buildDriverCard() {
    final String title;
    final String subtitle;
    final IconData icon;
    final Color iconBackground;
    final Color borderColor;

    if (_isDriverStatusLoading) {
      title = 'Checking Driver Status...';
      subtitle = 'Please wait';
      icon = Icons.sync_rounded;
      iconBackground = const Color(0xFFEAF0F7);
      borderColor = const Color(0xFFE7EDF4);
    } else if (_driverStatusError != null) {
      title = 'Check Driver Status';
      subtitle = 'Tap to retry';
      icon = Icons.refresh_rounded;
      iconBackground = const Color(0xFFFFF3D6);
      borderColor = const Color(0xFFFFE3A0);
    } else if (_isDriverRegistered) {
      title = 'Driver Dashboard';
      subtitle = 'Your registration already exists';
      icon = Icons.dashboard_rounded;
      iconBackground = const Color(0xFFDDF5E4);
      borderColor = const Color(0xFFB7E4C7);
    } else {
      title = 'Become a Driver';
      subtitle = 'Register to drive with NandiRide';
      icon = Icons.two_wheeler_rounded;
      iconBackground = const Color(0xFFFFF3D6);
      borderColor = const Color(0xFFFFE3A0);
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(22),
        child: InkWell(
          borderRadius: BorderRadius.circular(22),
          onTap: _isDriverStatusLoading ? null : _handleDriverAction,
          child: Padding(
            padding: const EdgeInsets.all(17),
            child: Row(
              children: [
                Container(
                  height: 54,
                  width: 54,
                  decoration: BoxDecoration(
                    color: iconBackground,
                    borderRadius: BorderRadius.circular(17),
                  ),
                  child: _isDriverStatusLoading
                      ? const Padding(
                          padding: EdgeInsets.all(15),
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: navy,
                          ),
                        )
                      : Icon(
                          icon,
                          color: navy,
                          size: 29,
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
                          color: navy,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          color: Color(0xFF718096),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Icon(
                  _isDriverStatusLoading
                      ? Icons.hourglass_empty_rounded
                      : Icons.arrow_forward_ios_rounded,
                  color: navy,
                  size: 17,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: pageBg,
      appBar: AppBar(
        backgroundColor: navy,
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'My Profile',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            tooltip: 'Edit profile',
            onPressed: _isLoading || _isSaving ? null : _openEditProfile,
            icon: const Icon(Icons.edit_outlined),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: gold),
            )
          : RefreshIndicator(
              onRefresh: _loadProfile,
              child: ListView(
                padding: const EdgeInsets.fromLTRB(18, 20, 18, 28),
                children: [
                  // Profile header
                  Container(
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [navy, Color(0xFF244B6B)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(26),
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
                        Container(
                          padding: const EdgeInsets.all(5),
                          decoration: const BoxDecoration(
                            color: gold,
                            shape: BoxShape.circle,
                          ),
                          child: CircleAvatar(
                            radius: 43,
                            backgroundColor: Colors.white,
                            child: Text(
                              _initials,
                              style: const TextStyle(
                                color: navy,
                                fontWeight: FontWeight.bold,
                                fontSize: 29,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 14),
                        Text(
                          _name,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 23,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 7),
                        const Text(
                          'Customer Account',
                          style: TextStyle(
                            color: Color(0xFFE4ECF4),
                            fontSize: 13,
                          ),
                        ),
                        if (_phone.isNotEmpty || _email.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          if (_phone.isNotEmpty)
                            _HeaderDetail(
                              icon: Icons.phone_outlined,
                              text: _phone,
                            ),
                          if (_email.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            _HeaderDetail(
                              icon: Icons.email_outlined,
                              text: _email,
                            ),
                          ],
                        ],
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed:
                                _isSaving ? null : _openEditProfile,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: gold),
                              padding: const EdgeInsets.symmetric(
                                vertical: 13,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14),
                              ),
                            ),
                            icon: const Icon(
                              Icons.edit_outlined,
                              size: 18,
                            ),
                            label: Text(
                              _isSaving ? 'Saving...' : 'Edit Profile',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 28),
                  const _SectionHeading(
                    title: 'PERSONAL INFORMATION',
                  ),
                  const SizedBox(height: 12),

                  // Personal information
                  Container(
                    padding: const EdgeInsets.all(17),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color(0xFFE7EDF4),
                      ),
                    ),
                    child: Column(
                      children: [
                        _InfoRow(
                          icon: Icons.person_outline_rounded,
                          label: 'Full Name',
                          value: _name,
                        ),
                        const Divider(height: 25),
                        _InfoRow(
                          icon: Icons.phone_outlined,
                          label: 'Mobile Number',
                          value:
                              _phone.isEmpty ? 'Not added yet' : _phone,
                        ),
                        const Divider(height: 25),
                        _InfoRow(
                          icon: Icons.email_outlined,
                          label: 'Email Address',
                          value:
                              _email.isEmpty ? 'Not added yet' : _email,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 28),
                  const _SectionHeading(title: 'YOUR ACCOUNT'),
                  const SizedBox(height: 12),

                  _MenuTile(
                    icon: Icons.history_rounded,
                    title: 'Ride History',
                    subtitle: 'View your previous rides',
                    onTap: () => Navigator.pushNamed(
                      context,
                      AppRoutes.history,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _MenuTile(
                    icon: Icons.manage_accounts_outlined,
                    title: 'Edit Personal Details',
                    subtitle: 'Update your name, phone and email',
                    onTap: _isSaving ? null : _openEditProfile,
                  ),

                  const SizedBox(height: 28),
                  const _SectionHeading(
                    title: 'DRIVE WITH NANDIRIDE',
                  ),
                  const SizedBox(height: 12),

                  // Automatically switches between registration
                  // and the driver dashboard.
                  _buildDriverCard(),

                  if (_driverStatusError != null) ...[
                    const SizedBox(height: 8),
                    const Text(
                      'Driver status could not be verified. '
                      'Check your internet connection and tap the card to retry.',
                      style: TextStyle(
                        color: Color(0xFFB42318),
                        fontSize: 12,
                      ),
                    ),
                  ],

                  const SizedBox(height: 28),

                  OutlinedButton.icon(
                    onPressed: _isSaving ? null : _logout,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFB42318),
                      side: const BorderSide(
                        color: Color(0xFFF0C9C6),
                      ),
                      backgroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 15),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    icon: const Icon(Icons.logout_rounded),
                    label: const Text(
                      'Logout',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),

                  const SizedBox(height: 18),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.shield_outlined,
                        size: 15,
                        color: Color(0xFF718096),
                      ),
                      SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          'NandiRide • Your journey, our priority',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFF718096),
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }
}

class _HeaderDetail extends StatelessWidget {
  const _HeaderDetail({
    required this.icon,
    required this.text,
  });

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 16, color: ProfileScreen.gold),
        const SizedBox(width: 8),
        Flexible(
          child: Text(
            text,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _SectionHeading extends StatelessWidget {
  const _SectionHeading({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: const TextStyle(
          color: Color(0xFF66788A),
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.3,
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          height: 42,
          width: 42,
          decoration: BoxDecoration(
            color: const Color(0xFFEAF0F7),
            borderRadius: BorderRadius.circular(13),
          ),
          child: Icon(
            icon,
            color: ProfileScreen.navy,
            size: 22,
          ),
        ),
        const SizedBox(width: 13),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: Color(0xFF718096),
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  color: ProfileScreen.navy,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _MenuTile extends StatelessWidget {
  const _MenuTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(19),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(19),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(19),
            border: Border.all(
              color: const Color(0xFFE7EDF4),
            ),
          ),
          child: Row(
            children: [
              Container(
                height: 46,
                width: 46,
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF0F7),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  icon,
                  color: ProfileScreen.navy,
                  size: 24,
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
                        color: ProfileScreen.navy,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: Color(0xFF718096),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.chevron_right_rounded,
                color: Color(0xFF718096),
                size: 25,
              ),
            ],
          ),
        ),
      ),
    );
  }
}