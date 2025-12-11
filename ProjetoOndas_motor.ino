#define MIN 0
#define MAX 255

int pot = A10;
long int t;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(30,OUTPUT);
  pinMode(32,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(pot, INPUT);
  digitalWrite(30,HIGH);
  digitalWrite(32,LOW);
  int valA = analogRead(pot);
  int valM = map(valA,0,1023,MIN,MAX);
  analogWrite(3,valM);
}

void loop() {
  // put your main code here, to run repeatedly:
  t = millis();
  int valA = analogRead(pot);
  int valM = map(valA,0,1023,MIN,MAX);
  //Serial.println(t);
  Serial.println(valM*(1-exp(-t/1000)*sin(t/1000)));
  analogWrite(3,valM);
}
