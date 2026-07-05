import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/services/services.dart';

class RenderingScreen extends ConsumerStatefulWidget {
  final String jobId;

  const RenderingScreen({super.key, required this.jobId});

  @override
  ConsumerState<RenderingScreen> createState() => _RenderingScreenState();
}

class _RenderingScreenState extends ConsumerState<RenderingScreen> {
  String? _error;
  int _currentPhase = 0;

  static const _phases = [
    'Downloading clips',
    'Trimming + scaling per scene',
    'Concatenating segments',
    'Burning in captions',
    'Uploading output',
  ];

  @override
  void initState() {
    super.initState();
    _pollJob();
  }

  Future<void> _pollJob() async {
    final jobService = ref.read(jobServiceProvider);
    final stream = jobService.poll(widget.jobId).asBroadcastStream();

    stream.listen(
      (job) {
        setState(() {
          _currentPhase = (job.progress * _phases.length).floor().clamp(0, _phases.length - 1);
        });
        if (job.status == 'succeeded' && job.result != null) {
          final outputId = job.result!['output_video_id'];
          if (outputId != null && mounted) {
            context.go('/result/$outputId');
          }
        } else if (job.status == 'failed') {
          setState(() => _error = job.error ?? 'Render failed');
        }
      },
      onError: (e) {
        setState(() => _error = 'Polling error: $e');
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(leading: IconButton(
        icon: const Icon(Icons.close),
        onPressed: () => context.go('/'),
      )),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Spacer(),
            Center(
              child: SizedBox(
                width: 100,
                height: 100,
                child: Stack(
                  children: [
                    CircularProgressIndicator(
                      strokeWidth: 4,
                      valueColor: const AlwaysStoppedAnimation(Color(0xFFFB7185)),
                      backgroundColor: const Color(0xFFFB7185).withValues(alpha: 0.2),
                    ),
                    const Center(
                      child: Icon(Icons.movie_creation, color: Color(0xFFFB7185), size: 40),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            Text(
              'Rendering your video',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'FFmpeg is assembling your new video',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF71717A)),
            ),
            const SizedBox(height: 32),
            ..._phases.asMap().entries.map((entry) {
              final i = entry.key;
              final phase = entry.value;
              final isDone = i < _currentPhase;
              final isActive = i == _currentPhase;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    if (isDone)
                      const Icon(Icons.check_circle, color: Color(0xFF34D399), size: 20)
                    else if (isActive)
                      const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFFB7185)),
                      )
                    else
                      Icon(Icons.circle_outlined, color: Colors.grey.shade700, size: 20),
                    const SizedBox(width: 12),
                    Text(
                      phase,
                      style: TextStyle(
                        color: isDone
                            ? const Color(0xFF34D399)
                            : isActive
                                ? const Color(0xFFFAFAFA)
                                : const Color(0xFF52525B),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              );
            }),
            if (_error != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF87171).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(_error!, style: const TextStyle(color: Color(0xFFF87171))),
              ),
            ],
            const Spacer(),
          ],
        ),
      ),
    );
  }
}
