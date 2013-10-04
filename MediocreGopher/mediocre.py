#!/usr/bin/python
# MediocreGopher #

import socket,sys,os,signal
from struct import *

def send_post(stuff):
	packet = "POST /gopher HTTP/1.1\r\n";
	packet += "User-Agent: Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)\r\n";
	packet += "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\n";
	packet += "Keep-Alive: 300\r\n";
	packet += "Connection: keep-alive\r\n";
	packet += "Content-Type: application/octet-stream\r\n";
	packet += "Content-Length: "+str(len(str(stuff)))+"\r\n";
	packet += "\r\n"+str(stuff);
	gopher.send(packet)

def receive_response(wait):
	i = 130
	while i:
		try:
			buff = gopher.recv(i,socket.MSG_DONTWAIT)
			if buff==0: return False
			elif len(buff) < i: i-=len(buff)
			else: break
		except: 
			if wait: pass
			else: return
	length = ''
	while True:
		buff = gopher.recv(1)
		if buff == "\r": break
		else: length += str(buff)
		
	gopher.recv(3)
	return gopher.recv(int(length))

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

#Get gopher location from command line. Assumes gopher is on port 80
gopher_loc = sys.argv[1] if len(sys.argv) > 1 else exit('First parameter must be location of gopher server')

HOST = ''
PORT = 6666
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print "mediocre server listening on port "+str(PORT)


(client, addr) = s.accept()
while 1:
	#Parent process closes its connection and listens for more
	if os.fork():
		client.close()
		(client, addr) = s.accept()
	#Child process
	else:
		#Processes (ignores) the original request, assumes client supports no-authentication
		client.recv(ord(unpack('xc',client.recv(2))[0]))
		
		#Tell client to use no-authentication
		client.send('\x05\x00')

		#Make sure client is trying to create a tcp/ip stream
		command_code = ord(unpack('xcx',client.recv(3))[0])
		if command_code != 1:
			client.send('\x05\x07')
			exit('mediocre: this proxy software only supports tcp/ip streams')

		#Get host and port, stores the plain text in dst_dst/dst_port,
		# and the hex encoded versions in dst_dst_h/dst_port_h
		address_type_h = unpack('c',client.recv(1))[0]
		address_type = ord(address_type_h)
		if address_type == 1:
			dst_dst_h = client.recv(4)
			dst_port_h = client.recv(2)
			temp = list()
			for i in unpack('4c',dst_dst_h): temp.append(str(ord(i)))
			dst_dst = '.'.join(temp)
			dst_port = unpack('!H',dst_port_h)[0]
		elif address_type == 3:
			dst_dst_len = client.recv(1)
			dst_dst_h = dst_dst = client.recv(ord(dst_dst_len))
			dst_port_h = client.recv(2)
			dst_port = unpack('!H',dst_port_h)[0]
		else:
			client.send('\x05\x08')
			exit('mediocre: this proxy software only supports IPv4 and domain names')

		print dst_dst+":"+str(dst_port)

		#Open connection to gopher
		gopher = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		gopher.connect((gopher_loc, 80))

		#Tell gopher where to connect to
		req = address_type_h
		if address_type==3: req += str(dst_dst_len)
		req += str(dst_dst_h)+str(dst_port_h)
		send_post(req)

		#Determine if connection was made, die with an error if not
		response = receive_response(1)
		if response != 'OK':
			client.send('\x05\x01')
			exit(response)

		#Tell client that connection has been made
		res = "\x05\x00\x00"+address_type_h
		if address_type==3: res += str(dst_dst_len)
		res += str(dst_dst_h)+str(dst_port_h)
		client.send(res)

		while client and gopher:
			tbuffer = None
			cbuffer = None

			try:
				tbuffer = client.recv(1024,socket.MSG_DONTWAIT)
				if not tbuffer: break
			except: pass
		
			cbuffer = receive_response(False)
			if cbuffer==False: break

			if tbuffer: send_post(tbuffer)

			if cbuffer: client.send(cbuffer)

		gopher.close()
		client.close()
		exit()
