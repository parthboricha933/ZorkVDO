// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Video _$VideoFromJson(Map<String, dynamic> json) {
  return _Video.fromJson(json);
}

/// @nodoc
mixin _$Video {
  String get id => throw _privateConstructorUsedError;
  String get ownerId => throw _privateConstructorUsedError;
  String get kind =>
      throw _privateConstructorUsedError; // source | user_clip | output
  String get filename => throw _privateConstructorUsedError;
  String get contentType => throw _privateConstructorUsedError;
  int get sizeBytes => throw _privateConstructorUsedError;
  String get storageKey => throw _privateConstructorUsedError;
  String get storageUrl => throw _privateConstructorUsedError;
  double? get durationSeconds => throw _privateConstructorUsedError;
  int? get width => throw _privateConstructorUsedError;
  int? get height => throw _privateConstructorUsedError;
  double? get fps => throw _privateConstructorUsedError;
  String? get analysisId => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Video to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Video
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VideoCopyWith<Video> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VideoCopyWith<$Res> {
  factory $VideoCopyWith(Video value, $Res Function(Video) then) =
      _$VideoCopyWithImpl<$Res, Video>;
  @useResult
  $Res call(
      {String id,
      String ownerId,
      String kind,
      String filename,
      String contentType,
      int sizeBytes,
      String storageKey,
      String storageUrl,
      double? durationSeconds,
      int? width,
      int? height,
      double? fps,
      String? analysisId,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class _$VideoCopyWithImpl<$Res, $Val extends Video>
    implements $VideoCopyWith<$Res> {
  _$VideoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Video
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? ownerId = null,
    Object? kind = null,
    Object? filename = null,
    Object? contentType = null,
    Object? sizeBytes = null,
    Object? storageKey = null,
    Object? storageUrl = null,
    Object? durationSeconds = freezed,
    Object? width = freezed,
    Object? height = freezed,
    Object? fps = freezed,
    Object? analysisId = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      kind: null == kind
          ? _value.kind
          : kind // ignore: cast_nullable_to_non_nullable
              as String,
      filename: null == filename
          ? _value.filename
          : filename // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String,
      sizeBytes: null == sizeBytes
          ? _value.sizeBytes
          : sizeBytes // ignore: cast_nullable_to_non_nullable
              as int,
      storageKey: null == storageKey
          ? _value.storageKey
          : storageKey // ignore: cast_nullable_to_non_nullable
              as String,
      storageUrl: null == storageUrl
          ? _value.storageUrl
          : storageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      durationSeconds: freezed == durationSeconds
          ? _value.durationSeconds
          : durationSeconds // ignore: cast_nullable_to_non_nullable
              as double?,
      width: freezed == width
          ? _value.width
          : width // ignore: cast_nullable_to_non_nullable
              as int?,
      height: freezed == height
          ? _value.height
          : height // ignore: cast_nullable_to_non_nullable
              as int?,
      fps: freezed == fps
          ? _value.fps
          : fps // ignore: cast_nullable_to_non_nullable
              as double?,
      analysisId: freezed == analysisId
          ? _value.analysisId
          : analysisId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VideoImplCopyWith<$Res> implements $VideoCopyWith<$Res> {
  factory _$$VideoImplCopyWith(
          _$VideoImpl value, $Res Function(_$VideoImpl) then) =
      __$$VideoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String ownerId,
      String kind,
      String filename,
      String contentType,
      int sizeBytes,
      String storageKey,
      String storageUrl,
      double? durationSeconds,
      int? width,
      int? height,
      double? fps,
      String? analysisId,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class __$$VideoImplCopyWithImpl<$Res>
    extends _$VideoCopyWithImpl<$Res, _$VideoImpl>
    implements _$$VideoImplCopyWith<$Res> {
  __$$VideoImplCopyWithImpl(
      _$VideoImpl _value, $Res Function(_$VideoImpl) _then)
      : super(_value, _then);

  /// Create a copy of Video
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? ownerId = null,
    Object? kind = null,
    Object? filename = null,
    Object? contentType = null,
    Object? sizeBytes = null,
    Object? storageKey = null,
    Object? storageUrl = null,
    Object? durationSeconds = freezed,
    Object? width = freezed,
    Object? height = freezed,
    Object? fps = freezed,
    Object? analysisId = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$VideoImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      kind: null == kind
          ? _value.kind
          : kind // ignore: cast_nullable_to_non_nullable
              as String,
      filename: null == filename
          ? _value.filename
          : filename // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String,
      sizeBytes: null == sizeBytes
          ? _value.sizeBytes
          : sizeBytes // ignore: cast_nullable_to_non_nullable
              as int,
      storageKey: null == storageKey
          ? _value.storageKey
          : storageKey // ignore: cast_nullable_to_non_nullable
              as String,
      storageUrl: null == storageUrl
          ? _value.storageUrl
          : storageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      durationSeconds: freezed == durationSeconds
          ? _value.durationSeconds
          : durationSeconds // ignore: cast_nullable_to_non_nullable
              as double?,
      width: freezed == width
          ? _value.width
          : width // ignore: cast_nullable_to_non_nullable
              as int?,
      height: freezed == height
          ? _value.height
          : height // ignore: cast_nullable_to_non_nullable
              as int?,
      fps: freezed == fps
          ? _value.fps
          : fps // ignore: cast_nullable_to_non_nullable
              as double?,
      analysisId: freezed == analysisId
          ? _value.analysisId
          : analysisId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VideoImpl implements _Video {
  const _$VideoImpl(
      {required this.id,
      required this.ownerId,
      required this.kind,
      required this.filename,
      required this.contentType,
      required this.sizeBytes,
      required this.storageKey,
      required this.storageUrl,
      this.durationSeconds,
      this.width,
      this.height,
      this.fps,
      this.analysisId,
      required this.createdAt,
      required this.updatedAt});

  factory _$VideoImpl.fromJson(Map<String, dynamic> json) =>
      _$$VideoImplFromJson(json);

  @override
  final String id;
  @override
  final String ownerId;
  @override
  final String kind;
// source | user_clip | output
  @override
  final String filename;
  @override
  final String contentType;
  @override
  final int sizeBytes;
  @override
  final String storageKey;
  @override
  final String storageUrl;
  @override
  final double? durationSeconds;
  @override
  final int? width;
  @override
  final int? height;
  @override
  final double? fps;
  @override
  final String? analysisId;
  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'Video(id: $id, ownerId: $ownerId, kind: $kind, filename: $filename, contentType: $contentType, sizeBytes: $sizeBytes, storageKey: $storageKey, storageUrl: $storageUrl, durationSeconds: $durationSeconds, width: $width, height: $height, fps: $fps, analysisId: $analysisId, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VideoImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.ownerId, ownerId) || other.ownerId == ownerId) &&
            (identical(other.kind, kind) || other.kind == kind) &&
            (identical(other.filename, filename) ||
                other.filename == filename) &&
            (identical(other.contentType, contentType) ||
                other.contentType == contentType) &&
            (identical(other.sizeBytes, sizeBytes) ||
                other.sizeBytes == sizeBytes) &&
            (identical(other.storageKey, storageKey) ||
                other.storageKey == storageKey) &&
            (identical(other.storageUrl, storageUrl) ||
                other.storageUrl == storageUrl) &&
            (identical(other.durationSeconds, durationSeconds) ||
                other.durationSeconds == durationSeconds) &&
            (identical(other.width, width) || other.width == width) &&
            (identical(other.height, height) || other.height == height) &&
            (identical(other.fps, fps) || other.fps == fps) &&
            (identical(other.analysisId, analysisId) ||
                other.analysisId == analysisId) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      ownerId,
      kind,
      filename,
      contentType,
      sizeBytes,
      storageKey,
      storageUrl,
      durationSeconds,
      width,
      height,
      fps,
      analysisId,
      createdAt,
      updatedAt);

  /// Create a copy of Video
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VideoImplCopyWith<_$VideoImpl> get copyWith =>
      __$$VideoImplCopyWithImpl<_$VideoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VideoImplToJson(
      this,
    );
  }
}

abstract class _Video implements Video {
  const factory _Video(
      {required final String id,
      required final String ownerId,
      required final String kind,
      required final String filename,
      required final String contentType,
      required final int sizeBytes,
      required final String storageKey,
      required final String storageUrl,
      final double? durationSeconds,
      final int? width,
      final int? height,
      final double? fps,
      final String? analysisId,
      required final String createdAt,
      required final String updatedAt}) = _$VideoImpl;

  factory _Video.fromJson(Map<String, dynamic> json) = _$VideoImpl.fromJson;

  @override
  String get id;
  @override
  String get ownerId;
  @override
  String get kind; // source | user_clip | output
  @override
  String get filename;
  @override
  String get contentType;
  @override
  int get sizeBytes;
  @override
  String get storageKey;
  @override
  String get storageUrl;
  @override
  double? get durationSeconds;
  @override
  int? get width;
  @override
  int? get height;
  @override
  double? get fps;
  @override
  String? get analysisId;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of Video
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VideoImplCopyWith<_$VideoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Project _$ProjectFromJson(Map<String, dynamic> json) {
  return _Project.fromJson(json);
}

/// @nodoc
mixin _$Project {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  String get ownerId => throw _privateConstructorUsedError;
  String? get sourceVideoId => throw _privateConstructorUsedError;
  String? get blueprintId => throw _privateConstructorUsedError;
  String? get outputVideoId => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Project to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ProjectCopyWith<Project> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProjectCopyWith<$Res> {
  factory $ProjectCopyWith(Project value, $Res Function(Project) then) =
      _$ProjectCopyWithImpl<$Res, Project>;
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      String status,
      String ownerId,
      String? sourceVideoId,
      String? blueprintId,
      String? outputVideoId,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class _$ProjectCopyWithImpl<$Res, $Val extends Project>
    implements $ProjectCopyWith<$Res> {
  _$ProjectCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? status = null,
    Object? ownerId = null,
    Object? sourceVideoId = freezed,
    Object? blueprintId = freezed,
    Object? outputVideoId = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      sourceVideoId: freezed == sourceVideoId
          ? _value.sourceVideoId
          : sourceVideoId // ignore: cast_nullable_to_non_nullable
              as String?,
      blueprintId: freezed == blueprintId
          ? _value.blueprintId
          : blueprintId // ignore: cast_nullable_to_non_nullable
              as String?,
      outputVideoId: freezed == outputVideoId
          ? _value.outputVideoId
          : outputVideoId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ProjectImplCopyWith<$Res> implements $ProjectCopyWith<$Res> {
  factory _$$ProjectImplCopyWith(
          _$ProjectImpl value, $Res Function(_$ProjectImpl) then) =
      __$$ProjectImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      String status,
      String ownerId,
      String? sourceVideoId,
      String? blueprintId,
      String? outputVideoId,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class __$$ProjectImplCopyWithImpl<$Res>
    extends _$ProjectCopyWithImpl<$Res, _$ProjectImpl>
    implements _$$ProjectImplCopyWith<$Res> {
  __$$ProjectImplCopyWithImpl(
      _$ProjectImpl _value, $Res Function(_$ProjectImpl) _then)
      : super(_value, _then);

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? status = null,
    Object? ownerId = null,
    Object? sourceVideoId = freezed,
    Object? blueprintId = freezed,
    Object? outputVideoId = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$ProjectImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      sourceVideoId: freezed == sourceVideoId
          ? _value.sourceVideoId
          : sourceVideoId // ignore: cast_nullable_to_non_nullable
              as String?,
      blueprintId: freezed == blueprintId
          ? _value.blueprintId
          : blueprintId // ignore: cast_nullable_to_non_nullable
              as String?,
      outputVideoId: freezed == outputVideoId
          ? _value.outputVideoId
          : outputVideoId // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ProjectImpl implements _Project {
  const _$ProjectImpl(
      {required this.id,
      required this.name,
      this.description = '',
      this.status = 'active',
      required this.ownerId,
      this.sourceVideoId,
      this.blueprintId,
      this.outputVideoId,
      required this.createdAt,
      required this.updatedAt});

  factory _$ProjectImpl.fromJson(Map<String, dynamic> json) =>
      _$$ProjectImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  @JsonKey()
  final String description;
  @override
  @JsonKey()
  final String status;
  @override
  final String ownerId;
  @override
  final String? sourceVideoId;
  @override
  final String? blueprintId;
  @override
  final String? outputVideoId;
  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'Project(id: $id, name: $name, description: $description, status: $status, ownerId: $ownerId, sourceVideoId: $sourceVideoId, blueprintId: $blueprintId, outputVideoId: $outputVideoId, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ProjectImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.ownerId, ownerId) || other.ownerId == ownerId) &&
            (identical(other.sourceVideoId, sourceVideoId) ||
                other.sourceVideoId == sourceVideoId) &&
            (identical(other.blueprintId, blueprintId) ||
                other.blueprintId == blueprintId) &&
            (identical(other.outputVideoId, outputVideoId) ||
                other.outputVideoId == outputVideoId) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, description, status,
      ownerId, sourceVideoId, blueprintId, outputVideoId, createdAt, updatedAt);

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ProjectImplCopyWith<_$ProjectImpl> get copyWith =>
      __$$ProjectImplCopyWithImpl<_$ProjectImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ProjectImplToJson(
      this,
    );
  }
}

abstract class _Project implements Project {
  const factory _Project(
      {required final String id,
      required final String name,
      final String description,
      final String status,
      required final String ownerId,
      final String? sourceVideoId,
      final String? blueprintId,
      final String? outputVideoId,
      required final String createdAt,
      required final String updatedAt}) = _$ProjectImpl;

  factory _Project.fromJson(Map<String, dynamic> json) = _$ProjectImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get description;
  @override
  String get status;
  @override
  String get ownerId;
  @override
  String? get sourceVideoId;
  @override
  String? get blueprintId;
  @override
  String? get outputVideoId;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ProjectImplCopyWith<_$ProjectImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Job _$JobFromJson(Map<String, dynamic> json) {
  return _Job.fromJson(json);
}

/// @nodoc
mixin _$Job {
  String get id => throw _privateConstructorUsedError;
  String get userId => throw _privateConstructorUsedError;
  String? get projectId => throw _privateConstructorUsedError;
  String get jobType => throw _privateConstructorUsedError; // analyze | render
  String get status =>
      throw _privateConstructorUsedError; // queued | running | succeeded | failed | cancelled
  double get progress => throw _privateConstructorUsedError;
  String? get startedAt => throw _privateConstructorUsedError;
  String? get finishedAt => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  Map<String, dynamic>? get result => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Job to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobCopyWith<Job> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobCopyWith<$Res> {
  factory $JobCopyWith(Job value, $Res Function(Job) then) =
      _$JobCopyWithImpl<$Res, Job>;
  @useResult
  $Res call(
      {String id,
      String userId,
      String? projectId,
      String jobType,
      String status,
      double progress,
      String? startedAt,
      String? finishedAt,
      String? error,
      Map<String, dynamic>? result,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class _$JobCopyWithImpl<$Res, $Val extends Job> implements $JobCopyWith<$Res> {
  _$JobCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? projectId = freezed,
    Object? jobType = null,
    Object? status = null,
    Object? progress = null,
    Object? startedAt = freezed,
    Object? finishedAt = freezed,
    Object? error = freezed,
    Object? result = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      projectId: freezed == projectId
          ? _value.projectId
          : projectId // ignore: cast_nullable_to_non_nullable
              as String?,
      jobType: null == jobType
          ? _value.jobType
          : jobType // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      progress: null == progress
          ? _value.progress
          : progress // ignore: cast_nullable_to_non_nullable
              as double,
      startedAt: freezed == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as String?,
      finishedAt: freezed == finishedAt
          ? _value.finishedAt
          : finishedAt // ignore: cast_nullable_to_non_nullable
              as String?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      result: freezed == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$JobImplCopyWith<$Res> implements $JobCopyWith<$Res> {
  factory _$$JobImplCopyWith(_$JobImpl value, $Res Function(_$JobImpl) then) =
      __$$JobImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String userId,
      String? projectId,
      String jobType,
      String status,
      double progress,
      String? startedAt,
      String? finishedAt,
      String? error,
      Map<String, dynamic>? result,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class __$$JobImplCopyWithImpl<$Res> extends _$JobCopyWithImpl<$Res, _$JobImpl>
    implements _$$JobImplCopyWith<$Res> {
  __$$JobImplCopyWithImpl(_$JobImpl _value, $Res Function(_$JobImpl) _then)
      : super(_value, _then);

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? projectId = freezed,
    Object? jobType = null,
    Object? status = null,
    Object? progress = null,
    Object? startedAt = freezed,
    Object? finishedAt = freezed,
    Object? error = freezed,
    Object? result = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$JobImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      projectId: freezed == projectId
          ? _value.projectId
          : projectId // ignore: cast_nullable_to_non_nullable
              as String?,
      jobType: null == jobType
          ? _value.jobType
          : jobType // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      progress: null == progress
          ? _value.progress
          : progress // ignore: cast_nullable_to_non_nullable
              as double,
      startedAt: freezed == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as String?,
      finishedAt: freezed == finishedAt
          ? _value.finishedAt
          : finishedAt // ignore: cast_nullable_to_non_nullable
              as String?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      result: freezed == result
          ? _value._result
          : result // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$JobImpl implements _Job {
  const _$JobImpl(
      {required this.id,
      required this.userId,
      this.projectId,
      required this.jobType,
      required this.status,
      this.progress = 0.0,
      this.startedAt,
      this.finishedAt,
      this.error,
      final Map<String, dynamic>? result,
      required this.createdAt,
      required this.updatedAt})
      : _result = result;

  factory _$JobImpl.fromJson(Map<String, dynamic> json) =>
      _$$JobImplFromJson(json);

  @override
  final String id;
  @override
  final String userId;
  @override
  final String? projectId;
  @override
  final String jobType;
// analyze | render
  @override
  final String status;
// queued | running | succeeded | failed | cancelled
  @override
  @JsonKey()
  final double progress;
  @override
  final String? startedAt;
  @override
  final String? finishedAt;
  @override
  final String? error;
  final Map<String, dynamic>? _result;
  @override
  Map<String, dynamic>? get result {
    final value = _result;
    if (value == null) return null;
    if (_result is EqualUnmodifiableMapView) return _result;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'Job(id: $id, userId: $userId, projectId: $projectId, jobType: $jobType, status: $status, progress: $progress, startedAt: $startedAt, finishedAt: $finishedAt, error: $error, result: $result, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.projectId, projectId) ||
                other.projectId == projectId) &&
            (identical(other.jobType, jobType) || other.jobType == jobType) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.progress, progress) ||
                other.progress == progress) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.finishedAt, finishedAt) ||
                other.finishedAt == finishedAt) &&
            (identical(other.error, error) || other.error == error) &&
            const DeepCollectionEquality().equals(other._result, _result) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      userId,
      projectId,
      jobType,
      status,
      progress,
      startedAt,
      finishedAt,
      error,
      const DeepCollectionEquality().hash(_result),
      createdAt,
      updatedAt);

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      __$$JobImplCopyWithImpl<_$JobImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$JobImplToJson(
      this,
    );
  }
}

abstract class _Job implements Job {
  const factory _Job(
      {required final String id,
      required final String userId,
      final String? projectId,
      required final String jobType,
      required final String status,
      final double progress,
      final String? startedAt,
      final String? finishedAt,
      final String? error,
      final Map<String, dynamic>? result,
      required final String createdAt,
      required final String updatedAt}) = _$JobImpl;

  factory _Job.fromJson(Map<String, dynamic> json) = _$JobImpl.fromJson;

  @override
  String get id;
  @override
  String get userId;
  @override
  String? get projectId;
  @override
  String get jobType; // analyze | render
  @override
  String get status; // queued | running | succeeded | failed | cancelled
  @override
  double get progress;
  @override
  String? get startedAt;
  @override
  String? get finishedAt;
  @override
  String? get error;
  @override
  Map<String, dynamic>? get result;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CaptionStyle _$CaptionStyleFromJson(Map<String, dynamic> json) {
  return _CaptionStyle.fromJson(json);
}

/// @nodoc
mixin _$CaptionStyle {
  String get text => throw _privateConstructorUsedError;
  double get start => throw _privateConstructorUsedError;
  double get end => throw _privateConstructorUsedError;
  String get position => throw _privateConstructorUsedError;
  String get animation => throw _privateConstructorUsedError;
  String get fontFamily => throw _privateConstructorUsedError;
  double get fontSize => throw _privateConstructorUsedError;
  String get colorHex => throw _privateConstructorUsedError;
  String? get strokeColorHex => throw _privateConstructorUsedError;
  double get strokeWidth => throw _privateConstructorUsedError;
  bool get bold => throw _privateConstructorUsedError;
  bool get uppercase => throw _privateConstructorUsedError;

  /// Serializes this CaptionStyle to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CaptionStyle
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CaptionStyleCopyWith<CaptionStyle> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CaptionStyleCopyWith<$Res> {
  factory $CaptionStyleCopyWith(
          CaptionStyle value, $Res Function(CaptionStyle) then) =
      _$CaptionStyleCopyWithImpl<$Res, CaptionStyle>;
  @useResult
  $Res call(
      {String text,
      double start,
      double end,
      String position,
      String animation,
      String fontFamily,
      double fontSize,
      String colorHex,
      String? strokeColorHex,
      double strokeWidth,
      bool bold,
      bool uppercase});
}

/// @nodoc
class _$CaptionStyleCopyWithImpl<$Res, $Val extends CaptionStyle>
    implements $CaptionStyleCopyWith<$Res> {
  _$CaptionStyleCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CaptionStyle
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? text = null,
    Object? start = null,
    Object? end = null,
    Object? position = null,
    Object? animation = null,
    Object? fontFamily = null,
    Object? fontSize = null,
    Object? colorHex = null,
    Object? strokeColorHex = freezed,
    Object? strokeWidth = null,
    Object? bold = null,
    Object? uppercase = null,
  }) {
    return _then(_value.copyWith(
      text: null == text
          ? _value.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      start: null == start
          ? _value.start
          : start // ignore: cast_nullable_to_non_nullable
              as double,
      end: null == end
          ? _value.end
          : end // ignore: cast_nullable_to_non_nullable
              as double,
      position: null == position
          ? _value.position
          : position // ignore: cast_nullable_to_non_nullable
              as String,
      animation: null == animation
          ? _value.animation
          : animation // ignore: cast_nullable_to_non_nullable
              as String,
      fontFamily: null == fontFamily
          ? _value.fontFamily
          : fontFamily // ignore: cast_nullable_to_non_nullable
              as String,
      fontSize: null == fontSize
          ? _value.fontSize
          : fontSize // ignore: cast_nullable_to_non_nullable
              as double,
      colorHex: null == colorHex
          ? _value.colorHex
          : colorHex // ignore: cast_nullable_to_non_nullable
              as String,
      strokeColorHex: freezed == strokeColorHex
          ? _value.strokeColorHex
          : strokeColorHex // ignore: cast_nullable_to_non_nullable
              as String?,
      strokeWidth: null == strokeWidth
          ? _value.strokeWidth
          : strokeWidth // ignore: cast_nullable_to_non_nullable
              as double,
      bold: null == bold
          ? _value.bold
          : bold // ignore: cast_nullable_to_non_nullable
              as bool,
      uppercase: null == uppercase
          ? _value.uppercase
          : uppercase // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CaptionStyleImplCopyWith<$Res>
    implements $CaptionStyleCopyWith<$Res> {
  factory _$$CaptionStyleImplCopyWith(
          _$CaptionStyleImpl value, $Res Function(_$CaptionStyleImpl) then) =
      __$$CaptionStyleImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String text,
      double start,
      double end,
      String position,
      String animation,
      String fontFamily,
      double fontSize,
      String colorHex,
      String? strokeColorHex,
      double strokeWidth,
      bool bold,
      bool uppercase});
}

/// @nodoc
class __$$CaptionStyleImplCopyWithImpl<$Res>
    extends _$CaptionStyleCopyWithImpl<$Res, _$CaptionStyleImpl>
    implements _$$CaptionStyleImplCopyWith<$Res> {
  __$$CaptionStyleImplCopyWithImpl(
      _$CaptionStyleImpl _value, $Res Function(_$CaptionStyleImpl) _then)
      : super(_value, _then);

  /// Create a copy of CaptionStyle
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? text = null,
    Object? start = null,
    Object? end = null,
    Object? position = null,
    Object? animation = null,
    Object? fontFamily = null,
    Object? fontSize = null,
    Object? colorHex = null,
    Object? strokeColorHex = freezed,
    Object? strokeWidth = null,
    Object? bold = null,
    Object? uppercase = null,
  }) {
    return _then(_$CaptionStyleImpl(
      text: null == text
          ? _value.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      start: null == start
          ? _value.start
          : start // ignore: cast_nullable_to_non_nullable
              as double,
      end: null == end
          ? _value.end
          : end // ignore: cast_nullable_to_non_nullable
              as double,
      position: null == position
          ? _value.position
          : position // ignore: cast_nullable_to_non_nullable
              as String,
      animation: null == animation
          ? _value.animation
          : animation // ignore: cast_nullable_to_non_nullable
              as String,
      fontFamily: null == fontFamily
          ? _value.fontFamily
          : fontFamily // ignore: cast_nullable_to_non_nullable
              as String,
      fontSize: null == fontSize
          ? _value.fontSize
          : fontSize // ignore: cast_nullable_to_non_nullable
              as double,
      colorHex: null == colorHex
          ? _value.colorHex
          : colorHex // ignore: cast_nullable_to_non_nullable
              as String,
      strokeColorHex: freezed == strokeColorHex
          ? _value.strokeColorHex
          : strokeColorHex // ignore: cast_nullable_to_non_nullable
              as String?,
      strokeWidth: null == strokeWidth
          ? _value.strokeWidth
          : strokeWidth // ignore: cast_nullable_to_non_nullable
              as double,
      bold: null == bold
          ? _value.bold
          : bold // ignore: cast_nullable_to_non_nullable
              as bool,
      uppercase: null == uppercase
          ? _value.uppercase
          : uppercase // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CaptionStyleImpl implements _CaptionStyle {
  const _$CaptionStyleImpl(
      {required this.text,
      required this.start,
      required this.end,
      this.position = 'bottom_third',
      this.animation = 'pop',
      this.fontFamily = 'Inter',
      this.fontSize = 48.0,
      this.colorHex = '#FFFFFF',
      this.strokeColorHex,
      this.strokeWidth = 2.0,
      this.bold = true,
      this.uppercase = true});

  factory _$CaptionStyleImpl.fromJson(Map<String, dynamic> json) =>
      _$$CaptionStyleImplFromJson(json);

  @override
  final String text;
  @override
  final double start;
  @override
  final double end;
  @override
  @JsonKey()
  final String position;
  @override
  @JsonKey()
  final String animation;
  @override
  @JsonKey()
  final String fontFamily;
  @override
  @JsonKey()
  final double fontSize;
  @override
  @JsonKey()
  final String colorHex;
  @override
  final String? strokeColorHex;
  @override
  @JsonKey()
  final double strokeWidth;
  @override
  @JsonKey()
  final bool bold;
  @override
  @JsonKey()
  final bool uppercase;

  @override
  String toString() {
    return 'CaptionStyle(text: $text, start: $start, end: $end, position: $position, animation: $animation, fontFamily: $fontFamily, fontSize: $fontSize, colorHex: $colorHex, strokeColorHex: $strokeColorHex, strokeWidth: $strokeWidth, bold: $bold, uppercase: $uppercase)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CaptionStyleImpl &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.start, start) || other.start == start) &&
            (identical(other.end, end) || other.end == end) &&
            (identical(other.position, position) ||
                other.position == position) &&
            (identical(other.animation, animation) ||
                other.animation == animation) &&
            (identical(other.fontFamily, fontFamily) ||
                other.fontFamily == fontFamily) &&
            (identical(other.fontSize, fontSize) ||
                other.fontSize == fontSize) &&
            (identical(other.colorHex, colorHex) ||
                other.colorHex == colorHex) &&
            (identical(other.strokeColorHex, strokeColorHex) ||
                other.strokeColorHex == strokeColorHex) &&
            (identical(other.strokeWidth, strokeWidth) ||
                other.strokeWidth == strokeWidth) &&
            (identical(other.bold, bold) || other.bold == bold) &&
            (identical(other.uppercase, uppercase) ||
                other.uppercase == uppercase));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      text,
      start,
      end,
      position,
      animation,
      fontFamily,
      fontSize,
      colorHex,
      strokeColorHex,
      strokeWidth,
      bold,
      uppercase);

  /// Create a copy of CaptionStyle
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CaptionStyleImplCopyWith<_$CaptionStyleImpl> get copyWith =>
      __$$CaptionStyleImplCopyWithImpl<_$CaptionStyleImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CaptionStyleImplToJson(
      this,
    );
  }
}

abstract class _CaptionStyle implements CaptionStyle {
  const factory _CaptionStyle(
      {required final String text,
      required final double start,
      required final double end,
      final String position,
      final String animation,
      final String fontFamily,
      final double fontSize,
      final String colorHex,
      final String? strokeColorHex,
      final double strokeWidth,
      final bool bold,
      final bool uppercase}) = _$CaptionStyleImpl;

  factory _CaptionStyle.fromJson(Map<String, dynamic> json) =
      _$CaptionStyleImpl.fromJson;

  @override
  String get text;
  @override
  double get start;
  @override
  double get end;
  @override
  String get position;
  @override
  String get animation;
  @override
  String get fontFamily;
  @override
  double get fontSize;
  @override
  String get colorHex;
  @override
  String? get strokeColorHex;
  @override
  double get strokeWidth;
  @override
  bool get bold;
  @override
  bool get uppercase;

  /// Create a copy of CaptionStyle
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CaptionStyleImplCopyWith<_$CaptionStyleImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ClipSuggestion _$ClipSuggestionFromJson(Map<String, dynamic> json) {
  return _ClipSuggestion.fromJson(json);
}

/// @nodoc
mixin _$ClipSuggestion {
  String get role => throw _privateConstructorUsedError;
  String get preferredShot => throw _privateConstructorUsedError;
  List<double> get durationRange => throw _privateConstructorUsedError;
  String get motion => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  List<String> get keywords => throw _privateConstructorUsedError;
  int get minFaceCount => throw _privateConstructorUsedError;
  bool get allowTextOverlay => throw _privateConstructorUsedError;

  /// Serializes this ClipSuggestion to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ClipSuggestion
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ClipSuggestionCopyWith<ClipSuggestion> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ClipSuggestionCopyWith<$Res> {
  factory $ClipSuggestionCopyWith(
          ClipSuggestion value, $Res Function(ClipSuggestion) then) =
      _$ClipSuggestionCopyWithImpl<$Res, ClipSuggestion>;
  @useResult
  $Res call(
      {String role,
      String preferredShot,
      List<double> durationRange,
      String motion,
      String description,
      List<String> keywords,
      int minFaceCount,
      bool allowTextOverlay});
}

/// @nodoc
class _$ClipSuggestionCopyWithImpl<$Res, $Val extends ClipSuggestion>
    implements $ClipSuggestionCopyWith<$Res> {
  _$ClipSuggestionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ClipSuggestion
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? role = null,
    Object? preferredShot = null,
    Object? durationRange = null,
    Object? motion = null,
    Object? description = null,
    Object? keywords = null,
    Object? minFaceCount = null,
    Object? allowTextOverlay = null,
  }) {
    return _then(_value.copyWith(
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      preferredShot: null == preferredShot
          ? _value.preferredShot
          : preferredShot // ignore: cast_nullable_to_non_nullable
              as String,
      durationRange: null == durationRange
          ? _value.durationRange
          : durationRange // ignore: cast_nullable_to_non_nullable
              as List<double>,
      motion: null == motion
          ? _value.motion
          : motion // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      keywords: null == keywords
          ? _value.keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      minFaceCount: null == minFaceCount
          ? _value.minFaceCount
          : minFaceCount // ignore: cast_nullable_to_non_nullable
              as int,
      allowTextOverlay: null == allowTextOverlay
          ? _value.allowTextOverlay
          : allowTextOverlay // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ClipSuggestionImplCopyWith<$Res>
    implements $ClipSuggestionCopyWith<$Res> {
  factory _$$ClipSuggestionImplCopyWith(_$ClipSuggestionImpl value,
          $Res Function(_$ClipSuggestionImpl) then) =
      __$$ClipSuggestionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String role,
      String preferredShot,
      List<double> durationRange,
      String motion,
      String description,
      List<String> keywords,
      int minFaceCount,
      bool allowTextOverlay});
}

/// @nodoc
class __$$ClipSuggestionImplCopyWithImpl<$Res>
    extends _$ClipSuggestionCopyWithImpl<$Res, _$ClipSuggestionImpl>
    implements _$$ClipSuggestionImplCopyWith<$Res> {
  __$$ClipSuggestionImplCopyWithImpl(
      _$ClipSuggestionImpl _value, $Res Function(_$ClipSuggestionImpl) _then)
      : super(_value, _then);

  /// Create a copy of ClipSuggestion
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? role = null,
    Object? preferredShot = null,
    Object? durationRange = null,
    Object? motion = null,
    Object? description = null,
    Object? keywords = null,
    Object? minFaceCount = null,
    Object? allowTextOverlay = null,
  }) {
    return _then(_$ClipSuggestionImpl(
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      preferredShot: null == preferredShot
          ? _value.preferredShot
          : preferredShot // ignore: cast_nullable_to_non_nullable
              as String,
      durationRange: null == durationRange
          ? _value._durationRange
          : durationRange // ignore: cast_nullable_to_non_nullable
              as List<double>,
      motion: null == motion
          ? _value.motion
          : motion // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      keywords: null == keywords
          ? _value._keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      minFaceCount: null == minFaceCount
          ? _value.minFaceCount
          : minFaceCount // ignore: cast_nullable_to_non_nullable
              as int,
      allowTextOverlay: null == allowTextOverlay
          ? _value.allowTextOverlay
          : allowTextOverlay // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ClipSuggestionImpl implements _ClipSuggestion {
  const _$ClipSuggestionImpl(
      {this.role = 'any',
      this.preferredShot = 'unknown',
      final List<double> durationRange = const [0.5, 3.0],
      this.motion = 'static',
      this.description = '',
      final List<String> keywords = const [],
      this.minFaceCount = 0,
      this.allowTextOverlay = true})
      : _durationRange = durationRange,
        _keywords = keywords;

  factory _$ClipSuggestionImpl.fromJson(Map<String, dynamic> json) =>
      _$$ClipSuggestionImplFromJson(json);

  @override
  @JsonKey()
  final String role;
  @override
  @JsonKey()
  final String preferredShot;
  final List<double> _durationRange;
  @override
  @JsonKey()
  List<double> get durationRange {
    if (_durationRange is EqualUnmodifiableListView) return _durationRange;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_durationRange);
  }

  @override
  @JsonKey()
  final String motion;
  @override
  @JsonKey()
  final String description;
  final List<String> _keywords;
  @override
  @JsonKey()
  List<String> get keywords {
    if (_keywords is EqualUnmodifiableListView) return _keywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_keywords);
  }

  @override
  @JsonKey()
  final int minFaceCount;
  @override
  @JsonKey()
  final bool allowTextOverlay;

  @override
  String toString() {
    return 'ClipSuggestion(role: $role, preferredShot: $preferredShot, durationRange: $durationRange, motion: $motion, description: $description, keywords: $keywords, minFaceCount: $minFaceCount, allowTextOverlay: $allowTextOverlay)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ClipSuggestionImpl &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.preferredShot, preferredShot) ||
                other.preferredShot == preferredShot) &&
            const DeepCollectionEquality()
                .equals(other._durationRange, _durationRange) &&
            (identical(other.motion, motion) || other.motion == motion) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(other._keywords, _keywords) &&
            (identical(other.minFaceCount, minFaceCount) ||
                other.minFaceCount == minFaceCount) &&
            (identical(other.allowTextOverlay, allowTextOverlay) ||
                other.allowTextOverlay == allowTextOverlay));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      role,
      preferredShot,
      const DeepCollectionEquality().hash(_durationRange),
      motion,
      description,
      const DeepCollectionEquality().hash(_keywords),
      minFaceCount,
      allowTextOverlay);

  /// Create a copy of ClipSuggestion
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ClipSuggestionImplCopyWith<_$ClipSuggestionImpl> get copyWith =>
      __$$ClipSuggestionImplCopyWithImpl<_$ClipSuggestionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ClipSuggestionImplToJson(
      this,
    );
  }
}

abstract class _ClipSuggestion implements ClipSuggestion {
  const factory _ClipSuggestion(
      {final String role,
      final String preferredShot,
      final List<double> durationRange,
      final String motion,
      final String description,
      final List<String> keywords,
      final int minFaceCount,
      final bool allowTextOverlay}) = _$ClipSuggestionImpl;

  factory _ClipSuggestion.fromJson(Map<String, dynamic> json) =
      _$ClipSuggestionImpl.fromJson;

  @override
  String get role;
  @override
  String get preferredShot;
  @override
  List<double> get durationRange;
  @override
  String get motion;
  @override
  String get description;
  @override
  List<String> get keywords;
  @override
  int get minFaceCount;
  @override
  bool get allowTextOverlay;

  /// Create a copy of ClipSuggestion
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ClipSuggestionImplCopyWith<_$ClipSuggestionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BlueprintScene _$BlueprintSceneFromJson(Map<String, dynamic> json) {
  return _BlueprintScene.fromJson(json);
}

/// @nodoc
mixin _$BlueprintScene {
  int get index => throw _privateConstructorUsedError;
  double get start => throw _privateConstructorUsedError;
  double get end => throw _privateConstructorUsedError;
  double get duration => throw _privateConstructorUsedError;
  String get shotType => throw _privateConstructorUsedError;
  String get cameraMotion => throw _privateConstructorUsedError;
  double get zoomFactor => throw _privateConstructorUsedError;
  List<CaptionStyle> get captions => throw _privateConstructorUsedError;
  ClipSuggestion get clipSuggestion => throw _privateConstructorUsedError;
  List<String> get dominantColorsHex => throw _privateConstructorUsedError;
  double? get bpmSync => throw _privateConstructorUsedError;

  /// Serializes this BlueprintScene to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BlueprintSceneCopyWith<BlueprintScene> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BlueprintSceneCopyWith<$Res> {
  factory $BlueprintSceneCopyWith(
          BlueprintScene value, $Res Function(BlueprintScene) then) =
      _$BlueprintSceneCopyWithImpl<$Res, BlueprintScene>;
  @useResult
  $Res call(
      {int index,
      double start,
      double end,
      double duration,
      String shotType,
      String cameraMotion,
      double zoomFactor,
      List<CaptionStyle> captions,
      ClipSuggestion clipSuggestion,
      List<String> dominantColorsHex,
      double? bpmSync});

  $ClipSuggestionCopyWith<$Res> get clipSuggestion;
}

/// @nodoc
class _$BlueprintSceneCopyWithImpl<$Res, $Val extends BlueprintScene>
    implements $BlueprintSceneCopyWith<$Res> {
  _$BlueprintSceneCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? index = null,
    Object? start = null,
    Object? end = null,
    Object? duration = null,
    Object? shotType = null,
    Object? cameraMotion = null,
    Object? zoomFactor = null,
    Object? captions = null,
    Object? clipSuggestion = null,
    Object? dominantColorsHex = null,
    Object? bpmSync = freezed,
  }) {
    return _then(_value.copyWith(
      index: null == index
          ? _value.index
          : index // ignore: cast_nullable_to_non_nullable
              as int,
      start: null == start
          ? _value.start
          : start // ignore: cast_nullable_to_non_nullable
              as double,
      end: null == end
          ? _value.end
          : end // ignore: cast_nullable_to_non_nullable
              as double,
      duration: null == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as double,
      shotType: null == shotType
          ? _value.shotType
          : shotType // ignore: cast_nullable_to_non_nullable
              as String,
      cameraMotion: null == cameraMotion
          ? _value.cameraMotion
          : cameraMotion // ignore: cast_nullable_to_non_nullable
              as String,
      zoomFactor: null == zoomFactor
          ? _value.zoomFactor
          : zoomFactor // ignore: cast_nullable_to_non_nullable
              as double,
      captions: null == captions
          ? _value.captions
          : captions // ignore: cast_nullable_to_non_nullable
              as List<CaptionStyle>,
      clipSuggestion: null == clipSuggestion
          ? _value.clipSuggestion
          : clipSuggestion // ignore: cast_nullable_to_non_nullable
              as ClipSuggestion,
      dominantColorsHex: null == dominantColorsHex
          ? _value.dominantColorsHex
          : dominantColorsHex // ignore: cast_nullable_to_non_nullable
              as List<String>,
      bpmSync: freezed == bpmSync
          ? _value.bpmSync
          : bpmSync // ignore: cast_nullable_to_non_nullable
              as double?,
    ) as $Val);
  }

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ClipSuggestionCopyWith<$Res> get clipSuggestion {
    return $ClipSuggestionCopyWith<$Res>(_value.clipSuggestion, (value) {
      return _then(_value.copyWith(clipSuggestion: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$BlueprintSceneImplCopyWith<$Res>
    implements $BlueprintSceneCopyWith<$Res> {
  factory _$$BlueprintSceneImplCopyWith(_$BlueprintSceneImpl value,
          $Res Function(_$BlueprintSceneImpl) then) =
      __$$BlueprintSceneImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int index,
      double start,
      double end,
      double duration,
      String shotType,
      String cameraMotion,
      double zoomFactor,
      List<CaptionStyle> captions,
      ClipSuggestion clipSuggestion,
      List<String> dominantColorsHex,
      double? bpmSync});

  @override
  $ClipSuggestionCopyWith<$Res> get clipSuggestion;
}

/// @nodoc
class __$$BlueprintSceneImplCopyWithImpl<$Res>
    extends _$BlueprintSceneCopyWithImpl<$Res, _$BlueprintSceneImpl>
    implements _$$BlueprintSceneImplCopyWith<$Res> {
  __$$BlueprintSceneImplCopyWithImpl(
      _$BlueprintSceneImpl _value, $Res Function(_$BlueprintSceneImpl) _then)
      : super(_value, _then);

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? index = null,
    Object? start = null,
    Object? end = null,
    Object? duration = null,
    Object? shotType = null,
    Object? cameraMotion = null,
    Object? zoomFactor = null,
    Object? captions = null,
    Object? clipSuggestion = null,
    Object? dominantColorsHex = null,
    Object? bpmSync = freezed,
  }) {
    return _then(_$BlueprintSceneImpl(
      index: null == index
          ? _value.index
          : index // ignore: cast_nullable_to_non_nullable
              as int,
      start: null == start
          ? _value.start
          : start // ignore: cast_nullable_to_non_nullable
              as double,
      end: null == end
          ? _value.end
          : end // ignore: cast_nullable_to_non_nullable
              as double,
      duration: null == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as double,
      shotType: null == shotType
          ? _value.shotType
          : shotType // ignore: cast_nullable_to_non_nullable
              as String,
      cameraMotion: null == cameraMotion
          ? _value.cameraMotion
          : cameraMotion // ignore: cast_nullable_to_non_nullable
              as String,
      zoomFactor: null == zoomFactor
          ? _value.zoomFactor
          : zoomFactor // ignore: cast_nullable_to_non_nullable
              as double,
      captions: null == captions
          ? _value._captions
          : captions // ignore: cast_nullable_to_non_nullable
              as List<CaptionStyle>,
      clipSuggestion: null == clipSuggestion
          ? _value.clipSuggestion
          : clipSuggestion // ignore: cast_nullable_to_non_nullable
              as ClipSuggestion,
      dominantColorsHex: null == dominantColorsHex
          ? _value._dominantColorsHex
          : dominantColorsHex // ignore: cast_nullable_to_non_nullable
              as List<String>,
      bpmSync: freezed == bpmSync
          ? _value.bpmSync
          : bpmSync // ignore: cast_nullable_to_non_nullable
              as double?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BlueprintSceneImpl implements _BlueprintScene {
  const _$BlueprintSceneImpl(
      {required this.index,
      required this.start,
      required this.end,
      required this.duration,
      this.shotType = 'medium',
      this.cameraMotion = 'static',
      this.zoomFactor = 1.0,
      final List<CaptionStyle> captions = const [],
      required this.clipSuggestion,
      final List<String> dominantColorsHex = const [],
      this.bpmSync})
      : _captions = captions,
        _dominantColorsHex = dominantColorsHex;

  factory _$BlueprintSceneImpl.fromJson(Map<String, dynamic> json) =>
      _$$BlueprintSceneImplFromJson(json);

  @override
  final int index;
  @override
  final double start;
  @override
  final double end;
  @override
  final double duration;
  @override
  @JsonKey()
  final String shotType;
  @override
  @JsonKey()
  final String cameraMotion;
  @override
  @JsonKey()
  final double zoomFactor;
  final List<CaptionStyle> _captions;
  @override
  @JsonKey()
  List<CaptionStyle> get captions {
    if (_captions is EqualUnmodifiableListView) return _captions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_captions);
  }

  @override
  final ClipSuggestion clipSuggestion;
  final List<String> _dominantColorsHex;
  @override
  @JsonKey()
  List<String> get dominantColorsHex {
    if (_dominantColorsHex is EqualUnmodifiableListView)
      return _dominantColorsHex;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_dominantColorsHex);
  }

  @override
  final double? bpmSync;

  @override
  String toString() {
    return 'BlueprintScene(index: $index, start: $start, end: $end, duration: $duration, shotType: $shotType, cameraMotion: $cameraMotion, zoomFactor: $zoomFactor, captions: $captions, clipSuggestion: $clipSuggestion, dominantColorsHex: $dominantColorsHex, bpmSync: $bpmSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BlueprintSceneImpl &&
            (identical(other.index, index) || other.index == index) &&
            (identical(other.start, start) || other.start == start) &&
            (identical(other.end, end) || other.end == end) &&
            (identical(other.duration, duration) ||
                other.duration == duration) &&
            (identical(other.shotType, shotType) ||
                other.shotType == shotType) &&
            (identical(other.cameraMotion, cameraMotion) ||
                other.cameraMotion == cameraMotion) &&
            (identical(other.zoomFactor, zoomFactor) ||
                other.zoomFactor == zoomFactor) &&
            const DeepCollectionEquality().equals(other._captions, _captions) &&
            (identical(other.clipSuggestion, clipSuggestion) ||
                other.clipSuggestion == clipSuggestion) &&
            const DeepCollectionEquality()
                .equals(other._dominantColorsHex, _dominantColorsHex) &&
            (identical(other.bpmSync, bpmSync) || other.bpmSync == bpmSync));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      index,
      start,
      end,
      duration,
      shotType,
      cameraMotion,
      zoomFactor,
      const DeepCollectionEquality().hash(_captions),
      clipSuggestion,
      const DeepCollectionEquality().hash(_dominantColorsHex),
      bpmSync);

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BlueprintSceneImplCopyWith<_$BlueprintSceneImpl> get copyWith =>
      __$$BlueprintSceneImplCopyWithImpl<_$BlueprintSceneImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BlueprintSceneImplToJson(
      this,
    );
  }
}

abstract class _BlueprintScene implements BlueprintScene {
  const factory _BlueprintScene(
      {required final int index,
      required final double start,
      required final double end,
      required final double duration,
      final String shotType,
      final String cameraMotion,
      final double zoomFactor,
      final List<CaptionStyle> captions,
      required final ClipSuggestion clipSuggestion,
      final List<String> dominantColorsHex,
      final double? bpmSync}) = _$BlueprintSceneImpl;

  factory _BlueprintScene.fromJson(Map<String, dynamic> json) =
      _$BlueprintSceneImpl.fromJson;

  @override
  int get index;
  @override
  double get start;
  @override
  double get end;
  @override
  double get duration;
  @override
  String get shotType;
  @override
  String get cameraMotion;
  @override
  double get zoomFactor;
  @override
  List<CaptionStyle> get captions;
  @override
  ClipSuggestion get clipSuggestion;
  @override
  List<String> get dominantColorsHex;
  @override
  double? get bpmSync;

  /// Create a copy of BlueprintScene
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BlueprintSceneImplCopyWith<_$BlueprintSceneImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

MusicTrack _$MusicTrackFromJson(Map<String, dynamic> json) {
  return _MusicTrack.fromJson(json);
}

/// @nodoc
mixin _$MusicTrack {
  String get title => throw _privateConstructorUsedError;
  String get artist => throw _privateConstructorUsedError;
  double? get bpm => throw _privateConstructorUsedError;
  double get energy => throw _privateConstructorUsedError;
  List<double> get beatTimes => throw _privateConstructorUsedError;

  /// Serializes this MusicTrack to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MusicTrack
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MusicTrackCopyWith<MusicTrack> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MusicTrackCopyWith<$Res> {
  factory $MusicTrackCopyWith(
          MusicTrack value, $Res Function(MusicTrack) then) =
      _$MusicTrackCopyWithImpl<$Res, MusicTrack>;
  @useResult
  $Res call(
      {String title,
      String artist,
      double? bpm,
      double energy,
      List<double> beatTimes});
}

/// @nodoc
class _$MusicTrackCopyWithImpl<$Res, $Val extends MusicTrack>
    implements $MusicTrackCopyWith<$Res> {
  _$MusicTrackCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MusicTrack
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? artist = null,
    Object? bpm = freezed,
    Object? energy = null,
    Object? beatTimes = null,
  }) {
    return _then(_value.copyWith(
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      artist: null == artist
          ? _value.artist
          : artist // ignore: cast_nullable_to_non_nullable
              as String,
      bpm: freezed == bpm
          ? _value.bpm
          : bpm // ignore: cast_nullable_to_non_nullable
              as double?,
      energy: null == energy
          ? _value.energy
          : energy // ignore: cast_nullable_to_non_nullable
              as double,
      beatTimes: null == beatTimes
          ? _value.beatTimes
          : beatTimes // ignore: cast_nullable_to_non_nullable
              as List<double>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MusicTrackImplCopyWith<$Res>
    implements $MusicTrackCopyWith<$Res> {
  factory _$$MusicTrackImplCopyWith(
          _$MusicTrackImpl value, $Res Function(_$MusicTrackImpl) then) =
      __$$MusicTrackImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String title,
      String artist,
      double? bpm,
      double energy,
      List<double> beatTimes});
}

/// @nodoc
class __$$MusicTrackImplCopyWithImpl<$Res>
    extends _$MusicTrackCopyWithImpl<$Res, _$MusicTrackImpl>
    implements _$$MusicTrackImplCopyWith<$Res> {
  __$$MusicTrackImplCopyWithImpl(
      _$MusicTrackImpl _value, $Res Function(_$MusicTrackImpl) _then)
      : super(_value, _then);

  /// Create a copy of MusicTrack
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? artist = null,
    Object? bpm = freezed,
    Object? energy = null,
    Object? beatTimes = null,
  }) {
    return _then(_$MusicTrackImpl(
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      artist: null == artist
          ? _value.artist
          : artist // ignore: cast_nullable_to_non_nullable
              as String,
      bpm: freezed == bpm
          ? _value.bpm
          : bpm // ignore: cast_nullable_to_non_nullable
              as double?,
      energy: null == energy
          ? _value.energy
          : energy // ignore: cast_nullable_to_non_nullable
              as double,
      beatTimes: null == beatTimes
          ? _value._beatTimes
          : beatTimes // ignore: cast_nullable_to_non_nullable
              as List<double>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MusicTrackImpl implements _MusicTrack {
  const _$MusicTrackImpl(
      {this.title = '',
      this.artist = '',
      this.bpm,
      this.energy = 0.5,
      final List<double> beatTimes = const []})
      : _beatTimes = beatTimes;

  factory _$MusicTrackImpl.fromJson(Map<String, dynamic> json) =>
      _$$MusicTrackImplFromJson(json);

  @override
  @JsonKey()
  final String title;
  @override
  @JsonKey()
  final String artist;
  @override
  final double? bpm;
  @override
  @JsonKey()
  final double energy;
  final List<double> _beatTimes;
  @override
  @JsonKey()
  List<double> get beatTimes {
    if (_beatTimes is EqualUnmodifiableListView) return _beatTimes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_beatTimes);
  }

  @override
  String toString() {
    return 'MusicTrack(title: $title, artist: $artist, bpm: $bpm, energy: $energy, beatTimes: $beatTimes)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MusicTrackImpl &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.artist, artist) || other.artist == artist) &&
            (identical(other.bpm, bpm) || other.bpm == bpm) &&
            (identical(other.energy, energy) || other.energy == energy) &&
            const DeepCollectionEquality()
                .equals(other._beatTimes, _beatTimes));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, title, artist, bpm, energy,
      const DeepCollectionEquality().hash(_beatTimes));

  /// Create a copy of MusicTrack
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MusicTrackImplCopyWith<_$MusicTrackImpl> get copyWith =>
      __$$MusicTrackImplCopyWithImpl<_$MusicTrackImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MusicTrackImplToJson(
      this,
    );
  }
}

abstract class _MusicTrack implements MusicTrack {
  const factory _MusicTrack(
      {final String title,
      final String artist,
      final double? bpm,
      final double energy,
      final List<double> beatTimes}) = _$MusicTrackImpl;

  factory _MusicTrack.fromJson(Map<String, dynamic> json) =
      _$MusicTrackImpl.fromJson;

  @override
  String get title;
  @override
  String get artist;
  @override
  double? get bpm;
  @override
  double get energy;
  @override
  List<double> get beatTimes;

  /// Create a copy of MusicTrack
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MusicTrackImplCopyWith<_$MusicTrackImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Blueprint _$BlueprintFromJson(Map<String, dynamic> json) {
  return _Blueprint.fromJson(json);
}

/// @nodoc
mixin _$Blueprint {
  String get id => throw _privateConstructorUsedError;
  String get ownerId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get sourceVideoId => throw _privateConstructorUsedError;
  String get pace => throw _privateConstructorUsedError;
  double get overallDuration => throw _privateConstructorUsedError;
  List<BlueprintScene> get scenes => throw _privateConstructorUsedError;
  MusicTrack? get music => throw _privateConstructorUsedError;
  String get colorGrade => throw _privateConstructorUsedError;
  List<String> get tags => throw _privateConstructorUsedError;
  String get notes => throw _privateConstructorUsedError;
  String get schemaVersion => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Blueprint to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BlueprintCopyWith<Blueprint> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BlueprintCopyWith<$Res> {
  factory $BlueprintCopyWith(Blueprint value, $Res Function(Blueprint) then) =
      _$BlueprintCopyWithImpl<$Res, Blueprint>;
  @useResult
  $Res call(
      {String id,
      String ownerId,
      String name,
      String sourceVideoId,
      String pace,
      double overallDuration,
      List<BlueprintScene> scenes,
      MusicTrack? music,
      String colorGrade,
      List<String> tags,
      String notes,
      String schemaVersion,
      String createdAt,
      String updatedAt});

  $MusicTrackCopyWith<$Res>? get music;
}

/// @nodoc
class _$BlueprintCopyWithImpl<$Res, $Val extends Blueprint>
    implements $BlueprintCopyWith<$Res> {
  _$BlueprintCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? ownerId = null,
    Object? name = null,
    Object? sourceVideoId = null,
    Object? pace = null,
    Object? overallDuration = null,
    Object? scenes = null,
    Object? music = freezed,
    Object? colorGrade = null,
    Object? tags = null,
    Object? notes = null,
    Object? schemaVersion = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      sourceVideoId: null == sourceVideoId
          ? _value.sourceVideoId
          : sourceVideoId // ignore: cast_nullable_to_non_nullable
              as String,
      pace: null == pace
          ? _value.pace
          : pace // ignore: cast_nullable_to_non_nullable
              as String,
      overallDuration: null == overallDuration
          ? _value.overallDuration
          : overallDuration // ignore: cast_nullable_to_non_nullable
              as double,
      scenes: null == scenes
          ? _value.scenes
          : scenes // ignore: cast_nullable_to_non_nullable
              as List<BlueprintScene>,
      music: freezed == music
          ? _value.music
          : music // ignore: cast_nullable_to_non_nullable
              as MusicTrack?,
      colorGrade: null == colorGrade
          ? _value.colorGrade
          : colorGrade // ignore: cast_nullable_to_non_nullable
              as String,
      tags: null == tags
          ? _value.tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      schemaVersion: null == schemaVersion
          ? _value.schemaVersion
          : schemaVersion // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $MusicTrackCopyWith<$Res>? get music {
    if (_value.music == null) {
      return null;
    }

    return $MusicTrackCopyWith<$Res>(_value.music!, (value) {
      return _then(_value.copyWith(music: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$BlueprintImplCopyWith<$Res>
    implements $BlueprintCopyWith<$Res> {
  factory _$$BlueprintImplCopyWith(
          _$BlueprintImpl value, $Res Function(_$BlueprintImpl) then) =
      __$$BlueprintImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String ownerId,
      String name,
      String sourceVideoId,
      String pace,
      double overallDuration,
      List<BlueprintScene> scenes,
      MusicTrack? music,
      String colorGrade,
      List<String> tags,
      String notes,
      String schemaVersion,
      String createdAt,
      String updatedAt});

  @override
  $MusicTrackCopyWith<$Res>? get music;
}

/// @nodoc
class __$$BlueprintImplCopyWithImpl<$Res>
    extends _$BlueprintCopyWithImpl<$Res, _$BlueprintImpl>
    implements _$$BlueprintImplCopyWith<$Res> {
  __$$BlueprintImplCopyWithImpl(
      _$BlueprintImpl _value, $Res Function(_$BlueprintImpl) _then)
      : super(_value, _then);

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? ownerId = null,
    Object? name = null,
    Object? sourceVideoId = null,
    Object? pace = null,
    Object? overallDuration = null,
    Object? scenes = null,
    Object? music = freezed,
    Object? colorGrade = null,
    Object? tags = null,
    Object? notes = null,
    Object? schemaVersion = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$BlueprintImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      ownerId: null == ownerId
          ? _value.ownerId
          : ownerId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      sourceVideoId: null == sourceVideoId
          ? _value.sourceVideoId
          : sourceVideoId // ignore: cast_nullable_to_non_nullable
              as String,
      pace: null == pace
          ? _value.pace
          : pace // ignore: cast_nullable_to_non_nullable
              as String,
      overallDuration: null == overallDuration
          ? _value.overallDuration
          : overallDuration // ignore: cast_nullable_to_non_nullable
              as double,
      scenes: null == scenes
          ? _value._scenes
          : scenes // ignore: cast_nullable_to_non_nullable
              as List<BlueprintScene>,
      music: freezed == music
          ? _value.music
          : music // ignore: cast_nullable_to_non_nullable
              as MusicTrack?,
      colorGrade: null == colorGrade
          ? _value.colorGrade
          : colorGrade // ignore: cast_nullable_to_non_nullable
              as String,
      tags: null == tags
          ? _value._tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      schemaVersion: null == schemaVersion
          ? _value.schemaVersion
          : schemaVersion // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BlueprintImpl implements _Blueprint {
  const _$BlueprintImpl(
      {required this.id,
      required this.ownerId,
      required this.name,
      required this.sourceVideoId,
      this.pace = 'medium',
      required this.overallDuration,
      required final List<BlueprintScene> scenes,
      this.music,
      this.colorGrade = 'natural',
      final List<String> tags = const [],
      this.notes = '',
      this.schemaVersion = '1.0.0',
      required this.createdAt,
      required this.updatedAt})
      : _scenes = scenes,
        _tags = tags;

  factory _$BlueprintImpl.fromJson(Map<String, dynamic> json) =>
      _$$BlueprintImplFromJson(json);

  @override
  final String id;
  @override
  final String ownerId;
  @override
  final String name;
  @override
  final String sourceVideoId;
  @override
  @JsonKey()
  final String pace;
  @override
  final double overallDuration;
  final List<BlueprintScene> _scenes;
  @override
  List<BlueprintScene> get scenes {
    if (_scenes is EqualUnmodifiableListView) return _scenes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_scenes);
  }

  @override
  final MusicTrack? music;
  @override
  @JsonKey()
  final String colorGrade;
  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

  @override
  @JsonKey()
  final String notes;
  @override
  @JsonKey()
  final String schemaVersion;
  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'Blueprint(id: $id, ownerId: $ownerId, name: $name, sourceVideoId: $sourceVideoId, pace: $pace, overallDuration: $overallDuration, scenes: $scenes, music: $music, colorGrade: $colorGrade, tags: $tags, notes: $notes, schemaVersion: $schemaVersion, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BlueprintImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.ownerId, ownerId) || other.ownerId == ownerId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.sourceVideoId, sourceVideoId) ||
                other.sourceVideoId == sourceVideoId) &&
            (identical(other.pace, pace) || other.pace == pace) &&
            (identical(other.overallDuration, overallDuration) ||
                other.overallDuration == overallDuration) &&
            const DeepCollectionEquality().equals(other._scenes, _scenes) &&
            (identical(other.music, music) || other.music == music) &&
            (identical(other.colorGrade, colorGrade) ||
                other.colorGrade == colorGrade) &&
            const DeepCollectionEquality().equals(other._tags, _tags) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.schemaVersion, schemaVersion) ||
                other.schemaVersion == schemaVersion) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      ownerId,
      name,
      sourceVideoId,
      pace,
      overallDuration,
      const DeepCollectionEquality().hash(_scenes),
      music,
      colorGrade,
      const DeepCollectionEquality().hash(_tags),
      notes,
      schemaVersion,
      createdAt,
      updatedAt);

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BlueprintImplCopyWith<_$BlueprintImpl> get copyWith =>
      __$$BlueprintImplCopyWithImpl<_$BlueprintImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BlueprintImplToJson(
      this,
    );
  }
}

abstract class _Blueprint implements Blueprint {
  const factory _Blueprint(
      {required final String id,
      required final String ownerId,
      required final String name,
      required final String sourceVideoId,
      final String pace,
      required final double overallDuration,
      required final List<BlueprintScene> scenes,
      final MusicTrack? music,
      final String colorGrade,
      final List<String> tags,
      final String notes,
      final String schemaVersion,
      required final String createdAt,
      required final String updatedAt}) = _$BlueprintImpl;

  factory _Blueprint.fromJson(Map<String, dynamic> json) =
      _$BlueprintImpl.fromJson;

  @override
  String get id;
  @override
  String get ownerId;
  @override
  String get name;
  @override
  String get sourceVideoId;
  @override
  String get pace;
  @override
  double get overallDuration;
  @override
  List<BlueprintScene> get scenes;
  @override
  MusicTrack? get music;
  @override
  String get colorGrade;
  @override
  List<String> get tags;
  @override
  String get notes;
  @override
  String get schemaVersion;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of Blueprint
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BlueprintImplCopyWith<_$BlueprintImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

User _$UserFromJson(Map<String, dynamic> json) {
  return _User.fromJson(json);
}

/// @nodoc
mixin _$User {
  String get id => throw _privateConstructorUsedError;
  String get email => throw _privateConstructorUsedError;
  String get displayName => throw _privateConstructorUsedError;
  String? get avatarUrl => throw _privateConstructorUsedError;
  String get plan => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this User to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of User
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserCopyWith<User> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserCopyWith<$Res> {
  factory $UserCopyWith(User value, $Res Function(User) then) =
      _$UserCopyWithImpl<$Res, User>;
  @useResult
  $Res call(
      {String id,
      String email,
      String displayName,
      String? avatarUrl,
      String plan,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class _$UserCopyWithImpl<$Res, $Val extends User>
    implements $UserCopyWith<$Res> {
  _$UserCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of User
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = null,
    Object? displayName = null,
    Object? avatarUrl = freezed,
    Object? plan = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      plan: null == plan
          ? _value.plan
          : plan // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UserImplCopyWith<$Res> implements $UserCopyWith<$Res> {
  factory _$$UserImplCopyWith(
          _$UserImpl value, $Res Function(_$UserImpl) then) =
      __$$UserImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String email,
      String displayName,
      String? avatarUrl,
      String plan,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class __$$UserImplCopyWithImpl<$Res>
    extends _$UserCopyWithImpl<$Res, _$UserImpl>
    implements _$$UserImplCopyWith<$Res> {
  __$$UserImplCopyWithImpl(_$UserImpl _value, $Res Function(_$UserImpl) _then)
      : super(_value, _then);

  /// Create a copy of User
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = null,
    Object? displayName = null,
    Object? avatarUrl = freezed,
    Object? plan = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$UserImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      plan: null == plan
          ? _value.plan
          : plan // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UserImpl implements _User {
  const _$UserImpl(
      {required this.id,
      required this.email,
      required this.displayName,
      this.avatarUrl,
      this.plan = 'free',
      required this.createdAt,
      required this.updatedAt});

  factory _$UserImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserImplFromJson(json);

  @override
  final String id;
  @override
  final String email;
  @override
  final String displayName;
  @override
  final String? avatarUrl;
  @override
  @JsonKey()
  final String plan;
  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'User(id: $id, email: $email, displayName: $displayName, avatarUrl: $avatarUrl, plan: $plan, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.avatarUrl, avatarUrl) ||
                other.avatarUrl == avatarUrl) &&
            (identical(other.plan, plan) || other.plan == plan) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, email, displayName,
      avatarUrl, plan, createdAt, updatedAt);

  /// Create a copy of User
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserImplCopyWith<_$UserImpl> get copyWith =>
      __$$UserImplCopyWithImpl<_$UserImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UserImplToJson(
      this,
    );
  }
}

abstract class _User implements User {
  const factory _User(
      {required final String id,
      required final String email,
      required final String displayName,
      final String? avatarUrl,
      final String plan,
      required final String createdAt,
      required final String updatedAt}) = _$UserImpl;

  factory _User.fromJson(Map<String, dynamic> json) = _$UserImpl.fromJson;

  @override
  String get id;
  @override
  String get email;
  @override
  String get displayName;
  @override
  String? get avatarUrl;
  @override
  String get plan;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of User
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserImplCopyWith<_$UserImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
