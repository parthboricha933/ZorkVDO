import 'package:flutter/material.dart';

/// ZorkVDO Material 3 theme — dark premium aesthetic with
/// fuchsia/purple/rose gradient accents.
///
/// Matches the web app's design system.
class AppTheme {
  const AppTheme._();

  // ── Brand colors ───────────────────────────────────────────────
  static const Color _primary = Color(0xFFE879F9); // fuchsia-400
  static const Color _primaryDark = Color(0xFFC026D3); // fuchsia-600
  static const Color _secondary = Color(0xFFFB7185); // rose-400
  static const Color _accent = Color(0xFFA855F7); // purple-500
  static const Color _background = Color(0xFF09090B); // zinc-950
  static const Color _surface = Color(0xFF18181B); // zinc-900
  static const Color _surfaceVariant = Color(0xFF27272A); // zinc-800
  static const Color _onBackground = Color(0xFFFAFAFA); // zinc-50
  static const Color _onSurface = Color(0xFFE4E4E7); // zinc-200
  static const Color _muted = Color(0xFF71717A); // zinc-500
  static const Color _success = Color(0xFF34D399); // emerald-400
  static const Color _warning = Color(0xFFFBBF24); // amber-400
  static const Color _error = Color(0xFFF87171); // red-400

  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.dark(
      primary: _primary,
      onPrimary: Colors.white,
      primaryContainer: _primaryDark,
      onPrimaryContainer: Colors.white,
      secondary: _secondary,
      onSecondary: Colors.white,
      secondaryContainer: _secondary,
      tertiary: _accent,
      surface: _surface,
      onSurface: _onSurface,
      error: _error,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: _background,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: _onBackground,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(color: _onBackground),
      ),
      cardTheme: CardThemeData(
        color: _surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: _surfaceVariant, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: _primary,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: _onSurface,
          side: BorderSide(color: _surfaceVariant),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: _surfaceVariant,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _primary, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        labelStyle: const TextStyle(color: _muted),
        hintStyle: const TextStyle(color: _muted),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: _surface,
        selectedItemColor: _primary,
        unselectedItemColor: _muted,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: _primary,
        linearTrackColor: _surfaceVariant,
      ),
      dividerTheme: const DividerThemeData(
        color: _surfaceVariant,
        thickness: 1,
        space: 1,
      ),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(color: _onBackground, fontSize: 32, fontWeight: FontWeight.w700),
        headlineMedium: TextStyle(color: _onBackground, fontSize: 24, fontWeight: FontWeight.w600),
        titleLarge: TextStyle(color: _onBackground, fontSize: 20, fontWeight: FontWeight.w600),
        titleMedium: TextStyle(color: _onBackground, fontSize: 16, fontWeight: FontWeight.w500),
        bodyLarge: TextStyle(color: _onSurface, fontSize: 16),
        bodyMedium: TextStyle(color: _onSurface, fontSize: 14),
        bodySmall: TextStyle(color: _muted, fontSize: 12),
        labelLarge: TextStyle(color: _onBackground, fontSize: 14, fontWeight: FontWeight.w500),
        labelSmall: TextStyle(color: _muted, fontSize: 11),
      ),
    );
  }

  /// Brand gradient (fuchsia → rose) for buttons, headers, etc.
  static const LinearGradient brandGradient = LinearGradient(
    colors: [_primary, _secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  /// Brand gradient (purple → fuchsia → rose) for hero sections.
  static const LinearGradient heroGradient = LinearGradient(
    colors: [Color(0xFFA855F7), _primary, _secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
