#include <../MPU925X.h>

/*MPU925X(TwoWire &bus,uint8_t address) An MPU925X object should be declared, specifying the I2C bus and MPU-925X I2C address. The MPU-925X I2C address will be 0x68 if the AD0
 pin is grounded or 0x69 if the AD0 pin is pulled high. For example, the following code declares an MPU925X object called IMU with an MPU-925X sensor located on I2C bus 0 with
  a sensor address of 0x68 (AD0 grounded).*/

MPU925X IMU(Wire, 0x68);
int status;
float pos = 0;

def 

void setup()
{
  // serial to display data
  Serial.begin(115200);
  while (!Serial)
  {
  }

  // start communication with IMU
  status = IMU.begin();
  if (status < 0)
  {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while (1)
    {
    }
  }
}

void loop(){
    // Lê o sensor
    IMU.readSensor();
    Serial.println('A aceleracao em X é:');
    Serial.println(IMU.getAccelX_mss());
    Serial.println('A aceleracao em Y é:');
    Serial.println(IMU.getAccelY_mss());
    Serial.println('A aceleracao em Z é:');
    Serial.println(IMU.getAccelZ_mss());
}