import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_theme.dart';
import '../../data/services/services.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ZorkVDO'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push('/profile'),
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF09090B), Color(0xFF18181B)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Spacer(),
                Container(
                  height: 96,
                  width: 96,
                  decoration: BoxDecoration(
                    gradient: AppTheme.heroGradient,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFE879F9).withValues(alpha: 0.4),
                        blurRadius: 30,
                        offset: const Offset(0, 12),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.bolt, color: Colors.white, size: 48),
                ),
                const SizedBox(height: 32),
                Text(
                  'Create viral videos\nfrom any inspiration',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 12),
                Text(
                  'Upload a viral video. AI reverse-engineers its editing style.\nDrop in your clips. Get a brand-new video with the same energy.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF71717A),
                      ),
                ),
                const Spacer(),
                _buildStepCard(
                  context,
                  icon: Icons.upload_file,
                  step: '01',
                  title: 'Upload a viral video',
                  description: 'Any video that went viral — TikTok, Reel, Short',
                ),
                const SizedBox(height: 12),
                _buildStepCard(
                  context,
                  icon: Icons.auto_awesome,
                  step: '02',
                  title: 'AI generates a blueprint',
                  description: 'Scene cuts, beats, captions, color, motion',
                ),
                const SizedBox(height: 12),
                _buildStepCard(
                  context,
                  icon: Icons.movie_creation_outlined,
                  step: '03',
                  title: 'Upload your clips, get a new video',
                  description: 'Same style, your footage, original content',
                ),
                const Spacer(),
                ElevatedButton(
                  onPressed: () => context.push('/upload'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: const Color(0xFFE879F9),
                  ),
                  child: const Text('Start creating'),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStepCard(
    BuildContext context, {
    required IconData icon,
    required String step,
    required String title,
    required String description,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF27272A)),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFFE879F9).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: const Color(0xFFE879F9), size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Color(0xFFFAFAFA),
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: const TextStyle(color: Color(0xFF71717A), fontSize: 13),
                ),
              ],
            ),
          ),
          Text(
            step,
            style: TextStyle(
              color: const Color(0xFF71717A).withValues(alpha: 0.5),
              fontSize: 12,
              fontWeight: FontWeight.w600,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      ),
    );
  }
}
