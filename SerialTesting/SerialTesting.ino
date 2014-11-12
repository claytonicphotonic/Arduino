/*
  Serial Event example
 
 When new serial data arrives, this sketch adds it to a String.
 When a newline is received, the loop prints the string and 
 clears it.
 
 A good test for this is to try it with a GPS receiver 
 that sends out NMEA 0183 sentences. 
 
 Created 9 May 2011
 by Tom Igoe
 
 This example code is in the public domain.
 
 http://www.arduino.cc/en/Tutorial/SerialEvent
 
 */
#include <AFMotor.h>
// #include <SoftwareSerial.h>
// the fan is hooked up to pin 9 (must change this to reflect the new shield
// initialize the stepper library on pins :
AF_Stepper myStepper(200,1);  
int array[3];         // a string to hold incoming data
// boolean stringComplete = false;  // whether the string is complete
int command;
boolean neg;
int data;

void setup() {
  // initialize the serial port:
  Serial.begin(9600);      // mega also capable of 115200
  myStepper.setSpeed(30);

}

void loop() {
   if (Serial.available()>0 ){
      command = Serial.read();        //    Pull off the command for the switch statement below
      // Serial.println(command);                                     //    10 being a carriage return
      data = Serial.read();
      if(data == '-'){ 
          neg = true;                          //    case a negative number, defaults to false (positive)
          Serial.println("Neg True");
      }
      else if(data >= '0' && data <= '9') {
          array[0] = Serial.read();
          array[1] = Serial.read();
          array[2] = Serial.read();
          //Serial.println(dataIn);
      }
   
      Serial.println(command);
      Serial.println(data);
      Serial.println(array[0]);
      Serial.println(array[1]);
      Serial.println(array[2]);
   }
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    } 
  }
}

*/
