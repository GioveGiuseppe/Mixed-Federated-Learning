import tqdm
import sys
import os
from wrapper2 import *
import time

def convert4to6(ipv4):
  numbers = list(map(int, ipv4.split('.')))
  return('0:0:0:0:0:FFFF:{:02x}{:02x}:{:02x}{:02x}'.format(*numbers))

def client(ipv4):
  c =  FlwrProcess() 
  c.start_client(convert4to6(ipv4), defaultModel = True)
  
def server(ipv4):
  h = FlwrProcess() 
  h.start_server(convert4to6(ipv4))
  
  
if __name__ == "__main__":
  ipv4 = sys.argv[1]
  if sys.argv[2] == "1":
    server(ipv4)
  else:
    client(ipv4)
