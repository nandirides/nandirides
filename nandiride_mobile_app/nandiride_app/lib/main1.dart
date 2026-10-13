import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const NandiRideApp());
}

const brandGreen = Color(0xFF16A66A);
const darkGreen = Color(0xFF087F52);
const navy = Color(0xFF142B3B);
const mint = Color(0xFFE7F8EF);
const pageColor = Color(0xFFF7F9F8);
const muted = Color(0xFF718078);

Route<dynamic> smoothRoute(Widget page) {
  return PageRouteBuilder(
    transitionDuration: const Duration(milliseconds: 350),
    pageBuilder: (_, animation, secondaryAnimation) => page,
    transitionsBuilder: (_, animation, secondaryAnimation, child) {
      final curved = CurvedAnimation(
        parent: animation,
        curve: Curves.easeOutCubic,
      );

      return FadeTransition(
        opacity: curved,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0.035, 0),
            end: Offset.zero,
          ).animate(curved),
          child: child,
        ),
      );
    },
  );
}

void goTo(BuildContext context, Widget page) {
  Navigator.push(context, smoothRoute(page));
}

class NandiRideApp extends StatelessWidget {
  const NandiRideApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NandiRide',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: pageColor,
        colorScheme: ColorScheme.fromSeed(
          seedColor: brandGreen,
          primary: brandGreen,
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: pageColor,
          foregroundColor: navy,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 18,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(17),
            borderSide: const BorderSide(color: Color(0xFFE1E9E4)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(17),
            borderSide: const BorderSide(color: Color(0xFFE1E9E4)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(17),
            borderSide: const BorderSide(color: brandGreen, width: 1.5),
          ),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}

// Original NandiRide logo asset.
class BrandLogo extends StatelessWidget {
  final double size;

  const BrandLogo({super.key, this.size = 76});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(size * 0.27),
        boxShadow: [
          BoxShadow(
            color: brandGreen.withValues(alpha: 0.12),
            blurRadius: 18,
            offset: const Offset(0, 7),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(size * 0.22),
        child: Image.asset(
          'assets/images/nandiride_logo.png',
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              decoration: BoxDecoration(
                color: brandGreen,
                borderRadius: BorderRadius.circular(size * 0.22),
              ),
              child: Icon(
                Icons.route_rounded,
                color: Colors.white,
                size: size * 0.55,
              ),
            );
          },
        ),
      ),
    );
  }
}

class PrimaryButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final IconData? icon;

  const PrimaryButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 57,
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: brandGreen,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              text,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
            ),
            if (icon != null) ...[const SizedBox(width: 10), Icon(icon)],
          ],
        ),
      ),
    );
  }
}

