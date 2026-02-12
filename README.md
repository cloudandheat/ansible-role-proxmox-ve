# ansible-role-proxmox-ve

Installs and configures **P**roxmox **V**irtual **E**nvironment 8.x/9.x on Debian servers with Ceph as storage backend.

This repository is a fork of https://github.com/lae/ansible-role-proxmox . The [original Readme](README_old.md) still exist, but was replaced by this one here, because of the amount of changes at this repository.

## Requirements

- Multi-node setup with Ceph storage:
    - 3 (virtual-) machines with Debian 12 for PVE 8 or Debian 13 for PVE 9 
    - at least 2 additional storage devices per node for the Ceph OSDs
- Single-node setup with ZFS storage:
    - 1 (virtual-) machine with Debian 12 for PVE 8 or Debian 13 for PVE 9 
    - at least 2 additional storage devices for the ZFS storage
- ssh-access to these nodes
- internal network between the nodes for synchronization

See for further information: https://www.proxmox.com/en/products/proxmox-virtual-environment/requirements

## Install

- install dependency

    ```bash
    mkdir roles
    cd roles
    git clone https://github.com/cloudandheat/ansible-role-proxmox-ve.git
    ```

- create inventory

    As template the test-inventory `tests/vagrant/inventory` can be used and modified for an initial setup. There is additional documentation for the single config-parameters in the defaults `defaults/main.yml`.

- create playbook, which uses the proxmox-ve role. For example with:

    ```yaml
    ---
    - hosts:
        - pve-test
    become: yes
    any_errors_fatal: true
    tasks:
      - name: Install chrony
        apt:
          name: chrony
          state: present
          update_cache: yes
        tags:
          - chrony

      - ansible.builtin.import_role:
          name: proxmox-ve
        tags:
          - pve
    ```

*IMPORTANT*: under `hosts` is a host-GROUP, not a single-host!

## Basic configuration

The following sections are example references for configuration. Further details and more options can be read in the defaults `defaults/main.yml`. 

### Debian version

- for Debian 12 with PVE 8

    ```yaml
    pve_debian_version: "bookworm"
    ```

- for Debian 12 with PVE 9

    ```yaml
    pve_debian_version: "trixie"
    ```

### Ceph storage for multi-node installation

#### General example

```yaml
pve_ceph_enhanced_enabled: true

pve_ceph_osds: 
  - hosts: [ "pve1-1", "pve1-2", "pve1-3" ]
    device: "/dev/vdb"
    encrypted: true
  - hosts: [ "pve1-1", "pve1-2", "pve1-3" ]
    device: "/dev/vdc"
    encrypted: true
  - hosts: [ "pve1-1", "pve1-2", "pve1-3" ]
    device: "/dev/vdd"
    encrypted: true

pve_pools:
  - poolid: test_pool
    comment: "testing it"
    storage:
      - test-ceph-storage
      - test-cephfs-storage

pve_storages:
  - storage: test-ceph-storage
    type: rbd 
    pool: test-ceph
    content:
      - images
      - rootdir
  - storage: test-cephfs-storage
    type: cephfs 
    fs-name: test-cephfs
    content:
      - backup
      - iso
      - vztmpl
      - snippets

pve_ceph_pools:
  - name: test-ceph 
    quota: 3 
    add_storages: false
    target_size: 3 
    pg_autoscale_mode: "on"

pve_ceph_fs:
  - name: test-cephfs
    pools:
      quota: 10
      pg_autoscale_mode: "on"
    meta_pool:
      pg_autoscale_mode: "on"
```

#### Additional options

1. clear all OSDs

    Set `pve_ceph_clear_all_osds: true` to wipe all OSD disk in the initial deploy process. This in necessary in case the disks come from an older or another Ceph. To avoid conflicts, with this flag the header of the disks will be deleted to ensure an clean Ceph installation. This in only done in an initial installation. When Ceph is already installed, the flag is ignored.

2. detect disks for OSDs

    Instead of defining all disks manually, it is also possible to automatically detect all non-root disks and use them as OSDs for ceph. Add:
    
    ```yaml
    pve_ceph_osd_detection:
      enabled: true
      only_nvme: true
      encrypted: true
    ```

    - `enabled` enables the feature
    - `only_nvme` uses only NVMs-SSDs for the OSDs
    - `encrypted` define all as encrypted OSDs

    The option `pve_ceph_osds` must be removed from the inventory in case the detection is enabled. 

