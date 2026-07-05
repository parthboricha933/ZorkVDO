# ZorkVDO Flutter App

AI-powered viral video blueprint generator — Android client.

## Tech stack

- **Flutter 3.27+** / Dart 3.6+
- **Riverpod 2** — state management + dependency injection
- **go_router** — declarative routing
- **Firebase** — Auth, Firestore, Storage, Messaging, Analytics, Crashlytics
- **dio** — HTTP client (auto-attaches Firebase ID token)
- **image_picker / video_player** — media picking + playback
- **Material 3** — dark premium theme matching the web app

## Getting started

```bash
cd apps/flutter

# Install dependencies
flutter pub get

# Run on Android emulator or device
flutter run

# Run with a custom backend URL (default: http://10.0.2.2:8000/api/v1)
flutter run --dart-define=BACKEND_URL=https://your-railway-url/api/v1

# Disable Firebase Auth (use backend demo mode)
flutter run --dart-define=USE_FIREBASE_AUTH=false
```

## Project structure

```
lib/
├── main.dart                    # App entry + Firebase init
├── firebase_options.dart        # Generated from google-services.json
├── core/
│   ├── config/app_config.dart   # Backend URL, feature flags
│   ├── theme/app_theme.dart     # Material 3 dark theme + brand gradients
│   └── router.dart              # go_router config with auth redirect
├── data/
│   ├── api/api_client.dart      # Dio wrapper with Firebase token interceptor
│   ├── models/models.dart       # Freezed models (Video, Project, Job, Blueprint, etc.)
│   ├── providers/providers.dart # Riverpod providers (auth state, services)
│   └── services/services.dart   # API services (Auth, Project, Video, Job, Blueprint)
└── features/
    ├── auth/auth_screen.dart         # Sign in / sign up (Firebase Auth)
    ├── home/home_screen.dart         # Landing with 3-step explainer
    ├── upload/upload_screen.dart     # Pick + upload viral video
    ├── analyzing/analyzing_screen.dart  # Animated analysis progress
    ├── blueprint/blueprint_screen.dart  # View generated blueprint
    ├── clips/clips_screen.dart       # Upload user clips + start render
    ├── rendering/rendering_screen.dart  # Animated render progress
    ├── result/result_screen.dart     # Video player + download
    ├── profile/profile_screen.dart   # User profile + sign out
    └── settings/settings_screen.dart # Theme, quality, aspect ratio
```

## Screen flow

```
Auth → Home → Upload → Analyzing → Blueprint → Clips → Rendering → Result
                                                                    ↓
                                                                  Home (loop)
```

## Configuration

### Firebase

`google-services.json` is at `android/app/google-services.json` (gitignored).
`firebase_options.dart` was generated from it — the values are public client
SDK config (no secrets).

### Backend URL

Default: `http://10.0.2.2:8000/api/v1` (Android emulator → host machine)

Override at build time:
```bash
flutter run --dart-define=BACKEND_URL=https://your-railway-url/api/v1
```

### Firebase Auth

Enabled by default. The app requires sign-in before accessing the main flow.
The backend verifies the Firebase ID token via `firebase-admin`.

To disable (use backend demo mode):
```bash
flutter run --dart-define=USE_FIREBASE_AUTH=false
```

## Building for release

```bash
# Generate app icons
flutter pub run flutter_launcher_icons

# Build release APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release \
  --dart-define=BACKEND_URL=https://your-railway-url/api/v1
```

## Code generation

Models use Freezed + json_serializable. After editing `models.dart`:

```bash
dart run build_runner build --delete-conflicting-outputs
```

This generates `models.freezed.dart` and `models.g.dart`.
