
import 'package:flutter/material.dart';

import '../../app/app_routes.dart';
import '../../services/driver_service.dart';

class DriverRegistrationScreen extends StatefulWidget {
  const DriverRegistrationScreen({super.key});

  @override
  State<DriverRegistrationScreen> createState() =>
      _DriverRegistrationScreenState();
}

class _DriverRegistrationScreenState
    extends State<DriverRegistrationScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();

  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _licenseController = TextEditingController();
  final _experienceController = TextEditingController(text: '0');

  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  static const Color navy = Color(0xFF102A43);
  static const Color darkNavy = Color(0xFF0B1F3A);
  static const Color gold = Color(0xFFFFC857);
  static const Color background = Color(0xFFF4F7FB);
  static const Color mutedText = Color(0xFF68778D);

  DateTime? _licenseExpiry;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 650),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.06),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeOutCubic,
      ),
    );

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _licenseController.dispose();
    _experienceController.dispose();
    super.dispose();
  }

  Future<void> _selectLicenseExpiry() async {
    final now = DateTime.now();

    final selected = await showDatePicker(
      context: context,
      initialDate:
          _licenseExpiry ?? DateTime(now.year + 1, now.month, now.day),
      firstDate: DateTime(now.year - 20),
      lastDate: DateTime(now.year + 30),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: navy,
              onPrimary: Colors.white,
              secondary: gold,
              onSecondary: navy,
              surface: Colors.white,
              onSurface: navy,
            ),
          ),
          child: child!,
        );
      },
    );

    if (selected != null && mounted) {
      setState(() {
        _licenseExpiry = selected;
      });
    }
  }

  String _formatDate(DateTime date) {
    return '${date.year.toString().padLeft(4, '0')}-'
        '${date.month.toString().padLeft(2, '0')}-'
        '${date.day.toString().padLeft(2, '0')}';
  }

  Future<void> _submitForm() async {
    FocusScope.of(context).unfocus();

    if (_isSubmitting) return;

    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      final response =
          await DriverService.registerOrGetExistingProfile(
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        email: _emailController.text.trim(),
        phone: _phoneController.text.trim(),
        licenseNumber:
            _licenseController.text.trim().toUpperCase(),
        licenseExpiry: _licenseExpiry == null
            ? null
            : _formatDate(_licenseExpiry!),
        experienceYears:
            int.tryParse(_experienceController.text.trim()) ?? 0,
      );

      if (!mounted) return;

      // Registration succeeded or the logged-in user's existing
      // driver profile was found.
      ScaffoldMessenger.of(context).hideCurrentSnackBar();

      Navigator.pushNamedAndRemoveUntil(
        context,
        AppRoutes.driverHome,
        (route) => route.isFirst,
        arguments: response,
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFFB42318),
            behavior: SnackBarBehavior.floating,
            content: Text(
              'Registration failed: ${_cleanError(error)}',
            ),
          ),
        );
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  String _cleanError(Object error) {
    return error.toString().replaceFirst('Exception: ', '');
  }

  InputDecoration _decoration(
    String label,
    IconData icon, {
    String? hint,
  }) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      prefixIcon: Icon(icon, color: navy),
      filled: true,
      fillColor: Colors.white,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 18,
      ),
      labelStyle: const TextStyle(color: mutedText),
      hintStyle: const TextStyle(
        color: Color(0xFF9AA6B5),
        fontSize: 13,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: Color(0xFFE0E7EF),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: navy,
          width: 1.6,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: Color(0xFFB42318),
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: Color(0xFFB42318),
          width: 1.5,
        ),
      ),
    );
  }

  Widget _sectionTitle(String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: navy,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            subtitle,
            style: const TextStyle(
              color: mutedText,
              fontSize: 12,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _animatedField({
    required int index,
    required Widget child,
  }) {
    return TweenAnimationBuilder<double>(
      key: ValueKey('registration-field-$index'),
      tween: Tween(begin: 0.96, end: 1),
      duration: Duration(milliseconds: 300 + index * 50),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          alignment: Alignment.center,
          child: child,
        );
      },
      child: child,
    );
  }

  Widget _buildHeader() {
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
            color: navy.withValues(alpha: 0.15),
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
                  'DRIVER PARTNER PROGRAM',
                  style: TextStyle(
                    color: gold,
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.1,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Become a NandiRide Driver',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                    height: 1.2,
                  ),
                ),
                const SizedBox(height: 9),
                Text(
                  'Complete your details to begin verification.',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.82),
                    fontSize: 12,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Container(
            height: 66,
            width: 62,
            decoration: BoxDecoration(
              color: gold,
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Icon(
              Icons.electric_bike_rounded,
              color: navy,
              size: 38,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpirySelector() {
    final date = _licenseExpiry;

    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(15),
      child: InkWell(
        borderRadius: BorderRadius.circular(15),
        onTap: _isSubmitting ? null : _selectLicenseExpiry,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(15),
            border: Border.all(
              color: date == null
                  ? const Color(0xFFE0E7EF)
                  : gold,
              width: date == null ? 1 : 1.5,
            ),
          ),
          child: Row(
            children: [
              Container(
                height: 44,
                width: 44,
                decoration: BoxDecoration(
                  color: gold.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: const Icon(
                  Icons.calendar_month_rounded,
                  color: navy,
                ),
              ),
              const SizedBox(width: 13),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Licence Expiry Date',
                      style: TextStyle(
                        color: mutedText,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      date == null
                          ? 'Select expiry date (optional)'
                          : '${date.day.toString().padLeft(2, '0')}/'
                              '${date.month.toString().padLeft(2, '0')}/'
                              '${date.year}',
                      style: const TextStyle(
                        color: navy,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.arrow_forward_ios_rounded,
                color: navy,
                size: 16,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      height: 54,
      child: FilledButton(
        onPressed: _isSubmitting ? null : _submitForm,
        style: FilledButton.styleFrom(
          backgroundColor: gold,
          foregroundColor: navy,
          disabledBackgroundColor: const Color(0xFFE6D5A8),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 220),
          child: _isSubmitting
              ? const Row(
                  key: ValueKey('submitting'),
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      height: 21,
                      width: 21,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: navy,
                      ),
                    ),
                    SizedBox(width: 12),
                    Text(
                      'Submitting...',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                )
              : const Row(
                  key: ValueKey('submit'),
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.verified_user_rounded),
                    SizedBox(width: 10),
                    Text(
                      'Submit Registration',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
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
          'Driver Registration',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: Form(
            key: _formKey,
            child: ListView(
              keyboardDismissBehavior:
                  ScrollViewKeyboardDismissBehavior.onDrag,
              padding: const EdgeInsets.fromLTRB(18, 20, 18, 30),
              children: [
                _buildHeader(),
                const SizedBox(height: 26),

                _sectionTitle(
                  'Personal Information',
                  'Enter the details associated with your account.',
                ),

                _animatedField(
                  index: 1,
                  child: TextFormField(
                    controller: _firstNameController,
                    textCapitalization: TextCapitalization.words,
                    enabled: !_isSubmitting,
                    decoration: _decoration(
                      'First Name *',
                      Icons.person_rounded,
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'First name is required';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 15),

                _animatedField(
                  index: 2,
                  child: TextFormField(
                    controller: _lastNameController,
                    textCapitalization: TextCapitalization.words,
                    enabled: !_isSubmitting,
                    decoration: _decoration(
                      'Last Name',
                      Icons.person_outline_rounded,
                    ),
                  ),
                ),

                const SizedBox(height: 15),

                _animatedField(
                  index: 3,
                  child: TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    enabled: !_isSubmitting,
                    decoration: _decoration(
                      'Email Address',
                      Icons.email_outlined,
                    ),
                    validator: (value) {
                      final email = value?.trim() ?? '';

                      if (email.isNotEmpty &&
                          !RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
                              .hasMatch(email)) {
                        return 'Enter a valid email address';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 15),

                _animatedField(
                  index: 4,
                  child: TextFormField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    enabled: !_isSubmitting,
                    maxLength: 10,
                    decoration: _decoration(
                      'Mobile Number *',
                      Icons.phone_android_rounded,
                      hint: '10-digit mobile number',
                    ).copyWith(counterText: ''),
                    validator: (value) {
                      final phone = value?.trim() ?? '';

                      if (!RegExp(r'^[6-9]\d{9}$').hasMatch(phone)) {
                        return 'Enter a valid 10-digit Indian mobile number';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 25),

                _sectionTitle(
                  'Driving Information',
                  'Provide your licence and experience details.',
                ),

                _animatedField(
                  index: 5,
                  child: TextFormField(
                    controller: _licenseController,
                    textCapitalization: TextCapitalization.characters,
                    enabled: !_isSubmitting,
                    decoration: _decoration(
                      'Driving Licence Number *',
                      Icons.badge_rounded,
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Driving licence number is required';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 15),

                _animatedField(
                  index: 6,
                  child: _buildExpirySelector(),
                ),

                const SizedBox(height: 15),

                _animatedField(
                  index: 7,
                  child: TextFormField(
                    controller: _experienceController,
                    keyboardType: TextInputType.number,
                    enabled: !_isSubmitting,
                    decoration: _decoration(
                      'Driving Experience (Years) *',
                      Icons.work_history_rounded,
                      hint: 'Example: 2',
                    ),
                    validator: (value) {
                      final years =
                          int.tryParse(value?.trim() ?? '');

                      if (years == null || years < 0 || years > 80) {
                        return 'Enter experience between 0 and 80 years';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 25),

                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF5DA),
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(
                      color: gold.withValues(alpha: 0.7),
                    ),
                  ),
                  child: const Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.info_outline_rounded,
                        color: navy,
                      ),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Your details will be submitted for verification. '
                          'Ride access may depend on approval by NandiRide.',
                          style: TextStyle(
                            color: navy,
                            fontSize: 12,
                            height: 1.5,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 22),
                _buildSubmitButton(),
                const SizedBox(height: 14),

                const Center(
                  child: Text(
                    '* Required fields',
                    style: TextStyle(
                      color: mutedText,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}