# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 19:02:02 2021

@author: Ankur
"""
""" For the automation of UCT using python.
Version 1: This code controls the stepper motors via Arduino, wave generator, DSO 
and systematically scan the object to generate the data.
"""
import serial

arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)
while True:
    data='056005600900'
    arduino.write(data.encode())
serial.close()