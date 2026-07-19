/// ZorkVDO app configuration.
///
/// All URLs and feature flags live here. Backend URL is read from
/// --dart-define=BACKEND_URL=... at build time, falling back to the
/// local dev URL.
class AppConfig {
  const AppConfig._();

  /// Backend API base URL (no trailing slash).
  /// Override at build time: `flutter run --dart-define=BACKEND_URL=https://your-railway-url/api/v1`
  static const String backendUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1', // 10.0.2.2 = host from Android emulator
  );

  /// Backend URL for downloading videos (same as backendUrl but without /api/v1).
  static String get downloadBaseUrl => backendUrl.replaceAll('/api/v1', '');

  /// Whether to use Firebase Auth. Set to false to test with demo mode.
  static const bool useFirebaseAuth = bool.fromEnvironment(
    'USE_FIREBASE_AUTH',
    defaultValue: true,
  );

  /// App version
  static const String version = '0.1.0';

  /// Whether we're in debug mode
  static bool get isDebug {
    bool inDebugMode = false;
    assert(inDebugMode = true);
    return inDebugMode;
  }
}
