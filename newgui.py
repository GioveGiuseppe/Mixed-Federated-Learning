import PySimpleGUI as sg
import operator
import json
from fl_multiProcess import *
from event_handler import *

class Item():
  def __init__(self,gid,text):
    self.gid = gid
    self.ip = None
    self.group = None
    self.fl = "V"
    self.textid = text
    
  def move(self,graph, delta_x , delta_y, items=None):  
    graph.move_figure(self.gid, delta_x, delta_y)
    graph.move_figure(self.textid, delta_x, delta_y)
      
  def remove(self, graph, node):
    graph.delete_figure(self.textid)
    graph.delete_figure(node)
    
  def change_text(self,graph,text):
    self.ip = text
    graph.delete_figure(self.textid)
    self.textid = graph.draw_text(text, (graph.get_bounding_box(self.gid)[0][0]+50, graph.get_bounding_box(self.gid)[0][1]-20))
    graph.update()  
    
class Group(Item):
  def __init__(self,gid,textid):
    super().__init__(gid,textid)
    self.nodes = []

  
  def move(self,graph, delta_x , delta_y, items = None):
    graph.move_figure(self.gid, delta_x, delta_y)
    graph.move_figure(self.textid, delta_x, delta_y)
    for node in self.nodes:
      graph.move_figure(node, delta_x, delta_y)      
      if items:
       graph.move_figure(items[node].textid, delta_x, delta_y)
    
  def addNode (self,node):
    if node not in self.nodes:
      self.nodes.append(node)
      
  def remove(self, graph, node):
    if node in self.nodes:
      self.nodes.remove(node)
    else:
      graph.delete_figure(node)
      graph.delete_figure(self.textid) 

  def change_text(self,graph,text):
    graph.delete_figure(self.textid)
    self.textid = graph.draw_text(self.fl, (graph.get_bounding_box(self.gid)[0][0]+125, graph.get_bounding_box(self.gid)[0][1]-60))
    graph.update() 

def main():

    sg.theme('Dark Blue 3')        
    t_size = (13,1)
    i_size = (15,1)
    file_types = [("MAT (*.mat)", "*.mat"),
                  ("All files (*.*)", "*.*")]

    #GUI ELEMENTS------------------------------------------------------------------------------------------------------------
    
    #data
    datacol= [[sg.Text('Data Path', size=t_size),sg.Input('',key='d1', size=i_size),sg.FileBrowse(file_types=file_types, key= 'd1b')],
             [sg.Text('Labels Path', size=t_size),sg.Input('',key='d2', size=i_size),sg.FileBrowse(file_types=file_types, key= 'd2b')],
             [sg.Text('Num Data', size=t_size),sg.Input('',key='d3', size=i_size)],
             [sg.Text('Num Tests', size=t_size),sg.Input('',key='d4', size=i_size)],
             [sg.Text('Offset Data ', size=t_size),sg.Input('',key='d5', size=i_size)],
             [sg.Button('Load Data')],
             [sg.Checkbox("Use Previous Data", enable_events=True , key="default")]]

    #fl     
    tabgrp = [[sg.Text('Torch Seed', size=t_size),sg.Input('',key='h1', size=i_size)],
             [sg.Text('Batch Size', size=t_size),sg.Input('',key='h2', size=i_size)],
             [sg.Text('Learning Rate', size=t_size),sg.Input('',key='h3', size=i_size)],
             [sg.Text('Epochs', size=t_size),sg.Input('',key='h4', size=i_size)],
             [sg.Text('Number Clients', size=t_size),sg.Input('',key='h5', size=i_size)],
             [sg.Text('Steps Epochs', size=t_size),sg.Input('',key='h6', size=i_size)],
             [sg.Text('Number Rounds', size=t_size),sg.Input('',key='h7', size=i_size)],
             [sg.Button('Save fl settings')],
             [sg.Checkbox("Use Previous Settings", enable_events=True , key="k1")],
             ]  
    
    #scheme
    col = [[sg.T('Choose what clicking a figure does', enable_events=True)],
           [sg.R('Draw Node', 1, key='-RECT-', enable_events=True)],
           [sg.R('Draw Groups', 1, key='-GROUP-', enable_events=True)],

           [sg.R('Erase item', 1, key='-ERASE-', enable_events=True)],
           [sg.R('Erase all', 1, key='-CLEAR-', enable_events=True)],

           [sg.R('Move Everything', 1, key='-MOVEALL-', enable_events=True)],
           [sg.R('Move Items', 1, True, key='-MOVE-', enable_events=True)],
           [sg.R('Remove node from group', 1, True, key='-RESET-', enable_events=True)],
           [sg.R('Select', 1, True, key='-SELECT-', enable_events=True)],
           [sg.Text("IP"),sg.Input(size=(25, 1), key="ip"),],
           [sg.T('Choose fl type', enable_events=True)],
           [sg.Button('Change Item settings')],
           [sg.Button('Save Settings')],
           ]
           
    #full layout
    layout = [               
        [sg.Graph(
        canvas_size=(1000, 700),
        graph_bottom_left=(0, 0),
        graph_top_right=(1000, 700),
        key="-GRAPH-",
        change_submits=True,  # mouse click events
        background_color='lightblue',
        drag_submits=True), 
        sg.TabGroup([[
        sg.Tab("Graph",col),
        sg.Tab("Data options",datacol),
        sg.Tab("fl options",tabgrp),
        ]])
                
        ],[sg.Button('Execute Fl')],]
        
    #---------------------------------------------------------------------------------------------------------------------


    window = sg.Window("MyFl IDE", layout, finalize=True)
    # get the graph element for ease of use later
    graph = window["-GRAPH-"]  # type: sg.Graph

    #various vars for the selection of element in the canvas
    overNode = overGroup = fig = start_point = end_point = selected_fig = None    
    items = {}  # dictionary holding all items created: {"figid" : item , ...} ->  {1 : Item(1), 2 : Group(2),...}

    #boolean for the creation and dragging of elements in canvas
    dragging = False
    block = False
    event_handler()




    window.close()

