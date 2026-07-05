import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../api/api_client.dart';

/// Singleton API client
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// Current Firebase auth state
final authStateProvider = StreamProvider<User?>((ref) {
  return FirebaseAuth.instance.authStateChanges();
});

/// Whether the user is currently signed in
final isSignedInProvider = Provider<bool>((ref) {
  final user = ref.watch(authStateProvider).maybeWhen(
        data: (user) => user,
        orElse: () => null,
  );
  return user != null;
});

/// Current user's UID
final currentUserIdProvider = Provider<String?>((ref) {
  final user = ref.watch(authStateProvider).maybeWhen(
        data: (user) => user,
        orElse: () => null,
  );
  return user?.uid;
});

/// Current user's email
final currentUserEmailProvider = Provider<String?>((ref) {
  final user = ref.watch(authStateProvider).maybeWhen(
        data: (user) => user,
        orElse: () => null,
  );
  return user?.email;
});
