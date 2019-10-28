# Static-Analysis-System

  A custom application in Python 2 communicates with Wii Balance Board (WBB) by Bluetooth. The WBB is a rigid plate with four strain gauges that can measure up to 150 kg (330 pounds). By measuring the four strain gauges forces, the Center of Pressure(COP) is calculated using equations 1 and 2 to Medio-Lateral (x) and Antero-Posterior (y) axis respectively.

![wbb](https://user-images.githubusercontent.com/57098324/67681367-87e5aa00-f9d0-11e9-99ce-4588602087b8.png)
![equation](https://user-images.githubusercontent.com/57098324/67681878-89fc3880-f9d1-11e9-8ad2-3bb883049656.png)

# How to run 

  1) Install python packages: Pandas, Numpy
  2) Install python bluetooth packages 

  sudo apt-get update
  sudo apt-get install python-pip python-dev ipython
  sudo apt-get install bluetooth libbluetooth-dev
  sudo pip install pybluez

  2) Press the red button on WBB to synchronize 
  
  ![aid808407-v4-728px-Sync-a-Wii-Fit-Balance-Board-Step-4](https://user-images.githubusercontent.com/57098324/67684503-a8b0fe00-f9d6-11e9-8200-eb99fa718d05.jpg)

  3) Run WiiBalanceBoard.py
  
# Result


