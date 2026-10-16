import 'package:flutter/material.dart';
import '../../app/app_routes.dart';

const Color navyDark = Color(0xFF041536);
const Color navyLight = Color(0xFF0B1F4D);
const Color yellow = Color(0xFFFFC94A);
const Color goldLight = Color(0xFFFFE6A0);

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  static const String _backgroundImage = 'assets/images/mahadev_harki_pauri.png';
  static const String _logoImage = 'assets/images/nandi.png';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: navyDark,
      body: SizedBox.expand(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final screenHeight = constraints.maxHeight;
            final screenWidth = constraints.maxWidth;
            final compact = screenHeight < 700;
            final veryCompact = screenHeight < 590;
            final horizontalPadding = (screenWidth * 0.065).clamp(18.0, 30.0);
            final logoSize = (screenWidth * 0.23).clamp(68.0, 100.0);
            final brandFontSize = (screenWidth * 0.095).clamp(30.0, 42.0);

            return Stack(
              fit: StackFit.expand,
              children: [
                _buildBackground(),
                _buildOverlay(),
                SafeArea(
                  child: Padding(
                    padding: EdgeInsets.fromLTRB(
                      horizontalPadding,
                      compact ? 8 : 16,
                      horizontalPadding,
                      compact ? 10 : 20,
                    ),
                    child: Column(
                      children: [
                        _buildLogo(logoSize),
                        SizedBox(height: compact ? 7 : 12),
                        _buildBrand(
                          compact: compact,
                          fontSize: brandFontSize,
                        ),
                        const Spacer(),
                        _buildTagline(compact: compact),
                        SizedBox(height: veryCompact ? 14 : compact ? 20 : 30),
                        _buildGetStartedButton(
                          context,
                          compact: compact,
                          screenWidth: screenWidth,
                        ),
                        SizedBox(height: compact ? 16 : 24),
                        _buildTrustLine(compact: compact),
                        SizedBox(height: veryCompact ? 2 : 8),
                      ],
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildBackground() {
    return Positioned.fill(
      child: Image.asset(
        _backgroundImage,
        fit: BoxFit.cover,
        alignment: Alignment.center,
        errorBuilder: (context, error, stackTrace) {
          return const ColoredBox(color: navyDark);
        },
      ),
    );
  }

  Widget _buildOverlay() {
    return const Positioned.fill(
      child: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0x65041536),
              Color(0x18041536),
              Color(0x30041536),
              Color(0xB8041536),
              Color(0xF9041536),
            ],
            stops: [0.0, 0.22, 0.42, 0.68, 1.0],
          ),
        ),
      ),
    );
  }

  Widget _buildLogo(double logoSize) {
    return Container(
      width: logoSize,
      height: logoSize,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        border: Border.all(
          color: yellow,
          width: 2.5,
        ),
        boxShadow: [
          BoxShadow(
            color: yellow.withValues(alpha: 0.28),
            blurRadius: 22,
            spreadRadius: 2,
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 14,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        _logoImage,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) {
          return Icon(
            Icons.two_wheeler_rounded,
            color: navyDark,
            size: logoSize * 0.52,
          );
        },
      ),
    );
  }

  Widget _buildBrand({
    required bool compact,
    required double fontSize,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        FittedBox(
          fit: BoxFit.scaleDown,
          child: RichText(
            textAlign: TextAlign.center,
            text: TextSpan(
              style: TextStyle(
                fontSize: fontSize,
                fontWeight: FontWeight.w900,
                letterSpacing: -1.2,
                height: 1.08,
                shadows: const [
                  Shadow(
                    color: Colors.black87,
                    blurRadius: 10,
                    offset: Offset(0, 3),
                  ),
                ],
              ),
              children: const [
                TextSpan(
                  text: 'Nandi',
                  style: TextStyle(color: Colors.white),
                ),
                TextSpan(
                  text: 'Ride',
                  style: TextStyle(color: yellow),
                ),
              ],
            ),
          ),
        ),
        SizedBox(height: compact ? 5 : 9),
        Text(
          'YOUR RIDE  •  OUR PRIORITY',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: goldLight,
            fontSize: compact ? 9 : 11,
            fontWeight: FontWeight.w800,
            letterSpacing: compact ? 1.5 : 2.2,
            shadows: const [
              Shadow(
                color: Colors.black,
                blurRadius: 7,
              ),
            ],
          ),
        ),
        SizedBox(height: compact ? 8 : 12),
        Container(
          width: 48,
          height: 3,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [goldLight, yellow],
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: yellow.withValues(alpha: 0.35),
                blurRadius: 8,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTagline({required bool compact}) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: 13,
            vertical: 7,
          ),
          decoration: BoxDecoration(
            color: navyDark.withValues(alpha: 0.48),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(
              color: yellow.withValues(alpha: 0.35),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.location_on_rounded,
                color: yellow,
                size: compact ? 15 : 18,
              ),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  'YOUR CITY, YOUR RIDE',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: goldLight,
                    fontSize: compact ? 9 : 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.1,
                  ),
                ),
              ),
            ],
          ),
        ),
        SizedBox(height: compact ? 10 : 16),
        Text(
          'Bike, Auto and Cab',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.white,
            fontSize: compact ? 23 : 29,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.5,
            height: 1.2,
            shadows: const [
              Shadow(
                color: Colors.black87,
                blurRadius: 10,
                offset: Offset(0, 2),
              ),
            ],
          ),
        ),
        const SizedBox(height: 5),
        Text(
          'Every Ride, Made Better.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: goldLight,
            fontSize: compact ? 14 : 17,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.4,
            shadows: const [
              Shadow(
                color: Colors.black87,
                blurRadius: 8,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGetStartedButton(
    BuildContext context, {
    required bool compact,
    required double screenWidth,
  }) {
    return SizedBox(
      width: double.infinity,
      height: compact ? 52 : 60,
      child: ElevatedButton(
        onPressed: () {
          Navigator.pushReplacementNamed(
            context,
            AppRoutes.login,
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: yellow,
          foregroundColor: navyDark,
          elevation: 10,
          shadowColor: yellow.withValues(alpha: 0.30),
          padding: const EdgeInsets.symmetric(horizontal: 22),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
            side: const BorderSide(
              color: goldLight,
              width: 1,
            ),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Flexible(
              child: Text(
                'Get Started',
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: compact ? 16 : 19,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0.3,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              width: compact ? 30 : 34,
              height: compact ? 30 : 34,
              decoration: BoxDecoration(
                color: navyDark.withValues(alpha: 0.09),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.arrow_forward_rounded,
                size: compact ? 19 : 22,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrustLine({required bool compact}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.verified_user_rounded,
          color: yellow,
          size: compact ? 15 : 18,
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Text(
            'SAFE  •  SIMPLE  •  RELIABLE',
            maxLines: 1,
            textAlign: TextAlign.center,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: Colors.white,
              fontSize: compact ? 9 : 10,
              fontWeight: FontWeight.w800,
              letterSpacing: compact ? 1.1 : 1.8,
              shadows: const [
                Shadow(
                  color: Colors.black,
                  blurRadius: 6,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}