3. journal migration

    The mirror-journal in now located in a separate ceph pool. It is possible to also migrate old journals into the new separeted structure, but this requires to set `pve_rbd_journal_migration` to true. This option is per default false, because the mirroring is canceled for the migration and triggered again after the change and so this migration should always be done on purpose when the admin is aware and prepared for this to avoid dataloss.

### ZFS storage for single-node installation

```yaml
pve_zfs_enabled: true

pve_pools:
  - poolid: test_pool
    comment: "testing it"
    storage:
      - zfs-storage

pve_storages:
  - storage: zfs-storage
    type: zfspool
    pool: zfs-pool
    content:
      - rootdir
      - images

pve_zfs_disks:
  - /dev/vdb
  - /dev/vdc
  - /dev/vdd
```

### Backup-server

To attach a Proxmox-Backup-Server, a block like the following can be added:

```yaml
  - storage: "pbs_ansible"
    type: "pbs"
    username: "backupuser@pbs"
    server: "192.168.121.42"
    datastore: "teststore"
    content: "backup"
    fingerprint: "cc:eb:98:25:34:6e:b8:13:d8:e4:5e:da:a7:f9:82:41:fb:7f:6a:bd:25:4e:7d:9a:a8:2a:cc:22:01:cb:90:d7"
    password: "asdfasdf"
    encryption-key: '{"kdf":null,"created":"2025-10-29T15:32:02+01:00","modified":"2025-10-29T15:32:02+01:00","data":"dGVzdC1rZXk=","fingerprint":"e7:93:02:00:5f:0c:57:dc:51:c3:a7:ac:8c:dd:c0:84:9d:01:de:8c:13:4c:06:4f:95:ff:e7:f2:1d:11:08:6c"}'

pve_pbs_encryption_keys_preserve:
  enabled: true
```

`datastore`, `username`, `fingerprint` and `password` coming from the backup-server. The encryption parameter are optional.

## Usage

### Access WebUI

call `https://SERVER_IP:8006` in your browser

As `SERVER_IP` the IP of each of the provisioned nodes can be used

### Login

Initial login with user-name and password of the root-user of the Debian under the proxmox-ve.

## Vagrant test setup

In order to make tests, especially with different Debian version, faster and more easy, there is a vagrant script available to deploy a local test environment of 3 virtual nodes with 3 OSDs per node and runs the ansible role within them.

There are no custom configurations necessary. The example inventories in `tests/vagrant` are used for the setup and doesn't require any modifications.

The Vagrant installation was tested with Debian 12 and 13 and uses 13 as default at the moment. To roll out the Debian 12 version, just change the image-version at the top of the Vagrantfile and in the test-inventory replace the the repository-config by the out-commented Debian 12 config.

### Installation

This installation uses Vagrant with libvirt as provider to deploy the virtual machines.

- install vagrant

    see: https://developer.hashicorp.com/vagrant/install#linux

- Install apt-packages necessary for libvirt and the libvirt-provider

    ```bash
    sudo apt update
    sudo apt install -y \
        make \
        python3 \
        gcc \
        qemu-kvm \
        libvirt-dev \
        libvirt-daemon-system
    ```

- Enable and start libvirt:

    ```bash
    sudo systemctl enable --now libvirtd
    ```

- So you don’t need sudo every time

    ```bash
    sudo usermod -aG libvirt,kvm $USER
    ```

    (after this logout and login again)

- Install the libvirt provider plugin

    ```bash
    vagrant plugin install vagrant-libvirt
    ```

- Install local ansible required to execute the playbook

  - via apt:

    ```bash
    sudo apt-get install ansible python3-jmespath python3-netaddr
    ```

  - or via pip

    ```bash
    sudo apt-get install python3.12-venv pip3
    python3 -m venv venv
    source venv/bin/activate
    pip3 install ansible jmespath netaddr
    ```

### Usage

In case you want to test custom configurations in the vagrant-setup, you have to add your desired changes in `tests/vagrant/` to `inventory_ceph_multi_node`, `inventory_ceph_multi_node_mirror` or `inventory_zfs_single_node`. 

Select the desired vagrantfile based on your desired setup. 

To tests a 3-node setup with Ceph storage use:

