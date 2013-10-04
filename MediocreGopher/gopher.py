#!/usr/bin/python
# MediocreGopher #

import socket
import sys
import os

HOST = 'localhost'    # The remote host
PORT = 6666              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send("\x05\x02\x00\x02")

s.recv(2)

s.send("\x05\x01\x00\x03\x0ewww.google.com\x00\x50")

		

