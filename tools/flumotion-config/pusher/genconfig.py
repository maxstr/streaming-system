#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Generate configuration files to be used on a bunch of flumotion boxes."""

import crypt
import optparse
import os
import sys
import json

mypath = os.path.dirname(__file__)
if not mypath:
    mypath = "."

config_path = os.path.realpath(mypath+"/../../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()


OPTIONS = optparse.OptionParser()
OPTIONS.add_option("-g", "--group",
                  action="store", dest="groups", default="",
                  help="Groups to write config for.")
OPTIONS.add_option("-e", "--encoders",
                  action="store_true", dest="encoders", default=True,
                  help="Write configs for encoders.")
OPTIONS.add_option("--no-encoders",
                  action="store_false", dest="encoders",
                  help="Don't write configs for encoders.")
OPTIONS.add_option("-c", "--collectors",
                  action="store_true", dest="collectors", default=True,
                  help="Write configs for collectors.")
OPTIONS.add_option("--no-collectors",
                  action="store_false", dest="collectors",
                  help="Don't write configs for collectors.")
def get_hosts():
    hosts = set()
    (options, args) = OPTIONS.parse_args()

    # Groups to write for
    active_groups = [x.strip() for x in options.groups.split(',') if x]
    if not active_groups:
        active_groups = CONFIG.groups()
    for group in CONFIG.groups():
        if group not in active_groups:
            print "Skipping", group, "for host generation"
            continue
        config = CONFIG.config(group)
        hosts.add(config['flumotion-encoder'])
        hosts.add(config['flumotion-collector'])
    return list(hosts)


def main(args):
    (options, args) = OPTIONS.parse_args()

    # Groups to write for
    active_groups = [x.strip() for x in options.groups.split(',') if x]
    if not active_groups:
        active_groups = CONFIG.groups()

    print "Writing for groups:", active_groups

    # First we generate our host files. Hosts need to know what collectors/encoders they are running and
    # what ports they are expected to be on
    hosts = {}
    default_connection = { "user":"", "password":"", "port":"22" }
    for group in CONFIG.groups():
        if group not in active_groups:
            print "Skipping", group, "for host generation"
            continue

        config = CONFIG.config(group)
        encoder_host = config['flumotion-encoder']
        collector_host = config['flumotion-collector']
        config['flumotion-password-crypt'] = crypt.crypt(
            config['flumotion-password'],
            config['flumotion-salt'])
        if encoder_host not in hosts:
            hosts[encoder_host] = { 'host':encoder_host, 'connection_details':default_connection, 'services':[] }
        if collector_host not in hosts:
            hosts[collector_host] = { 'host':collector_host, 'connection_details':{}, 'services':[] }
        hosts[encoder_host]['services'].append({ 'type': 'flumotion-encoder', 'conf':config })
        hosts[collector_host]['services'].append({ 'type': 'flumotion-collector', 'conf':config })

    # Hosts have been generated, now time to connect the collectors to the encoders and write our host config file
    for host in hosts:
        port = 49152
        encoders = filter(lambda x: x["type"] == "flumotion-encoder", hosts[host]['services'])
        # For each encoder on the host
        for encoder in encoders:
            # Set the encoder to listen on an incremented port
            group = encoder['conf']['group']
            encoder['conf']['flumotion-encoder-port'] = port
            # Grab the host the collector(to that encoder) is running on, then look through that host for the collector we want and then set the encoder port
            filter(lambda x: x['conf']['group'] == group and x['type'] == 'flumotion-collector', hosts[CONFIG.config(group)['flumotion-collector']]['services'])[0]['conf']['flumotion-encoder-port'] = port
            # Increment the port for this host so we don't use it again
            port += 1

    # Output each host to a configuration file that will get shipped along with the necessary configurations to each host
    # (this has to be done in a separate loop because we can't output our host files until after they've all been linked up.)
    for host in hosts:
        host_file = 'hosts/' + host
        f = file(host_file, 'w')
        f.write(json.dumps(hosts[host], indent=4, separators=(',', ': '), sort_keys=True))
        f.close()


if __name__ == "__main__":
    import sys
    main(sys.argv)
