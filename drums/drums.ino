#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (10)

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
  /* Get a new sensor event */
  sensors_event_t event;
  sensors_event_t event2;
  sensors_event_t accevent;
  sensors_event_t accevent2;
  bno.getEvent(&event);
  bno2.getEvent(&event2);
  bno.getEvent(&accevent, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno2.getEvent(&accevent2, Adafruit_BNO055::VECTOR_LINEARACCEL);

  /* Board layout:
         +----------+
         |         *| RST   PITCH  ROLL  HEADING
     ADR |*        *| SCL
     INT |*        *| SDA     ^            /->
     PS1 |*        *| GND     |            |
     PS0 |*        *| 3VO     Y    Z-->    \-X
         |         *| VIN
         +----------+
  */

  // /* The processing sketch expects data as roll, pitch, heading */
  Serial.print((float)event.orientation.x);
  Serial.print(F(" "));
  Serial.print((float)event.orientation.y);
  Serial.print(F(" "));
  Serial.print((float)event.orientation.z);
  Serial.print(F(" "));
  Serial.print((float)accevent.acceleration.z);
  Serial.print(F(" "));
  Serial.print((float)event2.orientation.x);
  Serial.print(F(" "));
  Serial.print((float)event2.orientation.y);
  Serial.print(F(" "));
  Serial.print((float)event2.orientation.z);
  Serial.print(F(" "));
  Serial.print((float)accevent2.acceleration.z);
  Serial.println(F(""));

  delay(BNO055_SAMPLERATE_DELAY_MS);
}
