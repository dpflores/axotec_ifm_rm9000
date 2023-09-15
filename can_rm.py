import canopen
import numpy as np
import time
import os

CALIBRATING_TIME = 5
EDS_FILE = os.path.dirname(os.path.realpath(__file__)) +\
    '/JD2xxx_v1.0.eds'
# Cargar archivo de configuración de dispositivo CANopen
g = 9.81

accel_resolution = g/1000
gyro_resolution = 0.1       # degrees/s

g_vector = np.array([0, 0, -g]).T

slope_resolutions = {"10": 0.01, "100": 0.1, "1000": 1}


class CANRM():
    def __init__(self, port='can1', node_id=32, speed0=0):
        network = canopen.Network()
        network.connect(bustype='socketcan', channel=port)
        self.node = network.add_node(node_id, EDS_FILE)
        self.slope_resolution = slope_resolutions[str(
            self.node.sdo[0x6000].raw)]
        self.speed = speed0
        self.slope_x = 0
        self.slope_y = 0

    def get_position(self):
        pos = self.node.sdo[0x2000].raw
        return pos


    def get_prop_accel(self):
        x = self.node.sdo[0x3403].raw * accel_resolution
        y = self.node.sdo[0x3404].raw * accel_resolution
        z = self.node.sdo[0x3405].raw * accel_resolution
        return x, y, z

    def get_prop_accel_vector(self):
        x = self.node.sdo[0x3403].raw * accel_resolution
        y = self.node.sdo[0x3404].raw * accel_resolution
        z = self.node.sdo[0x3405].raw * accel_resolution

        f = np.array([x, y, z]).T
        return f

    def get_gyro(self):
        x = self.node.sdo[0x3400].raw * gyro_resolution
        y = self.node.sdo[0x3401].raw * gyro_resolution
        z = self.node.sdo[0x3402].raw * gyro_resolution
        return x, y, z

    def get_slopes(self):
        x = self.node.sdo[0x6010].raw * self.slope_resolution - self.slope_x
        y = self.node.sdo[0x6020].raw * self.slope_resolution - self.slope_y
        return x, y

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

    def get_rot_grav(self):
        ''' Rotated gravity '''
        thetax_deg, thetay_deg = self.get_slopes()
        thetax = thetay_deg*np.pi/180
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(thetax), -np.sin(thetax)],
                       [0, np.sin(thetax), np.cos(thetax)]])

        thetay = -thetax_deg*np.pi/180
        Ry = np.array([[np.cos(thetay), 0, np.sin(thetay)],
                       [0, 1, 0],
                       [-np.sin(thetay), 0, np.cos(thetay)]])

        g_rotated = Ry@Rx@g_vector
        return g_rotated

    def get_accel(self):
        ''' Retorna el modulo de la aceleracion respecto al eje fijo, descontando el efecto de la gravedad
        en la aceleracion propia (proper acceleration)'''
        f = self.get_prop_accel_vector()
        g = self.get_rot_grav()
        r = f + g
        # r_norm = np.linalg.norm(r)
        return r

    def get_speed_stimation(self, iterations=4):
        start = time.time()
        accel_cumulative = 0
        for i in range(1, iterations+1):
            accel_raw = self.get_accel()
            accel_cumulative += accel_raw

        accel = accel_cumulative/iterations
        accel = np.round(accel, 1)

        end = time.time()

        delta = end-start
        self.speed += accel*delta

        self.speed_norm = np.linalg.norm(self.speed[0:1])

        return self.speed_norm
