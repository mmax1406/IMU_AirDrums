#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (10)
uint8_t system1 = 0, gyro1 = 0, accel1 = 0, mag1 = 0;
uint8_t system2 = 0, gyro2 = 0, accel2 = 0, mag2 = 0;

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28);

/**************************************************************************/
/*
    Arduino setup function (automatically called at startup)
*/
/**************************************************************************/
void setup(void)
{
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test"); Serial.println("");

  /* Initialise the sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  /* Initialise the sensor */
  if(!bno2.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055-2 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
   
  delay(1000);

  /* Use external crystal for better accuracy */
  bno.setExtCrystalUse(true);
  /* Use external crystal for better accuracy */
  bno2.setExtCrystalUse(true);
   
}

/**************************************************************************/
/*
    Arduino loop function, called once 'setup' is complete (your own code
    should go here)
*/
/**************************************************************************/
void loop(void)
{
  sensors_event_t accevent;
  sensors_event_t accevent2;
  bno.getEvent(&accevent, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno2.getEvent(&accevent2, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getCalibration(&system1, &gyro1, &accel1, &mag1);
  bno2.getCalibration(&system2, &gyro2, &accel2, &mag2);

  Serial.print(system1, DEC);
  Serial.print(F(" "));
  Serial.println(system2, DEC);

  if (system1>0 && system2>0){
    // Quaternion data
    imu::Quaternion quat = bno.getQuat();
    Serial.print(F(" "));
    Serial.print(quat.w(), 4);
    Serial.print(F(" "));
    Serial.print(quat.x(), 4);
    Serial.print(F(" "));
    Serial.print(quat.y(), 4);
    Serial.print(F(" "));
    Serial.print(quat.z(), 4);
    Serial.print(F(" "));
    Serial.print((float)accevent.gyro.z);
    Serial.print(F(" "));
    Serial.print(system1, DEC);

    // Quaternion data
    imu::Quaternion quat2 = bno2.getQuat();
    Serial.print(F(" "));
    Serial.print(quat2.w(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.x(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.y(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.z(), 4);
    Serial.print(F(" "));
    Serial.print((float)accevent2.gyro.z);
    Serial.print(F(" "));
    Serial.println(system2, DEC);

    delay(BNO055_SAMPLERATE_DELAY_MS);
  }
}
