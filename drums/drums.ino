#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples and init some vars*/
#define BNO055_SAMPLERATE_DELAY_MS (10)
uint8_t system1 = 0, gyro1 = 0, accel1 = 0, mag1 = 0;
bool initialized = false; // Track if we passed the grace period
unsigned long startTime;

// Check I2C device address and correct line below (by default address is 0x29 or 0x28) id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);

// Function to try and reconnect in case of disconnection
void attemptReconnect() {
  Serial.print(-1);
  Serial.print(F(" "));
  Serial.print(-2);
  Serial.print(F(" "));
  Serial.print(-3);
  Serial.print(F(" "));
  Serial.print(-4);
  Serial.print(F(" "));
  Serial.println(-5);

  if (!bno.begin()) {
    delay(10);
    return;
  }

  bno.setExtCrystalUse(true);

  initialized = false;
  startTime = millis(); // Record the start time
}

void setup(void)
{
  Serial.begin(115200);
  attemptReconnect();
}

void loop(void)
{
  sensors_event_t gravity_event;
  bno.getEvent(&gravity_event, Adafruit_BNO055::VECTOR_GRAVITY);

  // Allow 3 seconds before checking for sensor failure
  if ((millis() - startTime) > 3000) {
    initialized = true;  // After 3 seconds, enable error checking
  }  
  // Check if all gravity values are zero (indicating a sensor issue)
  if (initialized && gravity_event.acceleration.x == 0.0 && 
      gravity_event.acceleration.y == 0.0 && 
      gravity_event.acceleration.z == 0.0) 
  {
    attemptReconnect();
    return; // Skip the rest of the loop until the sensor is fixed
  }

  // Normal operation - read quaternion and gyroscope
  imu::Quaternion quat = bno.getQuat();
  bno.getCalibration(&system1, &gyro1, &accel1, &mag1);

  Serial.print(quat.w(), 4);
  Serial.print(F(" "));
  Serial.print(quat.x(), 4);
  Serial.print(F(" "));
  Serial.print(quat.y(), 4);
  Serial.print(F(" "));
  Serial.print(quat.z(), 4);
  Serial.print(F(" "));
  Serial.println(system1, DEC);

  delay(BNO055_SAMPLERATE_DELAY_MS);
}

