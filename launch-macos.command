#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
config_file="$script_dir/userdata.json"

if [[ ! -f "$config_file" ]]; then
  printf 'Missing configuration file: %s\n' "$config_file" >&2
  exit 1
fi

while IFS= read -r -d '' name && IFS= read -r -d '' value; do
  export "$name=$value"
done < <(
  python3 - "$config_file" <<'PY'
import json
import sys

required = ("TARGET", "CB_EVENTS_TOKEN", "CB_USERNAME", "CB_TITLE")

try:
    with open(sys.argv[1], encoding="utf-8") as config_file:
        config = json.load(config_file)
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit(f"Could not read userdata.json: {error}")

for name in required:
    value = config.get(name)
    if not isinstance(value, (str, int, float)) or value == "":
        raise SystemExit(f"userdata.json requires a non-empty {name}")
    sys.stdout.buffer.write(name.encode() + b"\0" + str(value).encode() + b"\0")
PY
)

python3 "$script_dir/server.py"
