# Changelog

## v1.1.0

### Added

- new flag `pve_ceph_clear_all_osds` to wipe all as OSD marked disks in an initial run, to avoid conflicts in case the disks come from another Ceph-cluster
- new ZFS-implementation to create also ZFS-pools and attach them to the proxmox-ve
- new Vagrant-file to test single-node installation with ZFS-storage
- new configs to enable and configure an automatic detection of additional devices, which should be used as Ceph-OSD's, so they have not configured manually one by one
- offload rbd mirror-journal into a separate pool and added optional `pve_rbd_journal_migration` to migrate existing mirror-journals into this new pool
- new optional tasks to backup all virtual machines at the start of the role to prevent dataloss in case of a broken ansible run

### Fixed

- rbd-mirroring was fixed for newer Ansible-versions

## v1.0.0

New initial version of this fork of the original role https://github.com/lae/ansible-role-proxmox with a bunch of updates, especially in context of the Ceph-storage.
