from dotenv import load_dotenv
load_dotenv()

import socket
from collections import namedtuple
import struct
from enum import IntEnum
import deepspeech
import numpy as np
import os
import time

class MessageType(IntEnum):
  AUDIO_START = 0
  AUDIO_END = 1
  AUDIO_DATA = 2
  INFERRED_START = 3
  INFERRED_DATA = 4
  INFERRED_END = 5

TCP_IP = os.getenv("INFERRER_TCP_IP")
TCP_PORT = int(os.getenv("INFERRER_TCP_PORT"))

MODEL_PATH = "models/deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "models/deepspeech-0.9.3-models.scorer"

ds = deepspeech.Model(MODEL_PATH)
ds.enableExternalScorer(SCORER_PATH)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

Message = namedtuple("Message", "type length data")


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap

@timing
def infer(audio_data: bytearray) -> str:
  audio = np.frombuffer(audio_data, dtype=np.int16)
  np.timedelta64
  infered_text = ds.stt(audio)
  return infered_text


def send_text(conn: socket.socket, text: str):
  conn.send(struct.pack("BH1020s", MessageType.INFERRED_START, 0, b""))
  for i in range(0, len(text), 1020):
    chunk = text[i:i+1020]
    conn.send(struct.pack("BH1020s", MessageType.INFERRED_DATA, len(chunk), bytes(chunk, "utf-8")))
  conn.send(struct.pack("BH1020s", MessageType.INFERRED_END, 0, b""))


while True:
  conn, addr = s.accept()
  audio_data = bytearray()
  print("connection from", addr)

  while True:
    data, addr = conn.recvfrom(1024)
    
    unpacked = struct.unpack("BH1020s", data)
    message = Message._make(unpacked)
    if (message.type == MessageType.AUDIO_START):
      print("started receiving")
      audio_data = bytearray()
    if (message.type == MessageType.AUDIO_END):
      print("finished receiving")
      text = infer(audio_data)
      print("inferred: ", text)
      send_text(conn, text)
      audio_data = bytearray()
    if (message.type == MessageType.AUDIO_DATA):
      audio_data.extend(message.data[0:message.length])