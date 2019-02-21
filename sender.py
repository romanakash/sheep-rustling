import os
import socket
import time
import struct
import gc
from network import LoRa
from time import sleep

from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack

# garbage collection
gc.enable()

py = Pytrack()
l76 = L76GNSS(py, timeout=30)
acc = LIS2HH12()

# returns gps data in str format (lat, long)
def get_gps_data():
    coord = l76.coordinates()
    coord_str = "{}".format(coord)
    return coord_str

# return accelerometer data in str format ((x,y,z), pitch, roll)
def get_acc_data():
    acceleration = acc.acceleration();
    pitch = acc.pitch()
    roll = acc.roll()
    acc_str = "{}".format((acc, pitch, roll))
    return acc_str

# config for LORA network
lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

# package config varibales
# struct format for data which we send
_LORA_PKG_FORMAT = "BB%ds"
# receiving data format
_LORA_PKG_ACK_FORMAT = "BBB"
# unique for every sheep device, should be generated by uuid but due to bandwidth constraints let's stick to this
DEVICE_ID = 0x01
# time interval between sending signals
TIME_INTERVAL = 5

while(True):
    msg = get_gps_data() + ":" + get_acc_data()
    # pack into binary struct for transmission
    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), DEVICE_ID, len(msg), msg)
    lora_sock.send(pkg)
    print("Sending ...")

    isSent = False
    while(not isSent):
        received_mes = lora_sock.recv(256)

        if (len(received_mes) > 0):
            # unpack into regular python strings
            device_id, pkg_len, status_code = struct.unpack(_LORA_PKG_ACK_FORMAT, received_mes
            # check if message from this device
            if (device_id == DEVICE_ID):
                if (status_code == 250):
                    isSent = True
                    print("Sent" + status_code)
                else:
                    isSent = True
                    print("Message Failed")

    time.sleep(TIME_INTERVAL)