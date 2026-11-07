## About

The focus of this ISO installer is to provide a straightforward & performant way to install Pond that works on any device.

It's 1.3GiB, and usually installs Pond in under a minute depending on your connection. The ISO and the installed system require at least 1GiB of RAM.

## Download

The download page is available on [Butterfly's website](https://butterfly.so/pond/install). The site always provides the latest tagged version.

## Performance

By keeping the ISO small, downloading and flashing it can be done quickly, and the rest of the installation and download can be done while the user configures the system.

An offline installer would require downloading dependencies that are not needed in the final system, then flashing them onto a USB drive. The time the user spends configuring the system and not waiting also gets wasted.

This architecture would allow us to further optimize final install time to ~10 seconds by doing all of the preparation & downloading in RAM while the user goes through the setup. The final operation would just be copying bytes from RAM to disk.

## Building

Build dependencies:

```sh
sudo pacman -S --needed archiso grub git make
```

From the repository root, run:

```sh
make check
make iso
```

Pond Gramercy is proprietary and is not included in this repository. You don't need it to build and test the ISO.
## Custom cylexVEVO image

The installed desktop is pinned by `src/backend/assets/rootfs.json`, which contains
ordered HTTPS download URLs and the SHA-256 of their concatenation. Downloads may
be split into GitHub Release assets; the complete archive is verified before extraction.

Build the signed replacement repository and target rootfs using
[cylexVEVO/pond-pkgbuilds](https://github.com/cylexVEVO/pond-pkgbuilds/tree/custom-pond/custom).
Then run `python3 scripts/use-rootfs.py /path/to/rootfs.json`, `make check`, and
`make iso VERSION=1.0.0`. `VERSION` labels the ISO; the manifest selects the desktop.
The target rootfs must carry its repository config, public signing key, packages,
and `/etc/skel` defaults. The live profile's pacman configuration does not configure
the installed system. The installer populates the custom keyring before upgrading.
