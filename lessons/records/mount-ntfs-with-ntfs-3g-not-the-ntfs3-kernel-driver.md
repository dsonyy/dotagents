---
title: "Mount NTFS with ntfs-3g, not the ntfs3 kernel driver"
tags: ["linux", "filesystem", "debugging"]
---

# Mount NTFS with ntfs-3g, not the ntfs3 kernel driver

**Context**: 2026-09-02. A shared Windows partition (`/dev/nvme0n1p4`, mounted at
`~/data`) was running on `ntfs3`, the in-kernel driver, because that is what udisks2 picks
automatically. After cloning 129 repositories onto it, `rm -rf` on one of those trees hung
for four minutes in `D+` state inside `vfs_unlink` with `utime=0 stime=0`, meaning it had
not executed a single instruction. `kill -9` does nothing to a process in uninterruptible
kernel sleep, so the only way out was a reboot. Switching `/etc/fstab` to `ntfs-3g` and
rebooting made the identical `rm` finish in 0.108 s, with no stuck processes.

**Problem**: every part of this setup is the default. udisks2 auto-mounts NTFS with `ntfs3`
and adds `acl`, which makes permissions derive from the volume's Windows security
descriptors instead of the mount options, so directories carrying `FILE_ATTRIBUTE_READONLY`
show up as `0555` no matter what `umask` says. Nothing warns about either. The deadlock
only appears under many-small-file workloads, so light use looks fine and the partition
seems healthy right up until it eats a reboot.

**Rule**: put `ntfs-3g` in `/etc/fstab` for any NTFS volume, and do not rely on the
automount. It is FUSE, so it is slower per syscall, but it does not deadlock the kernel and
a wedged FUSE daemon can be killed. Do not host git repositories or other many-small-file
work on NTFS at all; keep those on a Linux filesystem and use the NTFS volume for bulk data.
Mount options are not interchangeable between the two drivers: `iocharset` and `prealloc`
are `ntfs3`-only and will break an `ntfs-3g` mount, whose equivalents are `locale` and
nothing. Repositories cloned while the volume misbehaved keep a wrong cached
`core.filemode`, which survives fixing the mount and needs fixing per repository.

**Applies to**: every new machine with a Windows partition, external NTFS drives, and any
`D`-state process on a filesystem the kernel implements by reimplementing someone else's
format. `/etc/fstab` is not part of this repository, so nothing carries this automatically:
it has to be applied by hand on each new machine.
