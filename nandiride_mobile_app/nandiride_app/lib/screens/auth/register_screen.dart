
import 'package:flutter/material.dart';
import '../../services/auth_service.dart';
import '../../app/app_routes.dart';
import '../../widgets/app_button.dart';

const Color _navy = Color(0xFF041536);
const Color _navyLight = Color(0xFF102A52);
const Color _gold = Color(0xFFFFC94A);
const Color _background = Color(0xFFF5F7FB);
const Color _secondaryText = Color(0xFF667085);

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstName = TextEditingController();
  final _lastName = TextEditingController();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _password = TextEditingController();
  final _confirmPassword = TextEditingController();

  bool _hidePassword = true;
  bool _hideConfirmPassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _username.dispose();
    _email.dispose();
    _phone.dispose();
    _password.dispose();
    _confirmPassword.dispose();
    super.dispose();
  }

  String? _required(String? value, String field) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter $field';
    }
    return null;
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
        horizontal: 12,
        vertical: 15,
      ),
      labelStyle: const TextStyle(
        color: _secondaryText,
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
        borderSide: const BorderSide(color: _gold, width: 1.6),
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

  Future<void> _register() async {
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await AuthService.register(
        firstName: _firstName.text.trim(),
        lastName: _lastName.text.trim(),
        username: _username.text.trim(),
        email: _email.text.trim(),
        phone: _phone.text.trim(),
        password: _password.text,
        password2: _confirmPassword.text,
      );

      if (!mounted) return;

      final message = response['message']?.toString() ??
          response['detail']?.toString() ??
          'Registration successful! Please login.';

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: _navy,
          behavior: SnackBarBehavior.floating,
        ),
      );

      Navigator.pushReplacementNamed(context, AppRoutes.login);
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Registration failed: '
            '${error.toString().replaceFirst('Exception: ', '')}',
          ),
          duration: const Duration(seconds: 5),
          backgroundColor: const Color(0xFFB42318),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Widget _buildNameFields() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: TextFormField(
            controller: _firstName,
            textCapitalization: TextCapitalization.words,
            textInputAction: TextInputAction.next,
            decoration: _inputDecoration(
              label: 'First Name',
              icon: Icons.person_outline_rounded,
            ),
            validator: (value) => _required(value, 'first name'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: TextFormField(
            controller: _lastName,
            textCapitalization: TextCapitalization.words,
            textInputAction: TextInputAction.next,
            decoration: _inputDecoration(
              label: 'Last Name',
              icon: Icons.person_outline_rounded,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPasswordField() {
    return TextFormField(
      controller: _password,
      obscureText: _hidePassword,
      enableSuggestions: false,
      autocorrect: false,
      textInputAction: TextInputAction.next,
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
            color: _secondaryText,
            size: 20,
          ),
        ),
      ),
      validator: (value) {
        if (value == null || value.length < 8) {
          return 'Password must be at least 8 characters';
        }
        return null;
      },
    );
  }

  Widget _buildConfirmPasswordField() {
    return TextFormField(
      controller: _confirmPassword,
      obscureText: _hideConfirmPassword,
      enableSuggestions: false,
      autocorrect: false,
      textInputAction: TextInputAction.done,
      onFieldSubmitted: (_) {
        if (!_isLoading) _register();
      },
      decoration: _inputDecoration(
        label: 'Confirm Password',
        icon: Icons.lock_reset_rounded,
        suffixIcon: IconButton(
          visualDensity: VisualDensity.compact,
          onPressed: () {
            setState(() {
              _hideConfirmPassword = !_hideConfirmPassword;
            });
          },
          icon: Icon(
            _hideConfirmPassword
                ? Icons.visibility_outlined
                : Icons.visibility_off_outlined,
            color: _secondaryText,
            size: 20,
          ),
        ),
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please confirm your password';
        }
        if (value != _password.text) {
          return 'Passwords do not match';
        }
        return null;
      },
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        Container(
          width: 66,
          height: 66,
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            border: Border.all(color: _gold, width: 2),
            boxShadow: [
              BoxShadow(
                color: _gold.withValues(alpha: 0.20),
                blurRadius: 16,
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
                    size: 34,
                  ),
                );
              },
            ),
          ),
        ),
        const SizedBox(height: 10),
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
            fontSize: 28,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.6,
          ),
        ),
        const SizedBox(height: 5),
        const Text(
          'YOUR RIDE  •  OUR PRIORITY',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Color(0xFFD6DEED),
            fontSize: 9,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.5,
          ),
        ),
      ],
    );
  }

  Widget _buildRegisterCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(23),
        border: Border.all(color: const Color(0xFFE9EDF4)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.10),
            blurRadius: 24,
            offset: const Offset(0, 9),
          ),
        ],
      ),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Create Account',
              style: TextStyle(
                color: _navy,
                fontSize: 23,
                fontWeight: FontWeight.w900,
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 5),
            const Text(
              'Join NandiRide and start your journey.',
              style: TextStyle(
                color: _secondaryText,
                fontSize: 11,
              ),
            ),
            const SizedBox(height: 19),
            _buildNameFields(),
            const SizedBox(height: 13),
            TextFormField(
              controller: _username,
              textInputAction: TextInputAction.next,
              autocorrect: false,
              decoration: _inputDecoration(
                label: 'Username',
                icon: Icons.alternate_email_rounded,
              ),
              validator: (value) => _required(value, 'username'),
            ),
            const SizedBox(height: 13),
            TextFormField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              autocorrect: false,
              decoration: _inputDecoration(
                label: 'Email Address',
                icon: Icons.email_outlined,
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter email';
                }
                if (!RegExp(
                  r'^[^@\s]+@[^@\s]+\.[^@\s]+$',
                ).hasMatch(value.trim())) {
                  return 'Enter a valid email';
                }
                return null;
              },
            ),
            const SizedBox(height: 13),
            TextFormField(
              controller: _phone,
              keyboardType: TextInputType.phone,
              textInputAction: TextInputAction.next,
              maxLength: 10,
              decoration: _inputDecoration(
                label: '10-digit Phone Number',
                icon: Icons.phone_outlined,
              ).copyWith(counterText: ''),
              validator: (value) {
                if (value == null ||
                    !RegExp(r'^[6-9]\d{9}$').hasMatch(value.trim())) {
                  return 'Enter a valid 10-digit mobile number';
                }
                return null;
              },
            ),
            const SizedBox(height: 13),
            _buildPasswordField(),
            const SizedBox(height: 13),
            _buildConfirmPasswordField(),
            const SizedBox(height: 20),
            SizedBox(
              height: 49,
              child: AppButton(
                label: _isLoading
                    ? 'Creating Account...'
                    : 'Create Account',
                icon: Icons.person_add_alt_1_rounded,
                isLoading: _isLoading,
                onPressed: () {
                  if (!_isLoading) _register();
                },
              ),
            ),
            const SizedBox(height: 10),
            Center(
              child: Wrap(
                alignment: WrapAlignment.center,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  const Text(
                    'Already registered? ',
                    style: TextStyle(
                      color: _secondaryText,
                      fontSize: 12,
                    ),
                  ),
                  TextButton(
                    onPressed: _isLoading
                        ? null
                        : () {
                            Navigator.pushReplacementNamed(
                              context,
                              AppRoutes.login,
                            );
                          },
                    style: TextButton.styleFrom(
                      foregroundColor: _navy,
                      padding: const EdgeInsets.symmetric(horizontal: 3),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    child: const Text(
                      'Login',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
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
        centerTitle: true,
        title: const Text(
          'Join NandiRide',
          style: TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: Stack(
        children: [
          Positioned(
            top: -90,
            right: -80,
            child: Container(
              width: 230,
              height: 230,
              decoration: BoxDecoration(
                color: _gold.withValues(alpha: 0.06),
                shape: BoxShape.circle,
              ),
            ),
          ),
          SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) {
                final horizontalPadding =
                    constraints.maxWidth < 360 ? 12.0 : 20.0;
                final contentWidth =
                    (constraints.maxWidth - horizontalPadding * 2)
                        .clamp(0.0, 460.0);

                return Center(
                  child: SingleChildScrollView(
                    keyboardDismissBehavior:
                        ScrollViewKeyboardDismissBehavior.onDrag,
                    padding: EdgeInsets.fromLTRB(
                      horizontalPadding,
                      8,
                      horizontalPadding,
                      18,
                    ),
                    child: ConstrainedBox(
                      constraints: BoxConstraints(
                        minWidth: contentWidth,
                        maxWidth: contentWidth,
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _buildHeader(),
                          const SizedBox(height: 19),
                          _buildRegisterCard(),
                          const SizedBox(height: 15),
                          const Text(
                            'SAFE  •  SIMPLE  •  RELIABLE',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Color(0xFFD6DEED),
                              fontSize: 9,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.2,
                            ),
                          ),
                        ],
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
