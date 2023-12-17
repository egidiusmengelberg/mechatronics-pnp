"""
Example code to connect to a Siemens PLC through snap7. Code can be used as an example and to be added to the OpenCV
project.
	@author: F. Goedhart - HHS
	@date: 13-12-2023

Code based on examples from video's:
	https://www.youtube.com/watch?v=Eo8NyNE1bRY
	https://www.youtube.com/watch?v=xSTfmCdepyw

Functions write_bool and read_bool are based on:
	https://github.com/gijzelaerr/python-snap7/blob/master/example/boolean.py
	the minimum amount of data being read or written to a plc is 1 byte

Other functions are based on:
	https://buildmedia.readthedocs.org/media/pdf/python-snap7/latest/python-snap7.pdf
	Python snap7 documentation

General Constraints:
	PLC
		get/put get has to be enabled in PLC configuration
			- Properties of CPU -> Protection & Security -> Connection Mechanisms -> Check "Permit access with PUT/GET."
		Virtual adapter from plc sim advanced has to be used, or real controller
		DB cannot be optimized
			- Properties of DB -> Attributes -> Uncheck "Optimized block access"
	Python installed packages
		- python-snap7
		- setuptools
"""

# Import of library's
import snap7  # For PLC communication
import struct  # For struct pack and unpack commands to align big and little endian

# Initialization - Change IP to IP of the PLC
plc = snap7.client.Client()  # Create a PLC client
plc.connect('192.168.0.21', 0, 1)  # Connect to client using: IP address, rack and slot


def write_bool(db_number, start_offset, bit_offset, value):  # To write 1 bit to a specific variable in a DB
    reading = plc.db_read(db_number, start_offset, 1)  # (db number, start offset, read 1 byte)
    snap7.util.set_bool(reading, 0, bit_offset, value)  # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
    plc.db_write(db_number, start_offset, reading)  # write back the bytearray and now the boolean value is changed in the PLC.
    return None


def read_bool(db_number, start_offset, bit_offset):  # To read 1 bit from a specific variable in a DB
    reading = plc.db_read(db_number, start_offset, 1)
    a = snap7.util.get_bool(reading, 0, bit_offset)
    # print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
    return a


def write_int_db(db_number, start_address, value):  # To write 1 int to a specific variable in a DB
    plc.db_write(db_number, start_address, bytearray(struct.pack('>H', value)))  # big-endian
    return None


def write_lreal_db(db_number, start_address, value):  # To write 1 Lreal to a specific variable in a DB
    plc.db_write(db_number, start_address, bytearray(struct.pack('>d', value)))  # big-endian
    return None


# Example usages of the functions is displayed below. To be functional a DB18 in the Siemens project must be created.
# If the DB number changes, the db number used for the commands should also change. The offset is calculated when the
# PLC code is compiled based on the Data type size and is not set by the user.

"""
DB18:
 Name			Data type	Offset
 test_int		Int			0.0
 test_float		LReal		2.0
 test_bit		Bool		10.0
"""

# Read 1 bit from PLC offset 10.0, flip it, write it back.
if 1 == read_bool(18, 10, 0):  # Read DB18 bit 10.0 and if bit = 1
    write_bool(18, 10, 0, 0)  # Write 0 to DB18 bit 10.0
else:  # else bit = 0
    write_bool(18, 10, 0, 1)  # Write 1 to DB18 bit 10.0

# Write an int to DB18 offset 0
write_int_db(18, 0, 1337)

# Write a Lreal to DB18, offset 2
write_lreal_db(18, 2, 1234567.89)
