import 'package:flutter/material.dart';

void main() => runApp(const NandiRideApp());

const Color navy = Color(0xFF082B68);
const Color navyDark = Color(0xFF061D49);
const Color yellow = Color(0xFFFFC928);
const Color pageBg = Color(0xFFF4F7FB);

class NandiRideApp extends StatelessWidget {
  const NandiRideApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NandiRide',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: pageBg,
        colorScheme: ColorScheme.fromSeed(seedColor: navy),
        appBarTheme: const AppBarTheme(
          backgroundColor: navy,
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: false,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFDCE3ED)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFDCE3ED)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: navy, width: 1.5),
          ),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}

class RideRecord {
  RideRecord({
    required this.pickup,
    required this.drop,
    required this.vehicle,
    required this.fare,
    this.status = 'Searching for driver',
  });
  final String pickup;
  final String drop;
  final String vehicle;
  final int fare;
  String status;
}

class AppState {
  static final List<RideRecord> rides = [];
  static final List<RideRecord> driverRequests = [
    RideRecord(
      pickup: 'Railway Station, Roorkee',
      drop: 'IIT Roorkee Main Gate',
      vehicle: 'Auto',
      fare: 120,
      status: 'New request',
    ),
    RideRecord(
      pickup: 'Civil Lines, Roorkee',
      drop: 'Bus Stand, Roorkee',
      vehicle: 'Bike',
      fare: 65,
      status: 'New request',
    ),
    RideRecord(
      pickup: 'Bahadrabad, Haridwar',
      drop: 'Bus Stand, Bahadrabad',
      vehicle: 'Cab',
      fare: 95,
      status: 'New request',
    ),
  ];
  static String name = 'NandiRide Customer';
  static String contact = 'customer@nandiride.demo';
  static String customerId = 'CUS-1001';
  static String customerAddress = 'Civil Lines, Roorkee, Uttarakhand';
  static String customerPayment = 'Cash';
  static String driverName = 'Demo Driver';
  static String driverContact = '+91 98765 43210';
  static String driverId = 'DRV-2001';
  static String driverLicence = 'UK-08-2025-001234';
  static String driverVehicle = 'Auto • UK08 AB 1234';
  static String driverPayout = 'demo.driver@upi';
  static bool driverOnline = false;
  static bool isDriver = false;


class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: navyDark,
      body: Stack(
        fit: StackFit.expand,
        children: [
          CustomPaint(painter: TempleBackdropPainter()),
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  const Color(0xFF061B43).withValues(alpha: 0.08),
                  const Color(0xFF061B43).withValues(alpha: 0.30),
                  const Color(0xFF04183E).withValues(alpha: 0.98),
                ],
                stops: const [0.0, 0.45, 1.0],
              ),
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(28, 20, 28, 20),
              child: Column(
                children: [
                  const Spacer(flex: 3),
                  const BrandMark(size: 142),
                  const SizedBox(height: 16),
                  const Text.rich(
                    TextSpan(
                      children: [
                        TextSpan(
                          text: 'Nandi',
                          style: TextStyle(color: Colors.white),
                        ),
                        TextSpan(
                          text: 'rides',
                          style: TextStyle(color: yellow),
                        ),
                      ],
                    ),
                    style: TextStyle(
                      fontSize: 37,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -1.2,
                    ),
                  ),
                  const SizedBox(height: 7),
                  const Text(
                    'Your Ride  •  Our Priority',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      letterSpacing: .4,
                    ),
                  ),
                  const Spacer(flex: 3),
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: yellow,
                        foregroundColor: navyDark,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                      ),
                      onPressed: () => Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(builder: (_) => const LoginScreen()),
                      ),
                      child: const Text(
                        'Get Started',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 13),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white,
                        side: const BorderSide(color: yellow, width: 1.3),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                      ),
                      onPressed: () => Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(builder: (_) => const LoginScreen()),
                      ),
                      child: const Text(
                        'Login',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 26),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class BrandMark extends StatelessWidget {
  const BrandMark({super.key, this.size = 100});
  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Icon(
            Icons.directions_car_filled_rounded,
            color: Colors.white,
            size: size * .48,
          ),
          Positioned(
            top: size * .01,
            child: Icon(Icons.location_on, color: yellow, size: size * .48),
          ),
          Positioned(
            bottom: size * .03,
            left: size * .03,
            child: Transform.rotate(
              angle: -.55,
              child: Icon(
                Icons.refresh_rounded,
                color: Colors.white,
                size: size * .35,
              ),
            ),
          ),
          Positioned(
            bottom: size * .03,
            right: size * .03,
            child: Transform.rotate(
              angle: .55,
              child: Icon(
                Icons.refresh_rounded,
                color: Colors.white,
                size: size * .35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class TempleBackdropPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final canvasRect = Offset.zero & size;
    final sky = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFF142D67),
          Color(0xFF6E719F),
          Color(0xFFEB9C9A),
          Color(0xFF173C70),
        ],
        stops: [0.0, .42, .64, 1.0],
      ).createShader(canvasRect);
    canvas.drawRect(canvasRect, sky);

    final glow = Paint()
      ..color = const Color(0xFFFFC3A5).withValues(alpha: .25);
    canvas.drawCircle(
      Offset(size.width * .55, size.height * .34),
      size.width * .42,
      glow,
    );

    final mountainPaint = Paint()
      ..color = const Color(0xFF263D70).withValues(alpha: .78);
    final mountain = Path()
      ..moveTo(0, size.height * .53)
      ..lineTo(size.width * .15, size.height * .37)
      ..lineTo(size.width * .27, size.height * .49)
      ..lineTo(size.width * .43, size.height * .31)
      ..lineTo(size.width * .57, size.height * .48)
      ..lineTo(size.width * .72, size.height * .35)
      ..lineTo(size.width * .91, size.height * .51)
      ..lineTo(size.width, size.height * .43)
      ..lineTo(size.width, size.height * .77)
      ..lineTo(0, size.height * .77)
      ..close();
    canvas.drawPath(mountain, mountainPaint);

    final water = Paint()
      ..color = const Color(0xFF0A2D60).withValues(alpha: .65);
    canvas.drawRect(
      Rect.fromLTWH(0, size.height * .68, size.width, size.height * .32),
      water,
    );

    final templePaint = Paint()
      ..color = const Color(0xFF10264F).withValues(alpha: .92);
    final cx = size.width * .55;
    final baseY = size.height * .70;
    void rect(double x, double y, double w, double h) {
      canvas.drawRect(Rect.fromLTWH(x, y, w, h), templePaint);
    }

    void roof(double x, double y, double w, double h) {
      final path = Path()
        ..moveTo(x - w * .13, y + h)
        ..lineTo(x + w * .5, y)
        ..lineTo(x + w * 1.13, y + h)
        ..close();
      canvas.drawPath(path, templePaint);
      rect(x, y + h, w, h * .30);
    }

    rect(
      cx - size.width * .16,
      baseY - size.height * .13,
      size.width * .32,
      size.height * .18,
    );
    roof(
      cx - size.width * .14,
      baseY - size.height * .28,
      size.width * .28,
      size.height * .055,
    );
    rect(
      cx - size.width * .105,
      baseY - size.height * .37,
      size.width * .21,
      size.height * .10,
    );
    roof(
      cx - size.width * .105,
      baseY - size.height * .42,
      size.width * .21,
      size.height * .045,
    );
    rect(
      cx - size.width * .068,
      baseY - size.height * .49,
      size.width * .136,
      size.height * .075,
    );
    roof(
      cx - size.width * .068,
      baseY - size.height * .525,
      size.width * .136,
      size.height * .035,
    );
    rect(
      cx - size.width * .037,
      baseY - size.height * .575,
      size.width * .074,
      size.height * .055,
    );
    roof(
      cx - size.width * .037,
      baseY - size.height * .602,
      size.width * .074,
      size.height * .027,
    );
    final spirePaint = Paint();
    spirePaint.color = templePaint.color;
    spirePaint.strokeWidth = 3;
    canvas.drawLine(
      Offset(cx, baseY - size.height * .69),
      Offset(cx, baseY - size.height * .60),
      spirePaint,
    );

    for (int i = 0; i < 5; i++) {
      final x = cx - size.width * .12 + i * size.width * .06;
      rect(x, baseY - size.height * .10, size.width * .022, size.height * .10);
      rect(x, baseY - size.height * .31, size.width * .022, size.height * .08);
    }
    final reflection = Paint()
      ..color = const Color(0xFF7A9BC5).withValues(alpha: .16)
      ..strokeWidth = 2;
    for (int i = 0; i < 12; i++) {
      final y = size.height * (.76 + i * .018);
      canvas.drawLine(
        Offset(size.width * .15, y),
        Offset(size.width * (.40 + (i % 3) * .12), y),
        reflection,
      );
    }
    final treePaint = Paint()
      ..color = const Color(0xFF071D43).withValues(alpha: .85);
    for (int i = 0; i < 11; i++) {
      final x = size.width * (i / 10);
      final h = size.height * (.08 + (i % 3) * .025);
      final y = size.height * .70;
      final path = Path()
        ..moveTo(x, y - h)
        ..lineTo(x - size.width * .035, y)
        ..lineTo(x + size.width * .035, y)
        ..close();
      canvas.drawPath(path, treePaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final formKey = GlobalKey<FormState>();
  final contactController = TextEditingController();
  final passwordController = TextEditingController();
  bool isSignup = false;
  bool hidePassword = true;

  @override
  void dispose() {
    contactController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void continueToApp() {
    if (!formKey.currentState!.validate()) return;
    AppState.contact = contactController.text.trim();
    AppState.name = isSignup ? 'New NandiRide Customer' : 'NandiRide Customer';
    AppState.driverContact = contactController.text.trim();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const ModeSelectionScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const SplashScreen()),
          ),
          icon: const Icon(Icons.arrow_back),
        ),
        title: const Text('NandiRide'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 22),
            const Icon(Icons.account_circle_outlined, size: 76, color: navy),
            const SizedBox(height: 16),
            Text(
              isSignup ? 'Create your account' : 'Welcome Back',
              style: const TextStyle(
                fontSize: 27,
                fontWeight: FontWeight.w900,
                color: navyDark,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              isSignup
                  ? 'Sign up to start your journey.'
                  : 'Login to continue with NandiRide.',
              style: const TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 28),
            Form(
              key: formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: contactController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Mobile number or email',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                    validator: (v) => (v == null || v.trim().length < 5)
                        ? 'Enter a valid mobile number or email'
                        : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: passwordController,
                    obscureText: hidePassword,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        onPressed: () =>
                            setState(() => hidePassword = !hidePassword),
                        icon: Icon(
                          hidePassword
                              ? Icons.visibility_outlined
                              : Icons.visibility_off_outlined,
                        ),
                      ),
                    ),
                    validator: (v) => (v == null || v.length < 6)
                        ? 'Password must be at least 6 characters'
                        : null,
                  ),
                  if (!isSignup)
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () => ScaffoldMessenger.of(context)
                            .showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Connect password reset to your backend API.',
                                ),
                              ),
                            ),
                        child: const Text('Forgot Password?'),
                      ),
                    ),
                  const SizedBox(height: 18),
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: navy,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                      ),
                      onPressed: continueToApp,
                      child: Text(
                        isSignup ? 'Create Account' : 'Login',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  isSignup
                      ? 'Already have an account?'
                      : "Don't have an account?",
                ),
                TextButton(
                  onPressed: () => setState(() => isSignup = !isSignup),
                  child: Text(isSignup ? 'Login' : 'Sign Up'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'Demo mode: authentication is local only until the Django API is connected.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.black45, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int index = 0;
  void refreshShell() => setState(() {});
  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(onBooked: refreshShell),
      HistoryScreen(onChanged: refreshShell),
      const ProfileScreen(),
    ];
    return Scaffold(
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (v) => setState(() => index = v),
        indicatorColor: yellow.withValues(alpha: 0.35),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.history),
            label: 'Ride History',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.onBooked});
  final VoidCallback onBooked;
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final pickupController = TextEditingController();
  final dropController = TextEditingController();
  String vehicle = 'Auto';
  int fareFor(String v) => v == 'Bike'
      ? 20
      : v == 'Auto'
      ? 35
      : 60;

  @override
  void dispose() {
    pickupController.dispose();
    dropController.dispose();
    super.dispose();
  }

  void bookRide() {
    if (pickupController.text.trim().isEmpty ||
        dropController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter pickup and drop locations.'),
        ),
      );
      return;
    }
    final ride = RideRecord(
      pickup: pickupController.text.trim(),
      drop: dropController.text.trim(),
      vehicle: vehicle,
      fare: fareFor(vehicle),
    );
    AppState.rides.insert(0, ride);
    AppState.driverRequests.insert(0, ride);
    widget.onBooked();
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => TrackingScreen(ride: ride)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: yellow,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.local_taxi, color: navyDark),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'NandiRide',
                  style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20),
                ),
                Text(
                  'Your ride, your way',
                  style: TextStyle(fontSize: 11, color: Colors.white70),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Switch mode',
            onPressed: () => Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const ModeSelectionScreen()),
            ),
            icon: const Icon(Icons.swap_horiz_rounded),
          ),
          IconButton(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ProfileScreen()),
            ),
            icon: const Icon(Icons.account_circle_outlined, size: 28),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [navy, navyDark],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(24),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'NAMASTE! 👋',
                  style: TextStyle(
                    color: yellow,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.4,
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  'Where would you\nlike to go?',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    fontWeight: FontWeight.w900,
                    height: 1.15,
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  'Book a comfortable ride around your city.',
                  style: TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ),
          const SizedBox(height: 22),
          const Text(
            'Plan your ride',
            style: TextStyle(
              fontSize: 21,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE0E6EF)),
            ),
            child: Column(
              children: [
                TextField(
                  controller: pickupController,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Pickup location',
                    hintText: 'Enter pickup point',
                    prefixIcon: Icon(Icons.my_location, color: Colors.green),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: dropController,
                  decoration: const InputDecoration(
                    labelText: 'Drop location',
                    hintText: 'Where do you want to go?',
                    prefixIcon: Icon(
                      Icons.location_on,
                      color: Colors.deepOrange,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 22),
          const Text(
            'Choose your ride',
            style: TextStyle(
              fontSize: 21,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: VehicleCard(
                  name: 'Bike',
                  subtitle: 'Quick ride',
                  fare: '₹20+',
                  icon: Icons.two_wheeler,
                  selected: vehicle == 'Bike',
                  onTap: () => setState(() => vehicle = 'Bike'),
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: VehicleCard(
                  name: 'Auto',
                  subtitle: 'Everyday',
                  fare: '₹35+',
                  icon: Icons.electric_rickshaw,
                  selected: vehicle == 'Auto',
                  onTap: () => setState(() => vehicle = 'Auto'),
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: VehicleCard(
                  name: 'Cab',
                  subtitle: 'Comfort',
                  fare: '₹60+',
                  icon: Icons.local_taxi,
                  selected: vehicle == 'Cab',
                  onTap: () => setState(() => vehicle = 'Cab'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                const Icon(Icons.payments_outlined, color: navy, size: 27),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Estimated fare',
                        style: TextStyle(color: Colors.black54),
                      ),
                      Text(
                        'Pay after ride confirmation',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),
                Text(
                  '₹${fareFor(vehicle)}+',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    color: navy,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          SizedBox(
            height: 55,
            child: ElevatedButton.icon(
              onPressed: bookRide,
              icon: const Icon(Icons.arrow_forward_rounded),
              label: const Text(
                'Book Ride',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: yellow,
                foregroundColor: navyDark,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Center(
            child: Text(
              'NandiRide • Uttarakhand',
              style: TextStyle(color: Colors.black45, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}

class VehicleCard extends StatelessWidget {
  const VehicleCard({
    super.key,
    required this.name,
    required this.subtitle,
    required this.fare,
    required this.icon,
    required this.selected,
    required this.onTap,
  });
  final String name;
  final String subtitle;
  final String fare;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 4),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFFFFF4C7) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: selected ? navy : const Color(0xFFDCE3ED),
            width: selected ? 1.8 : 1,
          ),
        ),
        child: Column(
          children: [
            Icon(icon, size: 32, color: navy),
            const SizedBox(height: 8),
            Text(
              name,
              style: const TextStyle(
                fontWeight: FontWeight.w900,
                color: navyDark,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              subtitle,
              style: const TextStyle(fontSize: 10, color: Colors.black54),
            ),
            const SizedBox(height: 5),
            Text(
              fare,
              style: const TextStyle(fontWeight: FontWeight.bold, color: navy),
            ),
          ],
        ),
      ),
    );
  }
}

class TrackingScreen extends StatefulWidget {
  const TrackingScreen({super.key, required this.ride});
  final RideRecord ride;
  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  @override
  Widget build(BuildContext context) {
    final ride = widget.ride;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ride Tracking'),
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.arrow_back),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: Container(
              width: double.infinity,
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFE4ECF3),
                borderRadius: BorderRadius.circular(22),
              ),
              child: Stack(
                children: [
                  Positioned.fill(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(22),
                      child: CustomPaint(painter: MapPlaceholderPainter()),
                    ),
                  ),
                  const Positioned(
                    left: 28,
                    top: 35,
                    child: _MapLabel(icon: Icons.location_on, label: 'Pickup'),
                  ),
                  const Positioned(
                    right: 25,
                    top: 150,
                    child: _MapLabel(icon: Icons.flag, label: 'Drop'),
                  ),
                  const Center(
                    child: Icon(Icons.local_taxi, color: navy, size: 46),
                  ),
                  Positioned(
                    left: 16,
                    bottom: 16,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.info_outline, color: navy),
                          SizedBox(width: 7),
                          Text(
                            'Demo map preview',
                            style: TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 24),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(26)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Ride status',
                            style: TextStyle(color: Colors.black54),
                          ),
                          Text(
                            ride.status,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w900,
                              color: navyDark,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 10,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFF4C7),
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: Text(
                        '₹${ride.fare}+',
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w900,
                          color: navy,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _routeLine(
                  Icons.my_location,
                  'Pickup',
                  ride.pickup,
                  Colors.green,
                ),
                const SizedBox(height: 10),
                _routeLine(
                  Icons.location_on,
                  'Drop',
                  ride.drop,
                  Colors.deepOrange,
                ),
                const SizedBox(height: 18),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => ScaffoldMessenger.of(context)
                            .showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Driver calling will work after backend/phone integration.',
                                ),
                              ),
                            ),
                        icon: const Icon(Icons.call),
                        label: const Text('Call'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => setState(() {
                          ride.status = ride.status == 'Searching for driver'
                              ? 'Driver assigned (demo)'
                              : 'Searching for driver';
                        }),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: navy,
                          foregroundColor: Colors.white,
                        ),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Refresh status'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Driver GPS and live booking updates require a connected backend and maps API key.',
                  style: TextStyle(fontSize: 11, color: Colors.black45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MapLabel extends StatelessWidget {
  const _MapLabel({required this.icon, required this.label});
  final IconData icon;
  final String label;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: navy, size: 18),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    ),
  );
}

Widget _routeLine(IconData icon, String label, String value, Color color) =>
    Row(
      children: [
        Icon(icon, color: color, size: 22),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(fontSize: 11, color: Colors.black54),
              ),
              Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
            ],
          ),
        ),
      ],
    );

class MapPlaceholderPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final road = Paint()
      ..color = Colors.white
      ..strokeWidth = 16
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final minor = Paint()
      ..color = const Color(0xFFCBD8E4)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
    final route = Paint()
      ..color = const Color(0xFF2374D8)
      ..strokeWidth = 5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    for (var i = 1; i < 6; i++) {
      final y = size.height * i / 6;
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y + (i.isEven ? 25 : -18)),
        minor,
      );
    }
    for (var i = 1; i < 5; i++) {
      final x = size.width * i / 5;
      canvas.drawLine(Offset(x, 0), Offset(x + 20, size.height), minor);
    }
    final path1 = Path()
      ..moveTo(-10, size.height * .25)
      ..lineTo(size.width * .35, size.height * .4)
      ..lineTo(size.width * .6, size.height * .35)
      ..lineTo(size.width + 10, size.height * .55);
    final path2 = Path()
      ..moveTo(size.width * .1, size.height + 10)
      ..lineTo(size.width * .35, size.height * .65)
      ..lineTo(size.width * .55, size.height * .7)
      ..lineTo(size.width * .8, -10);
    canvas.drawPath(path1, road);
    canvas.drawPath(path2, road);
    final routePath = Path()
      ..moveTo(size.width * .18, size.height * .23)
      ..lineTo(size.width * .4, size.height * .38)
      ..lineTo(size.width * .52, size.height * .57)
      ..lineTo(size.width * .76, size.height * .72);
    canvas.drawPath(routePath, route);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key, required this.onChanged});
  final VoidCallback onChanged;
  @override
  Widget build(BuildContext context) {
    final rides = AppState.rides;
    return Scaffold(
      appBar: AppBar(title: const Text('Ride History')),
      body: rides.isEmpty
          ? const Center(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.history, size: 70, color: Colors.black26),
                    SizedBox(height: 12),
                    Text(
                      'No rides yet',
                      style: TextStyle(
                        fontSize: 21,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      'Your booked rides will appear here.',
                      style: TextStyle(color: Colors.black54),
                    ),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: rides.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, i) {
                final ride = rides[i];
                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: const Color(0xFFE1E7EF)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.local_taxi, color: navy),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              '${ride.vehicle} ride',
                              style: const TextStyle(
                                fontWeight: FontWeight.w900,
                                fontSize: 16,
                              ),
                            ),
                          ),
                          Text(
                            '₹${ride.fare}+',
                            style: const TextStyle(
                              color: navy,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 22),
                      _routeLine(
                        Icons.my_location,
                        'Pickup',
                        ride.pickup,
                        Colors.green,
                      ),
                      const SizedBox(height: 10),
                      _routeLine(
                        Icons.location_on,
                        'Drop',
                        ride.drop,
                        Colors.deepOrange,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              ride.status,
                              style: const TextStyle(
                                color: Colors.black54,
                                fontSize: 12,
                              ),
                            ),
                          ),
                          TextButton(
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => TrackingScreen(ride: ride),
                              ),
                            ),
                            child: const Text('View details'),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Future<void> _editProfile() async {
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => const DemoProfileEditScreen(isDriver: false),
      ),
    );
    if (changed == true && mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: [
          IconButton(
            tooltip: 'Edit profile',
            icon: const Icon(Icons.edit_outlined),
            onPressed: _editProfile,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [navy, navyDark]),
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 42,
                  backgroundColor: yellow,
                  child: Icon(Icons.person, size: 46, color: navyDark),
                ),
                const SizedBox(height: 12),
                Text(
                  AppState.name,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  AppState.contact.isEmpty
                      ? 'No contact saved'
                      : AppState.contact,
                  style: const TextStyle(color: Colors.white70),
                ),
                const SizedBox(height: 10),
                const Chip(
                  avatar: Icon(Icons.verified_user_outlined, size: 17),
                  label: Text('Demo Customer'),
                  backgroundColor: yellow,
                ),
                const SizedBox(height: 7),
                Text(
                  'Customer ID: ${AppState.customerId}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Personal Information',
            style: TextStyle(
              fontSize: 19,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 10),
          _profileInfo(Icons.person_outline, 'Full name', AppState.name),
          _profileInfo(
            Icons.phone_outlined,
            'Mobile / Email',
            AppState.contact,
          ),
          _profileInfo(
            Icons.badge_outlined,
            'Customer ID',
            AppState.customerId,
          ),
          _profileInfo(
            Icons.location_on_outlined,
            'Saved address',
            AppState.customerAddress,
          ),
          const SizedBox(height: 18),
          const Text(
            'Account & Services',
            style: TextStyle(
              fontSize: 19,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 10),
          _profileAction(
            Icons.edit_outlined,
            'Edit personal information',
            'Update demo name and contact',
            _editProfile,
          ),
          _profileAction(
            Icons.payments_outlined,
            'Payment methods',
            'Selected: ${AppState.customerPayment}',
            _showPaymentOptions,
          ),
          _profileAction(
            Icons.shield_outlined,
            'Safety & support',
            'Ride assistance and help',
            () => _showInfo('Safety & Support'),
          ),
          _profileAction(
            Icons.notifications_none,
            'Notifications',
            'Ride and account updates',
            () => _showInfo('Notifications'),
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () => Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const SplashScreen()),
              (_) => false,
            ),
            icon: const Icon(Icons.logout),
            label: const Text('Logout'),
            style: OutlinedButton.styleFrom(
              foregroundColor: navy,
              minimumSize: const Size.fromHeight(50),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Static testing profile. Changes are stored in memory only and reset when the app restarts.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: Colors.black45),
          ),
        ],
      ),
    );
  }

  Widget _profileInfo(IconData icon, String title, String value) => Card(
    color: Colors.white,
    elevation: 0,
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFFEAF0FA),
        child: Icon(icon, color: navy),
      ),
      title: Text(
        title,
        style: const TextStyle(fontSize: 12, color: Colors.black54),
      ),
      subtitle: Text(
        value.isEmpty ? 'Not provided' : value,
        style: const TextStyle(fontWeight: FontWeight.w700, color: navyDark),
      ),
    ),
  );

  Widget _profileAction(
    IconData icon,
    String title,
    String subtitle,
    VoidCallback onTap,
  ) => Card(
    color: Colors.white,
    elevation: 0,
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFFEAF0FA),
        child: Icon(icon, color: navy),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    ),
  );

  void _showPaymentOptions() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const ListTile(
              title: Text(
                'Payment methods',
                style: TextStyle(fontWeight: FontWeight.w900),
              ),
              subtitle: Text('Choose a demo payment method'),
            ),
            for (final method in ['Cash', 'UPI', 'Card'])
              ListTile(
                leading: Icon(
                  AppState.customerPayment == method
                      ? Icons.radio_button_checked
                      : Icons.radio_button_off,
                  color: navy,
                ),
                title: Text(method),
                onTap: () {
                  setState(() => AppState.customerPayment = method);
                  Navigator.pop(sheetContext);
                },
              ),
          ],
        ),
      ),
    );
  }

  void _showInfo(String title) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(title),
        content: const Text(
          'This section is available as a static demo. Backend integration can be added later.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class ModeSelectionScreen extends StatelessWidget {
  const ModeSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Choose your mode')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const SizedBox(height: 18),
          const BrandMark(size: 90),
          const SizedBox(height: 14),
          const Text(
            'Welcome to NandiRide',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 25,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Choose how you want to use the app.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.black54),
          ),
          const SizedBox(height: 28),
          _ModeCard(
            icon: Icons.person_pin_circle_rounded,
            title: 'Customer',
            subtitle: 'Book rides, track trips and view ride history.',
            color: navy,
            onTap: () {
              AppState.isDriver = false;
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const MainShell()),
              );
            },
          ),
          const SizedBox(height: 14),
          _ModeCard(
            icon: Icons.local_taxi_rounded,
            title: 'Driver',
            subtitle: 'Go online, accept ride requests and manage earnings.',
            color: const Color(0xFF15803D),
            onTap: () {
              AppState.isDriver = true;
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const DriverShell()),
              );
            },
          ),
          const SizedBox(height: 22),
          const Text(
            'Demo mode: both modes currently use local app data. Real account roles must be verified by the Django backend.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: Colors.black45),
          ),
        ],
      ),
    );
  }
}

