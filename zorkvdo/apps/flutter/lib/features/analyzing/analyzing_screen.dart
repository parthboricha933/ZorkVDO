import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/services/services.dart';

class AnalyzingScreen extends ConsumerStatefulWidget {
  final String videoId;

  const AnalyzingScreen({super.key, required this.videoId});

  @override
  ConsumerState<AnalyzingScreen> createState() => _AnalyzingScreenState();
}

class _AnalyzingScreenState extends ConsumerState<AnalyzingScreen> {
  String? _jobId;
  String? _error;
  int _currentPass = 0;

  static const _passes = [
    'Probing container (ffmpeg)',
    'Detecting scene cuts (OpenCV)',
    'Extracting camera motion (optical flow)',
    'Detecting beats (librosa)',
    'Reading captions (EasyOCR)',
    'Clustering dominant colors',
    'Detecting objects (YOLOv11)',
    'Building blueprint JSON',
  ];

  @override
  void initState() {
    super.initState();
    _startAnalysis();
  }

  Future<void> _startAnalysis() async {
    try {
      final jobService = ref.read(jobServiceProvider);
      final job = await jobService.startAnalysis(widget.videoId);

      setState(() => _jobId = job.id);

      // Poll for updates
      final pollStream = jobService.poll(job.id).asBroadcastStream();
      pollStream.listen(
        (j) {
          setState(() {
            _currentPass = (j.progress * _passes.length).floor().clamp(0, _passes.length - 1);
          });
          if (j.status == 'succeeded' && j.result != null) {
            final blueprintId = j.result!['blueprint_id'];
            if (blueprintId != null && mounted) {
              context.go('/blueprint/$blueprintId');
            }
          } else if (j.status == 'failed') {
            setState(() => _error = j.error ?? 'Analysis failed');
          }
        },
        onError: (e) {
          setState(() => _error = 'Polling error: $e');
        },
      );
    } catch (e) {
      setState(() => _error = 'Failed to start analysis: $e');
    }
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
            // Animated spinner
            Center(
              child: SizedBox(
                width: 100,
                height: 100,
                child: Stack(
                  children: [
                    CircularProgressIndicator(
                      strokeWidth: 4,
                      valueColor: AlwaysStoppedAnimation(Color(0xFFE879F9)),
                      backgroundColor: Color(0xFFE879F9).withValues(alpha: 0.2),
                    ),
                    Center(
                      child: Icon(Icons.auto_awesome, color: Color(0xFFE879F9), size: 40),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            Text(
              'Analyzing your video',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 32),
            ..._passes.asMap().entries.map((entry) {
              final i = entry.key;
              final pass = entry.value;
              final isDone = i < _currentPass;
              final isActive = i == _currentPass;
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
                        child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFE879F9)),
                      )
                    else
                      Icon(Icons.circle_outlined, color: Colors.grey.shade700, size: 20),
                    const SizedBox(width: 12),
                    Text(
                      pass,
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
                  color: Color(0xFFF87171).withValues(alpha: 0.1),
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