#logo200 = "img"

#----------------------------------------------------------------------

  
# settings that will have to be specified from the user
def create_config_file():
  config = {
  "data_path"      : "",
  "labels_path"    : "",
  "test_num"       : 5000,
  "data_num"       : 30000,
  "start"          : 0,
  "torch_seed"     : 0,
  "batch_size"     : 128,
  "learning_rate"  : 0.001,
  "num_clients"    : 2,
  "epochs"         : 3,
  "steps_per_epoch": 2,
  "rounds"         : 3, 
  } 
  with open("config.json","w") as f:
    json.dump(config,f, indent=2)
  f.close() 


def replace_data(values):
  with open('config.json', "r") as f:
    data = json.load(f)
    
  data['data_path']   =     values["d1"]
  data['labels_path'] =     values["d2"]
  data['test_num']    = int(values["d4"])
  data['data_num']    = int(values["d3"])
  data['start']       = int(values["d5"])
    
  with open('config.json', 'w') as f:
    json.dump(data, f, indent=2)
      
      
def replace_settings(values):
  with open('config.json', "r") as f:
    data = json.load(f)
    
  data['torch_seed']      =  int(values["h1"])
  data['batch_size']      =  int(values["h2"])
  data['learning_rate']   =  float(values["h3"])
  data['epochs']          =  int(values["h4"])
  data['num_clients']     =  int(values["h5"])
  data['steps_per_epoch'] =  int(values["h6"])
  data['rounds']          =  int(values["h7"])
    
  with open('config.json', 'w') as f:
    json.dump(data, f, indent=2) 



def execute_fl(items):
  
  groups = [] 
  
  for item in items.values():
    if isinstance(item, Group):
      groups.append(item)
  
  for group in groups:
    nodes = []
    nodesip = []
    if group.fl=="V":
      for node in group.nodes:
       nodesip.extend((items[node].ip , items[node].ip))
       break
      print(nodesip) 
      execute_V_groups(nodesip,65432)
  
  nodes = []
  nodesip = []
  
    
  for group in groups:
    if group.fl=="H":
      for node in group.nodes:
       nodesip.extend((items[node].ip , items[node].ip))
      print(nodesip) 
      execute_H_groups(nodesip,65432)
  

main()


