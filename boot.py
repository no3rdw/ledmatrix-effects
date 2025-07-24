import storage, board
from adafruit_neokey.neokey1x4 import NeoKey1x4
neokey = NeoKey1x4(board.I2C())
keys = neokey.get_keys()

if not any(keys):
	storage.remount("/", False) # WRITEABLE from local device when no keys pressed
else:
    storage.remount("/", True) # READ ONLY from local device when a key is pressed (writeable over USB, development mode)