#!/usr/bin/env python3
# 
# Windows Tray Ewelinks Lights Controller by Eliran Gonen - eliran.gonen at gmail dot com
#

import os
import sys
import subprocess
from functools import partial
import configparser
import random
# Net modules
import subprocess
import requests
from websocket import create_connection
# Messagebox 
import ctypes 
# System tray 
from SysTrayIcon import SysTrayIcon

config_file = "ewelink.ini" 

def MsgBox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

def generate_nonce(length):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def toggle_device(device_id, index):
        global devices
        device_state =  devices[index][2]
        desired_state = "off" if device_state == "on" else "on" 
            
        try:
            model = config['identity']['model']
        except KeyError:
            model = "Samsung Galaxy"
             
        try:
            os = config['identity']['os']
        except KeyError:
            os = "android"

        cmd1 = '{ "action":"userOnline", "userAgent":"app", "version":6, "nonce":"' + generate_nonce(15) + '", "apkVersion":"3.2.1", "os":"' + os + '", "apikey":"' + api_key +'", "ts":"1999999999", "model":"' + model + '", "romVersion":"6.0.1", "sequence":"'+ generate_nonce(13) + '" }'
         
        cmd2 = '{ "action": "update", "userAgent": "app", "apikey": "' + api_key + '", "deviceid": "' + device_id + '", "params": { "switch": "' + desired_state + '" }}'

        websocket = create_connection(wss_url)
        websocket.send(cmd1)
        websocket.send(cmd2)
        websocket.close()
         
        devices[index][2] = desired_state
  
def get_devices():
    payload = dict(Authorization='Bearer ' + token)
    r = requests.get(api_url, headers = payload)
    j = r.json()
    devices = [] 
    for i in range(0, len(j)):
        device_id = j[i]['deviceid']
        device_name = j[i]['name']
        device_state = j[i]['params']['switch']
        
        devices.append([device_name, device_id, device_state]) 
    return devices 

def read_config_file():
    if (not os.path.isfile(config_file)):
        response = MsgBox("Error", "No configuration file was found, create it now ?", 4)
        if (response == 6): # YES 
            MsgBox("Fatal Error", "GUI Configurator is yet to be implemented.\n You will have to manually create and edit ewelink.ini", 0)
            sys.exit(1)
        else:
            sys.exit(1)
         
    global config 
    config = configparser.ConfigParser()
    config.read(config_file) 
     
    if (not 'settings' in config):
        MsgBox("Fatal Error", "Missing settings section")
        sys.exit(1)

    global api_url, token, wss_url, api_key
    try:     
        if (not config['settings']['api_url'] == ""):
            api_url = config['settings']['api_url']
        else:
            MsgBox("Fatal Error", "Missing api_url setting", 0)
            sys.exit(1)
    except KeyError:
        MsgBox("Fatal Error", "Missing api_url setting", 0)
        sys.exit(1)

    try:
        if (not config['settings']['token'] == ""):
            token = config['settings']['token']
        else:
            MsgBox("Fatal Error", "Missing token setting", 0)
            sys.exit(1)
    except KeyError:
        MsgBox("Fatal Error", "Missing token setting", 0)
        sys.exit(1)

    try:
        if (not config['settings']['wss_url'] == ""): 
            wss_url = config['settings']['wss_url']
        else:             
            MsgBox("Fatal Error", "Missing wss_url setting", 0)
            sys.exit(1)
    except KeyError:
        MsgBox("Fatal Error", "Missing wss_url setting", 0)
        sys.exit(1)
         
    try:
        if (not config['settings']['api_key'] == ""):
            api_key = config['settings']['api_key']
        else:
            MsgBox("Fatal Error", "Missing api_key setting", 0)
            sys.exit(1)
    except KeyError:
        MsgBox("Fatal Error", "Missing api_key setting", 0)
        sys.exit(1)
 
if __name__ == '__main__':
    icon =  'ewelink.ico' 
    hover_text = "Ewelink Lights Controller"
    
    read_config_file()     
    devices = get_devices()
     
    menu_options = ()
    for i in range(0, len(devices)):
        menu_options = menu_options + ((devices[i][0], icon, partial(toggle_device, devices[i][1], i)),)

    SysTrayIcon(icon, hover_text, menu_options,  default_menu_index=1)
 
