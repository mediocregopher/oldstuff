#!/usr/bin/python
# MediocreGopher #

import re
import gtk.gdk
import hashlib
import sys
import time
import os
from pokereval import PokerEval
from decimal import Decimal
import random

def card_at_pos(pos,s): #s is reference to screen pixbuff
	crop = s.subpixbuf(pos[0],pos[1],card_size[0],card_size[1])
	crop.save("crop.png","png")

	f = open("crop.png")
	fhash = md5_for_file(f)
	f.close()

	if fhash in hashdb: return hashdb[fhash]
	else: return None

def md5_for_file(f, block_size=2**20):
	md5 = hashlib.md5()
	while True:
		data = f.read(block_size)
		if not data:
			break
		md5.update(data)
	return md5.hexdigest()

def is_op_at(pos,s): #s is reference to screen pixbuff
	crop = s.subpixbuf(pos[0],pos[1],op_card_size[0],op_card_size[1])
	crop.save("crop.png","png")

	f = open("crop.png")
	fhash = md5_for_file(f)
	f.close()

	if fhash == '6fa39168da7429a7366f589eb7f46e54': return True
	else: return False

def rand_pop(r_deck):
	return r_deck.pop(random.randint(0,len(r_deck)-1))

#Get loop parameter
loop = False
if len(sys.argv) > 1 and sys.argv[1] == '-l': loop = True

#Position window if loop
if loop: os.system('./position_window')

#create hash table
f = open('hashes/hashes.db')
hashdb = dict()
for line in f:
	r = re.match('([a-f0-9]{32}):([jkqat2-9]{1,2}[dhsc])',line)
	if r: hashdb[r.group(1)]=r.group(2)
f.close()

#Set some globals (card positions and sizes)
card_size = (11,29)
op_card_size = (12,21)
comm_cards_pos = (
	(272,157),
	(272+54,157),
	(272+54*2,157),
	(272+54*3,157),
	(272+54*4,157)
)
hand_cards_pos = (
	(	#Bottom right
		(580,319),
		(595,323)
	),
	(	#Top left
		(98,75),
		(113,79)	
	),
	(	#Mid Left
		(34,203),
		(49,207)
	),
	(	#Top Right
		(639,75),
		(654,79)
	),
	(	#Bottom Left
		(168,319),
		(183,323)
	),
	(	#Mid Right
		(712,203),
		(727,207)
	)
)

op_card_pos = (
	(187,120),
	(112,211),
	(182,284),
	(598,285),
	(682,212),
	(608,122)
)

once = True
i = 1
pokereval = PokerEval()
while (once or loop):

	board=list()
	pocket=list()

	#Get screenshot of whole table
	w = gtk.gdk.get_default_root_window()
	screen = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,795,548)
	screen = screen.get_from_drawable(w,w.get_colormap(),0,48,0,0,795,548) #src_x,src_y,dest_x,dest_y,width,height

	#Get Community Cards
	for p in comm_cards_pos: 
		card = card_at_pos(p,screen)
		if card != None: board.append(card)

	#Find and get Hand
	for p in hand_cards_pos:
		p_temp = card_at_pos(p[0],screen)
		if p_temp != None:
			pocket.append([p_temp,card_at_pos(p[1],screen)])
			break

	#Determine number of other players
	num_other_players = 0
	for p in op_card_pos:
		if is_op_at(p,screen): num_other_players += 1

	print num_other_players,board,pocket,

	win = None
	if len(pocket) == 1 and len(pocket[0]) == 2 and pocket[0][0] != None and pocket[0][1] != None:
		#Set up a fresh deck
		fresh_deck = pokereval.deck()
		for i in range(0,len(fresh_deck)): fresh_deck[i] = pokereval.card2string(fresh_deck[i])

		#Remove known cards from deck
		deck = list(fresh_deck)
		for i in pocket[0]: 
			if i in deck: deck.remove(i)
		for i in board: 
			if i in deck: deck.remove(i)

		#The important bit, calculates number of wins/losses for random sample
		win = 0
		loss = 0
		for i in range(0,5000):
			tmp_deck = list(deck)
			tmp_pocket = list(pocket)
			tmp_board = list(board)
			for o in range(0,5-len(board)): tmp_board.append(rand_pop(tmp_deck))
			for o in range(0,num_other_players): tmp_pocket.append([rand_pop(tmp_deck),rand_pop(tmp_deck)])
			r = pokereval.winners(game='holdem',pockets=tmp_pocket,board=tmp_board)['hi']
			if len(r)==1:
				if r[0]: loss+=1
				else: win+=1

	if win != None: print (Decimal(win)/Decimal(5000))*100,
	once = False
	if loop:
		print "\n\n\n"
		time.sleep(1)
