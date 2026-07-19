import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/providers/providers.dart';
import '../features/auth/auth_screen.dart';
import '../features/home/home_screen.dart';
import '../features/upload/upload_screen.dart';
import '../features/analyzing/analyzing_screen.dart';
import '../features/blueprint/blueprint_screen.dart';
import '../features/clips/clips_screen.dart';
import '../features/rendering/rendering_screen.dart';
import '../features/result/result_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/settings/settings_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final isSignedIn = ref.watch(isSignedInProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final loggedIn = isSignedIn;
      final path = state.matchedLocation;

      // Routes that don't require auth
      final publicRoutes = ['/auth'];

      if (!loggedIn && !publicRoutes.contains(path)) {
        return '/auth';
      }
      if (loggedIn && path == '/auth') {
        return '/';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/auth',
        builder: (context, state) => const AuthScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/upload',
        builder: (context, state) => const UploadScreen(),
      ),
      GoRoute(
        path: '/analyzing/:videoId',
        builder: (context, state) => AnalyzingScreen(
          videoId: state.pathParameters['videoId']!,
        ),
      ),
      GoRoute(
        path: '/blueprint/:blueprintId',
        builder: (context, state) => BlueprintScreen(
          blueprintId: state.pathParameters['blueprintId']!,
        ),
      ),
      GoRoute(
        path: '/clips/:blueprintId',
        builder: (context, state) => ClipsScreen(
          blueprintId: state.pathParameters['blueprintId']!,
        ),
      ),
      GoRoute(
        path: '/rendering/:jobId',
        builder: (context, state) => RenderingScreen(
          jobId: state.pathParameters['jobId']!,
        ),
      ),
      GoRoute(
        path: '/result/:videoId',
        builder: (context, state) => ResultScreen(
          videoId: state.pathParameters['videoId']!,
        ),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Route not found: ${state.matchedLocation}'),
      ),
    ),
  );
});
