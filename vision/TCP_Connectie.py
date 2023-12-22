"""
Code based on examples from video's:
	https://www.youtube.com/watch?v=Eo8NyNE1bRY
	https://www.youtube.com/watch?v=xSTfmCdepyw

Functions write_bool and read_bool are based on:
	https://github.com/gijzelaerr/python-snap7/blob/master/example/boolean.py
	the minimum amount of data being read or written to a plc is 1 byte

Other functions are based on:
	https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
	Python snap7 documentation
"""

# Import of library's
import snap7  # For PLC communication
import struct  # For struct pack and unpack commands to align big and little endian

# Initialization - Change IP to IP of the PLC
def setup_plc():
    plc = snap7.client.Client()  # Create a PLC client
    try: (plc.connect('192.168.0.21', 0, 1))  # Connect to client using: IP address, rack and slot
    except:
        print("Could not connect to this IP adress")
    return plc


def write_bool(db_number, start_offset, bit_offset, value, plc):  # To write 1 bit to a specific variable in a DB
    reading = plc.db_read(db_number, start_offset, 1)  # (db number, start offset, read 1 byte)
    snap7.util.set_bool(reading, 0, bit_offset, value)  # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
    plc.db_write(db_number, start_offset, reading)  # write back the bytearray and now the boolean value is changed in the PLC.
    return None


def read_bool(db_number, start_offset, bit_offset, plc):  # To read 1 bit from a specific variable in a DB
    reading = plc.db_read(db_number, start_offset, 1)
    a = snap7.util.get_bool(reading, 0, bit_offset)
    # print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
    return a


def write_int_db(db_number, start_address, value, plc):  # To write 1 int to a specific variable in a DB
    plc.db_write(db_number, start_address, bytearray(struct.pack('>H', value)))  # big-endian
    return None


def write_lreal_db(db_number, start_address, value, plc):  # To write 1 Lreal to a specific variable in a DB
    plc.db_write(db_number, start_address, bytearray(struct.pack('>d', value)))  # big-endian
    return None

"""
to test:
PYthondata(DB18):
 Name			Data type	Offset
 test_int		Int			0.0
 test_float		LReal		2.0
 test_bit		Bool		10.0

# Read 1 bit from PLC offset 10.0, flip it, write it back.
if 1 == read_bool(18, 10, 0):  # Read PYthondata(DB18) bit 10.0 and if bit = 1
    write_bool(18, 10, 0, 0)  # Write 0 to PYthondata(DB18) bit 10.0
else:  # else bit = 0
    write_bool(18, 10, 0, 1)  # Write 1 to PYthondata(DB18) bit 10.0

# Write an int to PYthondata(DB18) offset 0
write_int_db(18, 0, 1337)

# Write a Lreal to PYthondata(DB18), offset 2
write_lreal_db(18, 2, 1234567.89)
"""

def XYZO_ID(plc):
	if 0== read_bool(18, 0.0, 0, plc):# stuurt 1 naar functie waardoor alle coordinaten op de uitgang worden gezet
		write_bool(18, 0.0, 1, plc)
	else:
		write_bool(18, 0.0, 0, plc) 	# zet het coorinaat ontvangen uit

def X_out(a, plc):
     write_lreal_db(18, 2.0, a, plc) # stuurt x

def Y_out(b, plc):
     write_lreal_db(18, 10.0, b, plc)# stuurt y

def Z_out(c, plc):
     write_lreal_db(18, 18.0, -191.500, plc)# stuurt z

def O_out(d, plc):
     write_lreal_db(18, 26.0, d, plc)# stuurt o (hoek)

def ID_out(e, plc):
     write_lreal_db(18, 34.0, e, plc)# stuurt ID van het puzzelstukje

def send_CMD(plc, a, b, d, e):
    XYZO_ID(plc)
    X_out(a, plc)
    Y_out(b, plc)
    O_out(d, plc)
    ID_out(e, plc)
    XYZO_ID(plc)

