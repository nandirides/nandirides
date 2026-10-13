
import 'package:flutter/material.dart';
import 'app_routes.dart';
import 'app_theme.dart';

// Splash and authentication screens
import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';

// Customer screens
import '../screens/customer/home_screen.dart';
import '../screens/customer/booking_screen.dart';
import '../screens/customer/tracking_screen.dart';
import '../screens/customer/history_screen.dart';
import '../screens/customer/profile_screen.dart';
import '../screens/customer/edit_profile_screen.dart';

// Driver screens
import '../screens/driver/driver_registration_screen.dart';
import '../screens/driver/driver_home_screen.dart';
import '../screens/driver/ride_requests_screen.dart';
import '../screens/driver/trip_details_screen.dart';
import '../screens/driver/earnings_screen.dart';
import '../screens/driver/driver_profile_screen.dart';

class NandiRideApp extends StatelessWidget {
  const NandiRideApp({super.key});

  Route<dynamic>? _buildRoute(RouteSettings settings) {
    final Widget? page = switch (settings.name) {
      // Splash and authentication
      AppRoutes.splash => const SplashScreen(),
      AppRoutes.login => const LoginScreen(),
      AppRoutes.register => const RegisterScreen(),

      // Customer routes
      AppRoutes.home => const HomeScreen(),
      AppRoutes.booking => const BookingScreen(),
      AppRoutes.tracking => const TrackingScreen(),
      AppRoutes.history => const HistoryScreen(),
      AppRoutes.profile => const ProfileScreen(),
      AppRoutes.editProfile => const EditProfileScreen(),

      // Driver routes
      AppRoutes.driverHome => const DriverHomeScreen(),
      AppRoutes.driverRegistration => const DriverRegistrationScreen(),
      AppRoutes.rideRequests => const RideRequestsScreen(),
      AppRoutes.tripDetails => const TripDetailsScreen(),
      AppRoutes.earnings => const EarningsScreen(),
      AppRoutes.driverProfile => const DriverProfileScreen(),

      // Unknown route
      _ => null,
    };

    if (page == null) {
      return null;
    }

    // Show splash screen without a page transition.
    if (settings.name == AppRoutes.splash) {
      return MaterialPageRoute<dynamic>(
        builder: (_) => page,
        settings: settings,
      );
    }

    // Smooth fade and upward slide transition.
    return PageRouteBuilder<dynamic>(
      settings: settings,
      transitionDuration: AppTheme.animationNormal,
      reverseTransitionDuration: AppTheme.animationFast,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder:
          (context, animation, secondaryAnimation, child) {
        final curvedAnimation = CurvedAnimation(
          parent: animation,
          curve: AppTheme.animationCurve,
          reverseCurve: Curves.easeInCubic,
        );

        return FadeTransition(
          opacity: curvedAnimation,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0.035, 0.025),
              end: Offset.zero,
            ).animate(curvedAnimation),
            child: child,
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NandiRide',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      initialRoute: AppRoutes.splash,
      onGenerateRoute: _buildRoute,
    );
  }
}
