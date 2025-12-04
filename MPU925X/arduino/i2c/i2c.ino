#include <MPU925X.h>
#include <MadgwickAHRS.h>
#include <Wire.h>

MPU925X IMU(Wire, 0x68);
Madgwick filter;
float pico = 0;

unsigned long microsPerReading, microsPrevious;

// --- Variáveis de Física ---
float velocityZ = 0;
float positionZ = 0; 
float gravity = 9.81;

// --- Variáveis de Calibração (Offsets) ---
float baseAx = 0, baseAy = 0, baseAz = 0;
float baseGx = 0, baseGy = 0, baseGz = 0;
bool calibrado = false;

// --- Configuração do Filtro Passa-Alta ---
class HighPassFilter {
  private:
    float alpha;
    float last_input;
    float last_output;
  public:
    HighPassFilter(float cutoff_freq, float dt) {
      float RC = 1.0 / (cutoff_freq * 2 * 3.14159);
      alpha = RC / (RC + dt);
      last_input = 0;
      last_output = 0;
    }
    float update(float input) {
      float output = alpha * (last_output + input - last_input);
      last_input = input;
      last_output = output;
      return output;
    }
};

// Filtro um pouco mais agressivo (0.15 Hz) para tentar segurar o drift
HighPassFilter hpFilterVel(0.15, 0.01); 
HighPassFilter hpFilterPos(0.15, 0.01);

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  int status = IMU.begin();
  if (status < 0) {
    Serial.println("Erro no IMU");
    while (1) {}
  }
  
  filter.begin(25); 

  // --- ROTINA DE CALIBRAÇÃO ---
  Serial.println("CALIBRANDO... NAO MOVA O SENSOR!");
  delay(1000);
  
  float somaAx = 0, somaAy = 0, somaAz = 0;
  float somaGx = 0, somaGy = 0, somaGz = 0;
  int amostras = 500;

  for (int i = 0; i < amostras; i++) {
    IMU.readSensor();
    somaAx += IMU.getAccelX_mss();
    somaAy += IMU.getAccelY_mss();
    somaAz += IMU.getAccelZ_mss();
    somaGx += IMU.getGyroX_rads();
    somaGy += IMU.getGyroY_rads();
    somaGz += IMU.getGyroZ_rads();
    delay(2);
  }

  baseAx = somaAx / amostras;
  baseAy = somaAy / amostras;
  baseAz = somaAz / amostras;
  baseGx = somaGx / amostras;
  baseGy = somaGy / amostras;
  baseGz = somaGz / amostras;

  Serial.println("Calibracao Finalizada!");
  Serial.print("Offset Z (Gravidade inclusa): "); Serial.println(baseAz);
  delay(1000);

  microsPrevious = micros();
}

