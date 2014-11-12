
/* Stepper Motor Control - one step at a time
 
 This program drives a unipolar or bipolar stepper motor. 
 The motor is attached to digital pins 8 - 11 of the Arduino.
 
 The motor will step one step at a time, very slowly.  You can use this to
 test that you've got the four wires of your stepper wired to the correct
 pins. If wired correctly, all steps should be in the same direction.
 
Use this also to count the number of steps per revolution of your motor,
 if you don't know it.  Then plug that number into the oneRevolution
 example to see if you got it right.
 
 Created 30 Nov. 2009
 by Tom Igoe
 
 Later Enhanced by ClayBro: 10/16/2014
 
 this included stepper.h/stepper.cpp values that aren't in the original class that comes with your Arduino
 update them here: http://forum.arduino.cc/index.php/topic,143276.0.html
 
 
 */

#include <Stepper.h>

#define FAN_PIN 9                                // the fan is hooked up to pin 9
const int stepsPerRevolution = 200;              // change this to fit the number of steps per revolution for your motor
const int RPM = 30;                               // much over thirty is too fast to respond to      
int step_mode = 4;                               // 4 = full, 8 = half
int yPosition = 0;                               // number of steps the motor has taken
byte byte_step;                                  // serial only reads in bytes
long previous = stepsPerRevolution/2;            // This may come in handy
char dataIn;
int step_size[5];
int count = 0;
int i;
int num_steps = 0;
boolean neg = false;                            // Default to positive steps
boolean FAN = false;                            // Default to fan off

// initialize the stepper library on pins :
Stepper myStepper(stepsPerRevolution, 60,61,56,57, step_mode);         //Stepper(number_of_steps, motor_pin_1, motor_pin_2, motor_pin_3, motor_pin_4)   


void setup() {
  // initialize the serial port:
  Serial.begin(9600);
  myStepper.setSpeed(RPM);
}


void loop() {
   while(Serial.available()>0) {    
      dataIn = Serial.read();
      if (dataIn == 70 && FAN == false){
         FAN = true;
         analogWrite(FAN_PIN,90);              //   WRITE(FAN_PIN, HIGH); PWM because we have a 5V fan on a 12V pin
         dataIn = count = 0;
      }
      else if(dataIn == 70 && FAN == true){
         FAN = false;
         digitalWrite(FAN_PIN,LOW);            //   turn the fan off
         dataIn = count = 0;
      }        
      else if(dataIn == 45){                //    case you recieve a negative, defaults to false (positive)
         neg = true;
         count = 0;                            //   count back one so you dont mess up the array
      }
      else{ 
         step_size[count] = dataIn;               // make an array
         count++;                                 //   count is the length of the array
      } 
      delay(10);
   }                                   
 
   if (step_size[0] > 0){                     // must do this outside the loop because calculations are dependent on the size of the array
      for(i=0; i < count; i++){
          num_steps = num_steps + pow(10,(count-2))*(step_size[i]-48);    //convert it to a base 10 number for us humans 
          step_size[i] = 0;                                                // clear out the memory for the next loop
          count--;                                                         
          
      }
 
      if(neg == true){
         num_steps = num_steps*-1;    // Make it negative then default it back to positive
         neg = false; 
      }
    //Serial.println(num_steps);
      
      myStepper.step(num_steps);
      yPosition = yPosition + num_steps;
      Serial.println(yPosition);
      count = 0;
      num_steps = 0;
   }
   
   //////////// Make it so that it wont crash ////////////////////
   // Pin 14 is Y-min
   // Pin 15 is Y-Max
   
   
   delay(10);
   
}
