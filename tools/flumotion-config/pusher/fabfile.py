from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.console import confirm
import json
import sys
import time
import crypt
from os import getcwd, path
from genconfig import get_hosts

env.hosts = get_hosts()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def prepare_deploy():
    local('rm hosts/*')
    local('./genconfig.py')

def deploy():
    host = env.host
    host_conf = 'hosts/' + host
    host_load(host_conf, False)

def up():
    host = env.host
    host_conf = 'hosts/' + host
    host_load(host_conf)
    host_start(host_conf)

def down():
    host = env.host
    host_conf = 'hosts/' + host
    host_stop(host_conf)

def host_stop(host_file):
    host = json.loads(file_read(host_file))
    connection = host['connection_details']
    with settings(user = connection['user'] or 'docker', password = connection['password'] or 'tcuser', port = connection['port'] or 22, shell = "/bin/sh -c"):
        if (run('docker stop $(docker ps -q)').succeeded):
            print bcolors.OKGREEN + "All services on %s stopped successfully" % env.host + bcolors.ENDC
        else:
            print bcolors.FAIL + "Services on %s failed to stop correctly" % env.host + bcolors.ENDC


def host_load(host_file):
    host = json.loads(file_read(host_file))
    for service in host['services']:
        build_image(service, host['connection_details'])

def file_read(file_name):
    with open(file_name) as f:
        contents = f.read()
        return contents

def file_write(file_name, contents):
    with open(file_name, 'w') as f:
        f.write(contents)
        return

# Builds a Docker image on a remote host and potentially starts a container)
def build_image(service_dict, connection):
    service_type = service_dict['type']
    service_conf = service_dict['conf']
    success = False
    # if we are handling a flumotion service (only service currently supported~)
    if (service_type == 'flumotion-encoder' or service_type == 'flumotion-collector'):
        # First build flumotion and Docker files locally
        group = service_conf['group']
        timestamp = time.time()
        sgh = (service_type, group, env.host)
        sg = (service_type, group)
        try:
            docker_base = file_read('Dockerfile_base')
            encoder_base = file_read('encoder.xml')
            collector_base = file_read('collector.xml')
            worker_base = file_read('worker.xml')
        except Exception as e:
            raise Exception("Base read error on %s service for %s error({0}): {1}".format(e.errno, e.strerror) % sg)
        worker_file = '/tmp/worker-%s-%s.xml' % (timestamp, group)
        worker_contents = worker_base %  service_conf
        docker_file = '/tmp/Dockerfile-%s-%s-%s' % (timestamp, service_type, group)
        if (service_type == 'flumotion-encoder'):
            planet_file = '/tmp/encoder-%s-%s.xml' % (timestamp, group)
            planet_contents = encoder_base % service_conf
            docker_contents = docker_base % (path.basename(worker_file), path.basename(planet_file), 'EXPOSE\t\t15000')
        elif (service_type == 'flumotion-collector'):
            planet_file = '/tmp/collector-%s-%s.xml' % (timestamp, group)
            planet_contents = collector_base % service_conf
            docker_contents = docker_base % (path.basename(worker_file), path.basename(planet_file), '')
        file_write(planet_file, planet_contents)
        file_write(worker_file, worker_contents)
        file_write(docker_file, docker_contents)

        # All configurations should be built locally, let's push them out to our host and build them with Docker.
        build_dir = '/home/%s-%s-%s/' % (timestamp, service_type, group)
        sources_dir = build_dir + 'sources/'
        print "-" * 80
        with settings(user = connection['user'] or 'docker', password = connection['password'] or 'tcuser', port = connection['port'] or 22, shell = "/bin/sh -c"):
            print bcolors.HEADER + "Now pushing to %s" % env.host + bcolors.ENDC
            if (run("mkdir -p " + sources_dir).succeeded):
                put(planet_file, sources_dir)
                put(worker_file, sources_dir)
                put(docker_file, build_dir + 'Dockerfile')
            else:
                raise Exception("Failed to upload to remote host")
            with cd(build_dir):
                build_command = 'docker build -q --rm=false -t %s-%s:latest .' % sg
                if (run(build_command).succeeded):
                    print bcolors.OKBLUE + "%s for group %s image build on %s successful!" % sgh + bcolors.ENDC
                else:
                    print bcolors.FAIL + "%s for group %s image build on %s unsuccesful!" % sgh + bcolors.ENDC
                print "-" * 80
                print "\n" * 2

def host_start(host_file):
    try:
        f = open(host_file)
        host = json.loads(f.read())
        f.close()
    except IOError as e:
        raise Exception("File read error on " + host_file + " I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError as e:
        raise Exception("JSON parse error on " + host_file + " I/O error({0}): {1}".format(e.errno, e.strerror))
    for service in host['services']:
        start_container(service, host['connection_details'])

def start_container(service_dict, connection):
    service_type = service_dict['type']
    service_conf = service_dict['conf']

    # if we are handling a flumotion service (only service currently supported~)
    if (service_type == 'flumotion-encoder' or service_type == 'flumotion-collector'):
        group = service_conf['group']
        sgh = (service_type, group, env.host)

        if (service_type == 'flumotion-encoder'):
            start_command = 'docker run -d -p %i:15000 %s-%s:latest' % (service_conf['flumotion-encoder-port'], service_type, group)
        else:
            start_command = 'docker run -d %s-%s:latest' % (service_type, group)
    with settings(user = connection['user'] or 'docker', password = connection['password'] or 'tcuser', port = connection['port'] or 22, shell = "/bin/sh -c"):

        if (run(start_command).succeeded):
            print (bcolors.OKGREEN + "%s service for %s group started successfully on %s" % sgh + bcolors.ENDC)
        else:
            print (bcolors.FAIL + "%s service for %s group failed to start on %s with command" % sgh + bcolors.ENDC)


