import json
import urllib.request
from pyovpn.plugin import *

# MODIFY THIS!!!!!!!!!!!
WEBHOOK_URL = '*** PUT YOUR SLACK WEBOOK URL IN HERE ***'

# If False or undefined, AS will call us asynchronously in a worker thread.
# If True, AS will call us synchronously (server will block during call),
SYNCHRONOUS = True

# this function is called by the Access Server after normal authentication
def post_auth(authcred, attributes, authret, info):

    proplist_save = {}

    try:
        # The 'print' lines go to the log file at /var/log/openvpnas.log (by default).
        print("********** POST_AUTH", authcred, attributes, authret, info)

        if not WEBHOOK_URL:
            raise Exception("WEBHOOK_URL is not declared on server. Please contact to VPN Server Admin.")

        if attributes.get('vpn_auth'):                  # only do this for VPN authentication
            hw_addr = authcred.get('client_hw_addr')    # MAC address reported by the VPN client
            username = authcred.get('username')         # User name of the VPN client login attempt
            clientip = authcred.get('client_ip_addr')   # IP address of VPN client login attempt
            platform = '{0} {1}'.format(
                attributes.get('client_info').get('IV_PLAT'),
                attributes.get('client_info').get('UV_PLAT_REL')
            )

            # Send POST request to slack
            params = json.dumps({
                'text': "*New Connection*\n>>>• User: {username}\n• Originating IP Address: {clientip}\n• Mac Address: {hw_addr}\n• OS & Version: {platform}".format(
                    username=username,
                    clientip=clientip,
                    hw_addr=hw_addr,
                    platform=platform,
                )
            }).encode('utf-8')
            req = urllib.request.Request(WEBHOOK_URL,
                                  data=params,
                                  headers={'content-type': 'application/json'})
            resp = urllib.request.urlopen(req)
            resp.read()

    except Exception as ex:
        authret['status'] = FAIL
        authret['reason'] = str(ex)         # this error string is written to the server log file
        authret['client_reason'] = str(ex)  # this error string is reported to the client user

    finally:
        return authret, proplist_save
