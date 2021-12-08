def event_handler():
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
