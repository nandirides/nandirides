import 'package:flutter/material.dart';

import '../app/app_theme.dart';

class BrandLogo extends StatelessWidget {
  final double size;

  const BrandLogo({super.key, this.size = 80});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        color: AppTheme.accent,
        shape: BoxShape.circle,
      ),
      child: Icon(
        Icons.directions_bike,
        size: size * 0.58,
        color: AppTheme.primary,
      ),
    );
  }
}
