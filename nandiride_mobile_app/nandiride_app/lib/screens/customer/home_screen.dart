
import 'package:flutter/material.dart';
import '../../app/app_routes.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  static const Color navy = Color(0xFF101B3F);
  static const Color gold = Color(0xFFFFC928);
  static const Color background = Color(0xFFF5F7FC);
  static const Color muted = Color(0xFF68728A);

  int _selectedTab = 0;

  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 650),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.04),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeOutCubic,
      ),
    );

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: navy,
          behavior: SnackBarBehavior.floating,
        ),
      );
  }

  void _openBooking({String? rideType}) {
    Navigator.pushNamed(
      context,
      '/booking',
      arguments: {
        'pickup': 'Haridwar',
        'drop': 'Rishikesh',
        'rideType': 'bike',
      },
    );
  }

  void _onTabSelected(int index) {
    if (index == 0) {
      setState(() => _selectedTab = 0);
      return;
    }

    final route = index == 1
        ? AppRoutes.history
        : AppRoutes.profile;

    Navigator.pushNamed(context, route);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      body: SafeArea(
        bottom: false,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: CustomScrollView(
              physics: const BouncingScrollPhysics(),
              slivers: [
                SliverToBoxAdapter(child: _buildHeader()),
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 28),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      _buildWelcome(),
                      const SizedBox(height: 22),
                      _buildHeroCard(),
                      const SizedBox(height: 28),
                      _buildSectionTitle(
                        'Our services',
                        'Choose your preferred ride',
                      ),
                      const SizedBox(height: 15),
                      _buildServices(),
                      const SizedBox(height: 28),
                      _buildPromoCard(),
                      const SizedBox(height: 28),
                      _buildSectionTitle(
                        'Your convenience',
                        'Everything for a smoother journey',
                      ),
                      const SizedBox(height: 15),
                      _buildBenefits(),
                      const SizedBox(height: 24),
                      _buildHelpCard(),
                    ]),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: _buildBottomNavigation(),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 14, 16, 20),
      decoration: const BoxDecoration(
        color: navy,
        borderRadius: BorderRadius.vertical(
          bottom: Radius.circular(28),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: gold,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.electric_bike_rounded,
              color: navy,
              size: 29,
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'NandiRide',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                    letterSpacing: -0.6,
                  ),
                ),
                SizedBox(height: 3),
                Text(
                  'YOUR RIDE, YOUR WAY',
                  style: TextStyle(
                    color: gold,
                    fontSize: 9,
                    letterSpacing: 1.8,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          _headerIcon(
            icon: Icons.notifications_none_rounded,
            tooltip: 'Notifications',
            onTap: () {
              _showMessage('Notifications will be available soon.');
            },
          ),
          const SizedBox(width: 8),
          _headerIcon(
            icon: Icons.person_outline_rounded,
            tooltip: 'My profile',
            isGold: true,
            onTap: () {
              Navigator.pushNamed(context, AppRoutes.profile);
            },
          ),
        ],
      ),
    );
  }

  Widget _headerIcon({
    required IconData icon,
    required String tooltip,
    required VoidCallback onTap,
    bool isGold = false,
  }) {
    return Material(
      color: isGold
          ? gold
          : Colors.white.withValues(alpha: 0.12),
      shape: const CircleBorder(),
      child: IconButton(
        tooltip: tooltip,
        onPressed: onTap,
        icon: Icon(
          icon,
          color: isGold ? navy : Colors.white,
        ),
      ),
    );
  }

  Widget _buildWelcome() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Welcome! 👋',
          style: TextStyle(
            color: muted,
            fontSize: 12,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Where would you\nlike to go?',
          style: TextStyle(
            color: navy,
            fontSize: 30,
            height: 1.15,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.8,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Your city, your journey, your NandiRide.',
          style: TextStyle(
            color: muted,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  Widget _buildHeroCard() {
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: navy,
        borderRadius: BorderRadius.circular(26),
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.16),
            blurRadius: 22,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Stack(
        children: [
          Positioned(
            right: -28,
            top: -35,
            child: Container(
              width: 175,
              height: 175,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withValues(alpha: 0.045),
              ),
            ),
          ),
          Positioned(
            right: 20,
            top: 36,
            child: Transform.rotate(
              angle: -0.16,
              child: const Icon(
                Icons.electric_bike_rounded,
                color: gold,
                size: 106,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: gold.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: gold.withValues(alpha: 0.35),
                    ),
                  ),
                  child: const Text(
                    'YOUR NEXT RIDE STARTS HERE',
                    style: TextStyle(
                      color: gold,
                      fontSize: 9,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 0.7,
                    ),
                  ),
                ),
                const SizedBox(height: 22),
                const SizedBox(
                  width: 205,
                  child: Text(
                    'Ready to\nride?',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 34,
                      height: 1.05,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.8,
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                const SizedBox(
                  width: 205,
                  child: Text(
                    'Book a bike, auto or cab for your journey.',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                ),
                const SizedBox(height: 22),
                SizedBox(
                  height: 48,
                  child: ElevatedButton(
                    onPressed: () => _openBooking(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: gold,
                      foregroundColor: navy,
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 18,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Book a Ride',
                          style: TextStyle(
                            fontWeight: FontWeight.w900,
                            fontSize: 14,
                          ),
                        ),
                        SizedBox(width: 9),
                        Icon(
                          Icons.arrow_forward_rounded,
                          size: 19,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: navy,
            fontSize: 19,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.3,
          ),
        ),
        const SizedBox(height: 5),
        Text(
          subtitle,
          style: const TextStyle(
            color: muted,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildServices() {
    return Row(
      children: [
        Expanded(
          child: _serviceCard(
            name: 'Bike',
            subtitle: 'Quick & easy',
            icon: Icons.two_wheeler_rounded,
            color: const Color(0xFFEAF0FF),
            rideType: 'Bike',
          ),
        ),
        const SizedBox(width: 11),
        Expanded(
          child: _serviceCard(
            name: 'Auto',
            subtitle: 'Everyday ride',
            icon: Icons.electric_rickshaw_rounded,
            color: const Color(0xFFFFF4D5),
            rideType: 'Auto',
          ),
        ),
        const SizedBox(width: 11),
        Expanded(
          child: _serviceCard(
            name: 'Cab',
            subtitle: 'Extra comfort',
            icon: Icons.local_taxi_rounded,
            color: const Color(0xFFE2F6EE),
            rideType: 'Cab',
          ),
        ),
      ],
    );
  }

  Widget _serviceCard({
    required String name,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String rideType,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(19),
      child: InkWell(
        borderRadius: BorderRadius.circular(19),
        onTap: () => _openBooking(rideType: rideType),
        child: Container(
          padding: const EdgeInsets.symmetric(
            vertical: 17,
            horizontal: 4,
          ),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(19),
            border: Border.all(
              color: const Color(0xFFE7EBF3),
            ),
          ),
          child: Column(
            children: [
              Container(
                width: 49,
                height: 49,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Icon(
                  icon,
                  color: navy,
                  size: 28,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                name,
                style: const TextStyle(
                  color: navy,
                  fontSize: 14,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: muted,
                  fontSize: 9,
                ),
              ),
              const SizedBox(height: 10),
              const Icon(
                Icons.arrow_forward_rounded,
                color: navy,
                size: 17,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPromoCard() {
    return Container(
      padding: const EdgeInsets.all(19),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            Color(0xFFFFF4CF),
            Color(0xFFFFE6A0),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: const Color(0xFFFFE5A0),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 9,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: navy,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'NANDIRIDE',
                    style: TextStyle(
                      color: gold,
                      fontSize: 9,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Your journey,\nmade simpler.',
                  style: TextStyle(
                    color: navy,
                    fontSize: 20,
                    height: 1.2,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 7),
                const Text(
                  'Choose your ride and get going.',
                  style: TextStyle(
                    color: Color(0xFF62583C),
                    fontSize: 11,
                  ),
                ),
                const SizedBox(height: 14),
                GestureDetector(
                  onTap: () => _openBooking(),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Get started',
                        style: TextStyle(
                          color: navy,
                          fontSize: 12,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      SizedBox(width: 5),
                      Icon(
                        Icons.arrow_forward_rounded,
                        size: 16,
                        color: navy,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Container(
            width: 85,
            height: 85,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.75),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.route_rounded,
              color: navy,
              size: 48,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBenefits() {
    return Container(
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(0xFFE7EBF3),
        ),
      ),
      child: Column(
        children: [
          _benefitRow(
            icon: Icons.touch_app_rounded,
            title: 'Easy booking',
            subtitle: 'Start your booking in a few steps.',
            color: const Color(0xFFEAF0FF),
          ),
          const Divider(height: 25, color: Color(0xFFEEF0F5)),
          _benefitRow(
            icon: Icons.directions_car_filled_rounded,
            title: 'Multiple ride options',
            subtitle: 'Choose a bike, auto or cab.',
            color: const Color(0xFFFFF4D5),
          ),
          const Divider(height: 25, color: Color(0xFFEEF0F5)),
          _benefitRow(
            icon: Icons.receipt_long_rounded,
            title: 'Ride history',
            subtitle: 'Review your previous journeys.',
            color: const Color(0xFFE2F6EE),
          ),
        ],
      ),
    );
  }

  Widget _benefitRow({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    return Row(
      children: [
        Container(
          width: 43,
          height: 43,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(13),
          ),
          child: Icon(
            icon,
            color: navy,
            size: 23,
          ),
        ),
        const SizedBox(width: 13),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: navy,
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: const TextStyle(
                  color: muted,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
        const Icon(
          Icons.check_circle_rounded,
          color: Color(0xFF179B72),
          size: 20,
        ),
      ],
    );
  }

  Widget _buildHelpCard() {
    return InkWell(
      borderRadius: BorderRadius.circular(18),
      onTap: () {
        _showMessage('Help and support will be available soon.');
      },
      child: Container(
        padding: const EdgeInsets.all(17),
        decoration: BoxDecoration(
          color: const Color(0xFFEBEEF7),
          borderRadius: BorderRadius.circular(18),
        ),
        child: const Row(
          children: [
            Icon(
              Icons.support_agent_rounded,
              color: navy,
              size: 29,
            ),
            SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Need help?',
                    style: TextStyle(
                      color: navy,
                      fontSize: 13,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Visit our help and support section.',
                    style: TextStyle(
                      color: muted,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios_rounded,
              color: navy,
              size: 16,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNavigation() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: navy.withValues(alpha: 0.07),
            blurRadius: 18,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: NavigationBar(
          height: 66,
          selectedIndex: _selectedTab,
          backgroundColor: Colors.white,
          indicatorColor: gold.withValues(alpha: 0.25),
          onDestinationSelected: _onTabSelected,
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home_rounded),
              label: 'Home',
            ),
            NavigationDestination(
              icon: Icon(Icons.history_rounded),
              selectedIcon: Icon(Icons.history_rounded),
              label: 'Rides',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline_rounded),
              selectedIcon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}