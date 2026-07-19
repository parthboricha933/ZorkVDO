// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$VideoImpl _$$VideoImplFromJson(Map<String, dynamic> json) => _$VideoImpl(
      id: json['id'] as String,
      ownerId: json['ownerId'] as String,
      kind: json['kind'] as String,
      filename: json['filename'] as String,
      contentType: json['contentType'] as String,
      sizeBytes: (json['sizeBytes'] as num).toInt(),
      storageKey: json['storageKey'] as String,
      storageUrl: json['storageUrl'] as String,
      durationSeconds: (json['durationSeconds'] as num?)?.toDouble(),
      width: (json['width'] as num?)?.toInt(),
      height: (json['height'] as num?)?.toInt(),
      fps: (json['fps'] as num?)?.toDouble(),
      analysisId: json['analysisId'] as String?,
      createdAt: json['createdAt'] as String,
      updatedAt: json['updatedAt'] as String,
    );

Map<String, dynamic> _$$VideoImplToJson(_$VideoImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'ownerId': instance.ownerId,
      'kind': instance.kind,
      'filename': instance.filename,
      'contentType': instance.contentType,
      'sizeBytes': instance.sizeBytes,
      'storageKey': instance.storageKey,
      'storageUrl': instance.storageUrl,
      'durationSeconds': instance.durationSeconds,
      'width': instance.width,
      'height': instance.height,
      'fps': instance.fps,
      'analysisId': instance.analysisId,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
    };

_$ProjectImpl _$$ProjectImplFromJson(Map<String, dynamic> json) =>
    _$ProjectImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      status: json['status'] as String? ?? 'active',
      ownerId: json['ownerId'] as String,
      sourceVideoId: json['sourceVideoId'] as String?,
      blueprintId: json['blueprintId'] as String?,
      outputVideoId: json['outputVideoId'] as String?,
      createdAt: json['createdAt'] as String,
      updatedAt: json['updatedAt'] as String,
    );

Map<String, dynamic> _$$ProjectImplToJson(_$ProjectImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'status': instance.status,
      'ownerId': instance.ownerId,
      'sourceVideoId': instance.sourceVideoId,
      'blueprintId': instance.blueprintId,
      'outputVideoId': instance.outputVideoId,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
    };

_$JobImpl _$$JobImplFromJson(Map<String, dynamic> json) => _$JobImpl(
      id: json['id'] as String,
      userId: json['userId'] as String,
      projectId: json['projectId'] as String?,
      jobType: json['jobType'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num?)?.toDouble() ?? 0.0,
      startedAt: json['startedAt'] as String?,
      finishedAt: json['finishedAt'] as String?,
      error: json['error'] as String?,
      result: json['result'] as Map<String, dynamic>?,
      createdAt: json['createdAt'] as String,
      updatedAt: json['updatedAt'] as String,
    );

Map<String, dynamic> _$$JobImplToJson(_$JobImpl instance) => <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'projectId': instance.projectId,
      'jobType': instance.jobType,
      'status': instance.status,
      'progress': instance.progress,
      'startedAt': instance.startedAt,
      'finishedAt': instance.finishedAt,
      'error': instance.error,
      'result': instance.result,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
    };

_$CaptionStyleImpl _$$CaptionStyleImplFromJson(Map<String, dynamic> json) =>
    _$CaptionStyleImpl(
      text: json['text'] as String,
      start: (json['start'] as num).toDouble(),
      end: (json['end'] as num).toDouble(),
      position: json['position'] as String? ?? 'bottom_third',
      animation: json['animation'] as String? ?? 'pop',
      fontFamily: json['fontFamily'] as String? ?? 'Inter',
      fontSize: (json['fontSize'] as num?)?.toDouble() ?? 48.0,
      colorHex: json['colorHex'] as String? ?? '#FFFFFF',
      strokeColorHex: json['strokeColorHex'] as String?,
      strokeWidth: (json['strokeWidth'] as num?)?.toDouble() ?? 2.0,
      bold: json['bold'] as bool? ?? true,
      uppercase: json['uppercase'] as bool? ?? true,
    );

Map<String, dynamic> _$$CaptionStyleImplToJson(_$CaptionStyleImpl instance) =>
    <String, dynamic>{
      'text': instance.text,
      'start': instance.start,
      'end': instance.end,
      'position': instance.position,
      'animation': instance.animation,
      'fontFamily': instance.fontFamily,
      'fontSize': instance.fontSize,
      'colorHex': instance.colorHex,
      'strokeColorHex': instance.strokeColorHex,
      'strokeWidth': instance.strokeWidth,
      'bold': instance.bold,
      'uppercase': instance.uppercase,
    };

