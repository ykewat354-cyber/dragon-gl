#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABI="${1:-arm64-v8a}"
SO="${2:-$ROOT/build/libmobileglues.so}"
VERSION="${DRAGONGL_VERSION:-2.0.0-dragon.1}"
OUT="$ROOT/DragonGL-$VERSION.aar"

if [[ ! -f "$SO" ]]; then
    echo "missing $SO" >&2
    exit 1
fi

rm -rf "$ROOT/aar"
cp -a "$ROOT/aar-template" "$ROOT/aar"
mkdir -p "$ROOT/aar/jni/$ABI" "$ROOT/aar/assets/licenses"
cp "$SO" "$ROOT/aar/jni/$ABI/libmobileglues.so"
cp "$ROOT/LICENSE" "$ROOT/aar/assets/licenses/mobileglues-lgplv2.1-license.txt"
: > "$ROOT/aar/R.txt"

EMPTY_JAR_DIR="$(mktemp -d)"
trap 'rm -rf "$EMPTY_JAR_DIR"' EXIT
printf 'DragonGL\n' > "$EMPTY_JAR_DIR/README.txt"
(cd "$EMPTY_JAR_DIR" && zip -q -r "$ROOT/aar/classes.jar" .)

(cd "$ROOT/aar" && zip -q -r "$OUT" .)
echo "wrote $OUT"
unzip -l "$OUT"
