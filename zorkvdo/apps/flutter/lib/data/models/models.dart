import 'package:freezed_annotation/freezed_annotation.dart';

part 'models.freezed.dart';
part 'models.g.dart';

@freezed
class Video with _$Video {
  const factory Video({
    required String id,
    required String ownerId,
    required String kind, // source | user_clip | output
    required String filename,
    required String contentType,
    required int sizeBytes,
    required String storageKey,
    required String storageUrl,
    double? durationSeconds,
    int? width,
    int? height,
    double? fps,
    String? analysisId,
    required String createdAt,
    required String updatedAt,
  }) = _Video;

  factory Video.fromJson(Map<String, dynamic> json) => _$VideoFromJson(json);
}

@freezed
class Project with _$Project {
  const factory Project({
    required String id,
    required String name,
    @Default('') String description,
    @Default('active') String status,
    required String ownerId,
    String? sourceVideoId,
    String? blueprintId,
    String? outputVideoId,
    required String createdAt,
    required String updatedAt,
  }) = _Project;

  factory Project.fromJson(Map<String, dynamic> json) => _$ProjectFromJson(json);
}

@freezed
class Job with _$Job {
  const factory Job({
    required String id,
    required String userId,
    String? projectId,
    required String jobType, // analyze | render
    required String status, // queued | running | succeeded | failed | cancelled
    @Default(0.0) double progress,
    String? startedAt,
    String? finishedAt,
    String? error,
    Map<String, dynamic>? result,
    required String createdAt,
    required String updatedAt,
  }) = _Job;

  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
}

@freezed
class CaptionStyle with _$CaptionStyle {
  const factory CaptionStyle({
    required String text,
    required double start,
    required double end,
    @Default('bottom_third') String position,
    @Default('pop') String animation,
    @Default('Inter') String fontFamily,
    @Default(48.0) double fontSize,
    @Default('#FFFFFF') String colorHex,
    String? strokeColorHex,
    @Default(2.0) double strokeWidth,
    @Default(true) bool bold,
    @Default(true) bool uppercase,
  }) = _CaptionStyle;

  factory CaptionStyle.fromJson(Map<String, dynamic> json) =>
      _$CaptionStyleFromJson(json);
}

@freezed
class ClipSuggestion with _$ClipSuggestion {
  const factory ClipSuggestion({
    @Default('any') String role,
    @Default('unknown') String preferredShot,
    @Default([0.5, 3.0]) List<double> durationRange,
    @Default('static') String motion,
    @Default('') String description,
    @Default([]) List<String> keywords,
    @Default(0) int minFaceCount,
    @Default(true) bool allowTextOverlay,
  }) = _ClipSuggestion;

  factory ClipSuggestion.fromJson(Map<String, dynamic> json) =>
      _$ClipSuggestionFromJson(json);
}

@freezed
class BlueprintScene with _$BlueprintScene {
  const factory BlueprintScene({
    required int index,
    required double start,
    required double end,
    required double duration,
    @Default('medium') String shotType,
    @Default('static') String cameraMotion,
    @Default(1.0) double zoomFactor,
    @Default([]) List<CaptionStyle> captions,
    required ClipSuggestion clipSuggestion,
    @Default([]) List<String> dominantColorsHex,
    double? bpmSync,
  }) = _BlueprintScene;

  factory BlueprintScene.fromJson(Map<String, dynamic> json) =>
      _$BlueprintSceneFromJson(json);
}

@freezed
class MusicTrack with _$MusicTrack {
  const factory MusicTrack({
    @Default('') String title,
    @Default('') String artist,
    double? bpm,
    @Default(0.5) double energy,
    @Default([]) List<double> beatTimes,
  }) = _MusicTrack;

  factory MusicTrack.fromJson(Map<String, dynamic> json) =>
      _$MusicTrackFromJson(json);
}

@freezed
class Blueprint with _$Blueprint {
  const factory Blueprint({
    required String id,
    required String ownerId,
    required String name,
    required String sourceVideoId,
    @Default('medium') String pace,
    required double overallDuration,
    required List<BlueprintScene> scenes,
    MusicTrack? music,
    @Default('natural') String colorGrade,
    @Default([]) List<String> tags,
    @Default('') String notes,
    @Default('1.0.0') String schemaVersion,
    required String createdAt,
    required String updatedAt,
  }) = _Blueprint;

  factory Blueprint.fromJson(Map<String, dynamic> json) =>
      _$BlueprintFromJson(json);
}

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required String displayName,
    String? avatarUrl,
    @Default('free') String plan,
    required String createdAt,
    required String updatedAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
