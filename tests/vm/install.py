#!/usr/bin/env python3
"""Guest-only acceptance harness. Never enabled in the distributed live profile.

Attach a blank disk with serial 'pond-vm-test' and a read-only 9p 'pondtest' share
containing this script plus vm-test.pub. Run as root in the booted installer ISO.
The installer downloads and verifies its configured public release normally.
"""
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, '/usr/share/pond-installer')
import backend
from backend import storage
from backend.model import ROOT_TYPE

assert os.geteuid() == 0
assert Path('/etc/pond-installer-live').is_file()
assert subprocess.check_output(['lsblk', '-dn', '-o', 'SERIAL', '/dev/vda'], text=True).strip() == 'pond-vm-test'
disk = next(disk for disk in storage.probe() if disk.path == '/dev/vda')
assert not disk.partitions and not disk.busy, 'Only a blank test disk is accepted'
plan = backend.plan_install(disk, backend.Mode.REPLACE, boot_mode=backend.current_boot_mode())
profile = backend.Profile(username='pondtest', password='Pond-VM-Test-Only-1', hostname='pond-vm-test')
backend.install(plan, profile, progress=lambda value: print(f'INSTALL_PROGRESS {value}', flush=True))
print('INSTALL_SUCCEEDED', flush=True)
# Test transport only: enable key-authenticated SSH on the disposable installed disk
# so the host can inspect the running system. No test key goes into the release rootfs.
rootpart = next(p for d in storage.probe() if d.path == '/dev/vda' for p in d.partitions if p.kind == ROOT_TYPE)
mount = Path('/mnt/pond-vm-inspect')
mount.mkdir(exist_ok=True)
subprocess.run(['mount', '-o', 'subvol=@', rootpart.path, str(mount)], check=True)
try:
    subprocess.run(['mount', '-o', 'subvol=@home', rootpart.path, str(mount / 'home')], check=True)
    ssh = mount / 'home/pondtest/.ssh'
    ssh.mkdir(mode=0o700, exist_ok=True)
    (ssh / 'authorized_keys').write_bytes((Path(__file__).parent / 'vm-test.pub').read_bytes())
    (ssh / 'authorized_keys').chmod(0o600)
    subprocess.run(['arch-chroot', str(mount), 'chown', '-R', 'pondtest:pondtest', '/home/pondtest/.ssh'], check=True)
    subprocess.run(['arch-chroot', str(mount), 'systemctl', 'enable', 'sshd'], check=True)
    # QEMU user networking reaches the guest from this address. The base image
    # enables UFW; keep it enabled and permit SSH only from the test host.
    # Write the persistent rule offline, then restore the original enabled
    # state. Reloading a firewall inside this chroot targets the live kernel.
    ufw_conf = mount / 'etc/ufw/ufw.conf'
    original = ufw_conf.read_text()
    try:
        ufw_conf.write_text(original.replace('ENABLED=yes', 'ENABLED=no'))
        subprocess.run(['arch-chroot', str(mount), 'ufw', 'allow', 'from', '10.0.2.2',
                        'to', 'any', 'port', '22', 'proto', 'tcp'], check=True)
    finally:
        ufw_conf.write_text(original)
finally:
    subprocess.run(['umount', str(mount / 'home')], check=True)
    subprocess.run(['umount', str(mount)], check=True)
print('VM_TEST_TRANSPORT_READY', flush=True)
