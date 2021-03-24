#!/usr/bin/env python3
# This file is part of the Civilsphere AI VPN
# See the file 'LICENSE' for copying permission.
# Author: Veronica Valeros, vero.valeros@gmail.com, veronica.valeros@aic.fel.cvut.cz

import redis
import time
import json
import random
import ipaddress

WORDS_JSON = 'words.json'

# Import the word dictionary to be used for generating the profile_names
try:
    with open(WORDS_JSON) as f:
        WORDS_DICT = json.load(f)
except:
    pass

# REDIS COMMON
## Series of functions to handle the connections to the Redis database, as well
## as subscribing to channels using pub/sub.

def redis_connect_to_db(REDIS_SERVER):
    """ Function to connect to a Redis database. Returns object publisher. """
    try:
        client = redis.Redis(REDIS_SERVER, port=6379, db=0)
        return client
    except Exception as err:
        return err

def redis_create_subscriber(publisher):
    """ Function to create a pubsub() object. Returns object subscriber. """
    try:
        subscriber = publisher.pubsub()
        return subscriber
    except Exception as err:
        return err

def redis_subscribe_to_channel(subscriber,CHANNEL):
    """ Function to subscribe to a given Redis channel"""
    try:
        subscriber.subscribe(CHANNEL)
        return True
    except Exception as err:
        return err

# IDENTITY HANDLING
## The IDENTITY HANDLING are a series of functions associated with the handling
## of user identities. The identity of a user is an email address, account name or
## any other account identified used to communicate between the AIVPN and the user
##
## The hash table will be account_identities and the value will be a JSON.
## Fields: msg_addr
## Value:
## {'total_profiles':1,'profiles':'[profile_name1,profile_name2]','gpg':string-gpg}

identity_template = json.dumps({'total_profiles':0,'profiles':[],'gpg':''})
hash_account_identities = "account_identities"

def add_identity(msg_addr):
    """ Stores the msg_addr in redis  """

    status = hsetnx(hash_account_identities,msg_addr,identity_template)

    # status==1 if HSETNX created a field in the hash set
    # status==0 if the identity exists and no operation is done.
    return status

def exists_identity(msg_addr):
    """ Checks if the msg_addr in redis exists """
    hash_table = "account_identities"

    status = hexists(hash_account_identities,msg_addr)

    # Returns a boolean indicating if key exists within hash name
    return status

def upd_identity_counter(msg_addr):
    """ Updates counter if the msg_addr in redis exists  by 1. """
    identity_value = json.dumps(hget(hash_account_identities,msg_addr))
    identity_object = json.loads(identity_value)

    identity_object['total_profiles'] = identity_object['total_profiles'] + 1

    identity_value = json.dumps(identity_object)

    status = hset(hash_account_identities,msg_addr,identity_value)

def upd_identity_profiles(msg_addr,profile_name):
    """ If identity exists, add a new profile for the identity """
    identity_value = json.dumps(hget(hash_account_identities,msg_addr))
    identity_object = json.loads(identity_value)

    identity_object['profiles'].append(profile_name)

    identity_value = json.dumps(identity_object)

    status = hset(hash_account_identities,msg_addr,identity_value)

def upd_identity_gpg(msg_addr,gpg_key):
    """ If identity exists, add a new gpg key for the identity """
    identity_value = json.dumps(hget(hash_account_identities,msg_addr))
    identity_object = json.loads(identity_value)

    identity_object['gpg'] = gpg_key

    identity_value = json.dumps(identity_object)

    status = hset(hash_account_identities,msg_addr,identity_value)

def del_identity(msg_addr):
    """ Deletes the msg_addr in redis """
    try:
        hdel(hash_account_identities,msg_addr)
        return True
    except:
        return False

# ACTIVE PROFILE HASH
## We want to quickly consult the number of active profiles in a given identity
## to check that it a certain limit has been reached or not. Users cannot
## request unlimited number of accounts. This is a DDoS protection.
hash_active_profiles = "active_profiles"

def add_active_profile_counter(msg_addr):
    """ Increases the counter of active profiles for a given identity by one. """

    try:
        # Create a new entry if there is not one. Initalize at 0.
        hsetnx(hash_active_profiles,msg_addr,0)

        hincrby(hash_active_profiles,msg_addr,1) 

        return True
    except:
        return False

def subs_active_profile_counter(msg_addr):
    """ Decreases the counter of active profiles for a given identity by one. """

    try:
        # Get current value, if above zero substract one.
        counter_active_profiles = hget(hash_active_profiles,msg_addr)
        if counter_active_profiles > 0:
            hincrby(hash_active_profiles,msg_addr,-1) 
        return True
    except:
        return False

def get_active_profile_counter(msg_addr):
    """ Returns the counter of active profiles for a given identity. """
    counter_active_profiles = hget(hash_active_profiles,msg_addr)
    return counter_active_profiles


def del_active_profile_counter(msg_addr):
    """ Deletes the counter of active profiles for a given identity. """
    try:
        hdel(hash_active_profiles,msg_addr)
        return True
    except:
        return False

# OPEN VPN IP ADDRESS SPACE HANDLING
## We want to quickly check if an IP address is in use
hash_openvpn_blocked_ip_addresses = "mod_openvpn_blocked_ip_addresses"

