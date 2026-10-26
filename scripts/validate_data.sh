#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 no está disponible. No se puede ejecutar la validación automática."
  exit 2
fi

readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly DATA_DIR="$REPO_ROOT/data"
readonly TEMPLATES_DIR="$REPO_ROOT/templates"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0

check_json() {
  local file="$1"
  if ! python3 -c "import json, sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$file" >/dev/null 2>&1; then
    echo -e "${RED}❌ JSON no válido:${NC} $file"
    errors=$((errors + 1))
    return 1
  else
    echo -e "${GREEN}✔ JSON válido:${NC} $file"
    return 0
  fi
}

check_structure() {
  local file="$1"
  local top_keys="$2"
  python3 - <<PY
import json
import sys

path = sys.argv[1]
expected_top = sys.argv[2].split(",")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, dict):
    print("ERROR: {} no es un JSON objeto de nivel superior".format(path))
    sys.exit(1)

missing = [k for k in expected_top if k not in data]
if missing:
    print("WARN: {} falta(n) clave(s) de nivel superior: {}".format(path, ", ".join(missing)))
else:
    print("OK: {} tiene las claves de nivel superior básicas".format(path))
PY
}

run_for_dir() {
  local dir="$1"
  shift
  if [ ! -d "$dir" ]; then
    echo -e "${YELLOW}⚠ No existe:${NC} $dir"
    return
  fi
  while IFS= read -r -d '' file; do
    check_json "$file"
  done < <(find "$dir" -type f -name "*.json" -print0)
}

echo "=== Validación de estructura de datos del repo ==="
echo ""

run_for_dir "$DATA_DIR"
run_for_dir "$TEMPLATES_DIR"

echo ""
echo "=== Resumen ==="
if [ "$errors" -eq 0 ]; then
  echo -e "${GREEN}Todo correcto: todos los JSON son sintácticamente válidos.${NC}"
else
  echo -e "${RED}Se encontraron $errors error(es) de JSON. Revisa los ficheros marcados.${NC}"
fi

exit "$errors"