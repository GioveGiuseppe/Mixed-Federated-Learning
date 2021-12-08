from loadDataset import *

n = 0
x = 5
numImg = 10000

for i in range (x):
 dataset = MnistDataset(num_images = numImg, start = numImg * n)
 data, labels = dataset.getDataset()
 saveCustomDataset(data,labels,"partition" +str(n)+ ".mat")
 n+=1
