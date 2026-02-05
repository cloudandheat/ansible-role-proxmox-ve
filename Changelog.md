# Changelog

## [Unreleased]

### Added

- new flag `pve_ceph_clear_all_osds` to wipe all as OSD marked disks in an initial run, to avoid conflicts in case the disks come from another Ceph-cluster
- new ZFS-implementation to create also ZFS-pools and attach them to the proxmox-ve
- new Vagrant-file to test single-node installation with ZFS-storage

## v1.0.0

New initial version of this fork of the original role https://github.com/lae/ansible-role-proxmox with a bunch of updates, especially in context of the Ceph-storage.
