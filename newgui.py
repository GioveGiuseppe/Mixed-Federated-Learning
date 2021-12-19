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
    
    #EVENT LOGIC --------------------------
    while True:
        event, values = window.read()
        if event is None:
            break  # exit
        if event in ('-MOVE-', '-MOVEALL-'):
            graph.Widget.config(cursor='fleur')
        elif not event.startswith('-GRAPH-'):
            graph.Widget.config(cursor='left_ptr')

        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse event
            x, y = values["-GRAPH-"]
            if not dragging:
                start_point = (x, y)
                dragging = True
                drag_figures = graph.get_figures_at_location((x,y))
                lastxy = x, y
            else:
                end_point = (x, y)

            delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x,y
            if None not in (start_point, end_point):          
                
                if values['-MOVE-']:
                    for fig in drag_figures: 
                      items[fig].move(graph,delta_x,delta_y,items)
                      graph.update()
                      break                                
                       
                        
                elif values['-RECT-']:
                    if not block:
                      rect = graph.draw_rectangle((start_point[0]+50,start_point[1]+20),
                                   (start_point[0]-50,start_point[1]-20),fill_color='white', line_color='red')
                      text = graph.draw_text(rect,(start_point[0],start_point[1]))  
                    block = True
                    item = Item(rect,text)
                    items.update({rect:item})
                    
                    
                elif values['-GROUP-']:
                  if not block:
                    newgroup = graph.draw_rectangle((start_point[0]+125,start_point[1]+60), (start_point[0]-125,start_point[1]-60),fill_color='yellow', line_color='red') 
                    textid = graph.draw_text("V", (start_point[0], start_point[1]))
                    block = True 
                    tempg = Group(newgroup,textid)
                    items.update({newgroup:tempg})
                    graph.SendFigureToBack(newgroup)
          
                
                elif values['-ERASE-']:
                  for figure in drag_figures:
                   if figure in items:
                    # if figure is a node within a group                                       
                    group = items[figure].group
                    if group in items:
                      items[group].remove(graph,fig)
                    #if figure is a group with nodes
                    if isinstance(items[figure],Group):
                     for node in items[figure].nodes:
                      items[node].group = None
                      
                    items[figure].remove(graph,items[figure].gid)
                    del items[figure]                                   
                   fig = None
                   break
                        
                elif values['-CLEAR-']:
                  graph.erase()
                  items = {}
                  fig = None
                  
                elif values['-MOVEALL-']:
                  graph.move(delta_x, delta_y) # non muove gli oggetti ma il graph layer
               
                #to remove a node from a group
                elif values['-RESET-']:                  
                  for figure in drag_figures:                    
                    # remove the node from the group
                    group = items[figure].group
                    if group:
                      items[group].remove(graph,figure)                    
                    items[figure].group = None
                    items[figure].move(graph,150-graph.get_bounding_box(figure)[1][0]*(0.9), 50-graph.get_bounding_box(figure)[1][1]*(0.9))
                    graph.update()
                    
                                    
                elif values['-SELECT-']:
                  for figure in drag_figures:
                     selected_fig = figure
                     print(selected_fig)

                  


        elif event.endswith('+UP'):  # The drawing has ended because mouse up
            start_point, end_point = None, None  # enable grabbing a new rect
            dragging = False
            block = False 
            #makes elements bigger                       
            # per includere un nodo in un gruppo, si controlla se i due sono sovrapposti graficamente
            if(len(items) != 0 and fig != None ):
             for item in items.values():
              if isinstance(item,Group) and not isinstance(items[fig], Group) :                           
               if ((graph.get_bounding_box(item.gid)[1][0] > graph.get_bounding_box(fig)[0][0] and 
                  graph.get_bounding_box(item.gid)[1][1] < graph.get_bounding_box(fig)[0][1])  and 
                  (graph.get_bounding_box(item.gid)[0][0] < graph.get_bounding_box(fig)[1][0]  and
                  graph.get_bounding_box(item.gid)[0][1] > graph.get_bounding_box(fig)[1][1])):
                  print ("OVERLAPPING##################!!!!!!!!!!!")
                  item.addNode(fig)
                  items[fig].group = item.gid
        


        elif event == "Change Item settings":
         if selected_fig in items.keys():
          if selected_fig and items[selected_fig]:
            items[selected_fig].fl = "V" if items[selected_fig].fl == "H" else "H"                            
            items[selected_fig].change_text(graph,values["ip"])           


            
            
        elif event == "Save Settings":
         pass
        
        elif event == "Load Data":
         replace_data(values)
         
        elif event == "Save fl settings":
         replace_settings(values)
         
        elif event == "Execute Fl":
          execute_fl(items)




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


