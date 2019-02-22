import socket
import struct
from network import LoRa

# package config varibales
# struct format for data which we send
_LORA_PKG_FORMAT = "BB%ds"
# receiving data format
_LORA_PKG_ACK_FORMAT = "BBB"
STATUS_CODE_GOOD = 250

# config for LORA network
# use rx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, rx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

lora_sock.setblocking(False)

import urequests as requests
URL = "http://192.168.43.227:3333/lopy?"

while (True):
   recv_pkg = lora_sock.recv(512)
   # check if data received has any message
   if (len(recv_pkg) > 2):
       recv_pkg_len = recv_pkg[1]
       # unpack to regular python strings
       device_id, pkg_len, msg = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_pkg)
       print('Device: %d - Pkg:  %s' % (device_id, msg))

       gps = msg.split(":")[0]
       gps1 = gps[1:]
       gps2 = gps1[:-1]
       new_url = "{}coord={}".format(URL, gps2)

       r = requests.get(URL)
       r.close()

       # pack to send back data was received
       ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT, device_id, 1, STATUS_CODE_GOOD)
       lora_sock.send(ack_pkg)
