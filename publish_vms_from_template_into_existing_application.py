#!/usr/bin/env python
#
# publish_vms_from_template_into_existing_application.py : a program 
# that updates an existing Ravello application with several additional
# VMs cloned from the same template image.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys
import copy
import argparse
import logging
import getpass

from ravello_sdk import RavelloClient, update_luids
from ravello_cli import get_application

def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description="Publish several machines from a template into an exising Ravello application.")
    parser.add_argument('-b', '--basename', nargs=1, required=True, help='Basename of the newly deployed VMs', dest='basename', type=str)
    parser.add_argument('-n', '--number', nargs=1, required=True, help='Amount of VMs to deploy', dest='number', type=int)
    parser.add_argument('-p', '--password', nargs=1, required=False, help='The password with which to connect to the Ravello REST API. If not specified, the user is prompted at runtime for a password', dest='password', type=str)
    parser.add_argument('-t', '--template-id', nargs=1, required=True, help='Template ID to deploy', dest='template_id', type=int)
    parser.add_argument('-a', '--app-id', nargs=1, required=True, help='Application ID to update', dest='app_id', type=int)
    parser.add_argument('-u', '--user', nargs=1, required=True, help='The username with which to connect to the Ravello REST API', dest='username', type=str)
    args = parser.parse_args()
    return args

def create_compute_vm(app, img, num, basename):
    design = app['design']
    vm = copy.deepcopy(img)
    name = "%s%s" % (basename, num) 
    vm['name'] = name
    vm['hostnames'] = [name]
    update_luids(vm)
    design['vms'].append(vm)

def main():
    logger = logging.getLogger(__name__)

    # Handling arguments
    args = get_args()

    username = args.username[0]

    password = None
    if args.password:
        password = args.password[0]
    # Getting user password
    if password is None:
        logger.debug('No command line password received, requesting password from user')
        password = getpass.getpass(prompt='Enter password for Ravello REST API for user %s: ' % username)

    template_id = args.template_id[0]
    app_id = args.app_id[0]
    number = args.number[0]
    basename = args.basename[0]

    client = RavelloClient()
    client.login(username, password)

    try:
        app = client.get_application(app_id)
    except Exception as e:
        s = str(e)
        print(e)
        sys.exit(-1)
    print('Found Application: {0}'.format(app['name']))

    try:
        img = client.get_image(template_id)
    except Exception as e:
        s = str(e)
        print(e)
        sys.exit(-1)
    print('Found template: {0}'.format(img['name']))

    for i in range(number):
        create_compute_vm(app, img, i+1, basename)
    client.update_application(app)
    client.publish_application_updates(app, True)
    print("Success")

if __name__ == '__main__':
    sys.exit(main())

