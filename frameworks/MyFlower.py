import flwr as fl
import tensorflow as tf
import numpy as np
import torch
from typing import Callable, Dict, List, Optional, Tuple

def Myclient(x_train, y_train,x_test, y_test, model, optimizer, settings, server_ip = "[::]:8080"):
	class CifarClient(fl.client.NumPyClient):
	    def get_parameters(self):
	        return model.get_weights()

	    def fit(self, parameters, config):
	        print("setting weights")
	        model.set_weights(parameters)
	        print("fitting model")
	        model.fit(x_train, y_train, epochs=settings["fepochs"], batch_size=settings["batch_size"], 
	        steps_per_epoch=settings["steps_per_epoch"])#settings["epochs"]
	        return model.get_weights(), len(x_train), {}

	    def evaluate(self, parameters, config):
	        model.set_weights(parameters)
	        loss, accuracy = model.evaluate(x_test, y_test)
	        return loss, len(x_test), {"accuracy": accuracy}
	        
	
	
	model.compile(
	    optimizer=optimizer,
	    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
	    metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
	)
	connected = False
	while not connected:
	 try:
	  fl.client.start_numpy_client("["+server_ip+"]:8080", client=CifarClient())
	  connected = True
	 except Exception as e:
	  pass

  

def Myserver(settings, server_ip = "[::]:8080"):
	class SaveModelStrategy(fl.server.strategy.FedAvg):
		def conversion(self):
		 model = np.load("keras.npz")
		 temp = []
		 for x in model.files:
		  temp.append(model[x+".npy"])               
		 torch.save(temp,"tfmodel")
		   
		def aggregate_fit(
		 self,
		 rnd: int,
		 results: List[Tuple[fl.server.client_proxy.ClientProxy, fl.common.FitRes]],
		 failures: List[BaseException],
		) -> Optional[fl.common.Weights]:
		 aggregated_weights = super().aggregate_fit(rnd, results, failures)
		 if aggregated_weights is not None:
		    # Save aggregated_weights
		    print(f"Saving round {rnd} aggregated_weights...")
		    np.savez(f"keras.npz", *aggregated_weights)
		    self.conversion()
		    #temp = []
		    #for weight in (aggregated_weights):
		    #  temp.append(weight)
		    #torch.save(temp,"model")
		 return aggregated_weights
		 

		   

	def get_on_fit_config_fn() :
	    """Return a function which returns training configurations."""

	    def fit_config(rnd: int) :
	        """Return a configuration with static batch size and (local) epochs."""
	        config = {
	        "learning_rate": str(settings["learning_rate"]),
	        "batch_size": str(settings["batch_size"]),
		}
	        return config

	    return fit_config

	# Create strategy and run server
	strategy = SaveModelStrategy(
	     fraction_fit=0.7,
	     min_fit_clients=settings["num_clients"],
	     min_available_clients=settings["num_clients"],
	     on_fit_config_fn=get_on_fit_config_fn(),	 
	)
	fl.server.start_server("["+server_ip+"]:8080", config={"num_rounds": settings["rounds"]},strategy=strategy)





def Myserver2(settings):
	def get_on_fit_config_fn() :
	    """Return a function which returns training configurations."""

	    def fit_config(rnd: int) :
	        """Return a configuration with static batch size and (local) epochs."""
	        config = {
	        "learning_rate": str(settings["learning_rate"]),
	        "batch_size": str(settings["batch_size"]),
		}
	        return config

	    return fit_config

	strategy = fl.server.strategy.FedAvg(
	    fraction_fit=0.7,
	    min_fit_clients=settings["num_clients"],
	    min_available_clients=settings["num_clients"],
	    on_fit_config_fn=get_on_fit_config_fn(),
	)
	fl.server.start_server(config={"num_rounds": settings["rounds"]}, strategy=strategy)
