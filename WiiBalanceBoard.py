# Bluetooth library
from blue import Wiiboard 

#Graph
import numpy as np

import time as t
import sys
from graph import graph

import pandas as pd
def main():
    # name_files=["tamashiro"]
    # graph(name_files)

    board = Wiiboard()
    if len(sys.argv) == 1:
        print "Discovering board..."
        address = board.discover()
    else:
        address = sys.argv[1]

    try:
        # Disconnect already-connected devices.
        # This is basically Linux black magic just to get the thing to work.
        subprocess.check_output(["bluez-test-input", "disconnect", address], stderr=subprocess.STDOUT)
        subprocess.check_output(["bluez-test-input", "disconnect", address], stderr=subprocess.STDOUT)
    except:
        pass

    print "Trying to connect..."
    board.connect(address)  # The wii board must be in sync mode at this time
    board.wait(200)
        	# Flash the LED so we know we can step on.
    board.setLight(False)
    board.wait(500)
    board.setLight(True)
    
    name_files=[]

    i=0

######################### Calibration ##################
#    print("calibration...")
#    start_time = t.time() 
#    elapsed_time = t.time() - start_time
#    while (elapsed_time<5):
#        elapsed_time = t.time() - start_time
#        board.receive()
#        board.offset_topLeft+=board.topLeft
#        board.offset_topRight+=board.topRight
#        board.offset_bottomLeft+=board.bottomLeft
#        board.offset_bottomRight+=board.bottomRight
   
####################### Check sensors data ##############       
    # while(1):
    #     board.receive()
    #     print(board.topLeft)
    #     print(board.offset_topLeft)
    #     print(board.topRight)
    #     print(board.bottomLeft)
    #     print(board.topLeft+board.topRight+board.bottomLeft+board.bottomRight)
    #     print(" ")
#    
###################### Start record ####################
    while(1):
        # variables to store
        time=[]
        x=[]
        y=[]
        topLeft=[]
        topRight=[]
        bottomLeft=[]
        bottomRight=[]

        initialize= raw_input("Start measurement ? - yes (y) /no (n)")
        
        start_time = t.time()               
        elapsed_time = t.time() - start_time
        
        #initial data is trash
        while(elapsed_time<5):
                
            board.receive()
            elapsed_time = t.time() - start_time
            
        if initialize=="y":
            
            print("Starting measurements - 30s")
            start_time = t.time()               
            elapsed_time = t.time() - start_time
            
        #record 30s
            i=0
            while(elapsed_time<30):
                
                board.receive()
                elapsed_time = t.time() - start_time

                #create the timestamp object
                ts=pd.Timestamp('now')

                time.append(ts)
                x.append(board.x)
                y.append(board.y)
                topLeft.append(board.topLeft)
                topRight.append(board.topRight)
                bottomLeft.append(board.bottomLeft)
                bottomRight.append(board.bottomRight)

                
                # Wii Balance frequency is about 100hz 
                #every 10s print the time
                if (i%1000==0):
                    print ('%.1f'%elapsed_time)
                i+=1

    ########################### Save to file #############################
    #name
            name=raw_input("File name: ")
            name_files.append(name)
            
            data={
                # 'time':time,
                'x':x,
                'y':y,
                'topLeft':topLeft,
                'topRight':topRight,
                'bottomLeft':bottomLeft,
                'bottomRight':bottomRight,
            }

            df=pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(time)

            df = df.set_index('datetime')
            #df.drop(['datetime'], axis=1, inplace=True)

            df.to_csv(name+'.csv')       
        ########## call graph.py ################
            graph(name_files)
            

if __name__ == "__main__":
    main()
