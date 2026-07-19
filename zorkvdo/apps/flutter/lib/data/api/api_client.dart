import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../core/config/app_config.dart';

/// API client for the ZorkVDO FastAPI backend.
///
/// Automatically attaches the Firebase ID token to every request when
/// the user is signed in. Falls back to demo mode (no auth header) when
/// `AppConfig.useFirebaseAuth` is false or no user is signed in.
class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.backendUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 120), // uploads/analysis can be slow
        sendTimeout: const Duration(seconds: 120),
        headers: {'Accept': 'application/json'},
      ),
    );

    // Attach auth token to every request
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          if (AppConfig.useFirebaseAuth) {
            final user = FirebaseAuth.instance.currentUser;
            if (user != null) {
              final token = await user.getIdToken();
              options.headers['Authorization'] = 'Bearer $token';
            }
          }
          handler.next(options);
        },
        onError: (e, handler) {
          if (kDebugMode) {
            print('API error: ${e.response?.statusCode} ${e.response?.data}');
          }
          handler.next(e);
        },
      ),
    );

    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          request: true,
          requestHeader: false,
          responseHeader: false,
          responseBody: true,
          error: true,
          logPrint: (o) => print('[API] $o'),
        ),
      );
    }
  }

  Dio get dio => _dio;

  /// GET request
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    final resp = await _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
    return resp.data as T;
  }

  /// POST request with JSON body
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    final resp = await _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
    return resp.data as T;
  }

  /// Upload a file via multipart form data
  Future<T> upload<T>(
    String path, {
    required String filePath,
    required String fileName,
    required String contentType,
    String fieldName = 'file',
    Map<String, dynamic>? fields,
    ProgressCallback? onSendProgress,
  }) async {
    final form = FormData();
    form.files.add(
      MapEntry(
        fieldName,
        MultipartFile.fromFileSync(filePath, filename: fileName),
      ),
    );
    if (fields != null) {
      fields.forEach((k, v) => form.fields.add(MapEntry(k, v.toString())));
    }
    final resp = await _dio.post<T>(
      path,
      data: form,
      options: Options(contentType: 'multipart/form-data'),
      onSendProgress: onSendProgress,
    );
    return resp.data as T;
  }
}
