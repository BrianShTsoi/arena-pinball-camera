# Some guys' code
# import time
# import pigpio

# SDA=18
# SCL=19

# I2C_ADDR=0x13

# def i2c(id, tick):
#     global pi

#     s, b, d = pi.bsc_i2c(I2C_ADDR)
#     if b:
#         if d[0] == ord('t'):

#             print("sent={} FR={} received={} [{}]".
#                format(s>>16, s&0xfff,b,d))

#             s, b, d = pi.bsc_i2c(I2C_ADDR, 'ABCDE')

#         elif d[0] == ord('d'):

#             print("sent={} FR={} received={} [{}]".
#                format(s>>16, s&0xfff,b,d))

#             s, b, d = pi.bsc_i2c(I2C_ADDR, 'EDCBA')

# pi = pigpio.pi()

# if not pi.connected:
#     exit()

# # Respond to BSC slave activity

# pi.set_pull_up_down(SDA, pigpio.PUD_UP)
# pi.set_pull_up_down(SCL, pigpio.PUD_UP)

# e = pi.event_callback(pigpio.EVENT_BSC, i2c)

# pi.bsc_i2c(I2C_ADDR) # Configure BSC as I2C slave

# time.sleep(600)

# e.cancel()

# pi.bsc_i2c(0) # Disable BSC peripheral

# pi.stop()

# Some other guy's code
#!/usr/bin/env python

import time
import pigpio

I2C_ADDR=9

def i2c(id, tick):
    print("detect event i2c")
    global pi

    s, b, d = pi.bsc_i2c(I2C_ADDR)

    if b:
        print(d[:-1].decode())

pi = pigpio.pi()

if not pi.connected:
    print("Not connected")
    exit()

# Respond to BSC slave activity

e = pi.event_callback(pigpio.EVENT_BSC, i2c)

pi.bsc_i2c(I2C_ADDR) # Configure BSC as I2C slave
time.sleep(600)

e.cancel()
pi.bsc_i2c(0) # Disable BSC peripheral
pi.stop()