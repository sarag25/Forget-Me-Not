#include "Accelerometer.h"

#define DEBUG_MODE false

Accelerometer::Accelerometer(uint32_t id, uint8_t pin) {
  bno = Adafruit_BNO055(id, pin);
  timeLastMeasure = 0;
  lastAcceleration = 0.0;
}

double Accelerometer::getAcceleration() {
  if (timeLastMeasure == 0 ||
      millis() - timeLastMeasure > BNO055_SAMPLERATE_DELAY_MS) {
    sensors_event_t linearAccelData;
    bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
    double x = linearAccelData.acceleration.x;
    double y = linearAccelData.acceleration.y;
    double z = linearAccelData.acceleration.z;
    timeLastMeasure = millis();
    lastAcceleration = x * x + y * y + z * z;
  }
  return lastAcceleration;
}

void Accelerometer::setup() {
  if (DEBUG_MODE) Serial.println("Setup acc started");
  if (!bno.begin()) {
    /* There was a problem detecting the BNO055... check your connections */
    Serial.println(
        "ERROR: Accelerometer not found, no BNO055 detected... Check your wiring or I2C ADDR!");
    //while (true);
  }
  if (DEBUG_MODE) Serial.print("Setup acc comple");
}
