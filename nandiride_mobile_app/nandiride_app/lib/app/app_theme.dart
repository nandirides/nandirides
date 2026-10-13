import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  // NandiRide Brand Colors: Navy Blue + Gold
  static const Color primary = Color(0xFF101B3F);
  static const Color primaryDark = Color(0xFF091229);
  static const Color secondary = Color(0xFFFFC928);
  static const Color accent = Color(0xFFFFC928);

  // Background and surfaces
  static const Color background = Color(0xFFF5F7FC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color mint = Color(0xFFFFF4CC);

  // Text colors
  static const Color textPrimary = Color(0xFF101B3F);
  static const Color textSecondary = Color(0xFF68728A);

  // Borders and status colors
  static const Color border = Color(0xFFE4E9F2);
  static const Color success = Color(0xFF179B72);
  static const Color error = Color(0xFFE24B58);
  static const Color warning = Color(0xFFF59E0B);

  // Animations
  static const Duration animationFast =
      Duration(milliseconds: 200);

  static const Duration animationNormal =
      Duration(milliseconds: 350);

  static const Duration animationSlow =
      Duration(milliseconds: 600);

  static const Curve animationCurve = Curves.easeInOutCubic;

  // Main application theme
  static ThemeData get light {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: primary,
      brightness: Brightness.light,
    ).copyWith(
      primary: primary,
      onPrimary: Colors.white,
      secondary: secondary,
      onSecondary: primary,
      surface: surface,
      onSurface: textPrimary,
      error: error,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: background,
      fontFamily: 'Roboto',

      // App bar
      appBarTheme: const AppBarTheme(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleTextStyle: TextStyle(
          fontSize: 21,
          fontWeight: FontWeight.w700,
          color: Colors.white,
        ),
        iconTheme: IconThemeData(
          color: Colors.white,
        ),
      ),

      // Cards
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        margin: EdgeInsets.zero,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: border),
        ),
      ),

      // Primary buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          disabledBackgroundColor: border,
          disabledForegroundColor: textSecondary,
          minimumSize: const Size.fromHeight(52),
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            horizontal: 22,
            vertical: 15,
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),

      // Secondary outlined buttons
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primary,
          minimumSize: const Size.fromHeight(50),
          side: const BorderSide(color: primary),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),

      // Text fields
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 17,
        ),
        hintStyle: const TextStyle(
          color: textSecondary,
          fontSize: 14,
        ),
        labelStyle: const TextStyle(
          color: textSecondary,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: primary,
            width: 1.6,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: error,
            width: 1.5,
          ),
        ),
      ),

      // Dividers
      dividerTheme: const DividerThemeData(
        color: border,
        thickness: 1,
        space: 1,
      ),

      // Bottom navigation
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: surface,
        indicatorColor: secondary.withValues(alpha: 0.25),
        elevation: 0,
        labelBehavior:
            NavigationDestinationLabelBehavior.alwaysShow,
        labelTextStyle: const WidgetStatePropertyAll(
          TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Snackbars
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: primary,
        contentTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 14,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
      ),

      // Loading indicators
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: primary,
      ),

      // Floating action buttons
      floatingActionButtonTheme:
          const FloatingActionButtonThemeData(
        backgroundColor: secondary,
        foregroundColor: primary,
        elevation: 2,
      ),

      // Selection colors
      textSelectionTheme: const TextSelectionThemeData(
        cursorColor: primary,
        selectionColor: Color(0x553A5A9A),
        selectionHandleColor: primary,
      ),

      // Checkboxes and switches
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return primary;
          }
          return surface;
        }),
        checkColor:
            const WidgetStatePropertyAll(Colors.white),
      ),

      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return primary;
          }
          return Colors.white;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return secondary.withValues(alpha: 0.6);
          }
          return border;
        }),
      ),
    );
  }

  // Optional alias for code that uses AppTheme.lightTheme
  static ThemeData get lightTheme => light;
}
