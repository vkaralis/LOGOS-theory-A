"""Verify the source archive's tracked content hashes."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
entries=json.loads((root/'MANIFEST_SHA256.json').read_text())
failed=[name for name,digest in entries.items() if not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest]
if failed:raise SystemExit('Changed or missing files: '+', '.join(failed))
print(f'All {len(entries)} source hashes verified.')
