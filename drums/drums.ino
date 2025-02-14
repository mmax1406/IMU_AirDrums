#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples and init some vars*/
#define BNO055_SAMPLERATE_DELAY_MS (10)
#define LOOP_PERIOD_MS 25
uint8_t system1 = 0, gyro1 = 0, accel1 = 0, mag1 = 0;
uint8_t system2 = 0, gyro2 = 0, accel2 = 0, mag2 = 0;
bool initialized = false; // Track if we passed the grace period
unsigned long startTime, lastUpdateTime;

// Check I2C device address and correct line below (by default address is 0x29 or 0x28) id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28);

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
  /* Initialise the sensor */
  if (!bno.begin())
  {
    Serial.print("Sensor 1 no good!");
    while (1);
  }
  /* Initialise the sensor */
  if (!bno2.begin())
  {
    Serial.print("Sensor 2 no good!");
    while (1);
  }

  bno.setExtCrystalUse(true);
  bno2.setExtCrystalUse(true);

  delay(1000);
  startTime = millis();  // Record startup time
  lastUpdateTime = millis(); // Initialize loop timing
}

void loop(void)
{

  // Run at 40Hz (every 25ms)
  unsigned long currentTime = millis();

  if (currentTime - lastUpdateTime >= LOOP_PERIOD_MS) {
    lastUpdateTime = currentTime;

    // Mechanism for disconnections
    // Allow 3 seconds before checking for sensor failure
    if ((currentTime - startTime) > 3000) {
      initialized = true;  // After 3 seconds, enable error checking
    }  
    // Check if all values are zero for more than N consecutive samples (indicating a sensor issue)

    // Normal operation sensor1
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
    Serial.print(system1, DEC);
    Serial.print(F(" "));

    // Normal operation sensor2
    imu::Quaternion quat2 = bno2.getQuat();
    bno2.getCalibration(&system2, &gyro2, &accel2, &mag2);
    Serial.print(quat2.w(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.x(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.y(), 4);
    Serial.print(F(" "));
    Serial.print(quat2.z(), 4);
    Serial.print(F(" "));
    Serial.println(system2, DEC);

    delay(BNO055_SAMPLERATE_DELAY_MS);
  }
}