class _ModeCard extends StatelessWidget {
  const _ModeCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(22),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(22),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0xFFDCE3ED)),
          ),
          child: Row(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: .10),
                  borderRadius: BorderRadius.circular(17),
                ),
                child: Icon(icon, color: color, size: 32),
              ),
              const SizedBox(width: 15),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$title Mode',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        color: color,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: Colors.black54,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded, color: navy),
            ],
          ),
        ),
      ),
    );
  }
}

class DriverShell extends StatefulWidget {
  const DriverShell({super.key});
  @override
  State<DriverShell> createState() => _DriverShellState();
}

class _DriverShellState extends State<DriverShell> {
  int index = 0;
  bool isOnline = false;
  void refresh() => setState(() {});

  @override
  Widget build(BuildContext context) {
    final pages = [
      DriverHomeScreen(
        isOnline: isOnline,
        onOnlineChanged: (value) => setState(() {
          isOnline = value;
          AppState.driverOnline = value;
        }),
        onChanged: refresh,
      ),
      DriverRidesScreen(onChanged: refresh),
      const DriverEarningsScreen(),
      const DriverProfileScreen(),
    ];
    return Scaffold(
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (value) => setState(() => index = value),
        indicatorColor: yellow.withValues(alpha: .35),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.route_outlined),
            selectedIcon: Icon(Icons.route),
            label: 'My Rides',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet_outlined),
            selectedIcon: Icon(Icons.account_balance_wallet),
            label: 'Earnings',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class DriverHomeScreen extends StatelessWidget {
  const DriverHomeScreen({
    super.key,
    required this.isOnline,
    required this.onOnlineChanged,
    required this.onChanged,
  });
  final bool isOnline;
  final ValueChanged<bool> onOnlineChanged;
  final VoidCallback onChanged;

  @override
  Widget build(BuildContext context) {
    final requests = AppState.driverRequests
        .where((ride) => ride.status == 'New request')
        .toList();
    final completed = AppState.driverRequests
        .where((ride) => ride.status == 'Completed')
        .length;
    final total = AppState.driverRequests
        .where((ride) => ride.status == 'Completed')
        .fold<int>(0, (sum, ride) => sum + ride.fare);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Switch mode',
            onPressed: () => Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const ModeSelectionScreen()),
            ),
            icon: const Icon(Icons.swap_horiz_rounded),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0B7A43), Color(0xFF064E36)],
              ),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'DRIVER PARTNER',
                  style: TextStyle(
                    color: Color(0xFFC8F7D8),
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Namaste, ${AppState.name}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  isOnline ? 'You are online and can receive rides.' : 'You are offline. Turn online to start receiving rides.',
                  style: const TextStyle(color: Colors.white70),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        isOnline ? 'ONLINE' : 'OFFLINE',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1.3,
                        ),
                      ),
                    ),
                    Switch(
                      value: isOnline,
                      onChanged: onOnlineChanged,
                      activeColor: yellow,
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _DriverStat(
                  title: 'New requests',
                  value: '${requests.length}',
                  icon: Icons.notifications_active_outlined,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _DriverStat(
                  title: 'Completed trips',
                  value: '$completed',
                  icon: Icons.check_circle_outline,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _DriverStat(
                  title: 'Demo earnings',
                  value: '₹$total',
                  icon: Icons.currency_rupee,
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Ride requests',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    color: navyDark,
                  ),
                ),
              ),
              Text(
                '${requests.length} available',
                style: const TextStyle(color: Colors.black54, fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (!isOnline)
            const _DriverEmpty(
              icon: Icons.pause_circle_outline,
              title: 'You are offline',
              message: 'Turn on the switch above to review demo ride requests.',
            )
          else if (requests.isEmpty)
            const _DriverEmpty(
              icon: Icons.inbox_outlined,
              title: 'No new requests',
              message: 'New customer bookings will appear here after backend integration.',
            )
          else
            ...requests.map(
              (ride) => _RideRequestCard(ride: ride, onChanged: onChanged),
            ),
          const SizedBox(height: 12),
          const Text(
            'Demo notice: ride requests and earnings are stored locally on this device. Online status is not sent to the server yet.',
            style: TextStyle(color: Colors.black45, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

class _DriverStat extends StatelessWidget {
  const _DriverStat({
    required this.title,
    required this.value,
    required this.icon,
  });
  final String title;
  final String value;
  final IconData icon;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(17),
      border: Border.all(color: const Color(0xFFE1E7EF)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: navy, size: 21),
        const SizedBox(height: 9),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w900,
            color: navyDark,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          title,
          style: const TextStyle(fontSize: 10, color: Colors.black54),
        ),
      ],
    ),
  );
}

class _RideRequestCard extends StatelessWidget {
  const _RideRequestCard({required this.ride, required this.onChanged});
  final RideRecord ride;
  final VoidCallback onChanged;

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 12),
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: const Color(0xFFDCE3ED)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.local_taxi, color: navy),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                '${ride.vehicle} ride request',
                style: const TextStyle(
                  fontWeight: FontWeight.w900,
                  fontSize: 16,
                  color: navyDark,
                ),
              ),
            ),
            Text(
              '₹${ride.fare}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w900,
                color: navy,
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        _routeLine(Icons.my_location, 'Pickup', ride.pickup, Colors.green),
        const SizedBox(height: 10),
        _routeLine(Icons.location_on, 'Drop', ride.drop, Colors.deepOrange),
        const SizedBox(height: 15),
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () {
                  ride.status = 'Rejected';
                  onChanged();
                },
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.red,
                  side: const BorderSide(color: Colors.redAccent),
                ),
                child: const Text('Reject'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: ElevatedButton(
                onPressed: () {
                  ride.status = 'Accepted';
                  onChanged();
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          DriverTripScreen(ride: ride, onChanged: onChanged),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: navy,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Accept ride'),
              ),
            ),
          ],
        ),
      ],
    ),
  );
}

