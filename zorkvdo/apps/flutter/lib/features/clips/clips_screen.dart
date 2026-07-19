import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../data/models/models.dart';
import '../../data/services/services.dart';

class ClipsScreen extends ConsumerStatefulWidget {
  final String blueprintId;

  const ClipsScreen({super.key, required this.blueprintId});

  @override
  ConsumerState<ClipsScreen> createState() => _ClipsScreenState();
}

class _ClipsScreenState extends ConsumerState<ClipsScreen> {
  bool _loading = true;
  bool _uploading = false;
  String? _error;
  Blueprint? _blueprint;
  final List<Video> _clips = [];
  String? _projectId;

  @override
  void initState() {
    super.initState();
    _loadBlueprint();
  }

  Future<void> _loadBlueprint() async {
    try {
      final bpService = ref.read(blueprintServiceProvider);
      final bp = await bpService.get(widget.blueprintId);
      setState(() {
        _blueprint = bp;
        _loading = false;
      });

      // Create a project to associate the render with
      final projService = ref.read(projectServiceProvider);
      final proj = await projService.create(name: 'Render from ${bp.name}');
      setState(() => _projectId = proj.id);
    } catch (e) {
      setState(() {
        _error = 'Failed to load blueprint: $e';
        _loading = false;
      });
    }
  }

  Future<void> _pickClips() async {
    final picker = ImagePicker();
    final videos = await picker.pickMultipleMedia();
    if (videos.isEmpty) return;

    setState(() => _uploading = true);
    try {
      final videoService = ref.read(videoServiceProvider);
      for (final v in videos) {
        final uploaded = await videoService.upload(
          filePath: v.path,
          fileName: v.name,
          contentType: 'video/mp4',
          kind: 'user_clip',
        );
        setState(() => _clips.add(uploaded));
      }
    } catch (e) {
      setState(() => _error = 'Upload failed: $e');
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<void> _render() async {
    if (_blueprint == null || _projectId == null || _clips.isEmpty) return;

    setState(() => _loading = true);
    try {
      final jobService = ref.read(jobServiceProvider);
      final clipMapping = _blueprint!.scenes.asMap().entries.map((entry) {
        return {
          'scene_index': entry.value.index,
          'clip_id': _clips[entry.key % _clips.length].id,
          'suggested_start': 0.0,
          'suggested_end': entry.value.duration,
        };
      }).toList();

      final job = await jobService.startRender(
        projectId: _projectId!,
        blueprintId: _blueprint!.id,
        clipMapping: clipMapping,
        quality: 'high',
        aspectRatio: '9:16',
      );

      if (mounted) context.go('/rendering/${job.id}');
    } catch (e) {
      setState(() {
        _error = 'Render failed: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _blueprint == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Clips')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Upload your clips')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_blueprint != null) ...[
              Text(
                _blueprint!.name,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 4),
              Text(
                '${_blueprint!.scenes.length} scenes · ${_blueprint!.overallDuration.toStringAsFixed(1)}s · pace: ${_blueprint!.pace}',
                style: const TextStyle(color: Color(0xFF71717A)),
              ),
              const SizedBox(height: 24),
            ],

            // Scene timeline preview
            if (_blueprint != null)
              Container(
                height: 60,
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _blueprint!.scenes.length,
                  itemBuilder: (context, i) {
                    final scene = _blueprint!.scenes[i];
                    final color = scene.dominantColorsHex.isNotEmpty
                        ? _hexToColor(scene.dominantColorsHex.first)
                        : const Color(0xFFA855F7);
                    return Container(
                      width: scene.duration * 30,
                      margin: const EdgeInsets.only(right: 4),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [color, color.withValues(alpha: 0.7)],
                        ),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Center(
                        child: Text(
                          '${scene.duration.toStringAsFixed(1)}s',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            const SizedBox(height: 24),

            // Upload button
            ElevatedButton.icon(
              onPressed: _uploading ? null : _pickClips,
              icon: _uploading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.upload_file),
              label: Text(_uploading ? 'Uploading...' : 'Add clips'),
            ),
            const SizedBox(height: 16),

            // Clips list
            Expanded(
              child: _clips.isEmpty
                  ? Center(
                      child: Text(
                        'No clips yet',
                        style: TextStyle(color: Colors.grey.shade500),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _clips.length,
                      itemBuilder: (context, i) {
                        final clip = _clips[i];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: const Icon(Icons.movie, color: Color(0xFFE879F9)),
                            title: Text(clip.filename, style: const TextStyle(fontSize: 14)),
                            subtitle: Text(
                              '${(clip.sizeBytes / 1024 / 1024).toStringAsFixed(1)} MB',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ),
                        );
                      },
                    ),
            ),

            if (_error != null)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF87171).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(_error!, style: const TextStyle(color: Color(0xFFF87171), fontSize: 13)),
              ),

            // Render button
            ElevatedButton(
              onPressed: _clips.isEmpty || _loading ? null : _render,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: const Color(0xFFE879F9),
              ),
              child: _loading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : Text(_clips.isEmpty
                      ? 'Upload clips first'
                      : 'Render from ${_clips.length} clip${_clips.length > 1 ? 's' : ''}'),
            ),
          ],
        ),
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceAll('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }
}
