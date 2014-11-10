
/* 
 Stepper Motor Control - one step at a time
 
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
 
 Later Enhanced by ClayBro
 */

#include <Stepper.h>

#define FAN_PIN 9                                // the fan is hooked up to pin 9
const int stepsPerRevolution = 200;              // change this to fit the number of steps per revolution for your motor
const int RPM = 300;                                     
int step_mode = 8;                               // 4 = full, 8 = half
int yPosition = 0;                               // number of steps the motor has taken
byte byte_step;                                  // serial only reads in bytes
long previous = stepsPerRevolution/2;            // This may come in handy
byte character;
int step_size = 0;
int count = 0;

// initialize the stepper library on pins :
Stepper myStepper(stepsPerRevolution, 60,61,56,57, step_mode);         //Stepper(number_of_steps, motor_pin_1, motor_pin_2, motor_pin_3, motor_pin_4)   



void setup() {
  // initialize the serial port:
  Serial.begin(9600);
  analogWrite(FAN_PIN,90); //WRITE(FAN_PIN, HIGH); Changed this because we have a 5V fan tell it to just stay on and keep the unit cool
  myStepper.setSpeed(RPM);

}

void loop() {
   if (Serial.available()){    // make a string
      character = Serial.read()-'0';
      delay(10);
      step_size = step_size + character;
   }

   if (step_size >0){
      myStepper.step(step_size);
      //Serial.println("steps:" );
      //yPosition = yPosition + step_size;
      //Serial.write("yPosition is : ");
      Serial.print(step_size);
   }
   else if (step_size == 0){
      myStepper.step(-10);
      //yPosition = yPosition - step_size;
      // Serial.write("yPosition is : ");
      Serial.print(step_size);
   }
  // clear step_size
   step_size = 0;
   count = 0;
   delay(10);
}