void loop() {
  unsigned long microsNow = micros();
  float dt = (microsNow - microsPrevious) / 1000000.0; 
  microsPrevious = microsNow;

  if (dt <= 0 || dt > 1.0) return;

  IMU.readSensor();
  
  // 1. Aplica a calibração (Remove o offset inicial)
  // Nota: Para o Giroscópio, removemos a média simples.
  float gx = (IMU.getGyroX_rads() - baseGx) * (180.0 / PI);
  float gy = (IMU.getGyroY_rads() - baseGy) * (180.0 / PI);
  float gz = (IMU.getGyroZ_rads() - baseGz) * (180.0 / PI);
  
  // Para Aceleração, não subtraímos direto aqui porque precisamos da orientação primeiro,
  // mas usaremos os dados brutos para alimentar o Madgwick.
  float ax = IMU.getAccelX_mss();
  float ay = IMU.getAccelY_mss();
  float az = IMU.getAccelZ_mss();

  // 2. Madgwick (Orientation)
  filter.updateIMU(gx, gy, gz, ax, ay, az);

  float q0 = filter.getQ0();
  float q1 = filter.getQ1();
  float q2 = filter.getQ2();
  float q3 = filter.getQ3();

  // 3. Remover Gravidade (Linear Acceleration)
  // Projeta a aceleração lida no eixo Z do mundo real
  float linearAccelZ = (ax * (2.0f * (q1 * q3 - q0 * q2))) +
                       (ay * (2.0f * (q0 * q1 + q2 * q3))) + 
                       (az * (q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3));
  
  linearAccelZ -= gravity; 

  // --- CORREÇÃO DE ZONA MORTA (DEADZONE) ---
  // Se a aceleração for ruído (muito baixa), zera ela.
  if (fabs(linearAccelZ) < 0.15) { 
     linearAccelZ = 0.0;
     // Opcional: Se a aceleração é zero, podemos forçar a velocidade a decair mais rápido
     velocityZ *= 0.9; 
  }

  // 4. Integração Dupla
  velocityZ += linearAccelZ * dt;
  
  // Filtro Passa-Alta na velocidade
  velocityZ = hpFilterVel.update(velocityZ);
  
  // --- AMORTECIMENTO (DAMPING) ---
  // Reduz a velocidade artificialmente em 1% a cada ciclo para evitar drift infinito
  // Simula uma fricção que puxa os valores para zero.
  velocityZ *= 0.99; 

  positionZ += velocityZ * dt;
  positionZ = hpFilterPos.update(positionZ);

  // Zera posição se ficar muito tempo sem movimento significativo (evita drift lento acumulado)
  if (fabs(velocityZ) < 0.01) {
    positionZ *= 0.95; // Puxa suavemente para zero
  }

  // Output (Multiplicado por 100 para ver em CM no plotter)

  //unsigned long ultimo = mill
  //if (agora - ultimo >= 100) {
    Serial.print("AcelZ:");
    Serial.print(linearAccelZ);
    Serial.print(",");
    Serial.print("Altura_cm:");
    float altura = positionZ * 100;
    Serial.println(altura); // Exibe em CM
  //}
  
  unsigned long ultimoPico = millis();
  if (ultimoPico > 20000) {
    if (altura > pico)
      pico = altura;   

    Serial.print(",");
    Serial.print("Pico:");
    Serial.print(pico);
  }

  delay(10); 
}


































// CHECKPOINT ANTERIOR

