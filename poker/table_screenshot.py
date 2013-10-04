#!/usr/bin/python
# MediocreGopher #

import gtk.gdk
import hashlib
import os

def md5_for_file(f, block_size=2**20):
	md5 = hashlib.md5()
	while True:
		data = f.read(block_size)
		if not data:
			break
		md5.update(data)
	return md5.hexdigest()


w = gtk.gdk.get_default_root_window()

screen = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,795,548)
screen = screen.get_from_drawable(w,w.get_colormap(),0,48,0,0,795,548) #src_x,src_y,dest_x,dest_y,width,height

screen.save("screen.png","png")

f = open("screen.png")
fhash = md5_for_file(f)
f.close()

try: os.rename('screen.png','screen_'+fhash[:5]+'.png')
except OSError: pass
