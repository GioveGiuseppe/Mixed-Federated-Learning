# What is mixed-federated-learning
It's a process that combine both the well established type of fl (vertical and horizontal) in a unique coherent process.  
This allows to exploit all the benefits of the two type of fl, thus allowing for great flexibility.  

This tool uses [Flower](https://flower.dev/) and [OpenMined/pyvertical](https://github.com/OpenMined/PyVertical) as fl libraries.

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

## Starting the main server.
First of all you need to start the main server which is gonna send the configuration files for the process to all clients.  
The main server is also gonna deliver the updated model to all clients at the start of every mixed fl round.  
You can use the graphical user interface (newgui.py) to create you nodes and groups, and execute the main server function.    
You can also use the function execute_M_groups() in fl_multiProcess.py to manually start the main server and execute the mixed fl process in a larger context.  

## Starting the clients.
To start a client and have it be part of the process, you need to execute the fl_multiProcess.py file with the following args from command line.  

Argument 1:
- 0 for vertical fl
- 1 for horizontal group server
- 2 for horizontal group client
- 3 for mixed client

Argument 2: ipv4 address of the main server
