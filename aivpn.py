#!/usr/bin/env python
# This file is part of the Civilsphere AI VPN
# See the file 'LICENSE' for copying permission.
# Author: Veronica Valeros, vero.valeros@gmail.com, veronica.valeros@aic.fel.cvut.cz

import sys
import argparse
import logging
import configparser
from common.database import *

def manage_info(profile_name):
    """
    """
    try:
        logging.debug('Manage info: {profile_name}')
        pass
    except Exception as err:
        print(f'Exception in manage_info: {err}')

def manage_expire(profile_name):
    """
    """
    try:
        logging.debug(f'Manage expire: {profile_name}')
        pass
    except Exception as err:
        print(f'Exception in manage_expire: {err}')

def manage_extend(profile_name):
    """
    """
    try:
        logging.debug(f'Manage extend: {profile_name}')
        pass
    except Exception as err:
        print(f'Exception in manage_extend: {err}')

def manage_whois(profile_name):
    """
    """
    try:
        logging.debug(f'Manage whois: {profile_name}')
        pass
    except Exception as err:
        print(f'Exception in manage_whois: {err}')

def provision_new_openvpn():
    """
    """
    try:
        pass
    except Exception as err:
        print(f'Exception in provision_new_openvpn: {err}')

def provision_new_wireguard():
    """
    """
    try:
        pass
    except Exception as err:
        print(f'Exception in provision_new_wireguard: {err}')

def provision_new_novpn():
    """
    """
    try:
        pass
    except Exception as err:
        print(f'Exception in provision_new_novpn: {err}')

def audit_active_profiles():
    """
    """
    try:
        pass
    except Exception as err:
        print(f'Exception in audit_active_profiles: {err}')

def audit_expired_profiles():
    """
    """
    try:
        pass
    except Exception as err:
        print(f'Exception in audit_expired_profiles: {err}')


if __name__ == '__main__':
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    REDIS_SERVER = config['REDIS']['REDIS_SERVER']
    MOD_CHANNELS = json.loads(config['REDIS']['REDIS_MODULES'])
    LOG_FILE = config['LOGS']['LOG_CLI']

    parser = argparse.ArgumentParser(description = "AI VPN Command Line Tool")
    parser.add_argument( "-v", "--verbose", help="increase output verbosity", action="store_true")

    # Configure commands
    subparser = parser.add_subparsers(dest='command')
    manage = subparser.add_parser('manage', help=f'Manage an AI VPN profile')
    provision = subparser.add_parser('provision', help=f'Provision a new AI VPN account')
    audit = subparser.add_parser('audit', help=f'Audit AI VPN activities')

    # manage actions
    manage.add_argument('--info', help='retrieve information of a profile', type=str, required=False, metavar='<profile_name>')
    manage.add_argument('--expire', help='expire a profile', type=str, required=False, metavar='<profile_name>')
    manage.add_argument('--extend', help='extend the expiration of a profile (add default expiration on top of current date)', type=str, required=False, metavar='<profile_name>')
    manage.add_argument('--whois', help='retrieve identity associated with a profile', type=str, required=False, metavar='<profile_name>')

    # provision actions
    provision.add_argument('--openvpn', help='create a new openvpn profile for a given identity', type=str, required=True, metavar='<user email | user telegram>')
    provision.add_argument('--wireguard', help='create a new wireguard profile for a given identity', type=str, required=True, metavar='<user email | user telegram>')
    provision.add_argument('--novpn', help='create a new novpn profile for a given identity', type=str, required=True, metavar='<user email | user telegram>')

    # audit actions
    audit.add_argument('--active-profiles', help='list all AI VPN active profiles', type=str, required=True, metavar='')
    audit.add_argument('--expired-profiles', help='list all AI VPN expired profiles', type=str, required=True, metavar='')

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        log_level=logging.INFO
    else:
        log_level=logging.DEBUG

    logging.basicConfig(filename=LOG_FILE, level=log_level,format='%(asctime)s, AIVPN_CLI, %(message)s')

    # parsing commands
    if args.command == 'manage':
        logging.info('Managing profile')
        if args.info:
            cli_action = manage_info
            params = args.info
        elif args.expire:
            cli_action = manage_expire
            params = args.expire
        elif args.extend:
            cli_action = manage_extend
            params = args.extend
        elif args.whois:
            cli_action = manage_whois
            params = args.whois

    if args.command == 'provision':
        logging.info('Provisioning account')
        cli_action = ''

    if args.command == 'audit':
        logging.info('audit mode')
        cli_action = ''

    cli_action(params)



