/*
  Serial Read Test
 */

int x;
String str;
byte step_size;

void setup(){
  Serial.begin(9600);
}

void loop() 
{
    if(Serial.available())
    {
        //step_size = Serial.read();
        
        x = Serial.parseInt();
        
        Serial.print(x);
    }
delay(10);
}
