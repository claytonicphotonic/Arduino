
/* 
 Stepper Motor Control - 
 Created 30 Nov. 2009
 by Tom Igoe
 
 Later Enhanced by ClayBro: 10/16/2014
 
 this included stepper.h/stepper.cpp values that aren't in the original class that comes with your Arduino
 update them here: http://forum.arduino.cc/index.php/topic,143276.0.html
 
 */
#define FAN_PIN 9
#include <Stepper.h>          //might not need this

#include <AFMotor.h>
// #include <SoftwareSerial.h>
                                // the fan is hooked up to pin 9 (must change this to reflect the new shield
// initialize the stepper library on pins :
AF_Stepper myStepper(200,1);                       //myStepper("steps per revolution", 1 is M1/M2)

//const int stepsPerRevolution = 200;              // change this to fit the number of steps per revolution for your motor
const int RPM = 30;                                // much over thirty is too fast to respond to      
int step_mode = 4;                                 // 4 = full, 8 = half
int yPosition = 0;                                 // number of steps the motor has taken
byte byte_step;                                    // serial only reads in bytes
char command;
int dataIn = 0;
int data = 0;
int step_size[20];
int count = 0;
int i;
int way = 'FORWARD';
int num_steps = 0;
boolean neg = false;                            // Default to positive steps
boolean FAN = false;                            // Default to fan off


//Stepper myStepper(stepsPerRevolution, 6,7,8,9, step_mode);         //Stepper(number_of_steps, motor_pin_1, motor_pin_2, motor_pin_3, motor_pin_4)   


void setup() {
  // initialize the serial port:
  Serial.begin(9600);      // mega also capable of 115200
  myStepper.setSpeed(RPM);

}

void loop() {
    while (Serial.available()>0){
        data= Serial.read();
        if (data >= 'A' && data <= 'Z'){
            command = data;
        }
        if(data == '-'){ 
            neg = true;                          //    case a negative number, defaults to false (positive)
            Serial.println("Neg True");
        }
        else if(data >= '0' && data <= '9' && command > 0){
            dataIn = dataIn * 10 + data-'0';
            //Serial.println(dataIn);
        }
        else{
            break;
        }
    }
    delay(10);
    //Serial.println(dataIn);
    if (command > 0){
//        command = Serial.read();        //    Pull off the command for the switch statement below
//        // Serial.println(command);                                     //    10 being a carriage return
//        data = Serial.read();
        Serial.println("I made it here to 1");
  
         switch(command){
             case 'F':                                      // case to turn the fan on/off
                 if (FAN == false){
                     FAN = true;
                     analogWrite(FAN_PIN,90);
                 }                                          //   WRITE(FAN_PIN, HIGH); PWM because we have a 5V fan on a 12V pin
                 else if(FAN == true){
                     FAN = false;
                     digitalWrite(FAN_PIN,LOW);               //   turn the fan off
                 }
                 command = 0; 
             break;
        
             case 'G':                               // the case of motor "a"       
                  if(neg == true){
                       way = 'BACKWARD'; 
                  }
                  myStepper.step(dataIn, way, SINGLE);
                  myStepper.release();
                  yPosition = yPosition + dataIn;
                  // Reset Values //
                  dataIn = 0;                      
                  data = 0;
                  neg = false;
                  way = 'FORWARD';
                  command = 0;
              break;
         }                     
         Serial.println(yPosition);    
    }    
return;
}