class DriverRidesScreen extends StatelessWidget {
  const DriverRidesScreen({super.key, required this.onChanged});
  final VoidCallback onChanged;
  @override
  Widget build(BuildContext context) {
    final rides = AppState.driverRequests
        .where((ride) => ride.status != 'New request')
        .toList();
    return Scaffold(
      appBar: AppBar(title: const Text('My Rides')),
      body: rides.isEmpty
          ? const _DriverEmpty(
              icon: Icons.route_outlined,
              title: 'No trips yet',
              message: 'Accepted and completed trips will appear here.',
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: rides.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final ride = rides[index];
                return Card(
                  color: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(17),
                    side: const BorderSide(color: Color(0xFFE1E7EF)),
                  ),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: const Color(0xFFEAF0FA),
                      child: Icon(
                        ride.status == 'Completed'
                            ? Icons.check
                            : ride.status == 'Rejected'
                            ? Icons.close
                            : Icons.local_taxi,
                        color: navy,
                      ),
                    ),
                    title: Text(
                      '${ride.pickup} → ${ride.drop}',
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text('${ride.status} • ${ride.vehicle}'),
                    trailing: Text(
                      '₹${ride.fare}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w900,
                        color: navy,
                      ),
                    ),
                    onTap: ride.status == 'Accepted' || ride.status == 'Started'
                        ? () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => DriverTripScreen(
                                ride: ride,
                                onChanged: onChanged,
                              ),
                            ),
                          )
                        : null,
                  ),
                );
              },
            ),
    );
  }
}

