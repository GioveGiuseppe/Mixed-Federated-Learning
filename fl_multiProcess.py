import socket
import tqdm
import sys
import os
from comm_prot import *
from wrapper2 import *
import time
import datetime



port = 65432

def convert4to6(ipv4):
  numbers = list(map(int, ipv4.split('.')))
  return('0:0:0:0:0:FFFF:{:02x}{:02x}:{:02x}{:02x}'.format(*numbers))

def nr():
  with open('config.json', "r") as f:
   data = json.load(f) 
  return data["mixed_rounds"]  

def execute_M_Groups(nodes=['172.31.14.68', '172.31.14.68', '172.31.14.92', '172.31.14.92','172.31.8.49','172.31.8.49','172.31.10.224','172.31.10.224'], port=65432 ):
 hostname = socket.gethostname()
 host = socket.gethostbyname(hostname)
 #ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]#ipv6 address self
 ipv6 = convert4to6(host)

 with open('config.json', "r") as f:
  data = json.load(f)
 
 data["ipv6"] = ipv6
  
 with open('config.json', 'w') as f:
  json.dump(data, f, indent=2)

 for x in range(data["mixed_rounds"]+1):
   nodesT = nodes.copy()
   
   server = MyServer()
   server.Open(host, port)
   print("i nodi sono")
   print(nodesT)
   
   i = 0  
   while nodesT:     

    print("server listening")
    
    #open a connection to send config.json file to the nodes  
    Client, address = server.Socket.accept()
    print("current client " + str(Client.getpeername()))   
    if Client.getpeername()[0] in nodesT:
      print("Connection established to " + str(Client.getpeername()))      
      fname = "config.json"
      filesize = os.path.getsize("config.json")      
      if server.send_file(Client, fname,filesize):
        nodesT.remove(Client.getpeername()[0])
      Client.close()
   
     
    i += 1
    #open a connection to send models files to the nodes      
    Client, address = server.Socket.accept()
    print("current client " + str(Client.getpeername()))
    if Client.getpeername()[0] in nodesT:
      print("Connection established to " + str(Client.getpeername()))
      fname = "model"+str(i)
      if not os.path.exists(fname):
        fname = "model"
      
      filesize = os.path.getsize(fname)
      if server.send_file(Client, fname,filesize):
        nodesT.remove(Client.getpeername()[0])
      Client.close()
    
    print("all files sent to client")   
    print("all files sent to all clients of the group")   
   
   server.Socket.close()
   
   
   #time.sleep(10)
   h = MixedProcess() 
   h.start_server(ipv6)
   print("round ended at " + str(datetime.datetime.now()))
   

def receive_files(host,filename="tfmodel"):
    client = MyClient()
    client.Open(host,port)
    client.receive_file(client.Socket,"config.json")
    client.Socket.close()
    print("config ricevuto")
    
    client.Open(host,port)
    client.receive_file(client.Socket, filename)
    client.Socket.close() 
    print("modello tf ricevuto")

def get_ipv6_S():
  with open('config.json', "r") as f:
    data = json.load(f)
  ipv6 = data["ipv6"]
  return ipv6 

#vertical client
def vertical_client():
  host=sys.argv[2]#ipv4 address centraal server

  nrounds = -1    
  while True:
    nrounds+=1

    receive_files(host)
    v = PyProcess()
    if nrounds == 0:
      v.execute()
    else:
      v.execute(True)
    if (nrounds >= nr()):
      break
     
    h = MixedProcess()
    h.start_client(get_ipv6_S())
    time.sleep(3)
    
def horizontal():
 host = sys.argv[2]#ipv4 central cerver
 nrounds = -1
 while True:
  nrounds += 1  
  receive_files(host)
  
  time.sleep(5) 
  h2 = MixedProcess() 
  h2.start_client(get_ipv6_S())
  time.sleep(5)
  if (nrounds >= nr()):
    break
  


#Not fully tested-------------------

#horizontal-group server    
def horizontal_server():
 hostname = socket.gethostname()
 host = socket.gethostbyname(hostname)#ipv4 self
 #ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)#ipv6 self
 ipv6 = convert4to6(host)
 serverip = sys.argv[2]#ipv4 address central server

 nrounds = -1
 while True:
  nrounds +=1

  receive_files(serverip)
  time.sleep(1)
  
  for i in range (2):
   server = MyServer()
   server.Open(host,54321)
   Client = True

   while Client == True:
    Client, address = server.Socket.accept()
    print(Client)
   server.Socket.close() 
  
  #execute group horizontal fl as server
  h1 = FlwrProcess()
  h1.start_server(ipv6)
  
  time.sleep(1) 
  #execute main horizontal fl as a client
  h2 = FlwrProcess() 
  h2.start_client(get_ipv6_S())
  time.sleep(5)

  if (nrounds >= nr()):
    break




#horizontal-group client
def horizontal_client():

 host= sys.argv[2]#ipv4 central server 
 #ipv6 = sys.argv[3]#ipv6 local server
 
 hostname = socket.gethostname()
 local_ip = socket.gethostbyname(hostname)#ipv4 self
 print(local_ip)
 group_host="127.0.0.1" #ipv4 local server
 
 nrounds = -1
 while True:
  nrounds += 1 
  receive_files(host)
  with open('config.json', "r") as f:
    data = json.load(f)
  n=0

  
  while True:
    if "group"+str(n) in data and local_ip in data["group"+str(n)]:
     group_host = data["group"+str(n)][0] #("SERVER HORIZONTAL DA CONFIG.JSON")
     print(group_host)
     break
    n+=1
 
  ipv6 = convert4to6(group_host)
  time.sleep(1)
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connected = False
  
  
  while not connected:
   try:

    s.connect((group_host,54321)) #("SERVER HORIZONTAL DA CONFIG.JSON")
    connected = True
   except Exception as e:
    pass 

  time.sleep(2) 
  h1 = FlwrProcess()
  h1.start_client(ipv6)
  if (nrounds >= nr()):
    break 
#-------------------------------------------------




import sys

if __name__ == "__main__":
  if sys.argv[1] == "0":
    vertical_client()
  elif sys.argv[1] == "2":
    horizontal_client()
  elif sys.argv[1] == "1":
    horizontal_server()
  elif sys.argv[1] == "3":
    horizontal()
  else:
    execute_M_Groups()



  
