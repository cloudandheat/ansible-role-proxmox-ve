# ansible-role-proxmox-ve

Installs and configures **P**roxmox **V**irtual **E**nvironment 8.x/9.x on Debian servers with Ceph as storage backend.

This repository is a fork of https://github.com/lae/ansible-role-proxmox . The [oritinal Readme](README_old.md) still exist, but was replaced by this one here, because of the amount of changes at this repository.

## Requirements

- 3 (virtual-) machines with Debian 12 for PVE 8 or Debian 13 for PVE 9 
- at least 2 ceph-osds per node
- ssh-access to these nodes
- internal network between the nodes for synchronization

## Install

- install dependency

    ```bash
    mkdir roles
    cd roles
    git clone https://github.com/cloudandheat/ansible-role-proxmox-ve.git
    cd ..

    ansible-galaxy install chrony
    ```

- create inventory

    As template the test-inventory `tests/vagrant/inventory` can be used and modified for an initial setup. There is additional documentation for the single config-parameters in the defaults `defaults/main.yml`.

- create install-playbook, which uses the proxmox-ve role. For example with:

    ```yaml
    #!/usr/bin/env -S ansible-playbook -i ./inventory
    ---
    - hosts:
        - pve-test
    become: yes
    any_errors_fatal: true
    tasks:

        - ansible.builtin.import_role:
            name: chrony
        tags:
            - chrony
            - never

        - ansible.builtin.import_role:
            name: proxmox-ve
        tags:
            - pve
    ```

*IMPORTANT*: under `hosts` is a host-GROUP, not a single-host!

## Usage

### Access WebUI

call `https://SERVER_IP:8006` in your browser

As `SERVER_IP` the IP of each of the provisioned nodes can be used

### Login

Initial login with user-name and password of the root-user of the Debian under the proxmox-ve.

## Vagrant test setup

In order to make tests, especially with different Debian version, faster and more easy, there is a vagrant script available to deploy a local test environment of 3 virtual nodes with 3 OSDs per node and runs the ansible role within them.

There are no custom configurations necessary. The example inventory `tests/vagrant/inventory` is used for the setup and doesn't require any modifications.

The Vagrant installation was tested with Debian 12 and 13 and uses 13 as default at the moment. To roll out the Debian 12 version, just change the image-version at the top of the `Vagrantfile` and in the test-inventory `tests/vagrant/inventory` replace the the repository-config by the out-commented Debian 12 config.

### Installation

This installation uses Vagrant with libvirt as provider to deploy the virtual machines.

- Install apt-packages necessary for libvirt and the libvirt-provider

    ```bash
    sudo apt update
    sudo apt install -y \
        qemu-kvm \
        libvirt-dev
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

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install ansible jmespath netaddr
    ```

### Usage

In case you want to test custom configurations in the vagrant-setup, you have to add your desired changes to `tests/vagrant/inventory`. 

Vagrant-actions:

- start a complete new installation

    `vagrant up`

- in case a run failed and you want to run it again or with updated playbooks against the same already existing vagrant environment

    `vagrant provision`

- ssh into one of the virtual machines

    `vagrant ssh pve1-3` 

- delete previous vagrant environment

    `vagrant destroy -f`

- access webui of the deployed proxmox by entering `https://10.10.111.11:8006` in your local browser. This address is defined in the Vagrantfile and points directly to the first instance. There is a pre-defined test admin user. Select the Realm `Proxmox VE authentication server` with username `adminuser` and password `asdfasdf` to login as this user.

## Troubleshooting:

### Blank webui

Problem is the workaround to remove the subscription warning banner. Can be fixed afterwards by 
running `apt install --reinstall pve-manager proxmox-widget-toolkit libjs-extjs pve-cluster` on all nodes
or set in inventory `pve_remove_subscription_warning: false` to fix this right from the beginning

### hangs at `Query RBD pool config overrides`

Reason is that it has not OSDs found. Either there are not OSDs available or the inventory is not correct. For example in libvirt instances, like in the vagrant test setup, the OSDs have as path `vda`, `vdb`, ... instead of `sda`, `sdb`, ...
