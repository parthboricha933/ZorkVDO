import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _darkMode = true;
  bool _notifications = true;
  bool _highQuality = true;
  String _aspectRatio = '9:16';

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _darkMode = prefs.getBool('dark_mode') ?? true;
      _notifications = prefs.getBool('notifications') ?? true;
      _highQuality = prefs.getBool('high_quality') ?? true;
      _aspectRatio = prefs.getString('aspect_ratio') ?? '9:16';
    });
  }

  Future<void> _set(String key, dynamic value) async {
    final prefs = await SharedPreferences.getInstance();
    if (value is bool) await prefs.setBool(key, value);
    if (value is String) await prefs.setString(key, value);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _sectionHeader('Appearance'),
          SwitchListTile(
            title: const Text('Dark mode'),
            subtitle: const Text('Use dark theme'),
            value: _darkMode,
            onChanged: (v) {
              setState(() => _darkMode = v);
              _set('dark_mode', v);
            },
          ),
          const Divider(),

          _sectionHeader('Rendering'),
          SwitchListTile(
            title: const Text('High quality'),
            subtitle: const Text('1080p instead of 720p'),
            value: _highQuality,
            onChanged: (v) {
              setState(() => _highQuality = v);
              _set('high_quality', v);
            },
          ),
          ListTile(
            title: const Text('Aspect ratio'),
            subtitle: Text(_aspectRatio),
            trailing: DropdownButton<String>(
              value: _aspectRatio,
              items: const [
                DropdownMenuItem(value: '9:16', child: Text('9:16 (Vertical)')),
                DropdownMenuItem(value: '16:9', child: Text('16:9 (Horizontal)')),
                DropdownMenuItem(value: '1:1', child: Text('1:1 (Square)')),
                DropdownMenuItem(value: '4:5', child: Text('4:5 (Portrait)')),
              ],
              onChanged: (v) {
                if (v == null) return;
                setState(() => _aspectRatio = v);
                _set('aspect_ratio', v);
              },
            ),
          ),
          const Divider(),

          _sectionHeader('Notifications'),
          SwitchListTile(
            title: const Text('Push notifications'),
            subtitle: const Text('Render complete, analysis done'),
            value: _notifications,
            onChanged: (v) {
              setState(() => _notifications = v);
              _set('notifications', v);
            },
          ),
          const Divider(),

          _sectionHeader('About'),
          const ListTile(
            title: Text('Version'),
            trailing: Text('0.1.0'),
          ),
          const ListTile(
            title: Text('Backend'),
            trailing: Text('Connected', style: TextStyle(color: Color(0xFF34D399))),
          ),
        ],
      ),
    );
  }

  Widget _sectionHeader(String text) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        text.toUpperCase(),
        style: const TextStyle(
          color: Color(0xFF71717A),
          fontSize: 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
