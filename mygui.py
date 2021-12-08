import PySimpleGUI as sg
import json
from wrapper import *

class mygui():
  def __init__(self):
    pass
  
  def execute(self):

    t_size= (15,1)
    file_types = [("MAT (*.mat)", "*.mat"),
                  ("All files (*.*)", "*.*")]


    #define layout

    #vertical
    layout1 = [
    [sg.Text('Torch Seed', size=t_size),sg.Input('',key='v1')],
    [sg.Text('Batch Size', size=t_size),sg.Input('',key='v2')],
    [sg.Text('Learning Rate', size=t_size),sg.Input('',key='v3')],
    [sg.Text('Epochs', size=t_size),sg.Input('',key='v4')],
    [sg.Button('Start Vertical')]
    ]

    #horizontal
    layout2=[
    [sg.Text('Torch Seed', size=t_size),sg.Input('',key='h1')],
    [sg.Text('Batch Size', size=t_size),sg.Input('',key='h2')],
    [sg.Text('Learning Rate', size=t_size),sg.Input('',key='h3')],
    [sg.Text('Epochs', size=t_size),sg.Input('',key='h4')],
    [sg.Text('Number Clients', size=t_size),sg.Input('',key='h5')],
    [sg.Text('Steps per Epochs', size=t_size),sg.Input('',key='h6')],
    [sg.Text('Number Rounds', size=t_size),sg.Input('',key='h7')],
    [sg.Button('Start Client'), sg.Button('Start Server')]
    ]
    #mixed
    layout3= [
    [sg.Text('Torch Seed', size=t_size),sg.Input('',key='m1')],
    [sg.Text('Batch Size', size=t_size),sg.Input('',key='m2')],
    [sg.Text('Learning Rate', size=t_size),sg.Input('',key='m3')],
    [sg.Text('Epochs', size=t_size),sg.Input('',key='m4')],
    [sg.Text('Number Clients', size=t_size),sg.Input('',key='m5')],
    [sg.Text('Steps per Epochs', size=t_size),sg.Input('',key='m6')],
    [sg.Text('Number Rounds', size=t_size),sg.Input('',key='m7')],
    [sg.Button('Start Client.'), sg.Button('Start Server.')]
    ]

    #Define Layout with Tabs         
    tabgrp = [[
             [sg.Text('Data Path', size=t_size),sg.Input('',key='d1'),sg.FileBrowse(file_types=file_types, key= 'd1b')],
             [sg.Text('Labels Path', size=t_size),sg.Input('',key='d2'),sg.FileBrowse(file_types=file_types, key= 'd2b')],
             [sg.Text('Num Data', size=t_size),sg.Input('',key='d3')],
             [sg.Text('Num Tests', size=t_size),sg.Input('',key='d4')],
             [sg.Text('Offset Data ', size=t_size),sg.Input('',key='d5')],
             [sg.Button('Load Data')],
             [sg.Checkbox("Use Previous Data", enable_events=True , key="default")]
             ],
             [sg.TabGroup([[
                        sg.Tab('Vertical FL', layout1, title_color='Red',border_width =10, background_color='Green',
                                     element_justification= 'center'),
                        sg.Tab('Horizontal FL', layout2,title_color='Blue',border_width =10,background_color='Yellow',
                                     element_justification= 'center'),
                        sg.Tab('Mixed FL', layout3,title_color='Black',border_width =10,background_color='Pink', 
                        tooltip='execute a mixed fl process',element_justification= 'center')
                        ]], 
                        tab_location='centertop', title_color='Red', tab_background_color='Purple',selected_title_color='Green',
                        selected_background_color='Gray', border_width=10), 
             ],
             [sg.Checkbox("Use Previous Settings", enable_events=True , key="k1")]
             ]  
            
    #Define Window
    window =sg.Window("Tabs",tabgrp)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
            
        if event == "Load Data":
          self.data_path = values["d1"]
          self.labels_path = values["d2"]
          self.num_data = values["d3"]
          self.num_tests = values["d4"]
          self.start = values["d5"]
          self._replace_data()
            
        if event == "default":
          for i in range (1,6):
            window["d"+str(i)].update(disabled =  values["default"]) 
          window["d1b"].update(disabled = values["default"])
          window["d2b"].update(disabled = values["default"])
          window["Load Data"].update(disabled = values["default"])

        if event == "k1":
          for i in range (1,8):
           window["h"+str(i)].update(disabled = values["k1"])
          for i in range (1,5):
           window["v"+str(i)].update(disabled = values["k1"])
          for i in range (1,8):
           window["m"+str(i)].update(disabled = values["k1"])
        
        
            
        if event == "Start Client" or event == "Start Server" : 
          if not values["k1"]:
            print("changing values")            
            self.torch_seed = values["h1"]
            self.batch_size = values["h2"]
            self.learning_rate = values["h3"]
            self.epochs = values["h4"]
            
            self.num_clients = values["h5"]
            self.steps_per_epoch = values["h6"]
            self.rounds = values["h7"]
            self._replace_settings()
        
        if event == "Start Vertical":
          if not values["k1"]:
            print("changing values")            
            self.torch_seed = values["v1"]
            self.batch_size = values["v2"]
            self.learning_rate = values["v3"]
            self.epochs = values["v4"]
            self._replace_settings(True)
            
        if event == "Start Client." or event == "Start Server." : 
          if not values["k1"]:
            print("changing values")            
            self.torch_seed = values["m1"]
            self.batch_size = values["m2"]
            self.learning_rate = values["m3"]
            self.epochs = values["m4"]
            
            self.num_clients = values["m5"]
            self.steps_per_epoch = values["m6"]
            self.rounds = values["m7"]
            self._replace_settings()            
            




        if event == "Start Client":                      
          print("executing flwr client")
          processFlwr = FlwrProcess()
          processFlwr.start_client()

        if event == "Start Server" or event == "Start Server." :
          processFlwr = FlwrProcess()
          processFlwr.start_server()
          print("executing flwr server")

          
        if event == "Start Vertical":  
          processPy = PyProcess()
          processPy.execute()
        
          
        if event == "Start Client.":
          tempmixed()
          #mixedProcess = MixedProcess() 
          #mixedProcess.start_client()
        """ 
        if event == "Load Image":
            filename = values["-FILE-"]
            if os.path.exists(filename):
                image = Image.open(values["-FILE-"])
                image.thumbnail((400, 400))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue())
        """

    window.close()    




