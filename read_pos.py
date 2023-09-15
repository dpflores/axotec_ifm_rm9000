from can_rm import CANRM
import time
# CAN
PORT = 'can1'
SENSOR_ID = 10


can_rm = CANRM(PORT, SENSOR_ID)

while True:
    pos = can_rm.get_raw_position()

    print(f'{{"Position":{round(pos,4)}}}')
    time.sleep(0.1)
