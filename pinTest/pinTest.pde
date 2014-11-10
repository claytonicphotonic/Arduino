#define FAN_PIN 9
int TROUBLE_SHOOT_PIN = 1;

void setup(){
   Serial.begin(9600);
   pinMode(TROUBLE_SHOOT_PIN, OUTPUT);
   //analogWrite(FAN_PIN,90);
   
}
 //Loops through all pins setting them high for "delay" sec
void loop(){
  while(TROUBLE_SHOOT_PIN < 114){
     if (TROUBLE_SHOOT_PIN == 9) TROUBLE_SHOOT_PIN =10;
     Serial.print(TROUBLE_SHOOT_PIN);
     Serial.print("\n");
     digitalWrite(TROUBLE_SHOOT_PIN, HIGH);
     delay(1000);
     digitalWrite(TROUBLE_SHOOT_PIN, LOW);
   

      TROUBLE_SHOOT_PIN++;
   }
   
  TROUBLE_SHOOT_PIN = 1;
}

