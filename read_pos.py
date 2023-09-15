from can_rm import *
import time
# CAN
port = 'can1'
id = 32
can_rm = CANRM(port, id)

# calibrating
# can_jd.calibrate_slopes()

# Acclerations
while True:

    pos = can_rm.get_position()

    print(f'{{"Position":{round(pos,4)}}}')
    time.sleep(0.1)
