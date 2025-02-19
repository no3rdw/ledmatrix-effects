import storage, board
#from adafruit_neokey.neokey1x4 import NeoKey1x4
#neokey = NeoKey1x4(board.I2C())
#keys = neokey.get_keys()

#if not keys[3]:
#	storage.remount("/", False)
#else:
storage.remount("/", True)