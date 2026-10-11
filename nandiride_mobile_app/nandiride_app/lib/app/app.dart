import 'package:flutter/material.dart';

import 'app_routes.dart';
import 'app_theme.dart';

import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';

import '../screens/customer/home_screen.dart';
import '../screens/customer/booking_screen.dart';
import '../screens/customer/tracking_screen.dart';
import '../screens/customer/history_screen.dart';
import '../screens/customer/profile_screen.dart';
import '../screens/customer/edit_profile_screen.dart';

import '../screens/driver/driver_home_screen.dart';
import '../screens/driver/ride_requests_screen.dart';
import '../screens/driver/trip_details_screen.dart';
import '../screens/driver/earnings_screen.dart';
import '../screens/driver/driver_profile_screen.dart';

class NandiRideApp extends StatelessWidget {
  const NandiRideApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NandiRide',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      initialRoute: AppRoutes.splash,
      routes: {
        AppRoutes.splash: (_) => const SplashScreen(),
        AppRoutes.login: (_) => const LoginScreen(),
        AppRoutes.register: (_) => const RegisterScreen(),

        AppRoutes.home: (_) => const HomeScreen(),
        AppRoutes.booking: (_) => const BookingScreen(),
        AppRoutes.tracking: (_) => const TrackingScreen(),
        AppRoutes.history: (_) => const HistoryScreen(),
        AppRoutes.profile: (_) => const ProfileScreen(),
        AppRoutes.editProfile: (_) => const EditProfileScreen(),

        AppRoutes.driverHome: (_) => const DriverHomeScreen(),
        AppRoutes.rideRequests: (_) => const RideRequestsScreen(),
        AppRoutes.tripDetails: (_) => const TripDetailsScreen(),
        AppRoutes.earnings: (_) => const EarningsScreen(),
        AppRoutes.driverProfile: (_) => const DriverProfileScreen(),
      },
    );
  }
}
