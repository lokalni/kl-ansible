Teleklasa.lokalni.pl Ansible
============================

This repository provides bbb endpoints provisioning

Rules
=====

* One main.yml entrypoint which handles all bbb hosts configuration
* Keep most of generic config in group_vars
* Use hosts file variables to provide region, sponsor name and url (prevent creating multiple host_vars for each server) - to maintain single-point-of-knowledge file
* Hosts is also our secret store so keep it encrypted

Roles
=====
* bbb - Install BigBlueButton instance with letsencrypt and coturn
* bbb_customize - Customize BigBlueButton settings (remove default presentation and replace it with blank pdf which will act as a whiteboard, add sponsor info in welcome message, remove BBB landing page from /)
* common - System common config (ssh keys, firewall, etc.)
* heartbeat_daemon - landing page hartbeat daemon which registers instance in landing page system.
* local_cf_update_hosts - role that locally executes cloudflare api dns update to populate it from ansible hosts+ansible_ssh_host

Additional stuff
================
* misc - directory for all non-ansible stuff (scripts)