class DriverTripScreen extends StatefulWidget {
  const DriverTripScreen({
    super.key,
    required this.ride,
    required this.onChanged,
  });
  final RideRecord ride;
  final VoidCallback onChanged;
  @override
  State<DriverTripScreen> createState() => _DriverTripScreenState();
}

class _DriverTripScreenState extends State<DriverTripScreen> {
  void updateStatus(String status) {
    setState(() => widget.ride.status = status);
    widget.onChanged();
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('Trip status updated: $status')));
  }

  @override
  Widget build(BuildContext context) {
    final ride = widget.ride;
    final next = ride.status == 'Accepted'
        ? 'Start trip'
        : ride.status == 'Started'
        ? 'Complete trip'
        : null;
    return Scaffold(
      appBar: AppBar(title: const Text('Trip details')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: navy,
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'TRIP FARE',
                  style: TextStyle(color: Colors.white70, letterSpacing: 1.2),
                ),
                const SizedBox(height: 8),
                Text(
                  '₹${ride.fare}',
                  style: const TextStyle(
                    color: yellow,
                    fontSize: 34,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Status: ${ride.status}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            color: Colors.white,
            elevation: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _routeLine(
                    Icons.my_location,
                    'Pickup',
                    ride.pickup,
                    Colors.green,
                  ),
                  const SizedBox(height: 18),
                  _routeLine(
                    Icons.location_on,
                    'Drop',
                    ride.drop,
                    Colors.deepOrange,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            height: 190,
            decoration: BoxDecoration(
              color: const Color(0xFFE4ECF3),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.map_outlined, size: 48, color: navy),
                  SizedBox(height: 8),
                  Text(
                    'Map / navigation placeholder',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  Text(
                    'Connect Google Maps or another maps SDK',
                    style: TextStyle(color: Colors.black54, fontSize: 11),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 18),
          if (next != null)
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  updateStatus(
                    ride.status == 'Accepted' ? 'Started' : 'Completed',
                  );
                  if (ride.status == 'Completed') Navigator.pop(context);
                },
                icon: Icon(
                  ride.status == 'Accepted'
                      ? Icons.play_arrow
                      : Icons.check_circle,
                ),
                label: Text(next),
                style: ElevatedButton.styleFrom(
                  backgroundColor: yellow,
                  foregroundColor: navyDark,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
              ),
            ),
          if (ride.status == 'Completed')
            const Text(
              'Trip completed. Earnings are shown in demo totals.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.green,
                fontWeight: FontWeight.w700,
              ),
            ),
          const SizedBox(height: 10),
          const Text(
            'Trip status is local demo data and is not yet synchronized with Django.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.black45, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

class DriverEarningsScreen extends StatelessWidget {
  const DriverEarningsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final completed = AppState.driverRequests
        .where((ride) => ride.status == 'Completed')
        .toList();
    final total = completed.fold<int>(0, (sum, ride) => sum + ride.fare);
    return Scaffold(
      appBar: AppBar(title: const Text('Earnings')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [navy, navyDark]),
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'TOTAL DEMO EARNINGS',
                  style: TextStyle(color: Colors.white70, letterSpacing: 1.1),
                ),
                const SizedBox(height: 10),
                Text(
                  '₹$total',
                  style: const TextStyle(
                    color: yellow,
                    fontSize: 36,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  '${completed.length} completed trip(s)',
                  style: const TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Completed trips',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 10),
          if (completed.isEmpty)
            const _DriverEmpty(
              icon: Icons.account_balance_wallet_outlined,
              title: 'No earnings yet',
              message: 'Complete a demo trip to see earnings here.',
            )
          else
            ...completed.map(
              (ride) => Card(
                color: Colors.white,
                elevation: 0,
                child: ListTile(
                  leading: const Icon(Icons.check_circle, color: Colors.green),
                  title: Text(
                    '${ride.pickup} → ${ride.drop}',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: const Text('Completed trip'),
                  trailing: Text(
                    '₹${ride.fare}',
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      color: navy,
                    ),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 12),
          const Text(
            'Actual payouts, commissions and transaction history require backend integration.',
            style: TextStyle(color: Colors.black45, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

class DriverProfileScreen extends StatefulWidget {
  const DriverProfileScreen({super.key});
  @override
  State<DriverProfileScreen> createState() => _DriverProfileScreenState();
}

class _DriverProfileScreenState extends State<DriverProfileScreen> {
  Future<void> _editProfile() async {
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => const DemoProfileEditScreen(isDriver: true),
      ),
    );
    if (changed == true && mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Profile'),
        actions: [
          IconButton(
            tooltip: 'Edit driver profile',
            icon: const Icon(Icons.edit_outlined),
            onPressed: _editProfile,
          ),
          IconButton(
            tooltip: 'Switch mode',
            onPressed: () => Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const ModeSelectionScreen()),
            ),
            icon: const Icon(Icons.swap_horiz_rounded),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0B7A43), Color(0xFF064E36)],
              ),
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 43,
                  backgroundColor: yellow,
                  child: Icon(Icons.person, color: navyDark, size: 46),
                ),
                const SizedBox(height: 12),
                Text(
                  AppState.driverName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  AppState.driverContact,
                  style: const TextStyle(color: Colors.white70),
                ),
                const SizedBox(height: 10),
                const Chip(
                  avatar: Icon(Icons.verified_user_outlined, size: 17),
                  label: Text('Demo Driver Account'),
                  backgroundColor: yellow,
                ),
                const SizedBox(height: 7),
                Text(
                  'Driver ID: ${AppState.driverId}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 9,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: .12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        AppState.driverOnline
                            ? Icons.circle
                            : Icons.circle_outlined,
                        size: 12,
                        color: AppState.driverOnline ? yellow : Colors.white70,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        AppState.driverOnline ? 'ONLINE' : 'OFFLINE',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Driver Information',
            style: TextStyle(
              fontSize: 19,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 10),
          _info(Icons.person_outline, 'Full name', AppState.driverName),
          _info(Icons.phone_outlined, 'Contact number', AppState.driverContact),
          _info(Icons.badge_outlined, 'Driver ID', AppState.driverId),
          _info(
            Icons.credit_card_outlined,
            'Driving licence',
            AppState.driverLicence,
          ),
          _info(
            Icons.directions_car_outlined,
            'Vehicle details',
            AppState.driverVehicle,
          ),
          _info(
            Icons.account_balance_wallet_outlined,
            'Payout / UPI',
            AppState.driverPayout,
          ),
          const SizedBox(height: 18),
          const Text(
            'Driver Services',
            style: TextStyle(
              fontSize: 19,
              fontWeight: FontWeight.w900,
              color: navyDark,
            ),
          ),
          const SizedBox(height: 10),
          _action(
            Icons.edit_outlined,
            'Edit driver information',
            'Update demo profile and vehicle details',
            _editProfile,
          ),
          _action(
            Icons.verified_user_outlined,
            'Driver verification',
            'Demo only — not verified by backend',
            () => _showInfo('Driver verification'),
          ),
          _action(
            Icons.directions_car_outlined,
            'Vehicle details',
            AppState.driverVehicle,
            () => _showInfo('Vehicle details'),
          ),
          _action(
            Icons.account_balance_wallet_outlined,
            'Payout details',
            AppState.driverPayout,
            () => _showInfo('Payout details'),
          ),
          _action(
            Icons.support_agent,
            'Driver support',
            'Safety and assistance',
            () => _showInfo('Driver support'),
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () => Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const SplashScreen()),
              (_) => false,
            ),
            icon: const Icon(Icons.logout),
            label: const Text('Logout'),
            style: OutlinedButton.styleFrom(
              foregroundColor: navy,
              minimumSize: const Size.fromHeight(50),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Static demo only. Licence, vehicle and payout details are not verified or saved to Django.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.black45, fontSize: 11),
          ),
        ],
      ),
    );
  }

  Widget _info(IconData icon, String title, String value) => Card(
    color: Colors.white,
    elevation: 0,
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFFEAF0FA),
        child: Icon(icon, color: navy),
      ),
      title: Text(
        title,
        style: const TextStyle(fontSize: 12, color: Colors.black54),
      ),
      subtitle: Text(
        value.isEmpty ? 'Not provided' : value,
        style: const TextStyle(fontWeight: FontWeight.w700, color: navyDark),
      ),
    ),
  );

  Widget _action(
    IconData icon,
    String title,
    String subtitle,
    VoidCallback onTap,
  ) => Card(
    color: Colors.white,
    elevation: 0,
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFFEAF0FA),
        child: Icon(icon, color: navy),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    ),
  );

  void _showInfo(String title) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(title),
        content: const Text(
          'This is demo information. Real driver verification and saved details require backend integration.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _DriverEmpty extends StatelessWidget {
  const _DriverEmpty({
    required this.icon,
    required this.title,
    required this.message,
  });
  final IconData icon;
  final String title;
  final String message;
  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity,
    padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 18),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: const Color(0xFFE1E7EF)),
    ),
    child: Column(
      children: [
        Icon(icon, size: 42, color: Colors.black26),
        const SizedBox(height: 10),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w900,
            fontSize: 16,
            color: navyDark,
          ),
        ),
        const SizedBox(height: 5),
        Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Colors.black54),
        ),
      ],
    ),
  );
}

