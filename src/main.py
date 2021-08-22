import socket
from collections import namedtuple
import struct
from enum import IntEnum
import deepspeech
import numpy as np

class MessageType(IntEnum):
  START = 0
  END = 1
  AUDIO_DATA = 2
  INFERRED_TEXT = 3

TCP_IP = "127.0.0.1"
TCP_PORT = 5006

MODEL_PATH = "models/deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "models/deepspeech-0.9.3-models.scorer"

ds = deepspeech.Model(MODEL_PATH)
ds.enableExternalScorer(SCORER_PATH)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

Message = namedtuple("Message", "type length data")

while True:
  conn, addr = s.accept()
  audio_data = bytearray()

  while True:
    data, addr = conn.recvfrom(1024)
    unpacked = struct.unpack("BH1020s", data)
    message = Message._make(unpacked)
    if (message.type == MessageType.END):
      break
    if (message.type == MessageType.AUDIO_DATA):
      audio_data.extend(message.data[0:message.length])

  audio = np.frombuffer(audio_data, dtype=np.int16)
  infered_text = ds.stt(audio)
  print(infered_text)

  conn.send(struct.pack("BH1020s", MessageType.START, 0, b""))
  conn.send(struct.pack("BH1020s", MessageType.INFERRED_TEXT, len(infered_text), bytes(infered_text, "utf-8")))
  conn.send(struct.pack("BH1020s", MessageType.END, 0, b""))

  conn.close()

s.close()