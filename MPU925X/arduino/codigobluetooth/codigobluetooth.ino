
void setup() {
  //Initialize the hardware serial
  Serial.begin(9600);

  //Initialize the software serial
  Serial1.begin(9600);
  Serial.println(F("Type the AT commands:"));
}

void loop() {
  //Check received a byte from hardware serial
  if (Serial.available()) {
    char r = Serial.read(); //Read and save the byte
    Serial1.print(r);  //Send the byte to bluetooth by software serial
    Serial.print(r);  //Echo
  }
  //Check received a byte from bluetooth by software serial
  if (Serial1.available()) {
    char r = Serial1.read(); //Read and save the byte
    Serial.print(r); //Print the byte to hardware serial
  }
}
