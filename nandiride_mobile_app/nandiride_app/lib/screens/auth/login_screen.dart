
import 'package:flutter/material.dart';
import 'otp_login_screen.dart';
import '../../app/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/token_service.dart';

const Color _navy = Color(0xFF041536);
const Color _navyLight = Color(0xFF102A52);
const Color _gold = Color(0xFFFFC94A);
const Color _goldLight = Color(0xFFFFE6A0);
const Color _background = Color(0xFFF5F7FB);
const Color _textSecondary = Color(0xFF667085);

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _mobileController = TextEditingController();

  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<double> _logoAnimation;

  bool _hidePassword = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    );
    _logoAnimation = Tween<double>(
      begin: 0.85,
      end: 1,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeOutBack,
      ),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _mobileController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    FocusScope.of(context).unfocus();

    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await AuthService.login(
        username: _usernameController.text.trim(),
        password: _passwordController.text,
      );

      debugPrint('LOGIN: API response received.');

      if (!mounted) return;

      final token = response['token'];

      if (token == null || token.toString().trim().isEmpty) {
        debugPrint('LOGIN: Token missing in API response.');
        _showMessage(
          'Login response mein token nahi mila. Auth API response check karein.',
          isError: true,
        );
        return;
      }

      await TokenService.saveToken(token.toString());

      if (!mounted) return;

      Navigator.pushNamedAndRemoveUntil(
        context,
        AppRoutes.home,
        (route) => false,
      );
    } catch (error, stackTrace) {
      debugPrint('LOGIN ERROR: $error');
      debugPrint('LOGIN STACKTRACE: $stackTrace');

      if (!mounted) return;

      _showMessage(
        _friendlyLoginError(error),
        isError: true,
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  String _friendlyLoginError(Object error) {
    final message = error.toString().replaceFirst('Exception: ', '').trim();

    if (message.contains('SocketException') ||
        message.contains('Connection refused') ||
        message.contains('Failed host lookup')) {
      return 'Server se connection nahi ho raha. IP address, Wi-Fi aur Django server check karein.';
    }

    if (message.contains('TimeoutException')) {
      return 'Server response nahi de raha. Dobara try karein.';
    }

    if (message.contains('401') || message.contains('403')) {
      return 'Username ya password galat hai, ya login permission nahi hai.';
    }

    if (message.contains('404')) {
      return 'Login API endpoint nahi mila. Auth API URL check karein.';
    }

    if (message.contains('500')) {
      return 'Server par error aaya hai. Django terminal ka error check karein.';
    }

    if (message.isEmpty) {
      return 'Login nahi ho saka. Django terminal ka error check karein.';
    }

    return 'Login failed: $message';
  }

  void _showMessage(String message, {bool isError = false}) {
    if (!mounted) return;

    final messenger = ScaffoldMessenger.of(context);
    messenger
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(
            message,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
          behavior: SnackBarBehavior.fixed,
          backgroundColor: isError ? const Color(0xFFB42318) : _navy,
          duration: const Duration(seconds: 4),
        ),
      );
  }

  void _openOtpLogin() {
    FocusScope.of(context).unfocus();

    final mobile = _mobileController.text.trim();

    if (!RegExp(r'^[6-9]\d{9}$').hasMatch(mobile)) {
      _showMessage(
        'Valid 10-digit mobile number enter karein.',
        isError: true,
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => OtpLoginScreen(mobileNumber: mobile),
      ),
    );
  }

  InputDecoration _inputDecoration({
    required String label,
    required IconData icon,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      labelText: label,
      prefixIcon: Icon(icon, color: _navyLight, size: 20),
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: _background,
      isDense: true,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 14,
        vertical: 14,
      ),
      labelStyle: const TextStyle(
        color: _textSecondary,
        fontSize: 12,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(13),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(13),
        borderSide: const BorderSide(color: Color(0xFFE3E8F0)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(13),
        borderSide: const BorderSide(color: _gold, width: 1.7),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(13),
        borderSide: const BorderSide(color: Color(0xFFB42318)),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(13),
        borderSide: const BorderSide(
          color: Color(0xFFB42318),
          width: 1.5,
        ),
      ),
    );
  }

  Widget _buildLogo() {
    return ScaleTransition(
      scale: _logoAnimation,
      child: Container(
        width: 68,
        height: 68,
        padding: const EdgeInsets.all(7),
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          border: Border.all(color: _gold, width: 2),
          boxShadow: [
            BoxShadow(
              color: _gold.withValues(alpha: 0.20),
              blurRadius: 18,
              spreadRadius: 1,
            ),
          ],
        ),
        child: ClipOval(
          child: Image.asset(
            'assets/images/nandiride_logo.png',
            fit: BoxFit.contain,
            errorBuilder: (context, error, stackTrace) {
              return const ColoredBox(
                color: _navy,
                child: Icon(
                  Icons.two_wheeler_rounded,
                  color: _gold,
                  size: 35,
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildBrand() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const SizedBox(height: 8),
        const Text.rich(
          TextSpan(
            children: [
              TextSpan(
                text: 'Nandi',
                style: TextStyle(color: Colors.white),
              ),
              TextSpan(
                text: 'Ride',
                style: TextStyle(color: _gold),
              ),
            ],
          ),
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 30,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.8,
            height: 1.05,
          ),
        ),
        const SizedBox(height: 7),
        Container(
          width: 42,
          height: 3,
          decoration: BoxDecoration(
            color: _gold,
            borderRadius: BorderRadius.circular(10),
          ),
        ),
        const SizedBox(height: 7),
        const Text(
          'Haridwar ki ride, aapke saath.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Color(0xFFD6DEED),
            fontSize: 11,
            letterSpacing: 0.2,
          ),
        ),
      ],
    );
  }

  Widget _buildMobileLogin() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Row(
          children: [
            Icon(
              Icons.phone_android_rounded,
              color: _navy,
              size: 19,
            ),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'Login with Mobile Number',
                style: TextStyle(
                  color: _navy,
                  fontSize: 13,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _mobileController,
          keyboardType: TextInputType.phone,
          maxLength: 10,
          decoration: _inputDecoration(
            label: '10-digit Mobile Number',
            icon: Icons.call_outlined,
          ).copyWith(
            counterText: '',
            prefixIcon: Padding(
              padding: const EdgeInsets.only(left: 12, right: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    '+91',
                    style: TextStyle(
                      color: _navy,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(width: 9),
                  Container(
                    width: 1,
                    height: 20,
                    color: const Color(0xFFD0D5DD),
                  ),
                  const SizedBox(width: 8),
                  const Icon(
                    Icons.phone_android_rounded,
                    color: _navyLight,
                    size: 19,
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 9),
        SizedBox(
          height: 43,
          child: OutlinedButton.icon(
            onPressed: _isLoading ? null : _openOtpLogin,
            icon: const Icon(Icons.sms_outlined, size: 18),
            label: const Text(
              'Continue with OTP',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w800,
              ),
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: _navy,
              side: const BorderSide(color: _gold, width: 1.4),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return const Row(
      children: [
        Expanded(child: Divider(color: Color(0xFFE3E8F0))),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 10),
          child: Text(
            'OR LOGIN WITH',
            style: TextStyle(
              color: _textSecondary,
              fontSize: 9,
              fontWeight: FontWeight.w800,
              letterSpacing: 1,
            ),
          ),
        ),
        Expanded(child: Divider(color: Color(0xFFE3E8F0))),
      ],
    );
  }

  Widget _buildPasswordLogin() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            controller: _usernameController,
            textInputAction: TextInputAction.next,
            autocorrect: false,
            decoration: _inputDecoration(
              label: 'Username',
              icon: Icons.person_outline_rounded,
            ),
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Enter username';
              }
              return null;
            },
          ),
          const SizedBox(height: 10),
          TextFormField(
            controller: _passwordController,
            obscureText: _hidePassword,
            enableSuggestions: false,
            autocorrect: false,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) {
              if (!_isLoading) _login();
            },
            decoration: _inputDecoration(
              label: 'Password',
              icon: Icons.lock_outline_rounded,
              suffixIcon: IconButton(
                visualDensity: VisualDensity.compact,
                onPressed: () {
                  setState(() => _hidePassword = !_hidePassword);
                },
                icon: Icon(
                  _hidePassword
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                  color: _textSecondary,
                  size: 19,
                ),
              ),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Enter password';
              }
              return null;
            },
          ),
          const SizedBox(height: 14),
          SizedBox(
            height: 47,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _login,
              style: ElevatedButton.styleFrom(
                backgroundColor: _gold,
                foregroundColor: _navy,
                disabledBackgroundColor: const Color(0xFFE7D6A7),
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(13),
                ),
              ),
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 180),
                child: _isLoading
                    ? const SizedBox(
                        key: ValueKey('loading'),
                        width: 21,
                        height: 21,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.3,
                          color: _navy,
                        ),
                      )
                    : const Row(
                        key: ValueKey('login'),
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Login Securely',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                          SizedBox(width: 8),
                          Icon(
                            Icons.arrow_forward_rounded,
                            size: 19,
                          ),
                        ],
                      ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoginCard() {
    return Container(
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(23),
        border: Border.all(color: const Color(0xFFE9EDF4)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.12),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Welcome Back!',
            style: TextStyle(
              color: _navy,
              fontSize: 22,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.4,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Login karein aur apna safar shuru karein.',
            style: TextStyle(
              color: _textSecondary,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 16),
          _buildMobileLogin(),
          const SizedBox(height: 15),
          _buildDivider(),
          const SizedBox(height: 15),
          _buildPasswordLogin(),
          const SizedBox(height: 12),
          Center(
            child: Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                const Text(
                  "Don't have an account? ",
                  style: TextStyle(
                    color: _textSecondary,
                    fontSize: 11,
                  ),
                ),
                TextButton(
                  onPressed: _isLoading
                      ? null
                      : () {
                          Navigator.pushNamed(
                            context,
                            AppRoutes.register,
                          );
                        },
                  style: TextButton.styleFrom(
                    foregroundColor: _navy,
                    padding: const EdgeInsets.symmetric(horizontal: 3),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: const Text(
                    'Create Account',
                    style: TextStyle(
                      fontWeight: FontWeight.w900,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrustLine() {
    return const Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.shield_outlined,
          color: _goldLight,
          size: 15,
        ),
        SizedBox(width: 7),
        Flexible(
          child: Text(
            'SAFE  •  SIMPLE  •  RELIABLE',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 9,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.1,
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
      resizeToAvoidBottomInset: true,
      body: Stack(
        children: [
          Positioned(
            top: -100,
            right: -90,
            child: IgnorePointer(
              child: Container(
                width: 260,
                height: 260,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _gold.withValues(alpha: 0.07),
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 80,
            left: -130,
            child: IgnorePointer(
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.035),
                ),
              ),
            ),
          ),
          SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) {
                final horizontalPadding =
                    constraints.maxWidth < 360 ? 14.0 : 20.0;
                final availableWidth =
                    (constraints.maxWidth - horizontalPadding * 2)
                        .clamp(0.0, 460.0);

                return SingleChildScrollView(
                  keyboardDismissBehavior:
                      ScrollViewKeyboardDismissBehavior.onDrag,
                  padding: EdgeInsets.symmetric(
                    horizontal: horizontalPadding,
                    vertical: 12,
                  ),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight - 24,
                    ),
                    child: Center(
                      child: FadeTransition(
                        opacity: _fadeAnimation,
                        child: SizedBox(
                          width: availableWidth,
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              _buildLogo(),
                              _buildBrand(),
                              const SizedBox(height: 17),
                              _buildLoginCard(),
                              const SizedBox(height: 14),
                              _buildTrustLine(),
                              const SizedBox(height: 5),
                              const Text(
                                'NandiRide • Haridwar',
                                style: TextStyle(
                                  color: Color(0xFFB8C5DA),
                                  fontSize: 10,
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
        ],
      ),
    );
  }
}
