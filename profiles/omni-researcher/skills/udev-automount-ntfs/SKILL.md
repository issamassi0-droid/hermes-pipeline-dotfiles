---
name: udev-automount-ntfs
description: Automount NTFS USB via udev/udisks2, ntfs-3g, group access.
---

Use when you need to automatically mount NTFS USB storage devices with the user‑space ntfs-3g driver, giving read/write access to a designated Unix group without editing /etc/fstab.

## Why

The kernel’s built‑in ntfs3 driver is read‑only on many distros and does not support all NTFS features. Using udisks2 with a udev rule lets you:

* Force the use of ntfs-3g (the FUSE helper) for full read/write support.
* Set ownership/mode of the mount point via a udev rule.
* Allow any user in a chosen group (e.g. plugdev) to mount/unmount without sudo.
* Work on any desktop environment that relies on udisks2 (GNOME, KDE, Xfce, etc.) and also on headless sessions via `udisysctl`.

## Prerequisites

* `ntfs-3g` package installed (provides `/usr/bin/mount.ntfs-3g`).
* `udisks2` daemon running (enabled by default on most desktop installs).
* A Unix group that will be granted access (e.g. `plugdev`). Create it if missing:
 ```bash
 sudo groupadd -f plugdev
 ```

## Step‑by‑step

1. **Create the udev rule**
 Save the following as `/etc/udev/rules.d/99-ntfs-automount.rules`:
 ```udev
 # 99-ntfs-automount.rules
 # Automatically mount NTFS removable block devices with ntfs-3g.
 # Gives read/write access to the "plugdev" group.

 KERNEL=="sd*[0-9]", SUBSYSTEM=="block", ENV{ID_FS_TYPE}=="ntfs", \
 ENV{UDISKS_IGNORE}="0", \
 TAG+="systemd", ENV{SYSTEMD_WANTS}="udisks2.service", \
 ENV{UDISKS_FILESYSTEM}="ntfs-3g", \
 ENV{UDISKS_AUTO}="1", \
 MODE="0660", GROUP="plugdev"
 ```

 *Notes* 
 - `ENV{UDISKS_FILESYSTEM}` tells udisks2 which helper to use. 
 - `ENV{UDISKS_AUTO}` requests an automatic mount when a user session is active. 
 - `MODE="0660", GROUP="plugdev"` makes the mount point readable/writable by the group.

2. **Reload udev**
 ```bash
 sudo udevadm control --reload-rules
 sudo udevadm trigger # apply to already‑present devices
 ```

3. **Add users to the group**
 ```bash
 sudo gpasswd -a <username> plugdev
 newgrp plugdev # or log out/in
 ```

4. **Verify the rule** (after plugging in the NTFS stick):
 ```bash
 udevadm info --query=property --name=/dev/sdX1 | grep -E 'UDISKS_FILESYSTEM|UDISKS_IGNORE|UDISKS_AUTO'
 ```
 Expected output:
 ```
 UDISKS_FILESYSTEM=ntfs-3g
 UDISKS_IGNORE=0
 UDISKS_AUTO=1
 ```

5. **Mount** (optional manual step)
 As a regular user:
 ```bash
 udisysctl mount -b /dev/sdX1
 ```
 To unmount:
 ```bash
 udisysctl unmount -b /dev/sdX1
 ```

6. **Check that the correct driver is used**
 After mounting, verify:
 ```bash
 grep ntfs /proc/mounts | grep "$(blkid -s UUID -o value /dev/sdX1)"
 ```
 You should see `type ntfs-3g` (or `fuseblk`).

## Pitfalls & Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `udisysctl mount …` prints only usage | Alias or function hiding the real binary, or malformed option | Run `type udisysctl` and `which udisysctl` to confirm you’re calling `/usr/bin/udisysctl`. Remove any conflicting alias. |
| `Not authorized to perform operation` | User not in the `plugdev` group or a polkit rule denying the action | Ensure you’re in the group (`sudo gpasswd -a $USER plugdev`), then relogin. Check `/usr/share/polkit-1/actions/org.freedesktop.udisks2.policy` if you have custom restrictions. |
| `Requested filesystem type 'ntfs-3g' is neither well-known …` | You are still passing `-t ntfs-3g` on the command line **and** `/etc/filesystems` lacks the entry | Either remove the `-t` flag (rely on the udev rule) **or** add `ntfs-3g` to `/etc/filesystems` (`echo "ntfs-3g" | sudo tee -a /etc/filesystems`). |
| Permission denied when writing to the mount point | Wrong mode/group on the mount point | Verify the rule contains `MODE="0660", GROUP="plugdev"` (or your chosen group) and that you are a member of that group. Reload udev and remount. |
| Device never shows as NTFS in `lsblk -f` | The stick isn’t actually NTFS, or the kernel didn’t read the FS before udev ran | Run `sudo blkid -p /dev/sdX1` to see what the kernel thinks. If it truly is NTFS, ensure the rule matches `ENV{ID_FS_TYPE}=="ntfs"` (you can broaden it to `*ntfs*` if needed, but the exact match usually works). |
| Automount does not happen on a headless login | `UDISKS_AUTO` only works when an active user session is present | Either start a desktop session, or rely on manual mounting with `udisysctl`. For headless automation, consider a systemd user service that runs on login and calls `udisysctl monitor`. |

## References

* `udisysctl` man page – `man udisysctl`
* `udev` man page – `man udev`
* NTFS‑3g project: https://github.com/torvalds/linux/tree/master/fs/ntfs3 (kernel) and https://github.com/tuxera/ntfs-3g (userspace)