`export VAGRANT_VAGRANTFILE=Vagrantfile_ceph_multi_node`

To tests 2 mirrored proxmox-installations, with 3-node and Ceph storage each, use:

`export VAGRANT_VAGRANTFILE=Vagrantfile_ceph_multi_node_mirror`

To test a single node with a ZFS storage use:

`export VAGRANT_VAGRANTFILE=Vagrantfile_zfs_single_node`

Vagrant-actions:

- start a complete new installation

    `vagrant up`

- in case a run failed and you want to run it again or with updated playbooks against the same already existing vagrant environment

    `vagrant provision`

- ssh into one of the virtual machines

    `vagrant ssh pve1-3` 

- delete previous vagrant environment

    `vagrant destroy -f`

- access webui of the deployed proxmox by entering `https://10.10.111.11:8006` in your local browser. This address is defined in the Vagrantfile and points directly to the first instance. There is a pre-defined test admin user. Select the Realm `Proxmox VE authentication server` with username `adminuser` and password `asdfasdf` to login as this user. If you rolled out the vagrant setup on a remove system, like a VM in the cloud, then you can use an ssh-tunnel like `ssh -L 8006:10.10.111.11:8006 <USER>@<REMOTE_ADDRESS>` and then access the dashboard via `https://127.0.0.1:8006`.

### Add Proxmox-Backup-Server for testing

It is also possible to create a local Proxmox-Backup-Server and attach this to the Proxmox-VE installation in the Vagrant test-VMs.

HINT: The Vagrant-setup uses libvirt/KVM, so other hypervisor like Virtualbox doesn't work at the same time with the Vagrant VMs, so you have to use libvirt for this addtional PBS-VM too. To make this easier, the package `virt-manager` can be installed to get a minimal graphical GUI to create libvirt-VMs.

- Download a PBS image: https://www.proxmox.com/en/products/proxmox-backup-server/get-started

- Create a small VM in libvirt with the ISO-image and select the vagrant-network to place the new VM within this network too, to make the accessible by the Proxmox-VE in the Vagrant-VMs. Use a static IP-address.

- Run the normal installation in the GUI.

- Log into the PBS-VM over SSH from one of the Vangrant-VMs, because this makes the installation easier, than with the terminal of the virt-manager. The user within the PBS-VM for the ssh-login is `root`.

- Configure a basic setup within the PBS

    ```bash
    mkdir /mnt/backups/teststore
    mkdir -p /mnt/backups/teststore
    proxmox-backup-manager datastore create teststore /mnt/backups/teststore
    proxmox-backup-manager user create backupuser@pbs --password asdfasdf
    proxmox-backup-manager acl update /datastore/teststore DatastoreAdmin --auth-id backupuser@pbs
    proxmox-backup-manager cert info | grep Fingerprint
    ```

    For the configuration in the Proxmox-VE, you need the username `backupuser`, the password `asdfasdf`, the datastore-name `teststore` and the fingerprint of the last line.

- Configure PBS storage in Proxmox-VE based on the example-config for the PBS in the examples above. Set the necessary information for your setup. `server` has to be the IP-address of your PBS-server, where the Vagrant-VMs can reach it. The `encryption-key` is optional to encrypt the backups.

## Troubleshooting:

### Blank webui

Problem is the workaround to remove the subscription warning banner. Can be fixed afterwards by 
running `apt install --reinstall pve-manager proxmox-widget-toolkit libjs-extjs pve-cluster` on all nodes
or set in inventory `pve_remove_subscription_warning: false` to fix this right from the beginning

### hangs at `Query RBD pool config overrides`

Reason is that it has not OSDs found. Either there are not OSDs available or the inventory is not correct. For example in libvirt instances, like in the vagrant test setup, the OSDs have as path `vda`, `vdb`, ... instead of `sda`, `sdb`, ...

### create mds failed because host-name begins with number

In the rare case, that the hosts are using a number at the beginning of the name, the creation of the Ceph MDS failed, because it expects, that the name of the host starts with a letter. Instead of renaming the hosts, with a name-mapping this problem can be solved, because the names doesn't need to match the host-name. 

Example-config for this case:

```yaml
pve_ceph_mds_nodes:
  - hostname: 123-host
    name: mds-123-host
  - hostname: 124-host
    name: mds-124-host
  - hostname: 125-host
    name: mds-125-host
```
