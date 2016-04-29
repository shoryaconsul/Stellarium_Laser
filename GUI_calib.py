from Tkinter import *
import serial
from time import sleep, time

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

ser = serial.Serial("/dev/ttyACM0", 9600)
sleep(2);
ser.flush();
sleep(2);


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

