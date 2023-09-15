from can_rm import CANRM
import time
# CAN
PORT = 'can1'
SENSOR_ID = 10


can_rm = CANRM(PORT, SENSOR_ID)

# calibrating
# can_jd.calibrate_slopes()

print(can_rm.dimensionate())
can_rm.activate_speed()
# Acclerations
try:
    while True:
        pos = can_rm.get_speed()

        print(f'{{"Vel":{round(pos,4)}}}')
        time.sleep(0.1)
except:
    can_rm.deactivate_speed()