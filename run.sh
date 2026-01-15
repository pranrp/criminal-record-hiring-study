#!/usr/bin/env bash
set -euo pipefail

echo "=== RAILWAY PIPELINE START ==="

# -------------------------
# 0) Sanity check
# -------------------------
: "${RCLONE_CONF:?Missing RCLONE_CONF environment variable}"

# -------------------------
# 1) Ensure rclone exists
# -------------------------
echo "Checking rclone..."
which rclone
rclone version

# -------------------------
# 2) Write rclone config
# -------------------------
mkdir -p /root/.config/rclone
printf "%s" "$RCLONE_CONF" > /root/.config/rclone/rclone.conf

# -------------------------
# 3) Run pipeline
# -------------------------
echo "Running pipeline..."
python main.py
echo "Pipeline finished."

# -------------------------
# 4) Upload outputs to Google Drive
# -------------------------
DRIVE_ROOT="gdrive:outputs_jan_2026"

OPENAI_DIR="/app/output_csvs_openai"
ANTHROPIC_DIR="/app/output_csvs_anthropic"
MISTRAL_DIR="/app/output_csvs_mistral"

echo "Uploading outputs under outputs_jan_2026/"

# upload folders
[ -d "${OPENAI_DIR}" ] && rclone copy "${OPENAI_DIR}" "${DRIVE_ROOT}/openai" --progress
[ -d "${ANTHROPIC_DIR}" ] && rclone copy "${ANTHROPIC_DIR}" "${DRIVE_ROOT}/anthropic" --progress
[ -d "${MISTRAL_DIR}" ] && rclone copy "${MISTRAL_DIR}" "${DRIVE_ROOT}/mistral" --progress

# upload main.py
if [ -f "/app/main.py" ]; then
  rclone copy "/app/main.py" "${DRIVE_ROOT}/" --progress
else
  echo "WARN: main.py not found, skipping."
fi

echo "=== UPLOAD COMPLETE ==="
echo "Drive folder: outputs_jan_2026"