#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import logging
from PyQt4 import QtCore
import asyncore, socket
from time import sleep, time
from string import replace
from bitstring import BitArray, BitStream, ConstBitStream
import coords
from Alt_Az_Conv_Send import alt_az
from working_functions import strtochr
from Tkinter import *

#_____________________________________________________________________________________________________________

## import the serial library
import serial
#import time

## open the serial port that your ardiono is connected to.
ser = serial.Serial("/dev/ttyACM0", 9600)
sleep(2);
ser.flush();
sleep(2);

#______________________________________________________________________________________________________________


#Calibration GUI

app = Tk()
#app.title("Calibration")

#app.configure(background = "grey")

azframe = Frame(app)
azframe.pack()

altframe = Frame(app)
altframe.pack()

tframe = Frame(app)
tframe.pack()

lrframe = Frame(app)
lrframe.pack()

dframe = Frame(app)
dframe.pack()

bframe = Frame(app)
bframe.pack(side = BOTTOM)


def upCallBack():
	ser.write('w\n');
        #tkMessageBox.showinfo( "UP")


def downCallBack():
	ser.write("s\n");
	#tkMessageBox.showinfo( "DOWN")
def leftCallBack():
	ser.write("a\n");
	#tkMessageBox.showinfo( "LEFT")

def rightCallBack():
	ser.write("d\n");
	#tkMessageBox.showinfo( "RIGHT")
def close_window():
	ser.close();
	app.destroy();
def SendCallBack():
	Az_Str = str(360 - int(Azfield.get()))+'\n';
	ser.write(Az_Str)
	Alt_Str = Altfield.get()+'\n';
	ser.write(Alt_Str)

L1 = Label(azframe, text="Azimuth: ")
L1.pack(side = LEFT)
Azfield = Entry(azframe)
Azfield.pack(side = RIGHT)
L2 = Label(altframe, text="Altitude: ")
L2.pack(side = LEFT)
Altfield = Entry(altframe)
Altfield.pack(side = RIGHT)
SendButton = Button(tframe, text = "Send", command = SendCallBack);
SendButton.pack()
UpButton = Button(tframe, text = "Up", command = upCallBack);
UpButton.pack()
DownButton = Button(dframe, text = "Down", command = downCallBack);
DownButton.pack()
LeftButton = Button(lrframe, text = "Left", command = leftCallBack);
LeftButton.pack( side = LEFT)
RightButton = Button(lrframe, text = "Right", command = rightCallBack);
RightButton.pack( side = LEFT)
DoneButton = Button(bframe, text = "Done", command = close_window);
DoneButton.pack( side = BOTTOM)

app.mainloop();


#_______________________________________________________________________________________________________________
logging.basicConfig(level=logging.DEBUG, format="%(filename)s: %(funcName)s - %(levelname)s: %(message)s")

