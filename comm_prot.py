import socket
import tqdm
import sys
import os


class CommProt():
  def __init__(self, SEP = "<SEPARATOR>" , BUFF = 4096):
   self.SEP = SEP
   self.BUFF = BUFF
 
  def send_file(self,conn,fname,fsize):
    info_file = f"{fname}{self.SEP}{fsize}".encode("utf-8")
    info_file_header = f"{len(info_file):<5}".encode ("utf−8")
    conn.send(info_file_header+info_file)
    #sending
    progress = tqdm.tqdm (range(fsize), f" Sending { fname }" , unit="B", unit_scale=True, unit_divisor=1024)
    with open(fname,"rb") as f:
      for _ in progress:
        #reading bytes from file
        bytes_read = f.read(self.BUFF)
        if not bytes_read:
          break
        conn.sendall(bytes_read)
        #update on progress bar
        progress.update(len(bytes_read))
      progress.close()
    print("file sent")
    return True
    

  def receive_file (self,conn, filename):
    info_file_header = conn.recv(5)
    print (info_file_header)
    if not len (info_file_header):
      print("Connection error")
      sys.exit()
    info_file_lenght = int(info_file_header.decode("utf-8").strip())
    #print (info_file_lenght)
    info_file = conn.recv(info_file_lenght).decode("utf-8")
    print(info_file)
    fname, fsize = info_file.split(self.SEP)
    print(fname, fsize)
    fname = os.path.basename(fname)
      
    fsize = int(fsize)
    path = os.getcwd()
    progress = tqdm.tqdm(range ( fsize ) , f" Receiving { fname } " , unit="B", unit_scale = True , unit_divisor = 1024)

    
    with open(fname, "wb") as f:
     while True:      
        bytes_read = conn.recv(self.BUFF)
        if not bytes_read:
          break
        f.write(bytes_read)
        
        progress.update(len(bytes_read))
     progress.close()
    #shutil.move(fname, path+"/clients_model/"+fname)
    print("file received") 
    return True 

class MyServer(CommProt):
  def Open(self,host,port):
    self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.Socket.bind((host, port))
    self.Socket.listen(5)
    #return ServerSocket

class MyClient(CommProt):
  def Open(self,host,port):
    self.Socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    self.Socket.connect((host, port))
    #return ClientMultiSocket