class DemoProfileEditScreen extends StatefulWidget {
  const DemoProfileEditScreen({super.key, required this.isDriver});
  final bool isDriver;
  @override
  State<DemoProfileEditScreen> createState() => _DemoProfileEditScreenState();
}

class _DemoProfileEditScreenState extends State<DemoProfileEditScreen> {
  final formKey = GlobalKey<FormState>();
  late final TextEditingController nameController;
  late final TextEditingController contactController;
  late final TextEditingController detailController;
  late final TextEditingController extraController;

  @override
  void initState() {
    super.initState();
    nameController = TextEditingController(
      text: widget.isDriver ? AppState.driverName : AppState.name,
    );
    contactController = TextEditingController(
      text: widget.isDriver ? AppState.driverContact : AppState.contact,
    );
    detailController = TextEditingController(
      text: widget.isDriver ? AppState.driverVehicle : AppState.customerAddress,
    );
    extraController = TextEditingController(
      text: widget.isDriver ? AppState.driverLicence : AppState.customerPayment,
    );
  }

  @override
  void dispose() {
    nameController.dispose();
    contactController.dispose();
    detailController.dispose();
    extraController.dispose();
    super.dispose();
  }

  void saveProfile() {
    if (!formKey.currentState!.validate()) return;
    if (widget.isDriver) {
      AppState.driverName = nameController.text.trim();
      AppState.driverContact = contactController.text.trim();
      AppState.driverVehicle = detailController.text.trim();
      AppState.driverLicence = extraController.text.trim();
    } else {
      AppState.name = nameController.text.trim();
      AppState.contact = contactController.text.trim();
      AppState.customerAddress = detailController.text.trim();
      AppState.customerPayment = extraController.text.trim();
    }
    Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    final isDriver = widget.isDriver;
    return Scaffold(
      appBar: AppBar(
        title: Text(isDriver ? 'Edit Driver Profile' : 'Edit Customer Profile'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: navy,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              children: [
                Icon(
                  isDriver ? Icons.local_taxi : Icons.person,
                  color: yellow,
                  size: 36,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    isDriver ? 'Driver demo details' : 'Customer demo details',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 22),
          Form(
            key: formKey,
            child: Column(
              children: [
                TextFormField(
                  controller: nameController,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(
                    labelText: 'Full name',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (value) => value == null || value.trim().isEmpty
                      ? 'Please enter a name'
                      : null,
                ),
                const SizedBox(height: 14),
                TextFormField(
                  controller: contactController,
                  keyboardType: TextInputType.text,
                  decoration: const InputDecoration(
                    labelText: 'Mobile number / email',
                    prefixIcon: Icon(Icons.phone_outlined),
                  ),
                  validator: (value) => value == null || value.trim().length < 5
                      ? 'Please enter valid contact details'
                      : null,
                ),
                const SizedBox(height: 14),
                TextFormField(
                  controller: detailController,
                  maxLines: isDriver ? 1 : 2,
                  decoration: InputDecoration(
                    labelText: isDriver ? 'Vehicle details' : 'Saved address',
                    prefixIcon: Icon(
                      isDriver
                          ? Icons.directions_car_outlined
                          : Icons.location_on_outlined,
                    ),
                  ),
                  validator: (value) => value == null || value.trim().isEmpty
                      ? 'This field is required'
                      : null,
                ),
                const SizedBox(height: 14),
                if (isDriver)
                  TextFormField(
                    controller: extraController,
                    decoration: const InputDecoration(
                      labelText: 'Driving licence (demo)',
                      prefixIcon: Icon(Icons.badge_outlined),
                    ),
                    validator: (value) => value == null || value.trim().isEmpty
                        ? 'This field is required'
                        : null,
                  )
                else
                  DropdownButtonFormField<String>(
                    value:
                        ['Cash', 'UPI', 'Card'].contains(extraController.text)
                        ? extraController.text
                        : 'Cash',
                    decoration: const InputDecoration(
                      labelText: 'Preferred payment method',
                      prefixIcon: Icon(Icons.payments_outlined),
                    ),
                    items: ['Cash', 'UPI', 'Card']
                        .map(
                          (method) => DropdownMenuItem(
                            value: method,
                            child: Text(method),
                          ),
                        )
                        .toList(),
                    onChanged: (value) =>
                        extraController.text = value ?? 'Cash',
                  ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton.icon(
                    onPressed: saveProfile,
                    icon: const Icon(Icons.save_outlined),
                    label: const Text(
                      'Save Profile',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: yellow,
                      foregroundColor: navyDark,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Testing only: changes are kept in memory until the app is restarted.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 11, color: Colors.black45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
