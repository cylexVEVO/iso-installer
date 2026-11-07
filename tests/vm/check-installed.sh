#!/usr/bin/env bash
# Run as the VM's freshly installed user after logging into the graphical session.
set -euo pipefail
[[ $(hostname) == pond-vm-test ]]
[[ $(pacman-conf --repo-list | head -1) == pond-custom ]]
for package in pond-shell pond-lockscreen pond-wallpaper pond-screenshot pond-grub-config pond-plymouth-theme pond-launcher pond-pm pond-pm-extension; do
  [[ $(pacman -Q "$package") == "$package 1:"* ]]
  [[ $(pacman -Si "$package" | awk '/^Repository/{print $3;exit}') == pond-custom ]]
done
systemctl --user is-active vicinae.service
pgrep -u "$UID" -x niri
pgrep -u "$UID" -a -f 'qs -c pond-shell'
vicinae ping
vicinae cmd ls | tee /tmp/pond-vm-commands.txt
grep -E '(pond-pm-extension|pm-extension).*install' /tmp/pond-vm-commands.txt
helium-browser --version
python3 - <<'PY'
import json
from pathlib import Path
base=Path.home()/'.config'
assert json.loads((base/'pond-interface/theme.json').read_text())['theme']=='north'
wallpaper=json.loads((base/'pond-interface/wallpaper.json').read_text())
assert wallpaper['mode']=='custom'
assert wallpaper['path']=='/usr/share/pond-interface/wallpaper/included/ales krivec.jpg'
assert Path(wallpaper['path']).is_file()
assert json.loads((base/'vicinae/settings.json').read_text())['theme']['dark']['name']=='pond-north'
print('Installed user defaults match the requested configuration')
PY
printf 'INSTALLED_SYSTEM_CHECKS_PASSED\n'
