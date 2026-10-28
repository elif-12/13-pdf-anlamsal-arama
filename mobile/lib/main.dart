import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:webview_flutter/webview_flutter.dart';

import 'settings_screen.dart';

/// Android emulator'da 10.0.2.2, calistiran bilgisayarin localhost'una
/// karsilik gelir. Gercek telefonda test ederken Ayarlar'dan bilgisayarin
/// yerel ag IP adresine degistirilmeli (ikisi ayni WiFi'da olmali).
const String kDefaultBackendUrl = 'http://10.0.2.2:8000';
const String kPrefsKeyBackendUrl = 'backend_url';

void main() {
  runApp(const PdfSearchApp());
}

class PdfSearchApp extends StatelessWidget {
  const PdfSearchApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PDF Semantic Search',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFF2563EB),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final WebViewController _controller;
  bool _isLoading = true;
  String? _loadError;
  String _backendUrl = kDefaultBackendUrl;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFF5F6F8))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) {
            if (!mounted) return;
            setState(() {
              _isLoading = true;
              _loadError = null;
            });
          },
          onPageFinished: (_) {
            if (!mounted) return;
            setState(() => _isLoading = false);
          },
          onWebResourceError: (error) {
            if (!mounted) return;
            // Sadece ana sayfa yuklemesi basarisiz olursa hata ekranini goster;
            // sayfa icindeki kucuk kaynak hatalarinda (orn. favicon) kullaniciyi
            // bosuna korkutma.
            if (error.isForMainFrame ?? true) {
              setState(() {
                _isLoading = false;
                _loadError = 'Sunucuya baglanilamadi.\n${error.description}';
              });
            }
          },
        ),
      );
    _loadSavedUrlAndStart();
  }

  Future<void> _loadSavedUrlAndStart() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(kPrefsKeyBackendUrl);
    final url = (saved == null || saved.isEmpty) ? kDefaultBackendUrl : saved;
    if (!mounted) return;
    setState(() => _backendUrl = url);
    _controller.loadRequest(Uri.parse(url));
  }

  Future<void> _openSettings() async {
    final newUrl = await Navigator.of(context).push<String>(
      MaterialPageRoute(
        builder: (_) => SettingsScreen(currentUrl: _backendUrl),
      ),
    );
    if (newUrl == null || newUrl.isEmpty || newUrl == _backendUrl) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(kPrefsKeyBackendUrl, newUrl);
    if (!mounted) return;
    setState(() {
      _backendUrl = newUrl;
      _isLoading = true;
      _loadError = null;
    });
    _controller.loadRequest(Uri.parse(newUrl));
  }

  void _retry() {
    setState(() {
      _loadError = null;
      _isLoading = true;
    });
    _controller.loadRequest(Uri.parse(_backendUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF Semantic Search'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Yenile',
            onPressed: () => _controller.reload(),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Sunucu adresi',
            onPressed: _openSettings,
          ),
        ],
      ),
      body: SafeArea(
        child: Stack(
          children: [
            if (_loadError == null) WebViewWidget(controller: _controller),
            if (_loadError != null) _buildErrorView(),
            if (_isLoading && _loadError == null)
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: LinearProgressIndicator(minHeight: 3),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.wifi_off, size: 48, color: Colors.grey),
            const SizedBox(height: 12),
            Text(
              _loadError!,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text('Adres: $_backendUrl', style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _retry,
              icon: const Icon(Icons.refresh),
              label: const Text('Tekrar dene'),
            ),
            TextButton(
              onPressed: _openSettings,
              child: const Text('Sunucu adresini degistir'),
            ),
          ],
        ),
      ),
    );
  }
}
