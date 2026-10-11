import 'package:flutter/material.dart';

import '../../services/auth_service.dart';
import '../../app/app_routes.dart';
import '../../widgets/app_button.dart';

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

  Future<void> _register() async {
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

      final message =
          response['message']?.toString() ??
          response['detail']?.toString() ??
          'Registration successful! Please login.';

      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(message)));

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
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              const Text(
                'Join NandiRide',
                style: TextStyle(fontSize: 27, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('Create your passenger account.'),
              const SizedBox(height: 24),

              TextFormField(
                controller: _firstName,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(
                  labelText: 'First name',
                  prefixIcon: Icon(Icons.person_outline),
                ),
                validator: (v) => _required(v, 'first name'),
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _lastName,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(labelText: 'Last name'),
                validator: (v) => _required(v, 'last name'),
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _username,
                decoration: const InputDecoration(
                  labelText: 'Username',
                  prefixIcon: Icon(Icons.alternate_email),
                ),
                validator: (v) => _required(v, 'username'),
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _email,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email_outlined),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Please enter email';
                  }
                  if (!value.contains('@') || !value.contains('.')) {
                    return 'Enter a valid email';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _phone,
                keyboardType: TextInputType.phone,
                maxLength: 10,
                decoration: const InputDecoration(
                  labelText: '10-digit phone number',
                  prefixIcon: Icon(Icons.phone_outlined),
                  counterText: '',
                ),
                validator: (value) {
                  if (value == null ||
                      !RegExp(r'^\d{10}$').hasMatch(value.trim())) {
                    return 'Enter a valid 10-digit number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _password,
                obscureText: _hidePassword,
                decoration: InputDecoration(
                  labelText: 'Password',
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    onPressed: () {
                      setState(() {
                        _hidePassword = !_hidePassword;
                      });
                    },
                    icon: Icon(
                      _hidePassword ? Icons.visibility : Icons.visibility_off,
                    ),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.length < 8) {
                    return 'Password must be at least 8 characters';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _confirmPassword,
                obscureText: _hideConfirmPassword,
                decoration: InputDecoration(
                  labelText: 'Confirm password',
                  prefixIcon: const Icon(Icons.lock_reset),
                  suffixIcon: IconButton(
                    onPressed: () {
                      setState(() {
                        _hideConfirmPassword = !_hideConfirmPassword;
                      });
                    },
                    icon: Icon(
                      _hideConfirmPassword
                          ? Icons.visibility
                          : Icons.visibility_off,
                    ),
                  ),
                ),
                validator: (value) {
                  if (value != _password.text) {
                    return 'Passwords do not match';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              AppButton(
                label: _isLoading ? 'Creating Account...' : 'Create Account',
                icon: Icons.person_add_alt_1,
                isLoading: _isLoading,
                onPressed: () {
                  if (!_isLoading) {
                    _register();
                  }
                },
              ),
              const SizedBox(height: 12),

              TextButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, AppRoutes.login);
                },
                child: const Text('Already registered? Login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
