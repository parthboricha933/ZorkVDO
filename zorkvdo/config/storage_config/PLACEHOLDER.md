# Storage Configuration Placeholder
#
# Selects the storage backend used for user uploads (videos, clips, renders).
#
# Environment variables (see .env):
#   STORAGE_PROVIDER          (local | s3 | firebase)
#   STORAGE_CONNECTION_STRING (for s3 — endpoint URL; for firebase — bucket path)
#   S3_ACCESS_KEY
#   S3_SECRET_KEY
#   S3_BUCKET
#   S3_REGION
#   S3_USE_PATH_STYLE         (true for MinIO; false for AWS S3)
#   STORAGE_LOCAL_ROOT        (for local backend)
#
# Status: PLACEHOLDER — defaults to local filesystem (no key needed).