def add_ip_address(ip_address):
    """ Adds a new IP address to the blocked IP addresses hash table. """
    try:
        hsetnx(hash_openvpn_blocked_ip_addresses,ip_address)
        return True
    except:
        return False

def exists_ip_address(ip_address):
    """ Checks if a given IP address exists in the blocked IP addresses hash table. """

    status = hexists(hash_openvpn_blocked_ip_addresses,ip_address)
    return status

def del_ip_address(ip_address):
    """ Deletes an IP address from the blocked IP addresses hash table. """
    try:
        hdel(hash_openvpn_blocked_ip_addresses,ip_address)
        return True
    except;
        return False

def openvpn_obtain_client_ip_address(NETWORK_CIDR):
    """ Obtains a valid IP address for an OpenVPN  client """
    try:
        result=0
        maximum_attempts=len([str(ip) for ip in ipaddress.IPv4Network(NETWORK_CIDR)])
        while result<maximum_attempts::
            IP_ADDRESS=random.choice([str(ip) for ip in ipaddress.IPv4Network(NETWORK_CIDR)])
            if exists_ip_address(IP_ADDRESS):
                result+=1
            else:
                add_ip_address(IP_ADDRESS)
                return IP_ADDRESS
        return False
    except:
        return False

# PROFILE_NAME:IP_ADDRESS RELATIONSHIP
## We want to quickly obtain the IP from a profile name

hash_profile_name_ip_address='profile_name_ip_address'

def add_profile_ip_relationship(profile_name,ip_address):
    """ Adds a profile:ip to the list. """
    try:
        hsetnx(hash_profile_name_ip_address,profile_name,ip_address)
        return True
    except:
        return False

def del_profile_ip_relationship(profile_name):
    """ Adds a profile:ip to the list. """
    try:
        hdel(hash_profile_name_ip_address,profile_name)
        return True
    except:
        return False

def get_ip_for_profile(profile_name):
    """ Returns the IP address for a given profile name. """
    ip_address = hget(hash_profile_name_ip_address,profile_name)
    return ip_address

# PROFILE HANDLING
## The PROFILE_HANDLING are a series of functions associated with the
## generation on profile_names, storage, and other functions.

def gen_profile_name():
    """
    Generates a new profile_name based on a recipe.
    Profile name recipe: YYYYMMDDmmss_<word>_<word>
    """
    try:
        string1 = random.choice(WORDS_DICT['data'])
        string2 = random.choice(WORDS_DICT['data'])
        datenow = time.strftime("%Y%m%d%H%M%S")
        profile_name = "{}-{}_{}".format(date_now, string1, string2)

        return profile_name
    except Exception as e:
        return False

hash_profile_names = "profile_names"
def add_profile_name(profile_name,msg_addr):
    """ Stores the profile_name:msg_addr in Redis  """

    status = hsetnx(hash_profile_names,profile_name,msg_addr)

    # status==1 if HSETNX created a field in the hash set
    # status==0 if the identity exists and no operation is done.
    return status

def get_profile_name(profile_name):
    """ Obtains a msg_addr given a profile_name """

    msg_addr = hget(hash_profile_names,profile_name)
    return msg_addr

def del_profile_name(profile_name):
    """ Deletes a profile_name from Redis """

    try:
        hdel(hash_profile_names,profile_name)
        return True
    except:
        return False

# PROVISIONING QUEUE
## The provisioning queue is where new requests are queued before being handled.
## We receive many types of requests, through many types of messaging apps.
## One client can do many requests.
## We store { "msg_id":45, "msg_type":"email", "msg_addr":"email@email.com" }

def add_item_provisioning_queue(REDIS_CLIENT,msg_id,msg_type,msg_addr):
    """ Function to add an item to the provisioning_queue Redis SET"""

    try:
        redis_set = "provisioning_queue"
        score = time.time()

        # Build the JSON item to add to the set
        dataset = { "msg_id":int(msg_id), "msg_type":str(msg_type),
                "msg_addr":str(msg_addr) }
        new_request = json.dumps(dataset)

        # If new_request exists, ignore and do not update score.
        REDIS_CLIENT.zadd(redis_set,{new_request:score},nx=True)

        return True
    except Exception as err:
        return err


def get_item_provisioning_queue(REDIS_CLIENT):
    """ Function to get the 'oldest' item (lowest score) from the
    provisioning_queue Redis SET. """

    try:
        redis_set = "provisioning_queue"
        request = REDIS_CLIENT.zpopmin(redis_set,1)
        return request
    except Exception as err:
        return err

# PROVISIONING GENERATE VPN QUEUE
# name: prov_generate_vpn
# This is the queue were new profiles are queued in wait for a VPN profile.

def add_prov_generate_vpn(profile_name,REDIS_CLIENT):
    """ Function to add an item to the prov_generate_vpn queue."""

    try:
        redis_set = "prov_generate_vpn"
        score = time.time()

        REDIS_CLIENT.zadd(redis_set,{profile_name:score},nx=True)
        return True
    except Exception as err:
        return err

def get_prov_generate_vpn(REDIS_CLIENT):
    """ Function to get the 'oldest' item (lowest score) from the
    prov_generate_vpn Redis SET. """

    try:
        redis_set = "prov_generate_vpn"
        request = REDIS_CLIENT.zpopmin(redis_set,1)
        return profile_name
    except Exception as err:
        return err
