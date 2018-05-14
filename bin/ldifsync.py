#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import ldif

logging.basicConfig(level=logging.INFO)

# populate source
sourceparser = ldif.LDIFRecordList(open(sys.argv[1]))
sourceparser.parse()
sourced = {k: v for k, v in sourceparser.all_records}
sources = set(sourced)
logging.info("Source: %d entries" % len(sourced))

# populate target
targetparser = ldif.LDIFRecordList(open(sys.argv[2]))
targetparser.parse()
targetd = {k: v for k, v in targetparser.all_records}
targets = set(targetd)
logging.info("Target: %d entries" % len(targetd))

writer = ldif.LDIFWriter(sys.stdout)

# delete dn's that are only on the target - deepest first
todelete = targets - sources
logging.info('Only on target: delete {:d} entries'.format(len(todelete)))
for dn in sorted(todelete, key=lambda x: len(x.split(',')), reverse=True):
    writer.unparse(dn, {"changetype": [u"delete"]})

# add records which are only in our source - higher first
toadd = sources - targets
logging.info("Only on source: add {:d} entries".format(len(toadd)))
for dn in sorted(toadd, key=lambda x: len(x.split(','))):
    writer.unparse(dn, [(k, v) for k, v in sourced[dn].items()])

# create modifies where dn is same but attrs differ
modifys = {}  # Dict[dn, -> entry]
for dn in targets.intersection(sources):
    sourceattrs = sourced[dn]  # orderedDict
    targetattrs = targetd[dn]  # orderedDict
    entry = []
    # compare the dict values - see if we need to do more
    if sourceattrs == targetattrs:
        continue
    # add attributes only in source
    addattrs = set(sourceattrs) - set(targetattrs)
    for attr in addattrs:
        entry.append((0, attr, sourceattrs[attr]))
    # delete attributes not in source
    delattrs = set(targetattrs) - set(sourceattrs)
    for attr in delattrs:
        entry.append((1, attr, []))
    commonatrs = set(sourceattrs).intersection(targetattrs)
    for attr in commonatrs:
        if sorted(sourceattrs[attr]) != sorted(targetattrs[attr]):
            entry.append((2, attr, sourceattrs[attr]))
    if entry:
        modifys[dn] = entry
logging.info('DN\'s needing modification: {:d}'.format(len(modifys)))
for dn in modifys:
    writer.unparse(dn, modifys[dn])
