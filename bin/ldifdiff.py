#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Parameters: <from.ldif>[1] <to.ldif>[2]
# from.ldif shall contain all entries that are currently in the ldap server
# to.ldif shall contain the final state in the ldap server

import logging
import sys
import ldif3
import os


def dn_parts_count(par_dn):
    return len(par_dn.split(','))


logging.basicConfig(level=logging.INFO)

# populate from
fromparser = ldif3.LDIFParser(open(sys.argv[1], mode="rb"))
fromparser.parse()
from_dict = {k: v for k, v in fromparser.parse()}
from_set = set(from_dict)
logging.info("from: %d entries" % len(from_dict))

# populate to
toparser = ldif3.LDIFParser(open(sys.argv[2], mode="rb"))
toparser.parse()
to_dict = {k: v for k, v in toparser.parse()}
to_set = set(to_dict)
logging.info("to: %d entries" % len(to_dict))

writer = ldif3.LDIFWriter(os.fdopen(sys.stdout.fileno(), mode="wb"))

# delete dn's that are only on the to -
todelete = from_set - to_set  #
logging.info('Only on to: delete {:d} entries'.format(len(todelete)))
for dn in sorted(todelete, key=dn_parts_count, reverse=True):
    writer.unparse(dn, {"changetype": [u"delete"]})

# add records which are only in our from - DNs with less parts first
toadd = to_set - from_set
logging.info("Only on from: add {:d} entries".format(len(toadd)))
for dn in sorted(toadd, key=dn_parts_count):
    writer.unparse(dn, [(k, v) for k, v in to_dict[dn].items()])

# create modify items where dn is same but attrs differ
modifys = {}  # Dict[dn, -> entry]
for dn in to_set.intersection(from_set):

    from_attrs = from_dict[dn]  # orderedDict
    to_attrs = to_dict[dn]  # orderedDict
    entry = []

    # compare the dict values - see if we need to do more
    if from_attrs == to_attrs:  # should never happen
        logging.debug("same attrs for dn: %s" % dn)
        continue

    # add attributes that are wanted on the to and are not in from
    addattrs = set(to_attrs) - set(from_attrs)
    for attr in addattrs:
        entry.append((0, attr, to_attrs[attr]))

    # delete attributes not in from
    delattrs = set(from_attrs) - set(to_attrs)
    for attr in delattrs:
        entry.append((1, attr, []))

    # now modify attributes that exist in both but differ
    commonatrs = set(from_attrs).intersection(to_attrs)
    for attr in commonatrs:
        if sorted(from_attrs[attr]) != sorted(to_attrs[attr]):
            entry.append((2, attr, to_attrs[attr]))
    if entry:
        modifys[dn] = entry
logging.info('DN\'s needing modification: {:d}'.format(len(modifys)))
for dn in modifys:
    writer.unparse(dn, modifys[dn])
