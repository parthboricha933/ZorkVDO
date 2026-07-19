import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/services/services.dart';

class BlueprintScreen extends ConsumerStatefulWidget {
  final String blueprintId;

  const BlueprintScreen({super.key, required this.blueprintId});

  @override
  ConsumerState<BlueprintScreen> createState() => _BlueprintScreenState();
}

class _BlueprintScreenState extends ConsumerState<BlueprintScreen> {
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    // Blueprint is fetched when the user navigates to clips
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Blueprint'),
        actions: [
          TextButton(
            onPressed: () => context.push('/clips/${widget.blueprintId}'),
            child: const Text('Next'),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : const Center(child: Text('Blueprint ready')),
    );
  }
}
