# ldifconvert and ldifsync
- **ldifconvert:** convert ldifs according to rules in a config file
in order to populate a target system with the modified user data

- **ldifsync:** produces an incremental ldif for writing deltas to a target system

- Just copy the example directory and change the Makefile .. enjoy!

## ldifconvert:
`ldifconvert.py <configfile>`
(see example)

## ldifsync:
takes two input files (source, target) and generates an input file for ldapmodify
(part of the openldap suite)
`ldifsync.py <source-ldif> <target-ldif>`
(see example)

## Installation
- Prerequisites:
  - [python-ldap](https://www.python-ldap.org/) (only the ldif modulue is used here)
  - [openldap](http://www.openldap.org/)

## remarks
- using make
Make is truly old, but in this case it proves to be quite handy
as in case of failures it does all the exception handing for us.
