#!/usr/bin/env bash
# bootstrap.sh — copy + customize a NestJS template (BCFT-006)
#
# Usage:
#   .be/scripts/bootstrap.sh <template_name> [target_dir]
#
# Examples:
#   .be/scripts/bootstrap.sh nestjs-base .          # Prisma + Postgres
#   .be/scripts/bootstrap.sh nestjs-supabase .      # Supabase JS Client
#
# Env vars (optional):
#   APP_NAME=my-api  → substituted in package.json

set -e

TEMPLATE="${1:?Usage: bootstrap.sh <template_name> [target_dir]}"
TARGET="${2:-.}"
TEMPLATES_DIR="${TEMPLATES_DIR:-.be/templates}"
APP_NAME="${APP_NAME:-becraft-app}"

TEMPLATE_PATH="$TEMPLATES_DIR/$TEMPLATE"

# Validate template exists
if [ ! -d "$TEMPLATE_PATH" ]; then
  echo "❌ Template not found: $TEMPLATE_PATH" >&2
  echo "   Available templates:" >&2
  ls -1 "$TEMPLATES_DIR" 2>/dev/null | sed 's/^/     - /' >&2 || echo "     (none)" >&2
  exit 1
fi

# Validate target dir exists
mkdir -p "$TARGET"

# Detect rsync vs cp -r
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude='node_modules' \
    --exclude='dist' \
    --exclude='coverage' \
    --exclude='.next' \
    "$TEMPLATE_PATH/" "$TARGET/"
else
  # Fallback: cp -r (less precise but works on minimal systems)
  cp -r "$TEMPLATE_PATH/." "$TARGET/"
fi

# Substitute placeholders
if [ -f "$TARGET/package.json" ]; then
  # Use perl (works on macOS + Linux) for portable in-place sed
  perl -pi -e "s/\\{\\{APP_NAME\\}\\}/$APP_NAME/g" "$TARGET/package.json"
fi

# Make scripts executable
find "$TARGET" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true

# Report
file_count=$(find "$TARGET" -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l | tr -d ' ')
echo "✅ Bootstrap complete from template '$TEMPLATE'"
echo "   Target: $TARGET"
echo "   Files copied: $file_count"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET"
echo "  2. cp .env.example .env  # Edit secrets"
echo "  3. npm install"
echo "  4. npm run start:dev"
