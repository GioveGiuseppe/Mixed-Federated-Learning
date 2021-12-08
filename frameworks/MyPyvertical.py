import torch
from torchvision import datasets, transforms
from torch import nn, optim
from torchvision.transforms import ToTensor
import syft as sy
import datetime as dt
import os

import sys                
sys.path.append('../')
from src.dataloader import VerticalDataLoader
#from src.psi.util import compute_psi
from src.psi.util import *
from src.utils import add_ids
from src.future import dataset as ds



class SplitNN:
    def __init__(self, models, optimizers):
        self.models = models
        self.optimizers = optimizers

        self.data = []
        self.remote_tensors = []

    def forward(self, x):
        data = []
        remote_tensors = []

        data.append(self.models[0](x))

        if data[-1].location == self.models[1].location:
            remote_tensors.append(data[-1].detach().requires_grad_())
        else:
            remote_tensors.append(
                data[-1].detach().move(self.models[1].location).requires_grad_()
            )

        i = 1
        while i < (len(self.models) - 1):
            data.append(self.models[i](remote_tensors[-1]))

            if data[-1].location == self.models[i + 1].location:
                remote_tensors.append(data[-1].detach().requires_grad_())
            else:
                remote_tensors.append(
                    data[-1].detach().move(self.models[i + 1].location).requires_grad_()
                )

            i += 1

        data.append(self.models[i](remote_tensors[-1]))


        self.data = data
        self.remote_tensors = remote_tensors

        return data[-1]

    def backward(self):
        for i in range(len(self.models) - 2, -1, -1):
            if self.remote_tensors[i].location == self.data[i].location:
                grads = self.remote_tensors[i].grad.copy()
            else:
                grads = self.remote_tensors[i].grad.copy().move(self.data[i].location)

            self.data[i].backward(grads)

    def zero_grads(self):
        for opt in self.optimizers:
            opt.zero_grad()

    def step(self):
        for opt in self.optimizers:
            opt.step()    




def PyvProcess(data,models,optimizers,settings):

	hook = sy.TorchHook(torch)                
	print("loading data")
	dataloader = VerticalDataLoader(data, batch_size = settings["batch_size"]) 

	print("Private set intersection")
	# Compute private set intersection
	client_items = dataloader.dataloader1.dataset.get_ids()
	server_items = dataloader.dataloader2.dataset.get_ids()

	client = Client(client_items)
	server = Server(server_items)

	setup, response = server.process_request(client.request, len(client_items))
	intersection = client.compute_intersection(setup, response)

	# Order data
	dataloader.drop_non_intersecting(intersection)
	dataloader.sort_by_ids()    
	
	#data ready here-----------------------------------------------------------

	torch.manual_seed(settings["torch_seed"])

	# create some workers
	alice = sy.VirtualWorker(hook, id="alice")
	bob = sy.VirtualWorker(hook, id="bob")

	# Send Model Segments to model locations
	model_locations = [alice, bob]
	for model, location in zip(models, model_locations):
	    model.send(location)


	#Instantiate a SpliNN class with our distributed segments and their respective optimizers
	splitNN = SplitNN(models, optimizers)

	params= []
	names= []
	params2= []
	names2= []

	def train(x, target, splitNN, save):

		#1) Zero our grads
		splitNN.zero_grads()

		#2) Make a prediction
		pred = splitNN.forward(x)
		
		len_layers0 = 0
		len_layers1 = 0	
		
		# collect parameters
		if (save==True):		 
		 for name,param in splitNN.models[0].named_parameters():
		  params.append(param)
		  names.append(name)
		  len_layers0 += 1		  
		 	  
		 for name, param in splitNN.models[1].named_parameters():
		  params2.append(param)
		  names2.append(name)
		  len_layers1 += 1
		  

		  		
		#3) Figure out how much we missed by
		criterion = nn.NLLLoss()
		loss = criterion(pred, target)

		#4) Backprop the loss on the end layer
		loss.backward()
		
		#5) Feed Gradients backward through the nework
		splitNN.backward()

		#6) Change the weights
		splitNN.step()
			
		return loss, pred, len_layers0, len_layers1


	epochs= settings["epochs"]
	save = False
	
	print("starting training at:"+ str(dt.datetime.now()))
	for i in range(epochs):
	    running_loss = 0
	    correct_preds = 0
	    total_preds = 0
	    	    
	    if i==epochs-1:
	      save = True

	    for (data, ids1), (labels, ids2) in dataloader:
	        # Train a model
	        data = data.send(models[0].location)
	        data = data.view(data.shape[0], -1)
	        labels = labels.send(models[-1].location)

	        # Call model
	        loss, preds, len_layers0, len_layers1 = train(data, labels, splitNN, save)

	        # Collect statistics
	        running_loss += loss.get()
	        correct_preds += preds.max(1)[1].eq(labels).sum().get().item()
	        total_preds += preds.get().size(0)
	        
	    
	    print(f"Epoch {i} - Training loss: {running_loss/len(dataloader):.3f} - Accuracy: {100*correct_preds/total_preds:.3f}")


	model = []
	
	for i in range (len_layers0, 0, -1):
	  model.append(params[-i].get())
	  
	for i in range (len_layers1, 0, -1):
	  model.append(params2[-i].get())
	
	if os.path.exists("demofile.txt"):
         os.remove("model")
	
	print("saving updated model")  
	torch.save(model,"model")

	print ("end process: "+ str(dt.datetime.now()))
                
                
                
                
