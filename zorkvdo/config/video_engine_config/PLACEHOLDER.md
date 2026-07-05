# Video Engine Configuration Placeholder
#
# Paths to the CV / video processing binaries and model files.
# In Docker these are pre-installed at standard paths; on a dev machine
# you may need to point them at your local installs.
#
# Environment variables (see .env):
#   FFMPEG_PATH                     (default: ffmpeg — must be on PATH)
#   FFPROBE_PATH                    (default: ffprobe — must be on PATH)
#   OPENCV_PATH                     (optional — OpenCV data dir for Haar cascades)
#   YOLO_MODEL_PATH                 (default: yolov8n.pt — downloaded on first use)
#   MEDIAPIPE_MODEL_PATH            (optional — MediaPipe model cache dir)
#   OCR_MODEL_PATH                  (optional — EasyOCR model cache dir)
#   ANALYSIS_SCENE_THRESHOLD        (default: 27.0 — content threshold for scene cuts)
#   ANALYSIS_SAMPLE_FPS             (default: 2.0 — frames sampled per second)
#   ANALYSIS_MAX_VIDEO_SECONDS      (default: 600 — reject uploads longer than this)
#   ANALYSIS_OCR_LANGUAGES          (default: en — comma-separated)
#   ANALYSIS_ENABLE_FACE            (default: true)
#   ANALYSIS_ENABLE_POSE            (default: true)
#
# Status: PLACEHOLDER — ffmpeg/ffprobe must be installed; everything else falls back gracefully.
