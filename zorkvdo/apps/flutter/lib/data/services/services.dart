import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb_auth;
import '../api/api_client.dart';
import '../models/models.dart';
import '../providers/providers.dart';

/// Auth service — wraps Firebase Auth with email/password sign-in.
class AuthService {
  final Ref _ref;
  AuthService(this._ref);

  Future<fb_auth.UserCredential> signInWithEmail({
    required String email,
    required String password,
  }) async {
    return fb_auth.FirebaseAuth.instance.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
  }

  Future<fb_auth.UserCredential> signUpWithEmail({
    required String email,
    required String password,
  }) async {
    return fb_auth.FirebaseAuth.instance.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
  }

  Future<void> signOut() async {
    await fb_auth.FirebaseAuth.instance.signOut();
  }

  Future<void> resetPassword(String email) async {
    await fb_auth.FirebaseAuth.instance.sendPasswordResetEmail(email: email);
  }
}

final authServiceProvider = Provider<AuthService>((ref) => AuthService(ref));

/// Sync the current Firebase user to the backend.
/// Accepts either a Ref (from providers) or a WidgetRef (from widgets).
Future<User> syncUser(dynamic ref) async {
  final api = ref.read(apiClientProvider);
  final data = await api.post<Map<String, dynamic>>('/auth/sync', data: {});
  return User.fromJson(data['user'] as Map<String, dynamic>);
}

/// Project API service
class ProjectService {
  final Ref _ref;
  ProjectService(this._ref);

  Future<List<Project>> list() async {
    final api = _ref.read(apiClientProvider);
    final data = await api.get<List>('/projects');
    return data.map((j) => Project.fromJson(j as Map<String, dynamic>)).toList();
  }

  Future<Project> create({required String name, String description = ''}) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.post<Map<String, dynamic>>(
      '/projects',
      data: {'name': name, 'description': description},
    );
    return Project.fromJson(data);
  }
}

final projectServiceProvider = Provider<ProjectService>((ref) => ProjectService(ref));

/// Video API service
class VideoService {
  final Ref _ref;
  VideoService(this._ref);

  Future<Video> upload({
    required String filePath,
    required String fileName,
    required String contentType,
    String kind = 'source',
    void Function(int sent, int total)? onProgress,
  }) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.upload<Map<String, dynamic>>(
      '/videos/upload',
      filePath: filePath,
      fileName: fileName,
      contentType: contentType,
      fields: {'kind': kind},
      onSendProgress: onProgress,
    );
    return Video.fromJson(data);
  }

  Future<Video> get(String videoId) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.get<Map<String, dynamic>>('/videos/$videoId');
    return Video.fromJson(data);
  }

  Future<List<Video>> list({String? kind}) async {
    final api = _ref.read(apiClientProvider);
    final query = kind != null ? '?kind=$kind' : '';
    final data = await api.get<List>('/videos$query');
    return data.map((j) => Video.fromJson(j as Map<String, dynamic>)).toList();
  }

  String downloadUrl(String videoId) {
    final api = _ref.read(apiClientProvider);
    return '${api.dio.options.baseUrl}/videos/$videoId/download';
  }
}

final videoServiceProvider = Provider<VideoService>((ref) => VideoService(ref));

/// Job API service
class JobService {
  final Ref _ref;
  JobService(this._ref);

  Future<Job> startAnalysis(String videoId, {String blueprintName = 'Untitled Blueprint'}) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.post<Map<String, dynamic>>(
      '/jobs/analyze/$videoId',
      data: {'blueprint_name': blueprintName},
    );
    return Job.fromJson(data);
  }

  Future<Job> startRender({
    required String projectId,
    required String blueprintId,
    required List<Map<String, dynamic>> clipMapping,
    String quality = 'high',
    String? aspectRatio,
  }) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.post<Map<String, dynamic>>(
      '/jobs/render',
      data: {
        'project_id': projectId,
        'blueprint_id': blueprintId,
        'clip_mapping': clipMapping,
        'quality': quality,
        if (aspectRatio != null) 'aspect_ratio': aspectRatio,
      },
    );
    return Job.fromJson(data);
  }

  Future<Job> get(String jobId) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.get<Map<String, dynamic>>('/jobs/$jobId');
    return Job.fromJson(data);
  }

  Stream<Job> poll(String jobId, {Duration interval = const Duration(seconds: 2)}) async* {
    while (true) {
      final job = await get(jobId);
      yield job;
      if (job.status == 'succeeded' || job.status == 'failed' || job.status == 'cancelled') {
        break;
      }
      await Future.delayed(interval);
    }
  }
}

final jobServiceProvider = Provider<JobService>((ref) => JobService(ref));

/// Blueprint API service
class BlueprintService {
  final Ref _ref;
  BlueprintService(this._ref);

  Future<Blueprint> get(String blueprintId) async {
    final api = _ref.read(apiClientProvider);
    final data = await api.get<Map<String, dynamic>>('/blueprints/$blueprintId');
    return Blueprint.fromJson(data);
  }
}

final blueprintServiceProvider = Provider<BlueprintService>((ref) => BlueprintService(ref));
