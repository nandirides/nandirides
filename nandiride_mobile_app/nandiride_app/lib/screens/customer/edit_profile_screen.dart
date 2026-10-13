import 'package:flutter/material.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  static const Color navy = Color(0xFF102A43);
  static const Color gold = Color(0xFFFFC857);
  static const Color pageBg = Color(0xFFF4F7FB);

  final _formKey = GlobalKey<FormState>();

  final _firstName = TextEditingController();
  final _lastName = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();

  bool _initialized = false;
  bool _saving = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_initialized) return;
    _initialized = true;

    final args = ModalRoute.of(context)?.settings.arguments;

    if (args is Map) {
      final name = args['name']?.toString() ?? '';
      final parts = name.trim().split(RegExp(r'\s+'));

      if (name.trim().isNotEmpty) {
        _firstName.text = parts.first;

        if (parts.length > 1) {
          _lastName.text = parts.skip(1).join(' ');
        }
      }

      _phone.text = args['phone']?.toString() ?? '';
      _email.text = args['email']?.toString() ?? '';
    }
  }

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _email.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) return;

    final firstName = _firstName.text.trim();
    final lastName = _lastName.text.trim();
    final email = _email.text.trim();

    final fullName = [firstName, lastName]
        .where((part) => part.isNotEmpty)
        .join(' ');

    setState(() => _saving = true);

    final updatedProfile = <String, String>{
      'name': fullName,
      'phone': _phone.text.trim(),
      'email': email,
    };

    if (!mounted) return;

    setState(() => _saving = false);

    Navigator.pop(context, updatedProfile);
  }

  InputDecoration _decoration({
    required String label,
    required IconData icon,
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
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFE0E7EF)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFE0E7EF)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: navy, width: 1.6),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Colors.redAccent),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(
          color: Colors.redAccent,
          width: 1.6,
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
          'Edit Profile',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
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
                borderRadius: BorderRadius.circular(22),
              ),
              child: const Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: gold,
                    child: Icon(
                      Icons.manage_accounts_rounded,
                      color: navy,
                      size: 31,
                    ),
                  ),
                  SizedBox(width: 15),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Personal Details',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 19,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 5),
                        Text(
                          'Keep your information up to date',
                          style: TextStyle(
                            color: Color(0xFFE4ECF4),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 26),

            const Text(
              'BASIC INFORMATION',
              style: TextStyle(
                color: Color(0xFF66788A),
                fontWeight: FontWeight.bold,
                fontSize: 12,
                letterSpacing: 1.2,
              ),
            ),

            const SizedBox(height: 16),

            // First name
            TextFormField(
              controller: _firstName,
              enabled: !_saving,
              textCapitalization: TextCapitalization.words,
              textInputAction: TextInputAction.next,
              decoration: _decoration(
                label: 'First Name',
                icon: Icons.person_outline_rounded,
                hint: 'Enter your first name',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter your first name';
                }
                return null;
              },
            ),

            const SizedBox(height: 16),

            // Last name
            TextFormField(
              controller: _lastName,
              enabled: !_saving,
              textCapitalization: TextCapitalization.words,
              textInputAction: TextInputAction.next,
              decoration: _decoration(
                label: 'Last Name',
                icon: Icons.person_outline_rounded,
                hint: 'Enter your last name',
              ),
            ),

            const SizedBox(height: 16),

            // Mobile number
            TextFormField(
              controller: _phone,
              enabled: !_saving,
              keyboardType: TextInputType.phone,
              textInputAction: TextInputAction.next,
              maxLength: 10,
              decoration: _decoration(
                label: 'Mobile Number',
                icon: Icons.phone_android_rounded,
                hint: 'Enter 10-digit mobile number',
              ).copyWith(counterText: ''),
              validator: (value) {
                final phone = value?.trim() ?? '';

                if (phone.isNotEmpty &&
                    !RegExp(r'^[6-9]\d{9}$').hasMatch(phone)) {
                  return 'Enter a valid 10-digit Indian mobile number';
                }

                return null;
              },
            ),

            const SizedBox(height: 16),

            // Email
            TextFormField(
              controller: _email,
              enabled: !_saving,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.done,
              decoration: _decoration(
                label: 'Email Address',
                icon: Icons.email_outlined,
                hint: 'example@email.com',
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
              onFieldSubmitted: (_) {
                if (!_saving) {
                  _saveProfile();
                }
              },
            ),

            const SizedBox(height: 28),

            // Save button
            SizedBox(
              height: 54,
              child: ElevatedButton.icon(
                onPressed: _saving ? null : _saveProfile,
                style: ElevatedButton.styleFrom(
                  backgroundColor: navy,
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: Colors.blueGrey,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 2,
                ),
                icon: _saving
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: gold,
                        ),
                      )
                    : const Icon(
                        Icons.save_rounded,
                        color: gold,
                      ),
                label: Text(
                  _saving ? 'Please wait...' : 'Save Changes',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 14),

            const Text(
              'Your name and email will be updated on the server. '
              'Mobile number is not yet connected to server storage.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Color(0xFF718096),
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
