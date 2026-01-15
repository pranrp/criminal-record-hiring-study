#!/usr/bin/env bash
set -euo pipefail

echo "=== TEST RUN START ==="

# -----
# 0) Required env vars
# -----
: "${GDRIVE_SERVICE_ACCOUNT_JSON:?Missing GDRIVE_SERVICE_ACCOUNT_JSON}"
: "${FOLDER_ID:?Missing FOLDER_ID}"

# -----
# 1) Check rclone exists
# -----
echo "Checking rclone..."
which rclone
rclone version

# -----
# 2) Write service account JSON safely
# -----
RCLONE_DIR="/root/.config/rclone"
mkdir -p "${RCLONE_DIR}"

echo "Writing service account JSON..."
printf "%s" "${GDRIVE_SERVICE_ACCOUNT_JSON}" > "${RCLONE_DIR}/sa.json"

# Validate JSON
python - <<'PY'
import json
json.load(open("/root/.config/rclone/sa.json"))
print("Service account JSON is valid")
PY

# -----
# 3) Write rclone config
# -----
cat > "${RCLONE_DIR}/rclone.conf" <<EOF
[gdrive]
type = drive
scope = drive
service_account_file = ${RCLONE_DIR}/sa.json
root_folder_id = ${FOLDER_ID}
EOF

echo "rclone config written"

# -----
# 4) Create a fake test file
# -----
echo "Creating test file..."
echo "hello from railway test run" > /app/test_upload.txt

# -----
# 5) Upload test file
# -----
echo "Uploading test file to Google Drive..."
rclone copy /app/test_upload.txt gdrive:test_run --progress

echo "=== TEST RUN COMPLETE ==="