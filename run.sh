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
# 3) Define sync function
# -------------------------
DRIVE_ROOT="gdrive:outputs_jan_2026"
OPENAI_DIR="/app/output_csvs_openai"
ANTHROPIC_DIR="/app/output_csvs_anthropic"
MISTRAL_DIR="/app/output_csvs_mistral"
SYNC_INTERVAL="${SYNC_INTERVAL:-300}"  # Default: sync every 5 minutes

sync_to_drive() {
    echo "[$(date)] Syncing to Google Drive..."
    [ -d "${OPENAI_DIR}" ] && rclone copy "${OPENAI_DIR}" "${DRIVE_ROOT}/openai" --quiet
    [ -d "${ANTHROPIC_DIR}" ] && rclone copy "${ANTHROPIC_DIR}" "${DRIVE_ROOT}/anthropic" --quiet
    [ -d "${MISTRAL_DIR}" ] && rclone copy "${MISTRAL_DIR}" "${DRIVE_ROOT}/mistral" --quiet
    echo "[$(date)] Sync complete."
}

# -------------------------
# 4) Start background sync
# -------------------------
echo "Starting background sync (every ${SYNC_INTERVAL}s)..."
(
    while true; do
        sleep "${SYNC_INTERVAL}"
        sync_to_drive
    done
) &
SYNC_PID=$!
echo "Background sync PID: ${SYNC_PID}"

# -------------------------
# 5) Run pipeline
# -------------------------
echo "Running pipeline..."
python main.py
PIPELINE_EXIT=$?
echo "Pipeline finished with exit code: ${PIPELINE_EXIT}"

# -------------------------
# 6) Stop background sync
# -------------------------
echo "Stopping background sync..."
kill "${SYNC_PID}" 2>/dev/null || true

# -------------------------
# 7) Final upload to Google Drive
# -------------------------
echo "Final sync to Google Drive..."
sync_to_drive

# upload main.py and logs
[ -f "/app/main.py" ] && rclone copy "/app/main.py" "${DRIVE_ROOT}/" --quiet
[ -f "/app/llm_processing.log" ] && rclone copy "/app/llm_processing.log" "${DRIVE_ROOT}/" --quiet

echo "=== UPLOAD COMPLETE ==="
echo "Drive folder: outputs_jan_2026"

exit ${PIPELINE_EXIT}