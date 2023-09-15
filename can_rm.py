import canopen
import numpy as np
import time
import os

CALIBRATING_TIME = 5
EDS_FILE = os.path.dirname(os.path.realpath(__file__)) +\
    '/RM9000.eds'

PI = 3.14159


class CANRM():
    def __init__(self, port='can1', node_id=32, speed0=0):
        network = canopen.Network()
        network.connect(bustype='socketcan', channel=port)
        self.node = network.add_node(node_id, EDS_FILE)
        self.steps_per_revolution = self.node.sdo[0x6001].raw
        self.measure_range = self.node.sdo[0x6002].raw
        

    def get_raw_position(self):
        pos = self.node.sdo[0x2000].raw
        return pos

    def get_rev_position(self):
        # number of revolutions
        rev_pos = self.get_raw_position()/self.steps_per_revolution
        return rev_pos

    def get_rad_position(self):
        rad_pos = self.get_rev_position()*2*PI
        return rad_pos

    def activate_speed(self):
        self.node.sdo[0x3010][0x1].raw = 0x1 
        print("Speed activated")

    def deactivate_speed(self):
        self.node.sdo[0x3010][0x1].raw = 0x0
        print("Speed deactivated")

    def get_raw_speed(self):
        speed = self.node.sdo[0x6030][0x1].raw
        return speed

    def get_rpm_speed(self):
        rpm = self.get_raw_speed()*self.steps_per_revolution*60
        return rpm

    def dimensionate(self):
        print("Esto te permitirá dimensionar el sensor para la distancia de funcionamiento")
        r = float(input("Inserta el radio final en cm: "))
        max_rev = self.measure_range/self.steps_per_revolution
        max_dist = max_rev*2*PI*r/100
        print("\n Datos calculados")
        print(f"Máximas revoluciones: {max_rev} rev")
        print(f"Máxima distancia: {max_dist} m")



    # Funcion para calibrar el slope en x e y del JD y poder corregir la funcion get_slopes
    def calibrate_slopes(self):
        # obtener una media de 20 datos para hacer el promedio para calibrar
        print("calibrating...")
        x = 0
        y = 0
        for i in range(10*CALIBRATING_TIME):
            x1, y1 = self.get_slopes()
            x += x1
            y += y1
            time.sleep(0.01)
        x = x/(10*CALIBRATING_TIME)
        y = y/(10*CALIBRATING_TIME)

        self.slope_x = x
        self.slope_y = y
