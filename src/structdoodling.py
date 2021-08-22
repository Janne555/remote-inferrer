import struct
from collections import namedtuple

TYPE_START = 0
TYPE_END = 1
TYPE_DATA = 2

Message = namedtuple("Message", "type id length data")
# type = 1, id = 2, length = 2, data = 1018

packed = struct.pack("BHH1018s", TYPE_START, 123, len(b"hello world"), b"hello world")
unpacked = struct.unpack("BHH1018s", packed)
message = Message._make(unpacked)

print(len(packed))