#include <Servo.h>

  String inData;
  Servo hor;
  Servo ver;

  int hor_tomove=20;
  int ver_tomove=20;

  int hor_offset = 0;
  int ver_offset = 0;

  int hor_dest = hor_tomove + hor_offset;
  int ver_dest = ver_tomove + ver_offset;

  int hv = 1;

//function to move motor

    void move_motor(Servo motor, int dest)
    {
      int pos = motor.read();
      int j;
      if(pos!= dest){
        if(pos<=dest)
        {
          for(j = pos; j<=dest; j++)
          {
            motor.write(j); 
            delay(50);
          }
        }
  
        if(pos>=dest)
        {
          for(j = pos; j>dest; j--)
          {
            motor.write(j); 
             delay(70);
          }
        }
     }
    }

  


void setup() {
  Serial.begin(9600);
  
  hor.write(150);
  hor.attach(9);
  
  ver.write(20);
  ver.attach(10);
  

}

void loop() {
  move_motor(hor, hor_dest);
  move_motor(ver, ver_dest);
  

}

void serialEvent() {
    while (Serial.available() > 0)
    {
        char recieved = Serial.read();
        
        inData += recieved; 

       if(recieved == 'w')
          {
            ver_offset++;
            hv = 0;
            inData="";
          }
        else if(recieved =='s')
          {
            ver_offset--;
            hv = 0;
            inData="";          
          }
        else if(recieved == 'a')
          {
            hor_offset++;
            hv=0;
            inData="";
          }
        else if(recieved == 'd')
          {
            hor_offset--;
            hv=0; 
            inData="";
          }

        // Process message when new line character is recieved
        if (recieved == '\n')
        {
          if(hv == 0)
          {
            hv = 1;
          }
          else if(hv == 1)
          {
            hor_tomove = inData.toInt();
            hv = 2;
          }
          else if(hv == 2)
          {
            ver_tomove = inData.toInt();
            hv =1;
          }

            inData = ""; // Clear recieved buffer
            hor_dest = hor_tomove + hor_offset;
            ver_dest = ver_tomove + ver_offset;

            if(hor_dest>180)
            {
              hor_dest = hor_dest = hor_dest - 180;
              ver_dest = 180 - ver_dest;
            }
            else if(hor_dest<0)
            {
              hor_dest = hor_dest + 180;
              ver_dest = 180 - ver_dest;
            }
        }
    }
}
