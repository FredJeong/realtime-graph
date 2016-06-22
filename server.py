import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
from struct import unpack
from collections import defaultdict

port = serial.Serial('/dev/ttyUSB0', 115200)

buf = np.zeros(1024*1024, dtype=np.uint8)

offset = 0
step = 181
head = 0

control_gain = np.zeros(255, dtype=np.float32)

log = defaultdict(list)

def read_from_serial(bytes=1024):
    s = port.read(bytes)
    buf[offset:offset + len(s)] = s
    offset += len(s)
    if offset > 1024 * 100:
        np.roll(buf, -head)
        offset -= head
        head = 0
    flush()

def verify_data(data):
    if ((unpack('l', data[:4])[0] >> 8) & 0x00ffffff) != 0x00ff8382:
        return False
    return int(data[:-1].sum()) & 0xff  == data[-1]

def parse_data(data):
    data = data.tobytes()
    parsed = {}
    # used native byte order
    # if planning to use on systems with BE, append < in front of format

    whole_data = unpack('l' + 'fHH' + 'f' + 'ffffffffffff' + 'ff' + 'ffff' + 'ffffffffffff' + 'ffffffff' + 'ffffff', data[:170])

    parsed['checksum'] = (unpack('l', data[:4])[0] >> 8) & 0x00ffffff
    parsed['status'] = unpack('B', data[3:4])[0]
    parsed['time'] = unpack('f', data[4:8])[0]
    parsed['nav_ins_status'] = unpack('H', data[8:10])[0]
    parsed['volt'] = unpack('f', data[12:16])[0]
    
    nav_data = unpack('ffffffffffff', data[16:16 + 4 * 12])
    parsed['controller_angular_cmd'] = np.array(nav_data[0:6:2], dtype=np.float32)
    parsed['nav_pqr'] = np.array(nav_data[1:6:2], dtype=np.float32)
    
    parsed['controller_euler_cmd'] = np.array(nav_data[6:12:2], dtype=np.float32)
    parsed['nav_euler'] = np.array(nav_data[7:12:2], dtype=np.float32)

    parsed['nav_llh'] = np.array(unpack('dd', data[64: 64 + 16]), dtype=np.float64)

    parsed['nav_acc'] = np.array(unpack('fff', data[80: 80 + 12]), dtype=np.float32)
    parsed['nav_pres'] = unpack('f', data[23*4:23*4+4])[0]
    
    nav_data = unpack('ffffffffffff', data[24*4, 24*4 + 4*12])
    parsed['controller_velocity_cmd'] = np.array(nav_data[0:6:2], dtype=np.float32)
    parsed['nav_uvw'] = np.array(nav_data[1:6:2], dtype=np.float32)
    parsed['controller_position_cmd'] = np.array(nav_data[6:12:2], dtype=np.float32)
    parsed['guidance_uav_position'] = np.array(nav_data[7:12:2], dtype=np.float32)

    parsed['servo_fcc_pwm'] = np.array(unpack('HHHHHHHH', data[72*2: 72*2+8*2]), dtype=np.uint16)
    parsed['servo_rc_pwm'] = np.array(unpack('HHHHHH', data[80*2: 80*2+6*2]), dtype=np.uint16)

    send_num = unpack('B', data[172:173])[0]
    control_gain[sendnum] = unpack('f', data[44*4: 44*4+4])[0]

    return parsed

def relocate_head():
    while head + step <= offset:
        if buf[head] == 0x82:
            data = buf[head:head+step]
            if verify_data(data):
                return
        head += 1

def flush():
    read = 0
    while head + step <= offset:
        data = buf[head:head+step]
        if not verify_data(data):
            relocate_head()
            continue;
        parsed = parse_data(data)
        for key in parsed:
            log[key].append(parsed[key])
        read += 1
    return read

def animate(frameno):
    read_from_serial(181*5)
    """
    x = mu + sigma * np.random.randn(10000)
    n, _ = np.histogram(x, bins, normed=True)
    for rect, h in zip(patches, n):
        rect.set_height(h)
    """
"""
mu, sigma = 100, 15
fig, ax = plt.subplots()
x = mu + sigma * np.random.randn(10000)
n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
"""
ani = animation.FuncAnimation(fig, animate, blit=False, interval=10,
                              repeat=True)
plt.show()