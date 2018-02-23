#!/usr/bin/env python2

from imcsdk.imchandle import ImcHandle, ImcException
from imcsdk.imcexception import ImcOperationError
from imcsdk.apis.server import vmedia
from imcsdk.apis.server import boot
#from imcsdk.apis.v2 import Server

server_password = {
            "10.93.130.90" : { "user" : "admin", "password" : "cisco", "hostname" : "esxi01" },
            "10.93.130.91": { "user" : "admin", "password" : "cisco", "hostname" : "esxi02" },
            "10.93.130.92": { "user" : "admin", "password" : "C1sco1234", "hostname" : "esxi03" },
            "10.93.130.93": { "user" : "admin", "password" : "C1sco1234", "hostname" : "esxi04" }, 
            "10.93.130.94": { "user" : "admin", "password" : "C1sco1234", "hostname" : "esxi05" } 
            }
kubam_server = "10.93.234.95"


# mount the virtual media
def mount_media(handle, hostname):
    print "Mounting Media"
    status = vmedia.vmedia_get_existing_status(handle)
    print status
    media = "%s.iso" % hostname
    print "mounting " , media
    try: 
        vmedia.vmedia_mount_create(
            handle,
            volume_name="c",
            map="www",
            mount_options="",
            remote_share="http://%s/kubam" % kubam_server,
            remote_file=media,
            username="",
            password="")
    #https://github.com/CiscoUcs/imcsdk/blob/master/imcsdk/imcexception.py
    except ImcOperationError as e:
        print("failed to mount media.  %s", e.message)
    

def set_boot(handle):      
    boot.boot_order_precision_set(handle,
            reboot_on_update="yes",
            reapply="yes",
            configured_boot_mode="Legacy",
            boot_devices = [{"order" : '1', "device-type":"vmedia", "name" : "vmedia"} ,
                            {"order" : "2", "device-type" : "hdd", "name" : "hdd" }]
        )

    boot_order_list = boot.boot_order_precision_get(handle, dump=True)



def install(server, attrs):
    print("Logging in to %s" % server)
    print(attrs["user"], attrs["password"])
    handle = ImcHandle(server, attrs["user"], attrs["password"], auto_refresh=True, force=True)
    try:
        handle.login()
    except ImcException as e:
        
        print("error logging in: %s" % e.error_descr, e.error_code)
        return
    except Exception as e:
        print "Error with server login.  Could be your firmware is too old?"
        return

    print("successfully logged into %s" % server)
    mount_media(handle, attrs["hostname"]) 
    set_boot(handle)
    handle.logout()

#for server, attrs in server_password.items():
server = "10.93.130.90"
attrs = server_password[server] 
install(server, attrs)
