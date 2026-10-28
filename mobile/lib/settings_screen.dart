import 'package:flutter/material.dart';

/// Backend adresini kullaniciya sordurup geri doner (kaydetmeyi cagiran
/// ekrana birakir, bu ekran sadece URL toplar).
class SettingsScreen extends StatefulWidget {
  final String currentUrl;

  const SettingsScreen({super.key, required this.currentUrl});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.currentUrl);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _save() {
    final url = _controller.text.trim();
    if (url.isEmpty) return;
    Navigator.of(context).pop(url);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Sunucu Adresi')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'PDF Semantic Search backend adresi.\n\n'
              '• Android emulator: 10.0.2.2, bilgisayarinin localhost adresine karsilik gelir.\n'
              '• Gercek telefon: bilgisayarinin yerel ag IP adresini yaz (orn. http://192.168.1.23:8000) '
              've telefonla bilgisayar ayni WiFi\'da olmali.\n\n'
              'Backend\'i "uvicorn main:app --host 0.0.0.0 --port 8000" ile baslatmayi unutma, '
              'yoksa disaridan erisilemez.',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                labelText: 'Backend URL',
                hintText: 'http://10.0.2.2:8000',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
              autofocus: true,
              onSubmitted: (_) => _save(),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _save,
              child: const Text('Kaydet ve Yukle'),
            ),
          ],
        ),
      ),
    );
  }
}