_$ClipSuggestionImpl _$$ClipSuggestionImplFromJson(Map<String, dynamic> json) =>
    _$ClipSuggestionImpl(
      role: json['role'] as String? ?? 'any',
      preferredShot: json['preferredShot'] as String? ?? 'unknown',
      durationRange: (json['durationRange'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          const [0.5, 3.0],
      motion: json['motion'] as String? ?? 'static',
      description: json['description'] as String? ?? '',
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      minFaceCount: (json['minFaceCount'] as num?)?.toInt() ?? 0,
      allowTextOverlay: json['allowTextOverlay'] as bool? ?? true,
    );

Map<String, dynamic> _$$ClipSuggestionImplToJson(
        _$ClipSuggestionImpl instance) =>
    <String, dynamic>{
      'role': instance.role,
      'preferredShot': instance.preferredShot,
      'durationRange': instance.durationRange,
      'motion': instance.motion,
      'description': instance.description,
      'keywords': instance.keywords,
      'minFaceCount': instance.minFaceCount,
      'allowTextOverlay': instance.allowTextOverlay,
    };

_$BlueprintSceneImpl _$$BlueprintSceneImplFromJson(Map<String, dynamic> json) =>
    _$BlueprintSceneImpl(
      index: (json['index'] as num).toInt(),
      start: (json['start'] as num).toDouble(),
      end: (json['end'] as num).toDouble(),
      duration: (json['duration'] as num).toDouble(),
      shotType: json['shotType'] as String? ?? 'medium',
      cameraMotion: json['cameraMotion'] as String? ?? 'static',
      zoomFactor: (json['zoomFactor'] as num?)?.toDouble() ?? 1.0,
      captions: (json['captions'] as List<dynamic>?)
              ?.map((e) => CaptionStyle.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      clipSuggestion: ClipSuggestion.fromJson(
          json['clipSuggestion'] as Map<String, dynamic>),
      dominantColorsHex: (json['dominantColorsHex'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      bpmSync: (json['bpmSync'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$$BlueprintSceneImplToJson(
        _$BlueprintSceneImpl instance) =>
    <String, dynamic>{
      'index': instance.index,
      'start': instance.start,
      'end': instance.end,
      'duration': instance.duration,
      'shotType': instance.shotType,
      'cameraMotion': instance.cameraMotion,
      'zoomFactor': instance.zoomFactor,
      'captions': instance.captions,
      'clipSuggestion': instance.clipSuggestion,
      'dominantColorsHex': instance.dominantColorsHex,
      'bpmSync': instance.bpmSync,
    };

_$MusicTrackImpl _$$MusicTrackImplFromJson(Map<String, dynamic> json) =>
    _$MusicTrackImpl(
      title: json['title'] as String? ?? '',
      artist: json['artist'] as String? ?? '',
      bpm: (json['bpm'] as num?)?.toDouble(),
      energy: (json['energy'] as num?)?.toDouble() ?? 0.5,
      beatTimes: (json['beatTimes'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$MusicTrackImplToJson(_$MusicTrackImpl instance) =>
    <String, dynamic>{
      'title': instance.title,
      'artist': instance.artist,
      'bpm': instance.bpm,
      'energy': instance.energy,
      'beatTimes': instance.beatTimes,
    };

_$BlueprintImpl _$$BlueprintImplFromJson(Map<String, dynamic> json) =>
    _$BlueprintImpl(
      id: json['id'] as String,
      ownerId: json['ownerId'] as String,
      name: json['name'] as String,
      sourceVideoId: json['sourceVideoId'] as String,
      pace: json['pace'] as String? ?? 'medium',
      overallDuration: (json['overallDuration'] as num).toDouble(),
      scenes: (json['scenes'] as List<dynamic>)
          .map((e) => BlueprintScene.fromJson(e as Map<String, dynamic>))
          .toList(),
      music: json['music'] == null
          ? null
          : MusicTrack.fromJson(json['music'] as Map<String, dynamic>),
      colorGrade: json['colorGrade'] as String? ?? 'natural',
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      notes: json['notes'] as String? ?? '',
      schemaVersion: json['schemaVersion'] as String? ?? '1.0.0',
      createdAt: json['createdAt'] as String,
      updatedAt: json['updatedAt'] as String,
    );

Map<String, dynamic> _$$BlueprintImplToJson(_$BlueprintImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'ownerId': instance.ownerId,
      'name': instance.name,
      'sourceVideoId': instance.sourceVideoId,
      'pace': instance.pace,
      'overallDuration': instance.overallDuration,
      'scenes': instance.scenes,
      'music': instance.music,
      'colorGrade': instance.colorGrade,
      'tags': instance.tags,
      'notes': instance.notes,
      'schemaVersion': instance.schemaVersion,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
    };

_$UserImpl _$$UserImplFromJson(Map<String, dynamic> json) => _$UserImpl(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['displayName'] as String,
      avatarUrl: json['avatarUrl'] as String?,
      plan: json['plan'] as String? ?? 'free',
      createdAt: json['createdAt'] as String,
      updatedAt: json['updatedAt'] as String,
    );

Map<String, dynamic> _$$UserImplToJson(_$UserImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'displayName': instance.displayName,
      'avatarUrl': instance.avatarUrl,
      'plan': instance.plan,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
    };