## \brief Implementation of the server side connection for 'Stellarium Telescope Protocol'
#
#  Manages the execution thread to the server side connection with Stellarium
class Telescope_Channel(QtCore.QThread, asyncore.dispatcher):

	## Class constructor
	#
	# \param conn_sock Connection socket
	def __init__(self, conn_sock):
		self.is_writable = False
		self.buffer = ''
		asyncore.dispatcher.__init__(self, conn_sock)
		QtCore.QThread.__init__(self, None)

	## Indicates the socket is readable
	#
	# \return Boolean True/False
	def readable(self):
		return True

	## Indicates the socket is writable
	#
	# \return Boolean True/False
	def writable(self):
		return self.is_writable

	## Close connection handler
	def handle_close(self):
		logging.debug("Disconnected")
		self.close()

	## Reading socket handler
	#	
	# Reads and processes client data, and throws the proper signal with coordinates as parameters
	def handle_read(self):
		#format: 20 bytes in total. Size: intle:16
		#Incomming messages comes with 160 bytes..
		data0 = self.recv(160);
		if data0:			
			data = ConstBitStream(bytes=data0, length=160)
			#print "All: %s" % data.bin

			msize = data.read('intle:16')
			mtype = data.read('intle:16')
			mtime = data.read('intle:64')

			# RA: 
			ant_pos = data.bitpos
			ra = data.read('hex:32')
			data.bitpos = ant_pos
			ra_uint = data.read('uintle:32')

			# DEC:
			ant_pos = data.bitpos
			dec = data.read('hex:32')
			data.bitpos = ant_pos
			dec_int = data.read('intle:32')

			logging.debug("Size: %d, Type: %d, Time: %d, RA: %d (%s), DEC: %d (%s)" % (msize, mtype, mtime, ra_uint, ra, dec_int, dec))
			(sra, sdec, stime) = coords.eCoords2str(float("%f" % ra_uint), float("%f" % dec_int), float("%f" %  mtime))

			#Sends back the coordinates to Stellarium
			self.act_pos(coords.hourStr_2_rad(sra), coords.degStr_2_rad(sdec))
			calibrate = raw_input("Do you want to calibrate? - Y/N \n")
			if calibrate == "Y":
				
				#Calibration GUI

				app = Tk()
				#app.title("Calibration")

				#app.configure(background = "grey")

				tframe = Frame(app)
				tframe.pack()

				lrframe = Frame(app)
				lrframe.pack()

				dframe = Frame(app)
				dframe.pack()

				bframe = Frame(app)
				bframe.pack(side = BOTTOM)

				def upCallBack():
					ser.write('w\n');
					#tkMessageBox.showinfo( "UP")


				def downCallBack():
					ser.write("s\n");
					#tkMessageBox.showinfo( "DOWN")
				def leftCallBack():
					ser.write("a\n");
					#tkMessageBox.showinfo( "LEFT")

				def rightCallBack():
					ser.write("d\n");
					#tkMessageBox.showinfo( "RIGHT")
				def close_window():
					app.destroy();


				UpButton = Button(tframe, text = "Up", command = upCallBack);
				UpButton.pack()
				DownButton = Button(dframe, text = "Down", command = downCallBack);
				DownButton.pack()
				LeftButton = Button(lrframe, text = "Left", command = leftCallBack);
				LeftButton.pack( side = LEFT)
				RightButton = Button(lrframe, text = "Right", command = rightCallBack);
				RightButton.pack( side = LEFT)
				DoneButton = Button(bframe, text = "Done", command = close_window);
				DoneButton.pack( side = BOTTOM)

				app.mainloop()
			#print "OK\n"

	## Updates the field of view indicator in Stellarium
	#
	# \param ra Right ascension in signed string format
	# \param dec Declination in signed string format
	def act_pos(self, ra, dec):
		(ra_p, dec_p, ra_s, dec_s) = coords.rad_2_stellarium_protocol(ra, dec)
		
		#print 'Received RA: ', ra_s, 'Received DEC: ', dec_s 
		f=open('testfile','w')
		(az_conv, alt_conv) = alt_az(ra_s, dec_s)		
				
		#print 'Converted AZ: ', az_conv, 'Converted ALT: ', alt_conv 
		f.write(str(az_conv)+'\n')
		f.write(str(alt_conv)+'\n')
		f.close
		f=open('testfile','r')		
		while 1:				
			line=f.readline()
			if not line:
				break			
			ser.write(line)			
			print(line)
			
		f.close
		

		#sending AZ, ALT to Arduino
		#(az_send, alt_send) = strtochr(az_conv, alt_conv)		
		#ser.write(az_send)
		#sleep(2)
		#ser.write(alt_send)
		
		times = 10 #Number of times that Stellarium expects to receive new coords //Absolutly empiric..
		for i in range(times):
			self.move(ra_p, dec_p)

	## Sends to Stellarium equatorial coordinates
	#
	#  Receives the coordinates in float format. Obtains the timestamp from local time
	#
	# \param ra Ascensión recta.
	# \param dec Declinación.
	def move(self, ra, dec):
		msize = '0x1800'
		mtype = '0x0000'
		localtime = ConstBitStream(replace('int:64=%r' % time(), '.', ''))
		#print "move: (%d, %d)" % (ra, dec)

		sdata = ConstBitStream(msize) + ConstBitStream(mtype)
		sdata += ConstBitStream(intle=localtime.intle, length=64) + ConstBitStream(uintle=ra, length=32)
		sdata += ConstBitStream(intle=dec, length=32) + ConstBitStream(intle=0, length=32)
		self.buffer = sdata
		self.is_writable = True
		self.handle_write()

	## Transmission handler
	#
	def handle_write(self):
		self.send(self.buffer.bytes)
		self.is_writable = False

## \brief Implementation of the server side communications for 'Stellarium Telescope Protocol'.
#
#  Each connection request generate an independent execution thread as instance of Telescope_Channel
class Telescope_Server(QtCore.QThread, asyncore.dispatcher):

	## Class constructor
	#
	# \param port Port to listen on
	def __init__(self, port=10001):
		asyncore.dispatcher.__init__(self, None)
		QtCore.QThread.__init__(self, None)
		self.tel = None
		self.port = port

	## Starts thread
	#
	# Sets the socket to listen on
	def run(self):
		logging.info(self.__class__.__name__+" running.")
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(('localhost', self.port))
		self.listen(1)
		self.connected = False
		asyncore.loop()

	## Handles incomming connection
	#
	# Stats a new thread as Telescope_Channel instance, passing it the opened socket as parameter
	def handle_accept(self):
		self.conn, self.addr = self.accept()
		logging.debug('%s Connected', self.addr)
		self.connected = True
		self.tel = Telescope_Channel(self.conn)

	## Closes the connection
	#
	def close_socket(self):
		if self.connected:
			self.conn.close()

#Run a Telescope Server
if __name__ == '__main__':
	try:
		Server = Telescope_Server()
		Server.run()
	except KeyboardInterrupt:
		logging.debug("\nBye!")
				
		ser.close();


