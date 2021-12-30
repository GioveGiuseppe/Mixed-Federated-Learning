# What is mixed-federated-learning
It's a process that combine both the well established type of fl (vertical and horizontal) in a unique coherent process.  
This allows to exploit all the benefits of the two type of fl, thus allowing for great flexibility.  

This tool uses [Flower](https://flower.dev/) and [OpenMined/pyvertical](https://github.com/OpenMined/PyVertical) as fl libraries.  
The src folder is the source code of the Pyvertical framework.

# Dependencies that must be installed installed:

pip install tensorflow  
pip install flwr  
pip install PySimpleGUI  
pip install tqdm   
pip install openmined.psi  
pip install syft==0.2.5  
pip install opencv-python  
pip install opencv-contrib-python  
sudo apt-get install -y libgl1-mesa-dev  


# How to use.

*Note: This tool does not work in local. Only via socket on multiple machines*

## Starting the main server.
First of all you need to start the main server which is gonna send the configuration files for the process to all clients.  
The main server is also gonna deliver the updated model to all clients at the start of every mixed fl round.  
You can use the graphical user interface (newgui.py) to create you nodes and groups, and execute the main server function.    
You can also use the function execute_M_groups() in fl_multiProcess.py to manually start the main server and execute the mixed fl process in a larger context.  

## Starting the clients.
To start a client and have it be part of the process, you need to execute the fl_multiProcess.py file with the following args from command line.  

Argument 1:
- 0 for vertical fl
- 3 for mixed client
- 4 for the central server

Argument 2: ipv4 address of the main server  

*Note: The horizontal group is not fully tested*


## Files
Frameworks Folder.| Holds wrapped frameworks. Its what executes the real FL processes.  
Partition Folder.| Used to create multiple partitions of a data set.  
src Folder| pyvertical source code.  

comm prot.py| Code for the implementation of a Server-client system to exchange files.  
Config.json| Configuration file for the mixed process.  
fl_multiprocess.py| MAIN. Contain the logic for the execution and coordination of the mixed fl process.  
loadDataset.py| Utility library to create a custom dataset usable by flwr and pyvertical from raw data and images.  
myguy/new gui.py| Old Gui for the node management.  
wrapper2.py| Wrapper of the frameworks. Also hold the conversion functions between pyvertical and flower.  


## Configuration file.
 
  "data_path": path to the data to use (same for all the nodes),  
  "labels_path": path to the data related labels (same for all the nodes),  
  "data_num": number of data to use for training,  
  "test_num": number of data to use for testing,   
  "num_clients": total number of clients nodes,  
  "mixed_rounds": number of rounds of the mixed process,  
  "rounds": number of round of the vertical and horizontal fl processes,  
    
  Data related to the machine learning process. Change it based on the used dataset  
  "sizeX": 28,  
  "sizeY": 28,  
  "batch_size": 128,  
  "learning_rate": 0.003,  
    
  "nodes" : ["put the ipv4 addresses of your nodes heres"]  