#----------------------------------------------------------------------
  # settings that will have to be specified from the user
  def create_config_file(self):
    config = {
    "data_path": "",
    "labels_path": "",
    "test_num" : 5000,
    "data_num": 30000,
    "start":0,
    "torch_seed" : 0,
    "batch_size" : 128,
    "learning_rate" : 0.001,
    "num_clients" : 2,
    "epochs" : 3,
    "steps_per_epoch" : 2,
    "rounds" : 3, 
    } 
    with open("config.json","w") as f:
      json.dump(config,f, indent=2)
    f.close() 


  def _replace_data(self):
    with open('config.json', "r") as f:
      data = json.load(f)
    
    data['data_path'] = self.data_path
    data['labels_path'] = self.labels_path
    data['test_num'] = int(self.num_tests)
    data['data_num'] = int(self.num_data)
    data['start'] = int(self.start)
    
    with open('config.json', 'w') as f:
      json.dump(data, f, indent=2)
      
      
  def _replace_settings(self, vertical = False):
    with open('config.json', "r") as f:
      data = json.load(f)
    print(self.torch_seed)
    data['torch_seed'] = int(self.torch_seed)
    data['batch_size'] = int(self.batch_size)
    data['learning_rate'] = float(self.learning_rate)
    data['epochs'] = int(self.epochs)
    if (not vertical):
      data['num_clients'] = int(self.num_clients)
      data['steps_per_epoch'] = int(self.steps_per_epoch)
      data['rounds'] = int(self.rounds)
    
    with open('config.json', 'w') as f:
      json.dump(data, f, indent=2)    


if __name__ == "__main__":
  gui = mygui()
  gui.execute()


