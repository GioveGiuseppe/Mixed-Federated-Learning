from torch.utils.data import Dataset
import syft as sy  
import torch
from torchvision.transforms import ToTensor
from pathlib import Path
import os

import numpy as np
import gzip
from scipy.io import loadmat
import scipy.io as sc
import math

"""
Used to create a torchvision-like Dataset class.
Needed in PyVertical to feed the data to a wrapper class.
Neede in Flower to feed the data for the fl process
"""
class CustomDataset(Dataset):

    def __init__ (self, data, labels, toTensor=True, transform=ToTensor()):
        
        """Args:
             
             data (Numpy Array): Image Data
             labels (Numpy Array): Labels corresponding to each image
             transform (Optional): If any torch transform has to be performed on the dataset
             toTensor(Optional-bool): Tranform the data into torch tensor if needed. (Pyvertical)
             
        """
        
        #loading dataset                
        self.data = data #images
        self.targets = labels #labels
        self.target_transform = None
               
        #<For Pyvertical the data and target must be converted to torch tensors before it is returned by __getitem__ method
        if toTensor:
          self.to_torchtensor()
        
        #If any transforms have to be performed on the dataset
        self.transform = transform
    
        
    def to_torchtensor(self):        
        "Transform Numpy Arrays to Torch tensors."
        self.data=torch.from_numpy(self.data)
        self.labels=torch.from_numpy(self.targets)
    
        
    def __len__(self):
        """Required Method
            
           Returns:
           Length [int]: Length of Dataset/batches        
        """
        return len(self.data)
    

    def __getitem__(self, idx):     
        """Required Method
        
           The output of this method must be torch tensors since torch tensors are overloaded 
           with share() method which is used to share data to workers.
        
           Args:                 
                 idx [integer]: The index of required batch/example
                 
           Returns:                 
                 Data [Torch Tensor]:     The training examples
                 Target [ Torch Tensor]:  Corresponding labels of training examples         
        """  
        sample=self.data[idx]
        target=self.targets[idx]
                
        if self.transform:
            sample = self.transform(sample)

        return sample,target
       
    def getDataset (self):
        """ return the entire dataset via tuple"""
        return (self.data, self.targets )  
    


"""
sub-class of the CustomDataset class created specifically to load a slice of the mnist dataset OR
any mnist-like dataset saved in ubyte format.
"""
class MnistDataset(CustomDataset):
	def __init__(self, toTensor=False, image_size = 28, start = 0, num_images = 30000, dataPath = 'train-images.gz', labelPath = 'train-labels.gz', transform=ToTensor()):
	
		f = gzip.open(dataPath,'r')	
		#load data
		f.read(16)
		buf = f.read(image_size * image_size * (num_images + start))
		data = np.frombuffer(buf, dtype=np.uint8)#.astype(np.int64)
		data = data.reshape(num_images + start, image_size, image_size )

		#load labels
		f = gzip.open(labelPath,'r')
		f.read(8)
		labels = np.array([])
		for i in range(start,num_images+start):   
		    buf = f.read(1)
		    label = np.frombuffer(buf, dtype=np.uint8).astype(np.int64)
		    labels = np.append(labels,label)
		
		
		data = data[start :  num_images+start]
		
		super().__init__(data,labels,toTensor,transform)
         
      
"""
sub-class of the CustomDataset class created to load a generic dataset saved in .mat format

Args:
    sizex,sizey: dimentions of the images.
    path: file path containing the images as numpy.array
    num_images (Optional): load a slice of the dataset. 0 -> entire dataset gets loaded. 1/2 -> half data gets loaded
""" 
class CustomMatDataset(CustomDataset):
    def __init__(self, toTensor = False, sizex = 28, sizey = 28, path = "train.mat", start = 0,  num_images = 0, transform=ToTensor()):
      
      dataset = loadmat(path)
      labels = np.array(dataset['y'])
      labels = labels[0]
      data = np.array(dataset['X'])       
      
      #to load entire or half dataset
      if num_images == 0:
        num_images = len(labels)
      elif num_images == 0.5:
        num_images = len(labels)//2
            
      #load a slice  
      labels = labels[start: start + num_images]      
      data = data[start: start + num_images]
      
      super().__init__(data, labels , toTensor, transform)     



      
"""compose_dataset()
   transform a set of imgs to create an np.array holding the data that can be fed to the frameworks through the CustomMatDataset class and def saveCustomDataset() function

   input:
      directories: a list of the folders containing the images(currently only jpeg) divided in their respective
      classes (i.e  ["cat","dog","mouse"])
      path: the relative path to the folder containing the folders above

      output: (data,labels)
      data: the images in np.array form (shape (num_images,28,28) )
      labels: the integer labels in np.array form (shape (num_images,))
"""      

import os
import numpy as np
import cv2

def process_data (img_path, img_size = 28):
  img = cv2.imread(img_path , cv2.IMREAD_GRAYSCALE)
  img = cv2.resize(img , ( img_size , img_size ))
  return img

def compose_dataset (directories, path):
  data = []
  labels = []
  label = 0
  for directory in directories:
    label +=1
    for filename in os.listdir(path+"/"+directory): 
      if(filename.endswith(".jpeg")):
        data.append(process_data(os.path.join(path+"/"+directory, filename)))
        labels.append(label)

  return np.array(data)/255 , np.array(labels)
  

"""
saves a custom dataset in .mat format so it can be used after with these classes above     

input:
	data: an np.array that hold the data. ( for the framework the shape needs to be (num_images, len, heigh) greyscale )
	labels: an np.array that hold the labels. ( shape (num_images,1) )
	
	return: the dictionary holding the dataset
"""
def saveCustomDataset(data, labels, savepath = "train.mat"):
    # Create a dictionary
    adict = {}
    adict['X'] = data
    adict['y'] = labels
    sc.savemat(savepath, adict)
    
    return sc.loadmat(savepath)
    
      

 
 
 
 
 
 
 
 
 
 
