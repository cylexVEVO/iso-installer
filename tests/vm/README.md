# Disposable VM acceptance

`install.py` is a guest-only harness for the real installation library, including
its normal rootfs download, checksum verification, user creation, full upgrade,
hardware detection and boot setup. It accepts only a **blank `/dev/vda` disk with
serial `pond-vm-test`**, as root inside the installer live environment.

Give QEMU a fresh >=40 GiB virtual disk with that serial, UEFI firmware, network,
and a read-only 9p share named `pondtest` containing `install.py` and an ephemeral
SSH public key named `vm-test.pub`. Do not use a physical disk. Boot the ISO with
the test-only kernel argument `systemd.debug_shell=ttyS0` to obtain a root serial
shell, then run:

```sh
mkdir /run/pondtest
mount -t 9p -o trans=virtio,ro pondtest /run/pondtest
python /run/pondtest/install.py
```

The script installs a test user (`pondtest`, password `Pond-VM-Test-Only-1`) and,
after the installation completes, enables key-authenticated SSH **only on the
disposable test disk**. Neither the test user, debug shell, nor the SSH key is
included in the rootfs/ISO build. The debug kernel argument is for the live boot
only and is not part of the installed GRUB configuration.

Reboot from the disk, log in graphically, and run `check-installed.sh` as the test
user. Open the launcher package-manager command, confirm that its UI loads, and
launch Helium. Capture the desktop and extension as evidence. Repeat the script
after `sudo pacman -Syu` and another reboot. Also exercise a BIOS installation.
