#include <AFMotor.h>
#include <GFButton.h>

//sendo implementado como 4 motores
AF_DCMotor motor1(1);
AF_DCMotor motor2(2);
AF_DCMotor motor3(3);
AF_DCMotor motor4(4);

// Botoes
GFButton botao1(2);

bool ativado = false;

int potenciometro = A5;
int valor_potenciometro;

//funções
void toggle_ativo(){
    ativado = !ativado;
}

void setup(){
    Serial.begin(9600);
    pinMode(potenciometro,INPUT);
    botao1.setPressHandler(toggle_ativo);
}

void loop(){
    botao1.process();
    valor_lido = analogRead(potenciometro);
    int velocidade = map(valor_lido,0,1023,0,160);
    motor1.setSpeed(velocidade);
    motor2.setSpeed(velocidade);
    motor3.setSpeed(velocidade);
    motor4.setSpeed(velocidade);
    if(ativado){
        motor1.run(FORWARD);
        motor2.run(FORWARD);
        motor3.run(FORWARD);
        motor4.run(FORWARD);
    } else {
        motor1.run(RELEASE);
        motor2.run(RELEASE);
        motor3.run(RELEASE);
        motor4.run(RELEASE);
    }

}