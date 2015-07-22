#!/usr/bin/env python

# Author: Douglas Otwell
# This software is released to the public domain

# The Software is provided "as is" without warranty of any kind, either express or implied, 
# including without limitation any implied warranties of condition, uninterrupted use, 
# merchantability, fitness for a particular purpose, or non-infringement.

import os
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
from optparse import OptionParser
import subprocess
import traceback
import re

import public



pin_code = "0000"

def getRSSI(address):
	ret = None # RSSI Unknown
        cmd = 'hcitool rssi %s'%address
	print cmd
	cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	for line in cmd.stdout:
		print '<',line,'>'
		m = re.match('RSSI return value: *(-?[0-9]+)', line)
		if m is not None:
			if len(m.groups())==1:
				ret = int(m.group(1))

	print type(ret),ret
	return ret

class Agent(dbus.service.Object):

    def getDevice(self, device_path):
        bus = dbus.SystemBus()
        device_object = bus.get_object("org.bluez", device_path)
        device = dbus.Interface(device_object, "org.bluez.Device")
        return device

    def getDeviceProps(self, device_path):
        device = self.getDevice(device_path)
        properties = device.GetProperties()
        return properties

    def trustDevice(self, device_path):
        device = self.getDevice(device_path)
        device.SetProperty("Trusted", dbus.Boolean(True))

    def makePublic(self, properties, passKey):
        btName = properties["Alias"]
        btAddr = properties["Address"]
        public.sayPairingFrom(btAddr, btName, passKey)

    @dbus.service.signal("org.bluez.Adapter", signature="sv")
    def PropertyChanged(self, setting, value):
        """PropertyChanged(setting, value)
        Send a PropertyChanged signal. 'setting' and 'value' are
        string parameters as specified in doc/media-api.txt.
        """
        print 'PropertyChanged',setting,value 

    @dbus.service.method("org.bluez.Agent", in_signature="o", out_signature="s")
    def RequestPinCode(self, device_path):
        properties = self.getDeviceProp(device_path)
        msg = "0Pairing and trusting device %s [%s]"
        print msg % (properties["Alias"], properties["Address"])
        self.trustDevice(device_path)
        return pin_code

    @dbus.service.method("org.bluez.Agent", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device_path, passkey):
	try:
		self._RequestConfirmation(device_path, passkey)
	except:
		traceback.print_exc()

    def _RequestConfirmation(self, device_path, passkey):
        properties = self.getDeviceProps(device_path)
        msg = "1Pairing and trusting device %s [%s] with passkey [%s]"
        print msg % (properties["Alias"], properties["Address"], passkey)
        
        #print properties
        # pair the device only if near the host bluetooth controller
	rssi = getRSSI(properties["Address"])
	if rssi==0:
                self.makePublic(properties, passkey)
                self.trustDevice(device_path)

        return

    @dbus.service.method("org.bluez.Agent", in_signature="os", out_signature="")
    def Authorize(self, device, uuid):
        print "Authorize (%s, %s)" % (device, uuid)
        authorize = raw_input("Authorize connection (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Connection rejected by user")

def set_discoverable():
    try:
        _set_discoverable()
    except:
        traceback.print_exc()

def _set_discoverable():
    print '_set_discoverable'
    bus = dbus.SystemBus()

    # get the Bluez manager and default bluetooth adapter
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.bluez.Manager")
    adapter_path = manager.DefaultAdapter()
    adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter")

    # set the adapter to discoverable 
    print "Making Bluetooth adapter discoverable"
    adapter.SetProperty("Discoverable", dbus.Boolean(True))

def property_changed(name, value):
    print 'property_changed',name,value
    if name == 'Discoverable' and not value:
        # restart in a while
        print 'Restarting discoverable in 30secs start'
	gobject.timeout_add_seconds (30, set_discoverable)

def startAgent():
    print 'Starting as not reachable'

    if (os.getuid() != 0):
        print "You must have root privileges to run this agent. Try 'sudo pinaple-agent [--pin <PIN>]'"
        raise SystemExit

    # get the dbus system bus
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # get the Bluez manager and default bluetooth adapter
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.bluez.Manager")
    adapter_path = manager.DefaultAdapter()
    adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter")

    # set the adapter to discoverable 
    print "Making Bluetooth adapter discoverable"
    adapter.SetProperty("Discoverable", dbus.Boolean(True))

    # register the pinaple agent
    agent_path = "/pinaple/agent"
    agent = Agent(bus, agent_path)
    try:
        adapter.RegisterAgent(agent_path, "KeyboardDisplay")
        bus.add_signal_receiver(property_changed,
                dbus_interface = "org.bluez.Adapter",
                signal_name = "PropertyChanged")
        print "Waiting to pair devices...."
    except dbus.exceptions.DBusException, ex:
        print "A Bluetooth agent is currently running. Exiting pinaple-agent", ex
        raise SystemExit

    mainloop = gobject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print "\nMaking Bluetooth adapter undiscoverable"
        adapter.SetProperty("Discoverable", dbus.Boolean(False, variant_level=1))
        adapter.UnregisterAgent(agent_path)
#        raise SystemExit
        mainloop.quit()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-p", "--pin", action="store", dest="pin_code", help="PIN code to pair with", metavar="PIN")
    (options, args) = parser.parse_args()

    # use the pin code if provided
    if (options.pin_code):
        pin_code = options.pin_code

    startAgent()