/*
#include <MPU925X.h>
#include <MadgwickAHRS.h> // Você precisa instalar essa biblioteca
#include <Wire.h>

unsigned long ultimo = millis();

// --- Configurações do MPU ---
MPU925X IMU(Wire, 0x68);
int status;
float pos = 0;

// --- Configurações do Filtro Madgwick ---
Madgwick filter;
unsigned long microsPerReading, microsPrevious;

// --- Variáveis de Integração (Física) ---
float velocityZ = 0;
float positionZ = 0; // Essa é a altura da onda
float gravity = 9.81;

// --- Configuração do Filtro Passa-Alta (High Pass) ---
// Esse filtro é essencial para remover o drift da integração
class HighPassFilter {
  private:
    float alpha;
    float last_input;
    float last_output;
  public:
    HighPassFilter(float cutoff_freq, float dt) {
      float RC = 1.0 / (cutoff_freq * 2 * 3.14159);
      alpha = RC / (RC + dt);
      last_input = 0;
      last_output = 0;
    }
    float update(float input) {
      float output = alpha * (last_output + input - last_input);
      last_input = input;
      last_output = output;
      return output;
    }
};

// Instancia o filtro (Corte em 0.1Hz para ondas lentas)
// Se a onda for muito rápida, aumente para 0.2 ou 0.3
HighPassFilter hpFilterVel(0.1, 0.01); 
HighPassFilter hpFilterPos(0.1, 0.01);

void setup() {
  Serial.begin(115200);
  //Serial0.begin(9600);

  while (!Serial) {}

  // Inicia o MPU
  int status = IMU.begin();
  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    while (1) {}
  }
  
  // Inicia o filtro de fusão (25Hz é um chute inicial, será ajustado no loop)
  filter.begin(25); 

  microsPrevious = micros();
  
  // Calibração rápida inicial (opcional, deixe o sensor parado)
  Serial.println("Calibrando... Deixe parado.");
  delay(2000);
  Serial.println("Iniciando leituras.");
}

void loop() {
  // Controle de tempo (DT) para integração precisa
  unsigned long microsNow = micros();
  float dt = (microsNow - microsPrevious) / 1000000.0; // DT em segundos
  microsPrevious = microsNow;

  // Evita erros se o DT for zero ou muito grande
  if (dt <= 0 || dt > 1.0) return;

  // 1. Ler Sensores
  IMU.readSensor();
  
  // O MPU925X library geralmente retorna Rad/s e m/s^2.
  // O Madgwick geralmente espera Graus/s. Vamos converter.
  float gx = IMU.getGyroX_rads() * (180.0 / PI);
  float gy = IMU.getGyroY_rads() * (180.0 / PI);
  float gz = IMU.getGyroZ_rads() * (180.0 / PI);
  float ax = IMU.getAccelX_mss();
  float ay = IMU.getAccelY_mss();
  float az = IMU.getAccelZ_mss();

  // 2. Atualizar Orientação (Quaternion)
  // Isso substitui o "icm20948.readQuatData" do código original
  filter.updateIMU(gx, gy, gz, ax, ay, az);

  // Pega os Quaternions calculados
  float q0 = filter.getQ0(); // W
  float q1 = filter.getQ1(); // X
  float q2 = filter.getQ2(); // Y
  float q3 = filter.getQ3(); // Z

  // 3. Rotacionar a Aceleração para o "Mundo Real" (World Frame)
  // Precisamos remover a inclinação do sensor para saber o que é realmente ACIMA (Z)
  // Fórmula matemática de rotação por Quaternion para o eixo Z (simplificada):
  
  // Calcula a direção da gravidade esperada baseada na rotação atual
  // (Isso é o vetor gravidade "visto" pelo sensor)
  float gravityCompX = 2.0f * (q1 * q3 - q0 * q2);
  float gravityCompY = 2.0f * (q0 * q1 + q2 * q3);
  float gravityCompZ = q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3;

  // Aceleração linear (Remove a gravidade do eixo Z do sensor rotacionado)
  // Aqui estamos projetando a aceleração lida no eixo vertical real
  float linearAccelZ = (ax * (2.0f * (q1 * q3 - q0 * q2))) +
                       (ay * (2.0f * (q0 * q1 + q2 * q3))) + 
                       (az * (q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3));
  
  linearAccelZ -= gravity; // Remove os 9.81 m/s² da gravidade

  // 4. Filtragem e Integração (Dupla Integração)
  
  // Passo A: Aceleração -> Velocidade
  // Integra: v = v + a * dt
  velocityZ += linearAccelZ * dt;
  
  // Filtra Velocidade (Passa-Alta para remover drift da aceleração)
  velocityZ = hpFilterVel.update(velocityZ);

  // Passo B: Velocidade -> Posição (Altura)
  // Integra: p = p + v * dt
  positionZ += velocityZ * dt;

  // Filtra Posição (Passa-Alta para garantir que a média seja zero, ou seja, nível do mar)
  positionZ = hpFilterPos.update(positionZ);

  // 5. Output
  // Imprime para o Serial Plotter
  // Azul: Aceleração Real Z, Vermelho: Altura
  //Serial.print("AccelZ_Real:");
  //Serial.print(linearAccelZ);
  //Serial.print(",");
  //Serial.print("Altura_m:");
  //Serial.println(positionZ);

  unsigned long agora = millis();
  if (agora - ultimo >= 1000) {
    float altura = positionZ * 100;
    Serial.print("Altura(cm):");
    Serial.println(altura);
  }
  
  // Mantém uma frequência de atualização razoável
  delay(10); 
}
*/