// 1. Animated splash screen

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _logoAnimation;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  static const Color brandGreen = Color(0xFF16A66A);
  static const Color darkGreen = Color(0xFF087F52);
  static const Color navy = Color(0xFF142B3B);
  static const Color mint = Color(0xFFE7F8EF);

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );

    _logoAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    );

    _fadeAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.25, 1, curve: Curves.easeIn),
    );

    _slideAnimation =
        Tween<Offset>(begin: const Offset(0, 0.25), end: Offset.zero).animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.2, 1, curve: Curves.easeOutCubic),
          ),
        );

    _controller.forward();

    Future.delayed(const Duration(milliseconds: 2800), () {
      if (!mounted) return;

      Navigator.pushReplacement(context, smoothRoute(const WelcomeScreen()));
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Top green background shape
          Positioned(
            top: -150,
            right: -100,
            child: Container(
              width: 340,
              height: 340,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: mint.withValues(alpha: 0.9),
              ),
            ),
          ),

          // Bottom navy background shape
          Positioned(
            bottom: -180,
            left: -100,
            child: Container(
              width: 390,
              height: 390,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: navy,
              ),
            ),
          ),

          // Decorative route line
          Positioned(
            right: 30,
            top: MediaQuery.of(context).size.height * 0.34,
            child: Transform.rotate(
              angle: -0.35,
              child: Container(
                width: 100,
                height: 190,
                decoration: BoxDecoration(
                  border: Border.all(
                    color: brandGreen.withValues(alpha: 0.12),
                    width: 3,
                  ),
                  borderRadius: BorderRadius.circular(60),
                ),
              ),
            ),
          ),

          SafeArea(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 28),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Spacer(flex: 3),

                    // Animated logo
                    ScaleTransition(
                      scale: _logoAnimation,
                      child: Container(
                        width: 154,
                        height: 154,
                        padding: const EdgeInsets.all(22),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(42),
                          boxShadow: [
                            BoxShadow(
                              color: brandGreen.withValues(alpha: 0.16),
                              blurRadius: 35,
                              spreadRadius: 2,
                              offset: const Offset(0, 12),
                            ),
                          ],
                          border: Border.all(color: mint, width: 2),
                        ),
                        child: const BrandLogo(),
                      ),
                    ),

                    const SizedBox(height: 30),

                    // Animated app name
                    FadeTransition(
                      opacity: _fadeAnimation,
                      child: SlideTransition(
                        position: _slideAnimation,
                        child: Column(
                          children: [
                            RichText(
                              text: const TextSpan(
                                children: [
                                  TextSpan(
                                    text: 'Nandi',
                                    style: TextStyle(
                                      color: navy,
                                      fontSize: 37,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: -1.4,
                                    ),
                                  ),
                                  TextSpan(
                                    text: 'Ride',
                                    style: TextStyle(
                                      color: brandGreen,
                                      fontSize: 37,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: -1.4,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            const SizedBox(height: 12),

                            const Text(
                              'YOUR RIDE. YOUR WAY.',
                              style: TextStyle(
                                color: Color(0xFF657780),
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 3.0,
                              ),
                            ),

                            const SizedBox(height: 30),

                            // Feature chips
                            Wrap(
                              alignment: WrapAlignment.center,
                              spacing: 9,
                              runSpacing: 10,
                              children: const [
                                _SplashFeature(
                                  icon: Icons.bolt_rounded,
                                  label: 'Quick',
                                ),
                                _SplashFeature(
                                  icon: Icons.location_on_rounded,
                                  label: 'Easy',
                                ),
                                _SplashFeature(
                                  icon: Icons.verified_user_rounded,
                                  label: 'Reliable',
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),

                    const Spacer(flex: 2),

                    // Loading animation
                    FadeTransition(
                      opacity: _fadeAnimation,
                      child: Column(
                        children: [
                          const SizedBox(
                            width: 115,
                            child: LinearProgressIndicator(
                              minHeight: 4,
                              backgroundColor: mint,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                brandGreen,
                              ),
                              borderRadius: BorderRadius.all(
                                Radius.circular(20),
                              ),
                            ),
                          ),
                          const SizedBox(height: 14),
                          Text(
                            'Getting your ride ready...',
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.9),
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),

                    const Spacer(),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SplashFeature extends StatelessWidget {
  final IconData icon;
  final String label;

  const _SplashFeature({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
      decoration: BoxDecoration(
        color: const Color(0xFFE7F8EF),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: const Color(0xFFD1F0DF)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: const Color(0xFF087F52)),
          const SizedBox(width: 6),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: Color(0xFF142B3B),
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

// 2. Welcome screen

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen>
    with TickerProviderStateMixin {
  late final AnimationController _entranceController;
  late final AnimationController _floatController;

  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _textSlideAnimation;
  late final Animation<double> _heroScaleAnimation;
  late final Animation<double> _floatAnimation;

  @override
  void initState() {
    super.initState();

    _entranceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _entranceController,
      curve: const Interval(0.15, 1, curve: Curves.easeOut),
    );

    _textSlideAnimation =
        Tween<Offset>(begin: const Offset(0, 0.16), end: Offset.zero).animate(
          CurvedAnimation(
            parent: _entranceController,
            curve: const Interval(0.12, 1, curve: Curves.easeOutCubic),
          ),
        );

    _heroScaleAnimation = Tween<double>(begin: 0.88, end: 1).animate(
      CurvedAnimation(
        parent: _entranceController,
        curve: const Interval(0, 0.85, curve: Curves.easeOutBack),
      ),
    );

    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1900),
    )..repeat(reverse: true);

    _floatAnimation = Tween<double>(begin: -7, end: 7).animate(
      CurvedAnimation(parent: _floatController, curve: Curves.easeInOut),
    );

    _entranceController.forward();
  }

  @override
  void dispose() {
    _entranceController.dispose();
    _floatController.dispose();
    super.dispose();
  }

  void _getStarted() {
    goTo(context, const RoleSelectionScreen());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Soft decorative background
          Positioned(
            top: -105,
            right: -100,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                color: mint.withValues(alpha: 0.8),
                shape: BoxShape.circle,
              ),
            ),
          ),
          Positioned(
            top: 280,
            left: -120,
            child: Container(
              width: 190,
              height: 190,
              decoration: BoxDecoration(
                color: brandGreen.withValues(alpha: 0.045),
                shape: BoxShape.circle,
              ),
            ),
          ),

          SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) {
                return SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(23, 15, 23, 20),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight - 35,
                    ),
                    child: IntrinsicHeight(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Brand header
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: Row(
                              children: [
                                const BrandLogo(size: 49),
                                const SizedBox(width: 11),
                                const Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'NandiRide',
                                        style: TextStyle(
                                          color: navy,
                                          fontSize: 23,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: -0.8,
                                        ),
                                      ),
                                      SizedBox(height: 3),
                                      Text(
                                        'YOUR RIDE. YOUR WAY.',
                                        style: TextStyle(
                                          color: darkGreen,
                                          fontSize: 9,
                                          letterSpacing: 1.7,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 11,
                                    vertical: 8,
                                  ),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF1F8F3),
                                    borderRadius: BorderRadius.circular(30),
                                    border: Border.all(
                                      color: const Color(0xFFDDEFE4),
                                    ),
                                  ),
                                  child: const Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.circle,
                                        color: brandGreen,
                                        size: 8,
                                      ),
                                      SizedBox(width: 6),
                                      Text(
                                        'Ride easy',
                                        style: TextStyle(
                                          color: darkGreen,
                                          fontSize: 11,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const SizedBox(height: 30),

                          // Animated headline
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _textSlideAnimation,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Welcome To Nandiride',
                                    style: TextStyle(
                                      color: brandGreen,
                                      fontSize: 37,
                                      height: 1.12,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: -1.5,
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  const Text(
                                    'Your journey, your choice. Find a ride '
                                    'that fits your day.',
                                    style: TextStyle(
                                      color: muted,
                                      fontSize: 14,
                                      height: 1.6,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          const SizedBox(height: 23),

                          // Animated hero illustration
                          ScaleTransition(
                            scale: _heroScaleAnimation,
                            child: Container(
                              height: 238,
                              width: double.infinity,
                              clipBehavior: Clip.antiAlias,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(29),
                                gradient: const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFFEAF9F0),
                                    Color(0xFFD5F2E1),
                                    Color(0xFFBCE8D0),
                                  ],
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: brandGreen.withValues(alpha: 0.10),
                                    blurRadius: 24,
                                    offset: const Offset(0, 10),
                                  ),
                                ],
                              ),
                              child: Stack(
                                children: [
                                  // Background circles
                                  Positioned(
                                    top: -65,
                                    right: -30,
                                    child: Container(
                                      width: 190,
                                      height: 190,
                                      decoration: BoxDecoration(
                                        color: Colors.white.withValues(
                                          alpha: 0.35,
                                        ),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),
                                  Positioned(
                                    bottom: -85,
                                    left: 30,
                                    child: Container(
                                      width: 200,
                                      height: 200,
                                      decoration: BoxDecoration(
                                        color: brandGreen.withValues(
                                          alpha: 0.07,
                                        ),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),

                                  // Route decoration
                                  Positioned(
                                    left: 36,
                                    top: 49,
                                    child: Container(
                                      width: 102,
                                      height: 93,
                                      decoration: BoxDecoration(
                                        border: Border.all(
                                          color: brandGreen.withValues(
                                            alpha: 0.3,
                                          ),
                                          width: 2,
                                        ),
                                        borderRadius: BorderRadius.circular(48),
                                      ),
                                    ),
                                  ),

                                  // Animated pickup pin
                                  AnimatedBuilder(
                                    animation: _floatAnimation,
                                    builder: (context, child) {
                                      return Positioned(
                                        left: 23,
                                        top: 23 + _floatAnimation.value,
                                        child: child!,
                                      );
                                    },
                                    child: Container(
                                      width: 54,
                                      height: 54,
                                      decoration: BoxDecoration(
                                        color: Colors.white,
                                        borderRadius: BorderRadius.circular(19),
                                        boxShadow: [
                                          BoxShadow(
                                            color: darkGreen.withValues(
                                              alpha: 0.10,
                                            ),
                                            blurRadius: 15,
                                            offset: const Offset(0, 6),
                                          ),
                                        ],
                                      ),
                                      child: const Icon(
                                        Icons.location_on_rounded,
                                        color: brandGreen,
                                        size: 30,
                                      ),
                                    ),
                                  ),

                                  // Animated vehicle card
                                  AnimatedBuilder(
                                    animation: _floatAnimation,
                                    builder: (context, child) {
                                      return Positioned(
                                        right: 18,
                                        bottom: 25 - _floatAnimation.value,
                                        child: child!,
                                      );
                                    },
                                    child: Container(
                                      width: 143,
                                      height: 145,
                                      decoration: BoxDecoration(
                                        color: Colors.white,
                                        borderRadius: BorderRadius.circular(26),
                                        boxShadow: [
                                          BoxShadow(
                                            color: navy.withValues(alpha: 0.10),
                                            blurRadius: 25,
                                            offset: const Offset(0, 10),
                                          ),
                                        ],
                                      ),
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          Container(
                                            height: 83,
                                            width: 105,
                                            decoration: BoxDecoration(
                                              color: mint,
                                              borderRadius:
                                                  BorderRadius.circular(22),
                                            ),
                                            child: const Icon(
                                              Icons.electric_rickshaw_rounded,
                                              size: 58,
                                              color: navy,
                                            ),
                                          ),
                                          const SizedBox(height: 10),
                                          const Text(
                                            'Your ride awaits',
                                            style: TextStyle(
                                              color: navy,
                                              fontSize: 11,
                                              fontWeight: FontWeight.w800,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),

                                  // Route destination marker
                                  Positioned(
                                    right: 30,
                                    top: 22,
                                    child: Container(
                                      height: 42,
                                      width: 42,
                                      decoration: BoxDecoration(
                                        color: darkGreen,
                                        borderRadius: BorderRadius.circular(15),
                                        boxShadow: [
                                          BoxShadow(
                                            color: darkGreen.withValues(
                                              alpha: 0.18,
                                            ),
                                            blurRadius: 12,
                                            offset: const Offset(0, 5),
                                          ),
                                        ],
                                      ),
                                      child: const Icon(
                                        Icons.flag_rounded,
                                        color: Colors.white,
                                        size: 22,
                                      ),
                                    ),
                                  ),

                                  // Bottom label
                                  Positioned(
                                    left: 17,
                                    bottom: 19,
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 12,
                                        vertical: 10,
                                      ),
                                      decoration: BoxDecoration(
                                        color: Colors.white.withValues(
                                          alpha: 0.95,
                                        ),
                                        borderRadius: BorderRadius.circular(15),
                                      ),
                                      child: const Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Icon(
                                            Icons.bolt_rounded,
                                            color: brandGreen,
                                            size: 17,
                                          ),
                                          SizedBox(width: 5),
                                          Text(
                                            'Let’s get moving',
                                            style: TextStyle(
                                              color: navy,
                                              fontSize: 11,
                                              fontWeight: FontWeight.w800,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          const SizedBox(height: 21),

                          // Feature highlights
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: const Row(
                              children: [
                                Expanded(
                                  child: _WelcomeFeature(
                                    icon: Icons.two_wheeler_rounded,
                                    title: 'Bike',
                                    subtitle: 'Quick trips',
                                  ),
                                ),
                                SizedBox(width: 9),
                                Expanded(
                                  child: _WelcomeFeature(
                                    icon: Icons.electric_rickshaw_rounded,
                                    title: 'Auto',
                                    subtitle: 'City rides',
                                  ),
                                ),
                                SizedBox(width: 9),
                                Expanded(
                                  child: _WelcomeFeature(
                                    icon: Icons.directions_car_rounded,
                                    title: 'Cab',
                                    subtitle: 'More comfort',
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const Spacer(),

                          const SizedBox(height: 23),

                          // Main CTA
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SizedBox(
                              width: double.infinity,
                              height: 59,
                              child: DecoratedBox(
                                decoration: BoxDecoration(
                                  gradient: const LinearGradient(
                                    colors: [brandGreen, darkGreen],
                                  ),
                                  borderRadius: BorderRadius.circular(19),
                                  boxShadow: [
                                    BoxShadow(
                                      color: brandGreen.withValues(alpha: 0.25),
                                      blurRadius: 17,
                                      offset: const Offset(0, 7),
                                    ),
                                  ],
                                ),
                                child: ElevatedButton(
                                  onPressed: _getStarted,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.transparent,
                                    foregroundColor: Colors.white,
                                    shadowColor: Colors.transparent,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(19),
                                    ),
                                  ),
                                  child: const Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Text(
                                        'Get Started',
                                        style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.w900,
                                        ),
                                      ),
                                      SizedBox(width: 10),
                                      Icon(
                                        Icons.arrow_forward_rounded,
                                        size: 21,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),

                          const SizedBox(height: 13),

                          const Center(
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.shield_outlined,
                                  size: 14,
                                  color: darkGreen,
                                ),
                                SizedBox(width: 6),
                                Text(
                                  'Your journey starts here',
                                  style: TextStyle(
                                    color: muted,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
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

class _WelcomeFeature extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _WelcomeFeature({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 13, horizontal: 5),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(17),
        border: Border.all(color: const Color(0xFFE5EEE8)),
      ),
      child: Column(
        children: [
          Icon(icon, color: darkGreen, size: 25),
          const SizedBox(height: 7),
          Text(
            title,
            style: const TextStyle(
              color: navy,
              fontSize: 12,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            subtitle,
            textAlign: TextAlign.center,
            style: const TextStyle(color: muted, fontSize: 10),
          ),
        ],
      ),
    );
  }
}

// 3. Role selection

class RoleSelectionScreen extends StatefulWidget {
  const RoleSelectionScreen({super.key});

  @override
  State<RoleSelectionScreen> createState() => _RoleSelectionScreenState();
}

class _RoleSelectionScreenState extends State<RoleSelectionScreen>
    with TickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _headerFade;
  late final Animation<Offset> _headerSlide;
  late final Animation<double> _riderFade;
  late final Animation<Offset> _riderSlide;
  late final Animation<double> _driverFade;
  late final Animation<Offset> _driverSlide;
  late final Animation<double> _footerFade;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );

    _headerFade = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.45, curve: Curves.easeOut),
    );

    _headerSlide = Tween<Offset>(begin: const Offset(0, 0.15), end: Offset.zero)
        .animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.0, 0.50, curve: Curves.easeOutCubic),
          ),
        );

    _riderFade = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.20, 0.65, curve: Curves.easeOut),
    );

    _riderSlide = Tween<Offset>(begin: const Offset(0.12, 0), end: Offset.zero)
        .animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.20, 0.65, curve: Curves.easeOutCubic),
          ),
        );

    _driverFade = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.35, 0.80, curve: Curves.easeOut),
    );

    _driverSlide = Tween<Offset>(begin: const Offset(0.12, 0), end: Offset.zero)
        .animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.35, 0.80, curve: Curves.easeOutCubic),
          ),
        );

    _footerFade = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.55, 1.0, curve: Curves.easeOut),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _openLogin(String role) {
    goTo(context, PhoneLoginScreen(role: role));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: pageColor,
      appBar: AppBar(
        backgroundColor: pageColor,
        elevation: 0,
        scrolledUnderElevation: 0,
        leading: Padding(
          padding: const EdgeInsets.only(left: 8),
          child: IconButton(
            onPressed: () => Navigator.pop(context),
            style: IconButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: navy,
            ),
            icon: const Icon(Icons.arrow_back_rounded),
          ),
        ),
      ),
      body: SafeArea(
        top: false,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(23, 12, 23, 25),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              FadeTransition(
                opacity: _headerFade,
                child: SlideTransition(
                  position: _headerSlide,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 5,
                            height: 24,
                            decoration: BoxDecoration(
                              color: brandGreen,
                              borderRadius: BorderRadius.circular(5),
                            ),
                          ),
                          const SizedBox(width: 10),
                          const Text(
                            'NANDIRIDE',
                            style: TextStyle(
                              color: darkGreen,
                              fontSize: 12,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 2.4,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 25),
                      const Text(
                        'How would you like to ride?',
                        style: TextStyle(
                          color: navy,
                          fontSize: 36,
                          height: 1.12,
                          fontWeight: FontWeight.w900,
                          letterSpacing: -1.2,
                        ),
                      ),
                      const SizedBox(height: 13),
                      const Text(
                        'Choose your experience. We will take it from here.',
                        style: TextStyle(
                          color: muted,
                          fontSize: 14,
                          height: 1.65,
                        ),
                      ),
                      const SizedBox(height: 27),
                    ],
                  ),
                ),
              ),

              FadeTransition(
                opacity: _riderFade,
                child: SlideTransition(
                  position: _riderSlide,
                  child: _RoleCard(
                    icon: Icons.electric_rickshaw_rounded,
                    title: 'Book a ride',
                    subtitle: 'Reach your destination with ease',
                    tag: 'FOR PASSENGERS',
                    color: brandGreen,
                    backgroundColor: const Color(0xFFE9F8EF),
                    number: '01',
                    onTap: () => _openLogin('Rider'),
                  ),
                ),
              ),

              const SizedBox(height: 17),

              FadeTransition(
                opacity: _driverFade,
                child: SlideTransition(
                  position: _driverSlide,
                  child: _RoleCard(
                    icon: Icons.directions_bike_rounded,
                    title: 'Drive with us',
                    subtitle: 'Start your driver journey with us',
                    tag: 'FOR DRIVERS',
                    color: navy,
                    backgroundColor: const Color(0xFFEAF0F5),
                    number: '02',
                    onTap: () => _openLogin('Driver'),
                  ),
                ),
              ),

              const SizedBox(height: 27),

              FadeTransition(
                opacity: _footerFade,
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE8F8EE), Color(0xFFF3FBF6)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: const Color(0xFFD9EFE0)),
                  ),
                  child: const Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      DecoratedBox(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: SizedBox(
                          width: 47,
                          height: 47,
                          child: Icon(
                            Icons.verified_user_rounded,
                            color: darkGreen,
                            size: 25,
                          ),
                        ),
                      ),
                      SizedBox(width: 13),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Your journey starts here',
                              style: TextStyle(
                                color: navy,
                                fontSize: 14,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            SizedBox(height: 6),
                            Text(
                              'A simple and convenient travel experience, '
                              'designed around you.',
                              style: TextStyle(
                                color: muted,
                                fontSize: 12,
                                height: 1.6,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 22),

              const Center(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.favorite_rounded, color: brandGreen, size: 15),
                    SizedBox(width: 7),
                    Text(
                      'Made for your everyday journeys',
                      style: TextStyle(
                        color: muted,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleCard extends StatefulWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String tag;
  final Color color;
  final Color backgroundColor;
  final String number;
  final VoidCallback onTap;

  const _RoleCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.tag,
    required this.color,
    required this.backgroundColor,
    required this.number,
    required this.onTap,
  });

  @override
  State<_RoleCard> createState() => _RoleCardState();
}

class _RoleCardState extends State<_RoleCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    return AnimatedScale(
      scale: _pressed ? 0.98 : 1.0,
      duration: const Duration(milliseconds: 130),
      curve: Curves.easeOut,
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(25),
        child: InkWell(
          borderRadius: BorderRadius.circular(25),
          onTap: widget.onTap,
          onHighlightChanged: (value) {
            if (mounted) {
              setState(() => _pressed = value);
            }
          },
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(25),
              border: Border.all(color: const Color(0xFFE5ECE7)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x08000000),
                  blurRadius: 18,
                  offset: Offset(0, 7),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  width: 68,
                  height: 72,
                  decoration: BoxDecoration(
                    color: widget.backgroundColor,
                    borderRadius: BorderRadius.circular(21),
                  ),
                  child: Icon(widget.icon, color: widget.color, size: 37),
                ),
                const SizedBox(width: 15),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.tag,
                        style: TextStyle(
                          color: widget.color,
                          fontSize: 9,
                          letterSpacing: 1.4,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 7),
                      Text(
                        widget.title,
                        style: const TextStyle(
                          color: navy,
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        widget.subtitle,
                        style: const TextStyle(
                          color: muted,
                          fontSize: 11,
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 7),
                Container(
                  width: 33,
                  height: 33,
                  decoration: BoxDecoration(
                    color: widget.backgroundColor,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.arrow_forward_rounded,
                    color: widget.color,
                    size: 19,
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

// 4. Mobile login

class PhoneLoginScreen extends StatefulWidget {
  final String role;

  const PhoneLoginScreen({super.key, required this.role});

  @override
  State<PhoneLoginScreen> createState() => _PhoneLoginScreenState();
}

class _PhoneLoginScreenState extends State<PhoneLoginScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController phoneController = TextEditingController();
  final FocusNode phoneFocusNode = FocusNode();

  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  bool _isPhoneValid = false;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 850),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    );

    _slideAnimation =
        Tween<Offset>(begin: const Offset(0, 0.08), end: Offset.zero).animate(
          CurvedAnimation(
            parent: _animationController,
            curve: Curves.easeOutCubic,
          ),
        );

    _animationController.forward();

    phoneController.addListener(_validatePhone);
  }

  void _validatePhone() {
    final phone = phoneController.text.trim();
    final valid = RegExp(r'^[6-9]\d{9}$').hasMatch(phone);

    if (valid != _isPhoneValid && mounted) {
      setState(() => _isPhoneValid = valid);
    }
  }

  @override
  void dispose() {
    phoneController.removeListener(_validatePhone);
    phoneController.dispose();
    phoneFocusNode.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void continueToOtp() {
    final phone = phoneController.text.trim();

    if (!RegExp(r'^[6-9]\d{9}$').hasMatch(phone)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Enter a valid 10-digit Indian mobile number.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    FocusScope.of(context).unfocus();

    goTo(context, OtpScreen(role: widget.role, phone: phone));
  }

  @override
  Widget build(BuildContext context) {
    final isRider = widget.role == 'Rider';
    final roleColor = isRider ? brandGreen : navy;
    final roleIcon = isRider
        ? Icons.electric_rickshaw_rounded
        : Icons.directions_bike_rounded;

    return Scaffold(
      backgroundColor: pageColor,
      appBar: AppBar(
        backgroundColor: pageColor,
        elevation: 0,
        scrolledUnderElevation: 0,
        leading: Padding(
          padding: const EdgeInsets.only(left: 8),
          child: IconButton(
            onPressed: () => Navigator.pop(context),
            style: IconButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: navy,
            ),
            icon: const Icon(Icons.arrow_back_rounded),
          ),
        ),
      ),
      body: SafeArea(
        top: false,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 12, 24, 28),
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight:
                      MediaQuery.sizeOf(context).height -
                      MediaQuery.paddingOf(context).top -
                      kToolbarHeight -
                      55,
                ),
                child: IntrinsicHeight(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Center(child: BrandLogo(size: 64)),

                      const SizedBox(height: 30),

                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: isRider
                              ? const Color(0xFFE4F7EB)
                              : const Color(0xFFE8EDF3),
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(roleIcon, size: 17, color: roleColor),
                            const SizedBox(width: 7),
                            Text(
                              '${widget.role.toUpperCase()} ACCOUNT',
                              style: TextStyle(
                                color: roleColor,
                                fontSize: 10,
                                fontWeight: FontWeight.w900,
                                letterSpacing: 1.3,
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 20),

                      Text(
                        isRider
                            ? 'Your next ride\nstarts here.'
                            : 'Your driving\njourney starts here.',
                        style: const TextStyle(
                          color: navy,
                          fontSize: 34,
                          height: 1.14,
                          letterSpacing: -1.1,
                          fontWeight: FontWeight.w900,
                        ),
                      ),

                      const SizedBox(height: 13),

                      Text(
                        isRider
                            ? 'Enter your mobile number to continue '
                                  'with NandiRide.'
                            : 'Enter your mobile number to continue '
                                  'your journey with NandiRide.',
                        style: const TextStyle(
                          color: muted,
                          fontSize: 14,
                          height: 1.65,
                        ),
                      ),

                      const SizedBox(height: 32),

                      const Text(
                        'MOBILE NUMBER',
                        style: TextStyle(
                          color: navy,
                          fontSize: 11,
                          letterSpacing: 1.4,
                          fontWeight: FontWeight.w900,
                        ),
                      ),

                      const SizedBox(height: 11),

                      AnimatedContainer(
                        duration: const Duration(milliseconds: 220),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(19),
                          border: Border.all(
                            color: phoneFocusNode.hasFocus
                                ? brandGreen
                                : const Color(0xFFE0E9E3),
                            width: phoneFocusNode.hasFocus ? 1.6 : 1,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: brandGreen.withValues(
                                alpha: phoneFocusNode.hasFocus ? 0.08 : 0.02,
                              ),
                              blurRadius: 18,
                              offset: const Offset(0, 6),
                            ),
                          ],
                        ),
                        child: Focus(
                          onFocusChange: (_) {
                            if (mounted) setState(() {});
                          },
                          child: Row(
                            children: [
                              const SizedBox(width: 16),

                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 11,
                                  vertical: 12,
                                ),
                                decoration: BoxDecoration(
                                  color: mint,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Row(
                                  children: [
                                    Text(
                                      '🇮🇳',
                                      style: TextStyle(fontSize: 20),
                                    ),
                                    SizedBox(width: 7),
                                    Text(
                                      '+91',
                                      style: TextStyle(
                                        color: navy,
                                        fontSize: 15,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              Container(
                                height: 34,
                                width: 1,
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 13,
                                ),
                                color: const Color(0xFFE5ECE7),
                              ),

                              Expanded(
                                child: TextField(
                                  controller: phoneController,
                                  focusNode: phoneFocusNode,
                                  keyboardType: TextInputType.phone,
                                  textInputAction: TextInputAction.done,
                                  maxLength: 10,
                                  inputFormatters: [
                                    FilteringTextInputFormatter.digitsOnly,
                                  ],
                                  onSubmitted: (_) {
                                    if (_isPhoneValid) continueToOtp();
                                  },
                                  style: const TextStyle(
                                    color: navy,
                                    fontSize: 17,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 1,
                                  ),
                                  decoration: const InputDecoration(
                                    hintText: '00000 00000',
                                    counterText: '',
                                    border: InputBorder.none,
                                    enabledBorder: InputBorder.none,
                                    focusedBorder: InputBorder.none,
                                    filled: false,
                                    contentPadding: EdgeInsets.symmetric(
                                      vertical: 20,
                                    ),
                                  ),
                                ),
                              ),

                              AnimatedSwitcher(
                                duration: const Duration(milliseconds: 200),
                                child: _isPhoneValid
                                    ? const Padding(
                                        key: ValueKey('valid'),
                                        padding: EdgeInsets.only(right: 15),
                                        child: Icon(
                                          Icons.check_circle_rounded,
                                          color: brandGreen,
                                          size: 23,
                                        ),
                                      )
                                    : const SizedBox(
                                        key: ValueKey('empty'),
                                        width: 15,
                                      ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 12),

                      const Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            Icons.info_outline_rounded,
                            color: muted,
                            size: 16,
                          ),
                          SizedBox(width: 7),
                          Expanded(
                            child: Text(
                              'Use a valid Indian mobile number '
                              'starting with 6, 7, 8 or 9.',
                              style: TextStyle(
                                color: muted,
                                fontSize: 11,
                                height: 1.5,
                              ),
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 26),

                      AnimatedOpacity(
                        duration: const Duration(milliseconds: 200),
                        opacity: _isPhoneValid ? 1 : 0.65,
                        child: SizedBox(
                          width: double.infinity,
                          child: PrimaryButton(
                            text: 'Continue',
                            icon: Icons.arrow_forward_rounded,
                            onPressed: continueToOtp,
                          ),
                        ),
                      ),

                      const SizedBox(height: 20),

                      const Spacer(),

                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(15),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(17),
                          border: Border.all(color: const Color(0xFFEBF0EC)),
                        ),
                        child: const Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(
                              Icons.lock_outline_rounded,
                              color: darkGreen,
                              size: 22,
                            ),
                            SizedBox(width: 11),
                            Expanded(
                              child: Text(
                                'Your number is used to continue '
                                'your account journey. Actual SMS '
                                'verification must be connected separately.',
                                style: TextStyle(
                                  color: muted,
                                  fontSize: 11,
                                  height: 1.55,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 17),

                      const Center(
                        child: Text(
                          'By continuing, you agree to our Terms of Service '
                          'and Privacy Policy.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFF8A968F),
                            fontSize: 10,
                            height: 1.6,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// 5. OTP entry UI. Backend SMS verification is not connected yet.
class OtpScreen extends StatefulWidget {
  final String role;
  final String phone;

  const OtpScreen({super.key, required this.role, required this.phone});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final otpController = TextEditingController();

  @override
  void dispose() {
    otpController.dispose();
    super.dispose();
  }

  void verifyOtp() {
    if (otpController.text.trim().length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter the complete 6-digit OTP.')),
      );
      return;
    }

    // Demo navigation only. Real OTP verification is not connected.
    if (widget.role == 'Rider') {
      Navigator.pushAndRemoveUntil(
        context,
        smoothRoute(const RiderHomeScreen()),
        (route) => false,
      );
    } else {
      Navigator.pushAndRemoveUntil(
        context,
        smoothRoute(const DriverHomeScreen()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 18, 24, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 70,
                height: 70,
                decoration: const BoxDecoration(
                  color: mint,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.sms_outlined,
                  color: darkGreen,
                  size: 34,
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'Verify your\nnumber',
                style: TextStyle(
                  color: navy,
                  fontSize: 34,
                  height: 1.15,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 13),
              const Text(
                'Enter the 6-digit verification code for',
                style: TextStyle(color: muted, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Text(
                '+91 ${widget.phone}',
                style: const TextStyle(
                  color: navy,
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 28),
              TextField(
                controller: otpController,
                keyboardType: TextInputType.number,
                maxLength: 6,
                autofocus: true,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: navy,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 10,
                ),
                decoration: const InputDecoration(
                  counterText: '',
                  hintText: '------',
                  hintStyle: TextStyle(
                    color: Color(0xFFB8C3BC),
                    letterSpacing: 8,
                  ),
                ),
              ),
              const SizedBox(height: 22),
              PrimaryButton(text: 'Verify & Continue', onPressed: verifyOtp),
              const SizedBox(height: 12),
              Center(
                child: TextButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Resend OTP works after backend integration.',
                        ),
                      ),
                    );
                  },
                  child: const Text(
                    'Resend OTP',
                    style: TextStyle(
                      color: darkGreen,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const Spacer(),
              Center(
                child: Text(
                  '${widget.role} account • NandiRide',
                  style: const TextStyle(color: muted, fontSize: 12),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class RiderHomeScreen extends StatefulWidget {
  const RiderHomeScreen({super.key});

  @override
  State<RiderHomeScreen> createState() => _RiderHomeScreenState();
}

class _RiderHomeScreenState extends State<RiderHomeScreen> {
  final pickupController = TextEditingController(text: 'My current location');
  final dropController = TextEditingController();

  String selectedVehicle = 'Bike';

  final Map<String, Map<String, dynamic>> vehicles = {
    'Bike': {
      'icon': Icons.electric_bike_rounded,
      'price': 35,
      'time': '3 min away',
    },
    'Auto': {
      'icon': Icons.electric_rickshaw_rounded,
      'price': 65,
      'time': '5 min away',
    },
    'Cab': {
      'icon': Icons.directions_car_rounded,
      'price': 120,
      'time': '7 min away',
    },
  };

  @override
  void dispose() {
    pickupController.dispose();
    dropController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vehicle = vehicles[selectedVehicle]!;

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Row(
          children: [
            BrandLogo(size: 39),
            SizedBox(width: 10),
            Text(
              'NandiRide',
              style: TextStyle(
                color: navy,
                fontWeight: FontWeight.w900,
                fontSize: 22,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Profile screen will be added next.'),
                ),
              );
            },
            icon: const Icon(Icons.account_circle_outlined, size: 29),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 25),
          children: [
            const Text(
              'Where are you',
              style: TextStyle(
                color: navy,
                fontSize: 29,
                fontWeight: FontWeight.w900,
                letterSpacing: -0.6,
              ),
            ),
            const Text(
              'going today?',
              style: TextStyle(
                color: brandGreen,
                fontSize: 29,
                fontWeight: FontWeight.w900,
                letterSpacing: -0.6,
              ),
            ),
            const SizedBox(height: 9),
            const Text(
              'Your ride is just a few taps away.',
              style: TextStyle(color: muted, fontSize: 14),
            ),
            const SizedBox(height: 23),

            // Location inputs
            Container(
              padding: const EdgeInsets.all(17),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(23),
                border: Border.all(color: const Color(0xFFE4EBE6)),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.my_location_rounded,
                        color: brandGreen,
                        size: 22,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          controller: pickupController,
                          decoration: const InputDecoration(
                            filled: false,
                            hintText: 'Enter pickup location',
                            labelText: 'PICKUP LOCATION',
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const Padding(
                    padding: EdgeInsets.only(left: 9),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: SizedBox(
                        height: 22,
                        child: VerticalDivider(
                          color: Color(0xFFB8C8BE),
                          thickness: 1.5,
                        ),
                      ),
                    ),
                  ),
                  Row(
                    children: [
                      const Icon(
                        Icons.location_on_rounded,
                        color: Color(0xFFE76B58),
                        size: 23,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          controller: dropController,
                          decoration: const InputDecoration(
                            filled: false,
                            hintText: 'Where do you want to go?',
                            labelText: 'DROP LOCATION',
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 27),

            const Text(
              'Choose your ride',
              style: TextStyle(
                color: navy,
                fontSize: 20,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 5),
            const Text(
              'Select a ride that suits your journey.',
              style: TextStyle(color: muted, fontSize: 13),
            ),
            const SizedBox(height: 15),

            // Vehicle choices
            Row(
              children: vehicles.entries.map((entry) {
                final isSelected = selectedVehicle == entry.key;

                return Expanded(
                  child: GestureDetector(
                    onTap: () {
                      setState(() {
                        selectedVehicle = entry.key;
                      });
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 220),
                      margin: const EdgeInsets.only(right: 8),
                      padding: const EdgeInsets.symmetric(
                        vertical: 16,
                        horizontal: 4,
                      ),
                      decoration: BoxDecoration(
                        color: isSelected ? mint : Colors.white,
                        borderRadius: BorderRadius.circular(19),
                        border: Border.all(
                          color: isSelected
                              ? brandGreen
                              : const Color(0xFFE4EBE6),
                          width: isSelected ? 1.7 : 1,
                        ),
                      ),
                      child: Column(
                        children: [
                          Icon(
                            entry.value['icon'] as IconData,
                            size: 34,
                            color: isSelected ? darkGreen : navy,
                          ),
                          const SizedBox(height: 9),
                          Text(
                            entry.key,
                            style: TextStyle(
                              color: navy,
                              fontSize: 14,
                              fontWeight: isSelected
                                  ? FontWeight.w900
                                  : FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 5),
                          Text(
                            '₹${entry.value['price']}*',
                            style: const TextStyle(
                              color: darkGreen,
                              fontWeight: FontWeight.w900,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 23),

            // Estimate card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: navy,
                borderRadius: BorderRadius.circular(22),
              ),
              child: Row(
                children: [
                  Container(
                    width: 49,
                    height: 49,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Icon(
                      vehicle['icon'] as IconData,
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 13),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '$selectedVehicle ride',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w800,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          vehicle['time'] as String,
                          style: const TextStyle(
                            color: Color(0xFFD2E0D8),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '₹${vehicle['price']}*',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                      fontSize: 22,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 17),

            PrimaryButton(
              text: 'Book Ride',
              icon: Icons.arrow_forward_rounded,
              onPressed: () {
                if (pickupController.text.trim().isEmpty ||
                    dropController.text.trim().isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Please enter both pickup and drop locations.',
                      ),
                    ),
                  );
                  return;
                }

                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Booking UI ready. Connect Django API for real rides.',
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 12),
            const Text(
              '*Illustrative prices only. Actual fare will be calculated '
              'using the backend after distance and fare rules are connected.',
              style: TextStyle(color: muted, fontSize: 11, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

class DriverHomeScreen extends StatelessWidget {
  const DriverHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Row(
          children: [
            BrandLogo(size: 39),
            SizedBox(width: 10),
            Text(
              'NandiRide Driver',
              style: TextStyle(
                color: navy,
                fontWeight: FontWeight.w900,
                fontSize: 19,
              ),
            ),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 22),
            const Text(
              'Welcome, Driver!',
              style: TextStyle(
                color: navy,
                fontSize: 29,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Your driver dashboard will show ride requests, '
              'earnings and verification status.',
              style: TextStyle(color: muted, height: 1.6),
            ),
            const SizedBox(height: 25),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: mint,
                borderRadius: BorderRadius.circular(22),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.verified_user_outlined,
                    color: darkGreen,
                    size: 35,
                  ),
                  SizedBox(height: 13),
                  Text(
                    'Driver verification required',
                    style: TextStyle(
                      color: navy,
                      fontWeight: FontWeight.w900,
                      fontSize: 18,
                    ),
                  ),
                  SizedBox(height: 7),
                  Text(
                    'Real ride requests will be available after '
                    'backend authentication and driver approval.',
                    style: TextStyle(color: muted, height: 1.5),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
