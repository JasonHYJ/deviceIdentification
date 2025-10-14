#!/usr/bin/env bash
set -euo pipefail

# Detect paths no matter where this script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PY=python3

# helper: copy cache or run command
sync_or_run () {
  local cache_dir="$1"; shift
  local out_dir="$1"; shift
  if [ -d "$cache_dir" ] && [ -n "$(ls -A "$cache_dir" 2>/dev/null)" ]; then
    echo "[Use cached] $cache_dir -> $out_dir"
    mkdir -p "$out_dir"
    rsync -a --delete "$cache_dir"/ "$out_dir"/
  else
    echo "[Run] $*"
    (cd "$REPO_ROOT" && "$@")
  fi
}

echo "[INFO] prepare output roots"
mkdir -p \
  "$REPO_ROOT/artifact/outputs/period" \
  "$REPO_ROOT/artifact/outputs/preproc" \
  "$REPO_ROOT/artifact/outputs/signatures" \
  "$REPO_ROOT/artifact/outputs/merged_signatures" \
  "$REPO_ROOT/artifact/outputs/eval"

########################################
# Phase 1: PeriodProcess
########################################
sync_or_run \
  "$REPO_ROOT/artifact/data/cached/period/3_selectDir" \
  "$REPO_ROOT/artifact/outputs/period/3_selectDir" \
  $PY artifact/PeriodProcess/1.1_process_pcap_sessions.py

sync_or_run \
  "$REPO_ROOT/artifact/data/cached/period/3_selectDir" \
  "$REPO_ROOT/artifact/outputs/period/3_selectDir" \
  $PY artifact/PeriodProcess/1.2_select_max_pcap_session.py

sync_or_run \
  "$REPO_ROOT/artifact/data/cached/period/3_selectDir" \
  "$REPO_ROOT/artifact/outputs/period/3_selectDir" \
  $PY artifact/PeriodProcess/1.3_periodic_pcap_processing.py

########################################
# Phase 2: preProcess
########################################
sync_or_run \
  "$REPO_ROOT/artifact/data/cached/preproc/12_featureClusterFilter" \
  "$REPO_ROOT/artifact/outputs/preproc/12_featureClusterFilter" \
  bash -lc "
    cd '$REPO_ROOT' && \
    $PY artifact/preProcess/2.1_filter_sessions_by_sample_count.py && \
    $PY artifact/preProcess/2.2_record_period_data.py && \
    $PY artifact/preProcess/2.3_extract_pcap_features_muti_workers.py && \
    $PY artifact/preProcess/2.4_add_time_interval_to_csv.py && \
    $PY artifact/preProcess/2.5_copy_and_filter_csv.py && \
    $PY artifact/preProcess/2.6_select_random_csv_files.py && \
    $PY artifact/preProcess/2.7_extract_features_from_csv.py && \
    $PY artifact/preProcess/2.8_merge_session_csv_files.py && \
    $PY artifact/preProcess/2.9_cluster_csv_samples.py && \
    $PY artifact/preProcess/2.10_filter_and_copy_csv_files.py
  "

########################################
# Phase 3: SignatureGeneration
########################################
sync_or_run \
  "$REPO_ROOT/artifact/data/cached/signatures/16_keyPacketSignatureWithLSH" \
  "$REPO_ROOT/artifact/outputs/signatures/16_keyPacketSignatureWithLSH" \
  bash -lc "
    cd '$REPO_ROOT' && \
    $PY artifact/SignatureGeneration/3.1_key_packet_statistics.py && \
    $PY artifact/SignatureGeneration/3.2_merge_key_packet_statistics.py && \
    $PY artifact/SignatureGeneration/3.3_update_csv_with_selected_period.py && \
    $PY artifact/SignatureGeneration/3.4_extract_key_packet_signatures.py && \
    $PY artifact/SignatureGeneration/3.5_process_payload_lsh.py
  "

########################################
# Phase 4: Signature Merging (optional)
########################################
if [ -d "$REPO_ROOT/artifact/data/cached/merged_signatures/17_signatureMerge" ] && \
   [ -n "$(ls -A "$REPO_ROOT/artifact/data/cached/merged_signatures/17_signatureMerge" 2>/dev/null)" ]; then
  echo "[Use cached] merged signatures"
  mkdir -p "$REPO_ROOT/artifact/outputs/merged_signatures/17_signatureMerge"
  rsync -a --delete \
    "$REPO_ROOT/artifact/data/cached/merged_signatures/17_signatureMerge"/ \
    "$REPO_ROOT/artifact/outputs/merged_signatures/17_signatureMerge"/
elif [ -f "$REPO_ROOT/artifact/signatureMatching/4.1_merge_device_signatures.py" ]; then
  echo "[Run] signature merge"
  (cd "$REPO_ROOT" && $PY artifact/signatureMatching/4.1_merge_device_signatures.py)
else
  echo "[Skip] no signature merge script"
fi

echo "[OK] Demo finished. See $REPO_ROOT/artifact/outputs/"
