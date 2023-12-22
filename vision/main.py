"""Python main Project P&P

alle functies kunnen vanaf hier aangeroepen worden

"""

import snap7
from math import sin, cos, tan, pie, sqrt, atan2
import numpy as np
import struct
import cv2
import TCP_Connectie as TCP 
import Hoekdetectie_v3 as HK3
import Randdetectie as RD 

def colors(): # hier ergens moet een ID verkregen worden, 1-7 voor welk puzzelstukje het is
    colors = {
        'rood': ([0, 100, 100], [10, 255, 255]),
        'blauw': ([100, 100, 100], [130, 255, 255]),
        'groen': ([40, 100, 100], [80, 255, 255]),
        'paars': ([130, 100, 100], [170, 255, 255]),
        'oranje': ([10, 100, 100], [25, 255, 255]),
        'wit': ([0, 0, 200], [180, 50, 255])
    }



plc = TCP.setup_plc() # setup connectie tussen plc en python, verbinding maken

# hiertussen komen calls naar programma HK3 en RD 
# uiteindelijk komen er 4 variablen naar voren
"""
a   - X coor
b   - Y coor
c   - O coor  (Hoek)
d   - ID 
"""
# worden verzonden met deze functie
TCP.send_CMD(plc, a, b, c, d)
