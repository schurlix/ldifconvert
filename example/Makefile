# for use with gnu make (gmake in *BSD)

source_host="localhost"
source_port=33899
source_user="georg@graf.priv.at"
source_pass="s3cr37"
source_basedn="O=TESTBH"
source_filter="(objectClass=inetOrgPerson)"

target_host="localhost"
target_port="389"
target_user="cn=root"
target_pass="urxnurxn"
target_basedn="ou=people,dc=example,dc=org"
target_filter="(objectClass=inetOrgPerson)"


default: sync

.PHONY: sync
sync: target_modify.ldif
	@echo "> running ldapmodify if not empty"
	if test -s $^; then echo ">> yes, really running"; ldapmodify -h ${target_host} -p ${target_port} -D ${target_user} -w ${target_pass} -f $^; fi

target_modify.ldif: source_converted.ldif target_before.ldif
	../bin/ldifsync.py $^ > $@

target_before.ldif::
	@echo "> getting current state of target"
	ldapsearch -LLL -h ${target_host} -p ${target_port} -D ${target_user} -w ${target_pass} -b ${target_basedn} ${target_filter} > $@

source_converted.ldif: source.ldif ldifconvert.cfg
	@echo "> converting source"
	../bin/ldifconvert.py ldifconvert.cfg

# "::" .. unconditionally build source.ldif
source.ldif::
	@echo "> getting current state of source"
	cat _*.ldif_ > $@
	@echo "> === change here to query your own ldap host ==="
	# ldapsearch -LLL -h ${source_host} -p ${source_port} -D ${source_user} -w ${source_pass} -b ${source_basedn} ${source_filter} > $@

.PHONY: clean
clean:
	rm -f *.ldif
