#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import ldif

from ConfigParser import ConfigParser
from copy import copy

try:
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(sys.argv[1])

except RuntimeError as e:
    print(e)
    print("need readable conversion file as argument.")
    sys.exit(1)

source = config.get("general", "sourcefile")
target = config.get("general", "targetfile")


class Target:

    def __init__(self, _entry):
        # build DN 
        prefixkey = config.get("dn", "prefix.name")
        prefixval = _entry[config.get("dn", "prefix.sourcename")][config.getint("dn", "prefix.sourceindex")]
        postfix = config.get("dn", "postfix")
        self.dn = "%s=%s,%s" % (prefixkey, prefixval, postfix)
        self.dnhash = hash(self.dn)
        self.attrs = {}
        # populate mapped keys [keymap]
        keymap_keys = config.options("keymap")  # ['cn', 'uid', 'uid.index', .. ]
        for key in keymap_keys:
            if key.endswith(".index"):
                continue
            sourceattrs = config.get("keymap", key).split(", ")
            for sourceattr in sourceattrs:
                if sourceattr not in _entry:
                    continue  # or raise ()?
                if key + ".index" in keymap_keys:
                    vals = set()
                    for index in map(lambda x: int(x), config.get("keymap", key + ".index").split(",")):
                        if index < len(_entry[sourceattr]):
                            vals.add(_entry[sourceattr][index])
                else:
                    vals = copy(_entry[sourceattr])
                if key == "mail":
                    for item in copy(vals):
                        if "@" not in item:
                            vals.remove(item)
                if key in self.attrs:
                    self.attrs[key].update(vals)
                else:
                    self.attrs[key] = set(vals)
        # search - replace
        for attrname, pattern in config.items("search"):
            if attrname not in self.attrs:
                continue
            replacement = config.get("replace", attrname)
            replaced = set()
            for value in self.attrs[attrname]:
                replaced.add(re.sub(pattern, replacement, value))
            self.attrs[attrname] = replaced
            # static
        for attrname, values in config.items("static"):
            if attrname not in self.attrs:
                self.attrs[attrname] = set()
            values = values.split(", ")
            for value in values:
                self.attrs[attrname].add(value)

    def __str__(self):
        return "%s\n%s\n" % (self.dn.encode("utf-8"), self.attrs)

    def __hash__(self):
        return self.dnhash

    def get_dn_and_entry(self):
        return self.dn, self.attrs


sourceparser = ldif.LDIFRecordList(open(source))
sourceparser.parse()
people = set()
for dn, entry in sourceparser.all_records:
    people.add(Target(entry))

writer = ldif.LDIFWriter(open(target, 'w'))
for person in people:
    writer.unparse(*person.get_dn_and_entry())
