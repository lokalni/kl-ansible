Teleklasa.lokalni.pl Ansible
============================

This repository provides bbb endpoints provisioning

Rules
=====

* One main.yml entrypoint which handles all bbb hosts configuration
* Keep most of generic config in group_vars
* Use hosts file variables to provide region, sponsor name and url (prevent creating multiple host_vars for each server)

