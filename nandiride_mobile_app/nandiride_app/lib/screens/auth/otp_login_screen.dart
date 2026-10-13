import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

const Color _navy = Color(0xFF041536);
const Color _navyLight = Color(0xFF102A52);
const Color _gold = Color(0xFFFFC94A);
const Color _goldLight = Color(0xFFFFE6A0);
const Color _surface = Color(0xFFF5F7FB);
const Color _border = Color(0xFFE3E8F0);
const Color _textSecondary = Color(0xFF667085);

class OtpLoginScreen extends StatefulWidget {
  final String? mobileNumber;

  const OtpLoginScreen({
    super.key,
    this.mobileNumber,
  });

  @override
  State<OtpLoginScreen> createState() => _OtpLoginScreenState();
}

class _OtpLoginScreenState extends State<OtpLoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _mobileController = TextEditingController();
  final _otpController = TextEditingController();
  final _mobileFocus = FocusNode();
  final _otpFocus = FocusNode();

  bool _otpSent = false;
  bool _isLoading = false;
  int _secondsRemaining = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();

    final initialMobile = widget.mobileNumber?.replaceAll(
      RegExp(r'\D'),
      '',
    );

    if (initialMobile != null && initialMobile.isNotEmpty) {
      _mobileController.text = initialMobile.length > 10
          ? initialMobile.substring(initialMobile.length - 10)
          : initialMobile;
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _mobileController.dispose();
    _otpController.dispose();
    _mobileFocus.dispose();
    _otpFocus.dispose();
    super.dispose();
  }

  void _showMessage(
    String message, {
    bool isError = false,
  }) {
    if (!mounted) return;

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(
                isError
                    ? Icons.error_outline_rounded
                    : Icons.info_outline_rounded,
                color: Colors.white,
              ),
              const SizedBox(width: 10),
              Expanded(child: Text(message)),
            ],
          ),
          backgroundColor: isError ? const Color(0xFFB42318) : _navyLight,
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      );
  }

  String get _mobile => _mobileController.text.trim();

  void _startTimer() {
    _timer?.cancel();

    setState(() => _secondsRemaining = 30);

    _timer = Timer.periodic(
      const Duration(seconds: 1),
      (timer) {
        if (!mounted) {
          timer.cancel();
          return;
        }

        if (_secondsRemaining <= 1) {
          timer.cancel();
          setState(() => _secondsRemaining = 0);
        } else {
          setState(() => _secondsRemaining--);
        }
      },
    );
  }

  Future<void> _sendOtp() async {
    FocusScope.of(context).unfocus();

    if (_isLoading) return;

    final mobile = _mobileController.text.trim();

    if (!RegExp(r'^[6-9]\d{9}$').hasMatch(mobile)) {
      _showMessage(
        'Valid 10-digit mobile number enter karein.',
        isError: true,
      );
      return;
    }

    setState(() {
      _otpSent = true;
      _otpController.clear();
    });

    _startTimer();

    _showMessage(
      'Testing mode: OTP field khul gayi hai. SMS send nahi hua.',
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _otpFocus.requestFocus();
    });
  }

  Future<void> _verifyOtp() async {
    FocusScope.of(context).unfocus();

    if (_isLoading) return;

    final otp = _otpController.text.trim();

    if (!RegExp(r'^\d{6}$').hasMatch(otp)) {
      _showMessage(
        '6-digit OTP enter karein.',
        isError: true,
      );
      _otpFocus.requestFocus();
      return;
    }

    setState(() => _isLoading = true);

    try {
      // TODO: Django Verify OTP API connect karein.
      // Sirf backend verification successful hone par token save karein
      // aur Home screen par navigate karein.
      await Future<void>.delayed(const Duration(milliseconds: 250));

      if (!mounted) return;

      _showMessage(
        'OTP verification API connect nahi hai. Login complete nahi hua.',
        isError: true,
      );
    } catch (_) {
      if (!mounted) return;
      _showMessage(
        'OTP verify nahi ho saka. Dobara try karein.',
        isError: true,
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _resendOtp() async {
    if (_secondsRemaining > 0 || _isLoading) return;

    _otpController.clear();
    await _sendOtp();
  }

  void _changeMobileNumber() {
    _timer?.cancel();

    setState(() {
      _otpSent = false;
      _secondsRemaining = 0;
      _otpController.clear();
    });

    _mobileFocus.requestFocus();
  }

  InputDecoration _inputDecoration({
    required String hint,
    Widget? prefixIcon,
    Widget? prefix,
  }) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(
        color: _textSecondary,
        fontSize: 14,
      ),
      prefixIcon: prefixIcon,
      prefix: prefix,
      filled: true,
      fillColor: _surface,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 17,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(color: _border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(color: _border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: _gold,
          width: 1.8,
        ),
      ),
      disabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(color: _border),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(color: Color(0xFFD92D20)),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15),
        borderSide: const BorderSide(
          color: Color(0xFFD92D20),
          width: 1.5,
        ),
      ),
    );
  }

  Widget _sectionLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),
      child: Text(
        label,
        style: const TextStyle(
          color: _navy,
          fontSize: 14,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  Widget _buildMobileField() {
    return TextFormField(
      controller: _mobileController,
      focusNode: _mobileFocus,
      keyboardType: TextInputType.phone,
      textInputAction: TextInputAction.done,
      enabled: !_otpSent && !_isLoading,
      maxLength: 10,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(10),
      ],
      decoration: _inputDecoration(
        hint: 'Enter mobile number',
        prefix: const Padding(
          padding: EdgeInsets.only(right: 10),
          child: Text(
            '+91',
            style: TextStyle(
              color: _navy,
              fontWeight: FontWeight.w900,
              fontSize: 14,
            ),
          ),
        ),
      ).copyWith(counterText: ''),
      style: const TextStyle(
        color: _navy,
        fontWeight: FontWeight.w700,
        letterSpacing: 1,
      ),
      validator: (value) {
        final mobile = value?.trim() ?? '';

        if (!RegExp(r'^[6-9]\d{9}$').hasMatch(mobile)) {
          return 'Valid 10-digit mobile number enter karein.';
        }

        return null;
      },
      onFieldSubmitted: (_) {
        if (!_otpSent) _sendOtp();
      },
    );
  }

  Widget _buildOtpField() {
    return TextFormField(
      controller: _otpController,
      focusNode: _otpFocus,
      keyboardType: TextInputType.number,
      textInputAction: TextInputAction.done,
      maxLength: 6,
      autofocus: false,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(6),
      ],
      decoration: _inputDecoration(
        hint: 'Enter 6-digit OTP',
        prefixIcon: const Icon(
          Icons.lock_outline_rounded,
          color: _navyLight,
        ),
      ).copyWith(counterText: ''),
      style: const TextStyle(
        color: _navy,
        fontWeight: FontWeight.w800,
        fontSize: 18,
        letterSpacing: 5,
      ),
      validator: (value) {
        if (!RegExp(r'^\d{6}$').hasMatch(value?.trim() ?? '')) {
          return '6-digit OTP enter karein.';
        }

        return null;
      },
      onFieldSubmitted: (_) => _verifyOtp(),
    );
  }

  Widget _buildPrimaryButton() {
    return SizedBox(
      height: 55,
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading
            ? null
            : (_otpSent ? _verifyOtp : _sendOtp),
        style: ElevatedButton.styleFrom(
          backgroundColor: _gold,
          foregroundColor: _navy,
          disabledBackgroundColor: _goldLight,
          disabledForegroundColor: _navyLight,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
        ),
        child: _isLoading
            ? const SizedBox(
                width: 23,
                height: 23,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  valueColor: AlwaysStoppedAnimation<Color>(_navy),
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    _otpSent
                        ? Icons.verified_user_rounded
                        : Icons.sms_outlined,
                    size: 21,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    _otpSent ? 'Verify OTP' : 'Send OTP',
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Icon(
                    Icons.arrow_forward_rounded,
                    size: 19,
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildOtpOptions() {
    if (!_otpSent) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _sectionLabel('Enter 6-Digit OTP'),
        _buildOtpField(),
        const SizedBox(height: 8),
        Row(
          children: [
            const Icon(
              Icons.mark_email_read_outlined,
              color: _textSecondary,
              size: 17,
            ),
            const SizedBox(width: 7),
            Expanded(
              child: Text(
                'OTP for +91 $_mobile',
                style: const TextStyle(
                  color: _textSecondary,
                  fontSize: 12,
                ),
              ),
            ),
            TextButton(
              onPressed: _isLoading ? null : _changeMobileNumber,
              style: TextButton.styleFrom(
                foregroundColor: _navy,
                padding: const EdgeInsets.symmetric(horizontal: 5),
              ),
              child: const Text(
                'Change',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ],
        ),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton(
            onPressed: _secondsRemaining > 0 || _isLoading
                ? null
                : _resendOtp,
            style: TextButton.styleFrom(
              foregroundColor: _navy,
            ),
            child: Text(
              _secondsRemaining > 0
                  ? 'Resend OTP in ${_secondsRemaining}s'
                  : 'Resend OTP',
              style: const TextStyle(
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _navy,
      appBar: AppBar(
        backgroundColor: _navy,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        title: const Text(
          'Mobile OTP Login',
          style: TextStyle(
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
      ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              keyboardDismissBehavior:
                  ScrollViewKeyboardDismissBehavior.onDrag,
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 430),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(26),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.16),
                          blurRadius: 30,
                          offset: const Offset(0, 12),
                        ),
                      ],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Center(
                            child: Container(
                              width: 84,
                              height: 84,
                              decoration: BoxDecoration(
                                color: const Color(0xFFFFF4D6),
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: _gold,
                                  width: 1.5,
                                ),
                              ),
                              child: const Icon(
                                Icons.phonelink_lock_rounded,
                                color: _navy,
                                size: 40,
                              ),
                            ),
                          ),
                          const SizedBox(height: 22),
                          const Text(
                            'Verify Your Number',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: _navy,
                              fontSize: 25,
                              fontWeight: FontWeight.w900,
                              letterSpacing: -0.5,
                            ),
                          ),
                          const SizedBox(height: 10),
                          const Text(
                            'NandiRide mein login karne ke liye '
                            'apna mobile number enter karein aur '
                            'OTP verification complete karein.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: _textSecondary,
                              fontSize: 13,
                              height: 1.6,
                            ),
                          ),
                          const SizedBox(height: 30),
                          _sectionLabel('Mobile Number'),
                          _buildMobileField(),
                          _buildOtpOptions(),
                          const SizedBox(height: 22),
                          _buildPrimaryButton(),
                          const SizedBox(height: 22),
                          Container(
                            padding: const EdgeInsets.all(13),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFF9E9),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: const Color(0xFFFFE6A0),
                              ),
                            ),
                            child: const Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Icon(
                                  Icons.shield_outlined,
                                  color: _navyLight,
                                  size: 21,
                                ),
                                SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    'Your login is protected. Apna OTP '
                                    'kisi ke saath share na karein.',
                                    style: TextStyle(
                                      color: _navyLight,
                                      fontSize: 12,
                                      height: 1.5,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextButton.icon(
                            onPressed: _isLoading
                                ? null
                                : () => Navigator.maybePop(context),
                            icon: const Icon(
                              Icons.arrow_back_rounded,
                              size: 18,
                            ),
                            label: const Text(
                              'Back to Login',
                              style: TextStyle(
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            style: TextButton.styleFrom(
                              foregroundColor: _navy,
                              padding: const EdgeInsets.symmetric(
                                vertical: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}