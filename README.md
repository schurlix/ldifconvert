# ldifmangle and ldifdiff

- **ldifmangle:** mangle (i.e. convert) ldif files according to rules in a
config file maybe in order to populate a target system with the modified user
data.

- **ldifdiff:** produces an ldif suited as input for ldapmodify for writing deltas to a target system

- Just copy the example directory and change the Makefile .. enjoy!

## ldifmangle:
`ldifmangle.py <configfile>`
(see example)

## ldifdiff:
takes two input files (source, target resp. \<from\> and \<to\>) and generates an input file for ldapmodify
to stdout (ldapmodify is part of the openldap suite)
`ldifdiff.py <from-ldif> <to-ldif> > output.ldif` 
(see example)

## Installation
- Prerequisites:
  - [python-ldif3](https://pypi.org/project/ldif3/) (pip install ldif3)

## Optional, but likely
  - [openldap](http://www.openldap.org/)

## remarks
- using make
Make is truly old, but here it is quite handy
as in case of failures it does all the exception handling for us.
