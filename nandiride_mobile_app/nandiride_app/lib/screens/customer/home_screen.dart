import 'package:flutter/material.dart';
import '../../app/app_routes.dart';
import '../../services/auth_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  static const Color navy = Color(0xFF0B1F4D);
  static const Color navyDark = Color(0xFF061431);
  static const Color gold = Color(0xFFFFC928);
  static const Color background = Color(0xFFF5F7FC);
  static const Color muted = Color(0xFF68748C);
  static const Color green = Color(0xFF168765);
  int _selectedTab = 0;
  late final AnimationController _animationController;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;
  String _userName = 'Rider';
  bool _isLoadingUser = true;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnimation = CurvedAnimation(parent: _animationController, curve: Curves.easeOut);
    _slideAnimation = Tween<Offset>(begin: const Offset(0, 0.035), end: Offset.zero).animate(CurvedAnimation(parent: _animationController, curve: Curves.easeOutCubic));
    _animationController.forward();
    _loadCurrentUser();
  }

  Future<void> _loadCurrentUser() async {
    try {
      final response = await AuthService.getCurrentUser();
      final user = _extractUser(response);
      final firstName = _readString(user, ['first_name', 'firstName']);
      final lastName = _readString(user, ['last_name', 'lastName']);
      final fullName = _readString(user, ['full_name', 'fullName', 'name', 'display_name']);
      final username = _readString(user, ['username']);
      final name = firstName.isNotEmpty
          ? firstName
          : fullName.isNotEmpty
              ? fullName
              : username.isNotEmpty
                  ? username
                  : 'Rider';
      final displayName = name == firstName && lastName.isNotEmpty
          ? '$firstName $lastName'
          : name;
      if (!mounted) return;
      setState(() {
        _userName = displayName.trim().isNotEmpty ? displayName.trim() : 'Rider';
        _isLoadingUser = false;
      });
    } catch (error) {
      debugPrint('HOME USER PROFILE ERROR: $error');
      if (!mounted) return;
      setState(() {
        _userName = 'Rider';
        _isLoadingUser = false;
      });
    }
  }

  Map<String, dynamic> _extractUser(Map<String, dynamic> response) {
    Map<String, dynamic> asMap(dynamic value) {
      if (value is Map<String, dynamic>) return value;
      if (value is Map) return Map<String, dynamic>.from(value);
      return <String, dynamic>{};
    }

    final direct = asMap(response['user']);
    if (direct.isNotEmpty) return direct;
    final data = response['data'];
    if (data is List && data.isNotEmpty) {
      final first = asMap(data.first);
      if (first.isNotEmpty) return first;
    }
    final dataMap = asMap(data);
    if (dataMap.isNotEmpty) {
      final nestedUser = asMap(dataMap['user']);
      if (nestedUser.isNotEmpty) return nestedUser;
      if (_hasUserFields(dataMap)) return dataMap;
      final results = dataMap['results'];
      if (results is List && results.isNotEmpty) {
        final first = asMap(results.first);
        if (first.isNotEmpty) return first;
      }
    }
    final results = response['results'];
    if (results is List && results.isNotEmpty) {
      final first = asMap(results.first);
      if (first.isNotEmpty) return first;
    }
    if (_hasUserFields(response)) return response;
    return <String, dynamic>{};
  }

  bool _hasUserFields(Map<String, dynamic> value) {
    return [
      'first_name',
      'firstName',
      'last_name',
      'lastName',
      'full_name',
      'fullName',
      'name',
      'username',
    ].any(value.containsKey);
  }

  String _readString(Map<String, dynamic> user, List<String> keys) {
    for (final key in keys) {
      final value = user[key];
      if (value != null && value is! Map && value is! List) {
        final result = value.toString().trim();
        if (result.isNotEmpty && result.toLowerCase() != 'null') {
          return result;
        }
      }
    }
    return '';
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message), backgroundColor: navy, behavior: SnackBarBehavior.floating, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)), margin: const EdgeInsets.all(14)));
  }

  void _openBooking({String? rideType}) {
    Navigator.pushNamed(context, '/booking', arguments: {'pickup': 'Haridwar', 'drop': 'Rishikesh', 'rideType': (rideType ?? 'Bike').toLowerCase()});
  }

  void _onTabSelected(int index) {
    if (index == 0) {
      setState(() => _selectedTab = 0);
      return;
    }
    final route = index == 1 ? AppRoutes.history : AppRoutes.profile;
    Navigator.pushNamed(context, route).then((_) {
      if (mounted) setState(() => _selectedTab = 0);
    });
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
                  padding: const EdgeInsets.fromLTRB(18, 23, 18, 28),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      _buildWelcome(),
                      const SizedBox(height: 22),
                      _buildHeroCard(),
                      const SizedBox(height: 28),
                      _buildSectionTitle('Ride your way', 'Choose the ride that suits you'),
                      const SizedBox(height: 15),
                      _buildServices(),
                      const SizedBox(height: 27),
                      _buildPromoCard(),
                      const SizedBox(height: 28),
                      _buildSectionTitle('Made for your comfort', 'A smoother way to get around'),
                      const SizedBox(height: 14),
                      _buildBenefits(),
                      const SizedBox(height: 20),
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
      padding: const EdgeInsets.fromLTRB(18, 13, 14, 21),
      decoration: const BoxDecoration(gradient: LinearGradient(colors: [navy, navyDark], begin: Alignment.topLeft, end: Alignment.bottomRight), borderRadius: BorderRadius.vertical(bottom: Radius.circular(28))),
      child: Row(
        children: [
          Container(width: 47, height: 47, decoration: BoxDecoration(color: gold, borderRadius: BorderRadius.circular(15)), child: const Icon(Icons.electric_bike_rounded, color: navy, size: 28)),
          const SizedBox(width: 11),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('NandiRide', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900, letterSpacing: -0.5)),
                SizedBox(height: 3),
                Text('YOUR RIDE, YOUR WAY', style: TextStyle(color: gold, fontSize: 9, letterSpacing: 1.5, fontWeight: FontWeight.w800)),
              ],
            ),
          ),
          _headerIcon(icon: Icons.notifications_none_rounded, tooltip: 'Notifications', onTap: () => _showMessage('Notifications will be available soon.')),
          const SizedBox(width: 7),
          _headerIcon(icon: Icons.person_rounded, tooltip: 'My profile', isGold: true, onTap: () => Navigator.pushNamed(context, AppRoutes.profile)),
        ],
      ),
    );
  }

  Widget _headerIcon({required IconData icon, required String tooltip, required VoidCallback onTap, bool isGold = false}) {
    return Material(
      color: isGold ? gold : Colors.white.withValues(alpha: 0.12),
      shape: const CircleBorder(),
      child: IconButton(tooltip: tooltip, onPressed: onTap, visualDensity: VisualDensity.compact, icon: Icon(icon, color: isGold ? navy : Colors.white, size: 22)),
    );
  }

  Widget _buildWelcome() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('WELCOME BACK', style: TextStyle(color: muted, fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 1.5)),
        const SizedBox(height: 7),
        Row(
          children: [
            Expanded(child: Text(_isLoadingUser ? 'Hello, Rider 👋' : 'Hello, $_userName 👋', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: navy, fontSize: 27, height: 1.15, fontWeight: FontWeight.w900, letterSpacing: -0.7))),
            Container(width: 44, height: 44, decoration: BoxDecoration(color: gold.withValues(alpha: 0.22), shape: BoxShape.circle), child: const Icon(Icons.waving_hand_rounded, color: navy, size: 24)),
          ],
        ),
        const SizedBox(height: 7),
        const Text('Where would you like to go today?', style: TextStyle(color: muted, fontSize: 13, height: 1.4)),
      ],
    );
  }

  Widget _buildHeroCard() {
    return Container(
      width: double.infinity,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(gradient: const LinearGradient(colors: [navy, Color(0xFF172E61), Color(0xFF0B1F4D)], begin: Alignment.topLeft, end: Alignment.bottomRight), borderRadius: BorderRadius.circular(25), boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.17), blurRadius: 22, offset: const Offset(0, 10))]),
      child: Stack(
        children: [
          Positioned(right: -35, top: -38, child: Container(width: 190, height: 190, decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: Colors.white.withValues(alpha: 0.08), width: 24)))),
          Positioned(right: -8, bottom: 15, child: Icon(Icons.electric_bike_rounded, size: 130, color: gold.withValues(alpha: 0.19))),
          Padding(
            padding: const EdgeInsets.all(21),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6), decoration: BoxDecoration(color: gold.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(20), border: Border.all(color: gold.withValues(alpha: 0.38))), child: const Text('YOUR NEXT RIDE STARTS HERE', style: TextStyle(color: gold, fontSize: 9, fontWeight: FontWeight.w900, letterSpacing: 0.6))),
                const SizedBox(height: 21),
                const SizedBox(width: 215, child: Text('Your journey.\nYour freedom.', style: TextStyle(color: Colors.white, fontSize: 30, height: 1.12, fontWeight: FontWeight.w900, letterSpacing: -0.7))),
                const SizedBox(height: 10),
                const SizedBox(width: 220, child: Text('Book a bike, auto or cab and get moving with NandiRide.', style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.55))),
                const SizedBox(height: 20),
                SizedBox(
                  height: 47,
                  child: ElevatedButton(
                    onPressed: () => _openBooking(),
                    style: ElevatedButton.styleFrom(backgroundColor: gold, foregroundColor: navy, elevation: 0, padding: const EdgeInsets.symmetric(horizontal: 17), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13))),
                    child: const Row(mainAxisSize: MainAxisSize.min, children: [Text('Book a ride', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w900)), SizedBox(width: 9), Icon(Icons.arrow_forward_rounded, size: 18)]),
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
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: const TextStyle(color: navy, fontSize: 19, fontWeight: FontWeight.w900, letterSpacing: -0.3)),
      const SizedBox(height: 5),
      Text(subtitle, style: const TextStyle(color: muted, fontSize: 12)),
    ]);
  }

  Widget _buildServices() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: _serviceCard(name: 'Bike', subtitle: 'Quick & easy', icon: Icons.two_wheeler_rounded, color: const Color(0xFFEAF0FF))),
        const SizedBox(width: 10),
        Expanded(child: _serviceCard(name: 'Auto', subtitle: 'Everyday ride', icon: Icons.electric_rickshaw_rounded, color: const Color(0xFFFFF3D2))),
        const SizedBox(width: 10),
        Expanded(child: _serviceCard(name: 'Cab', subtitle: 'Extra comfort', icon: Icons.local_taxi_rounded, color: const Color(0xFFE0F5EC))),
      ],
    );
  }

  Widget _serviceCard({required String name, required String subtitle, required IconData icon, required Color color}) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () => _openBooking(rideType: name),
        child: Container(
          constraints: const BoxConstraints(minHeight: 145),
          padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 3),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFE5EAF3))),
          child: Column(children: [
            Container(width: 47, height: 47, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(14)), child: Icon(icon, color: navy, size: 27)),
            const SizedBox(height: 10),
            Text(name, style: const TextStyle(color: navy, fontSize: 13, fontWeight: FontWeight.w900)),
            const SizedBox(height: 4),
            Text(subtitle, textAlign: TextAlign.center, style: const TextStyle(color: muted, fontSize: 9)),
            const SizedBox(height: 8),
            const Icon(Icons.arrow_forward_rounded, color: navy, size: 16),
          ]),
        ),
      ),
    );
  }

  Widget _buildPromoCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFFFFF5D7), Color(0xFFFFE7A3)], begin: Alignment.topLeft, end: Alignment.bottomRight), borderRadius: BorderRadius.circular(22), border: Border.all(color: const Color(0xFFFFE3A0))),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5), decoration: BoxDecoration(color: navy, borderRadius: BorderRadius.circular(7)), child: const Text('NANDIRIDE', style: TextStyle(color: gold, fontSize: 9, fontWeight: FontWeight.w900, letterSpacing: 1))),
                const SizedBox(height: 12),
                const Text('Every trip,\na little easier.', style: TextStyle(color: navy, fontSize: 20, height: 1.2, fontWeight: FontWeight.w900, letterSpacing: -0.3)),
                const SizedBox(height: 7),
                const Text('Pick your ride. Enjoy the journey.', style: TextStyle(color: Color(0xFF62583C), fontSize: 10, height: 1.4)),
                const SizedBox(height: 13),
                InkWell(
                  onTap: () => _openBooking(),
                  borderRadius: BorderRadius.circular(8),
                  child: const Padding(padding: EdgeInsets.symmetric(vertical: 4), child: Row(mainAxisSize: MainAxisSize.min, children: [Text('Get started', style: TextStyle(color: navy, fontSize: 12, fontWeight: FontWeight.w900)), SizedBox(width: 5), Icon(Icons.arrow_forward_rounded, size: 16, color: navy)])),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Container(width: 75, height: 75, decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.8), shape: BoxShape.circle), child: const Icon(Icons.route_rounded, color: navy, size: 42)),
        ],
      ),
    );
  }

  Widget _buildBenefits() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFFE5EAF3))),
      child: Column(children: [
        _benefitRow(icon: Icons.touch_app_rounded, title: 'Simple booking', subtitle: 'Book your next ride in a few steps.', color: const Color(0xFFEAF0FF)),
        const Divider(height: 25, color: Color(0xFFEEF0F5)),
        _benefitRow(icon: Icons.directions_car_filled_rounded, title: 'Ride options', subtitle: 'Bike, auto or cab — you choose.', color: const Color(0xFFFFF3D2)),
        const Divider(height: 25, color: Color(0xFFEEF0F5)),
        _benefitRow(icon: Icons.receipt_long_rounded, title: 'Ride history', subtitle: 'Find your previous journeys easily.', color: const Color(0xFFE0F5EC)),
      ]),
    );
  }

  Widget _benefitRow({required IconData icon, required String title, required String subtitle, required Color color}) {
    return Row(children: [
      Container(width: 43, height: 43, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(13)), child: Icon(icon, color: navy, size: 22)),
      const SizedBox(width: 12),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(color: navy, fontSize: 12, fontWeight: FontWeight.w900)),
        const SizedBox(height: 4),
        Text(subtitle, style: const TextStyle(color: muted, fontSize: 10, height: 1.4)),
      ])),
      const Icon(Icons.check_circle_rounded, color: green, size: 19),
    ]);
  }

  Widget _buildHelpCard() {
    return Material(
      color: const Color(0xFFE9EEF8),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () => _showMessage('Help and support will be available soon.'),
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Row(children: [
            Icon(Icons.support_agent_rounded, color: navy, size: 29),
            SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Need help?', style: TextStyle(color: navy, fontSize: 13, fontWeight: FontWeight.w900)),
              SizedBox(height: 4),
              Text('Visit our help and support section.', style: TextStyle(color: muted, fontSize: 11)),
            ])),
            Icon(Icons.arrow_forward_ios_rounded, color: navy, size: 15),
          ]),
        ),
      ),
    );
  }

  Widget _buildBottomNavigation() {
    return Container(
      decoration: BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: navy.withValues(alpha: 0.07), blurRadius: 18, offset: const Offset(0, -4))]),
      child: SafeArea(
        top: false,
        child: NavigationBar(
          height: 66,
          selectedIndex: _selectedTab,
          backgroundColor: Colors.white,
          indicatorColor: gold.withValues(alpha: 0.27),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          onDestinationSelected: _onTabSelected,
          destinations: const [
            NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Home'),
            NavigationDestination(icon: Icon(Icons.history_rounded), selectedIcon: Icon(Icons.history_rounded), label: 'Rides'),
            NavigationDestination(icon: Icon(Icons.person_outline_rounded), selectedIcon: Icon(Icons.person_rounded), label: 'Profile'),
          ],
        ),
      ),
    );
  }
}