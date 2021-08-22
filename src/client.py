import socket
import struct
from collections import namedtuple
from enum import IntEnum

class MessageType(IntEnum):
  START = 0
  END = 1
  DATA = 2

Message = namedtuple("Message", "type length data")

TCP_IP = "192.168.1.201"
TCP_PORT = 5006
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((TCP_IP, TCP_PORT))
s.send(struct.pack("BH1020s", MessageType.START, 0, b""))
s.send(struct.pack("BH1020s", MessageType.DATA, len(b"hello world"), b"hello world"))
s.send(struct.pack("BH1020s", MessageType.END, 0, b""))

while True:
  data, addr = s.recvfrom(1024)
  unpacked = struct.unpack("BH1020s", data)
  message = Message._make(unpacked)
  print(message.data[0:message.length])
  if (message.type == MessageType.END):
    break

s.close()