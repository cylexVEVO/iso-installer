#!/usr/bin/env python3
"""Pin a published, immutable rootfs manifest into the installer source."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from backend.model import load_rootfs_manifest
source = Path(sys.argv[1])
sha256, urls = load_rootfs_manifest(source)
destination = Path(__file__).resolve().parents[1] / 'src/backend/assets/rootfs.json'
destination.write_text(json.dumps({'sha256': sha256, 'urls': urls}, indent=2) + '\n')
print(f'Pinned {sha256} from {len(urls)} download part(s)')
