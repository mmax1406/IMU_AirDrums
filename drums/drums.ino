#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <ESP8266WiFi.h>

// Wi-Fi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// Wi-Fi server
WiFiServer server(12345);

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (10)
uint8_t system1 = 0, gyro1 = 0, accel1 = 0, mag1 = 0;
uint8_t system2 = 0, gyro2 = 0, accel2 = 0, mag2 = 0;

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28);

void setup(void) {
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test"); 

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();

  /* Initialise the sensor */
  if(!bno.begin()) {
    Serial.println("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  if(!bno2.begin()) {
    Serial.println("Ooops, no BNO055-2 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  delay(1000);

  /* Use external crystal for better accuracy */
  bno.setExtCrystalUse(true);
  bno2.setExtCrystalUse(true);
}

void loop(void) {
  WiFiClient client = server.available();  // Check for incoming connections
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      sensors_event_t accevent;
      sensors_event_t accevent2;
      bno.getEvent(&accevent, Adafruit_BNO055::VECTOR_GYROSCOPE);
      bno2.getEvent(&accevent2, Adafruit_BNO055::VECTOR_GYROSCOPE);
      bno.getCalibration(&system1, &gyro1, &accel1, &mag1);
      bno2.getCalibration(&system2, &gyro2, &accel2, &mag2);

      imu::Quaternion quat = bno.getQuat();
      imu::Quaternion quat2 = bno2.getQuat();

      // Transmit data to client
      client.print(quat.w(), 4); client.print(",");
      client.print(quat.x(), 4); client.print(",");
      client.print(quat.y(), 4); client.print(",");
      client.print(quat.z(), 4); client.print(",");
      client.print(accevent.gyro.z); client.print(",");
      client.print(system1); client.print(",");
      client.print(quat2.w(), 4); client.print(",");
      client.print(quat2.x(), 4); client.print(",");
      client.print(quat2.y(), 4); client.print(",");
      client.print(quat2.z(), 4); client.print(",");
      client.print(accevent2.gyro.z); client.print(",");
      client.println(system2);

      delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    client.stop();
    Serial.println("Client disconnected");
  }
}
