"""
To use the wrapper you have to specify:

1)The fl parameters (from the config file)
2)The object that contains the dataset
3)The pytorch and tensorflow NeuralNetworks (hard-coded)
4)The functions for the Models translation Pytorch <-> Tensorflow (hard-coded for the specific Neural-Networks since its not completely generilized)
"""

import json
from frameworks.MyFlower import * 
from frameworks.MyPyvertical import *
from loadDataset import MnistDataset as testingDataset 
from loadDataset import CustomMatDataset
import os
import torch
import tensorflow as tf
from tensorflow import keras
import numpy as np

class wrapper():
    def __init__(self, configFile = "config.json"):
      with open (configFile) as f: 
        self.settings = json.load(f)
    
    #create the right object to contain the data to be feeded
    def choose_data (self): 
      #Load data into dataloader
      data_path = self.settings["data_path"]
      if self.settings["labels_path"]:
         labels_path = self.settings["labels_path"]
      
      if data_path.endswith(".gz"):
        dataset = testingDataset(dataPath = data_path, labelPath = labels_path ,num_images=self.settings["data_num"], start = self.settings["start"])
        (x_train, y_train) = dataset.getDataset() 
        (x_test, y_test) = (x_train[:self.settings["test_num"]], y_train[:self.settings["test_num"]])
        return (x_train, y_train,x_test, y_test)
      else:
        dataset = CustomMatDataset(path = data_path , num_images=self.settings["data_num"], start = self.settings["start"])
        (x_train, y_train) = dataset.getDataset() 
        (x_test, y_test) = (x_train[:self.settings["test_num"]], y_train[:self.settings["test_num"]])
        return (x_train, y_train,x_test, y_test)
        


class PyProcess(wrapper):
    def execute(self, fromtf = False):
      #Load data into dataloader
      data = self.choose_data()
      model, optimizer = PyTorchModel(self.settings, fromtf)  
      print("starting pyvertical processes")
      PyvProcess(data, model, optimizer, self.settings)  
      

    def choose_data (self): 
      #Load data into dataloader
      data_path = self.settings["data_path"]
      if self.settings["labels_path"]:
         labels_path = self.settings["labels_path"]
      if data_path.endswith(".gz"):
        return add_ids(testingDataset)(toTensor = True, dataPath=data_path, labelPath=labels_path, num_images=self.settings["data_num"], 
      start=self.settings["start"])
      else:
        return add_ids(CustomMatDataset)(toTensor = True, path=data_path, num_images=self.settings["data_num"], 
      start=self.settings["start"])


class FlwrProcess(wrapper):
    def start_server(self, server_ip = "[::]:8080" ):
      print("starting flower server")
      Myserver(self.settings, server_ip)
    
    def start_client(self, server_ip = "[::]:8080", defaultModel = False):
      print("starting flower processes")
      (x_train, y_train,x_test, y_test) = self.choose_data()
      model, optimizer = FlwrModel(self.settings,defaultModel)
      Myclient(x_train, y_train,x_test, y_test, model, optimizer, self.settings, server_ip)
      


class MixedProcess(FlwrProcess):   
    def start_client(self, server_ip = "[::]:8080"):
      print("starting mixed processes")
      (x_train, y_train,x_test, y_test) = self.choose_data()
      model, optimizer = torch_to_tf(self.settings)
      Myclient(x_train, y_train,x_test, y_test, model, optimizer, self.settings,server_ip)










    
#PyVertical model-------------------------------------------------------------------------------------

def PyTorchModel(settings, fromtf = False):
  # Define our model segments/Neural network------------------------------
  input_size = 28*28 #settings[sizeX]*settings[sizeY]
  hidden_sizes = [128, 640]
  output_size = 10

  models = [
  nn.Sequential(
  nn.Linear(input_size, hidden_sizes[0]),
  #nn.ReLU(),
  nn.Linear(hidden_sizes[0], hidden_sizes[1]),
  #nn.ReLU(),
  ),
  nn.Sequential(nn.Linear(hidden_sizes[1], output_size), nn.LogSoftmax(dim=1)),
  ]
  models2 = models

  if fromtf:
    models2 = tf_to_torch(models)

  # Create optimizers for each segment and link to them
  optimizers = [
  optim.SGD(model.parameters(), lr=settings["learning_rate"],)
  for model in models
  ]

  print (models2)

  return models2, optimizers


	
#Flower model--------------------------------------------------

def FlwrModel(settings, defaultModel = False):
  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128,activation='relu'),
    tf.keras.layers.Dense(640,activation='relu'),
    tf.keras.layers.Dense(10)
  ])
  
  if not defaultModel:
    model = loadmodelparams(model)

  optimizer=tf.keras.optimizers.Adam(settings["learning_rate"])
  
  return model, optimizer


def loadmodelparams(model):
  params = torch.load("tfmodel")

  modelk = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(input_shape=(28, 28)),
      tf.keras.layers.Dense(128,activation='relu',kernel_initializer= tf.constant_initializer(params[0])),
      tf.keras.layers.Dense(640,activation='relu',kernel_initializer= tf.constant_initializer(params[1])),
      tf.keras.layers.Dense(10,kernel_initializer= tf.constant_initializer(params[2]))
  ])
  
  return modelk

  

"""model conversion functions -----------------------------------------------------------------------------------------------""" 

def torch_to_tf(settings):

  temp=torch.load("model") 


  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128,activation='relu',kernel_initializer= tf.constant_initializer(temp[0].detach().numpy()), bias_initializer=tf.constant_initializer(temp[1].detach().numpy())),
    
    tf.keras.layers.Dense(640,activation='relu',kernel_initializer= tf.constant_initializer(temp[2].detach().numpy()), bias_initializer=tf.constant_initializer(temp[3].detach().numpy())),
    
    tf.keras.layers.Dense(10,kernel_initializer= tf.constant_initializer(temp[4].detach().numpy()), bias_initializer=tf.constant_initializer(temp[5].detach().numpy()))
  ])

  with open ("config.json") as f: 
     settings = json.load(f)
  
  optimizer=tf.keras.optimizers.Adam(0.001)
  return model, optimizer


def tf_to_torch(net):
  model = torch.load("model")
  vmodel=net

  i=0
  for x in net[0]:
    x.weight = nn.Parameter(torch.Tensor(np.reshape (np.ravel (model[i].detach().numpy()), (x.weight.shape) )))
    i+=2
  for x in net[1]:
    x.weight = nn.Parameter(torch.Tensor(np.reshape (np.ravel (model[i].detach().numpy()), (x.weight.shape) )))
    break

  return vmodel
















#testing
  
import sys
  
if __name__ == "__main__":
  
  if sys.argv[1] == "0":
    h = FlwrProcess() 
    h.start_server()  
    for i in range(2):
      h.start_server()
  else:   
    v = PyProcess()
    h = MixedProcess()
    
    v.execute()  
    h.start_client()
      
    for i in range(2):   
      v.execute(True)  
      h.start_client()  
