#!/usr/bin/env bash
# setup-ca.sh — export the macOS trust store into ./ca-bundle.pem so that
# NODE_EXTRA_CA_CERTS can give Node the same chain that curl/Safari use.
#
# Why this exists:
#   Node 22+/25 on macOS does not consult the OS keychain for TLS validation
#   by default. For some public CA chains (e.g. Google Trust Services WE1 →
#   supabase.co), Node's bundled Mozilla CA list is insufficient and you get
#   UNABLE_TO_GET_ISSUER_CERT_LOCALLY even though curl/Safari work fine.
#   --use-system-ca was insufficient on Node 25.9 + macOS in our test, so
#   the reliable fix is exporting the keychain to a PEM and pointing
#   NODE_EXTRA_CA_CERTS at it.
#
# Usage:
#   ./scripts/setup-ca.sh                # writes ./ca-bundle.pem
#   ./scripts/setup-ca.sh /tmp/foo.pem   # custom output path
#
# Re-run any time IT pushes new corporate roots.

set -euo pipefail

OUT="${1:-./ca-bundle.pem}"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "setup-ca.sh: macOS only. On Linux, set:" >&2
  echo "  NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt" >&2
  echo "On Windows, configure certificates via Node's --use-system-ca flag." >&2
  exit 1
fi

{
  security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain 2>/dev/null || true
  security find-certificate -a -p /Library/Keychains/System.keychain 2>/dev/null || true
  security find-certificate -a -p "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null || true
} > "$OUT"

count=$(grep -c "BEGIN CERTIFICATE" "$OUT" || echo 0)
echo "✅ Wrote $count certificates to $OUT"
echo "   (re-run this script whenever the system trust store changes)"
