//ArduinoStepperControlv5.0
//2012-04-14 jdreyer
//Stepper motor control program
//Arduino will respond to ENQ character with the motor position 

int stepsToMoveNeg;
int StartByte;
int i;
int userInput[3];
int digitalVal;
int dir;
int steps;
int previous=0;
int val;
char direction;
int negVal;
int StepperPosition=0;
int byte1;
int byte2;
float Version=5.0;

int DirectionPin=3;
int StepPin=12;

void setup() {
   Serial.begin(115200);
   pinMode(13, OUTPUT); 
   pinMode(DirectionPin, OUTPUT);
   pinMode(StepPin, OUTPUT);
}

void loop()
{
  if (Serial.available() > 2) {
    StartByte = Serial.read();
    if (StartByte == 255) {
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      byte1 = userInput[0];
      byte2 = userInput[1];
      val = (byte2<<8) | byte1;
      int stepsToMove = val-previous;
      
      if (stepsToMove > 0){
        //Move Forward 
        TurnMotorClockWise(stepsToMove);
      }
      if (stepsToMove < 0){
        TurnMotorCounterClockWise(stepsToMove*-1);
      }
      previous = val;
    }
    
    if (StartByte == 220) {
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      byte1 = userInput[0];
      byte2 = userInput[1];
      val = (byte2<<8) | byte1;
      negVal = val * -1;
      int stepsToMove = negVal-previous;
      
      if (stepsToMove > 0){
        TurnMotorClockWise(stepsToMove);
      }
      if (stepsToMove < 0){
        TurnMotorCounterClockWise(stepsToMove*-1);
      }
      previous = negVal;
    }

    if (StartByte == 5) {
      Serial.print(StepperPosition);
    }
    
    if (StartByte == 118) {
      Serial.print(Version);
    }
  }
}

void FlashLED(int time)
{
  digitalWrite(13, HIGH);   // set the LED on
  delay(time);              // wait for time
  digitalWrite(13, LOW);    // set the LED off
  delay(10);              
}

void TurnMotorClockWise(int steps)
{
  //NOTE: LOW is clockwise
  //Set the direction.
  digitalWrite(DirectionPin, LOW);
  delay(100);
  
  // Iterate for [steps] microsteps
  for (i = 0; i<steps; i++)       
  {
    // This LOW to HIGH change is what creates the
    // "Rising Edge" so the easydriver knows to when to step.
    digitalWrite(StepPin, LOW);  
    digitalWrite(StepPin, HIGH); 
    // This delay time is close to top speed for the motor
    delayMicroseconds(200);      
  }
  StepperPosition=StepperPosition+steps;
}

void TurnMotorCounterClockWise(int steps)
{
  //Set the direction.
  digitalWrite(DirectionPin, HIGH);
  delay(100);
  
  for (i = 0; i<steps; i++)       
  {
    digitalWrite(StepPin, LOW);
    digitalWrite(StepPin, HIGH);
    delayMicroseconds(200);
  }
  StepperPosition=StepperPosition-steps;
}
