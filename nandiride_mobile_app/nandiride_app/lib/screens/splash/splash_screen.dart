
import 'package:flutter/material.dart';
import '../../app/app_routes.dart';

const Color navyDark = Color(0xFF041536);
const Color yellow = Color(0xFFFFC94A);
const Color goldLight = Color(0xFFFFE6A0);

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  static const String _backgroundImage =
      'assets/images/mahadev_harki_pauri.png';
  static const String _logoImage =
      'assets/images/nandiride_logo.png';

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.sizeOf(context).height;
    final compact = screenHeight < 750;

    return Scaffold(
      backgroundColor: navyDark,
      body: SizedBox.expand(
        child: Stack(
          fit: StackFit.expand,
          children: [
            _buildBackground(),
            _buildOverlay(),
            SafeArea(
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  22,
                  12,
                  22,
                  compact ? 12 : 22,
                ),
                child: Column(
                  children: [
                    const Spacer(flex: 5),
                    _buildLogo(compact),
                    SizedBox(height: compact ? 10 : 16),
                    _buildBrand(compact),
                    SizedBox(height: compact ? 20 : 30),
                    Text(
                      'Bike, Auto aur Cab — safar ho aasan.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: compact ? 15 : 18,
                        fontWeight: FontWeight.w700,
                        height: 1.4,
                        shadows: const [
                          Shadow(
                            color: Colors.black,
                            blurRadius: 8,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: compact ? 22 : 32),
                    _buildGetStartedButton(context, compact),
                    SizedBox(height: compact ? 18 : 26),
                    _buildTrustLine(compact),
                    SizedBox(height: 8),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackground() {
    return SizedBox.expand(
      child: Image.asset(
        _backgroundImage,
        fit: BoxFit.fill,
        alignment: Alignment.center,
        errorBuilder: (context, error, stackTrace) {
          return const ColoredBox(color: navyDark);
        },
      ),
    );
  }

  Widget _buildOverlay() {
    return const DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0x08041536),
            Color(0x00041536),
            Color(0x18041536),
            Color(0xA8041536),
            Color(0xF5041536),
          ],
          stops: [0.0, 0.30, 0.48, 0.70, 1.0],
        ),
      ),
    );
  }

  Widget _buildLogo(bool compact) {
    return Container(
      width: compact ? 84 : 104,
      height: compact ? 84 : 104,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        border: Border.all(
          color: yellow,
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: yellow.withValues(alpha: 0.35),
            blurRadius: 18,
            spreadRadius: 1,
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        _logoImage,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) {
          return const Icon(
            Icons.two_wheeler_rounded,
            color: navyDark,
            size: 46,
          );
        },
      ),
    );
  }

  Widget _buildBrand(bool compact) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        RichText(
          textAlign: TextAlign.center,
          text: TextSpan(
            style: TextStyle(
              fontSize: compact ? 34 : 42,
              fontWeight: FontWeight.w900,
              letterSpacing: -1.2,
              height: 1.1,
              shadows: const [
                Shadow(
                  color: Colors.black87,
                  blurRadius: 8,
                  offset: Offset(0, 2),
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
        SizedBox(height: compact ? 8 : 12),
        Text(
          'YOUR RIDE  •  OUR PRIORITY',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: goldLight,
            fontSize: compact ? 10 : 12,
            fontWeight: FontWeight.w800,
            letterSpacing: compact ? 1.4 : 2,
            shadows: const [
              Shadow(
                color: Colors.black,
                blurRadius: 6,
              ),
            ],
          ),
        ),
        SizedBox(height: compact ? 12 : 18),
        Container(
          width: 64,
          height: 4,
          decoration: BoxDecoration(
            color: yellow,
            borderRadius: BorderRadius.circular(20),
          ),
        ),
      ],
    );
  }

  Widget _buildGetStartedButton(
    BuildContext context,
    bool compact,
  ) {
    return SizedBox(
      width: double.infinity,
      height: compact ? 54 : 62,
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
          elevation: 8,
          shadowColor: yellow.withValues(alpha: 0.3),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(40),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Get Started',
              style: TextStyle(
                fontSize: compact ? 17 : 20,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(width: 12),
            Icon(
              Icons.arrow_forward_rounded,
              size: compact ? 22 : 26,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrustLine(bool compact) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.verified_user_rounded,
          color: yellow,
          size: compact ? 14 : 18,
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Text(
            'SAFE  •  SIMPLE  •  RELIABLE',
            maxLines: 1,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: compact ? 9 : 11,
              fontWeight: FontWeight.w800,
              letterSpacing: compact ? 1.1 : 1.8,
              shadows: const [
                Shadow(
                  color: Colors.black,
                  blurRadius: 5,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
