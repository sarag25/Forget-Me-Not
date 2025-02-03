#ifndef SENSORS_ACCELEROMETER_H_
#define SENSORS_ACCELEROMETER_H_

#include <Adafruit_BNO055.h>

#define ACCELEROMETER_DEFAULT_ID 55

class Accelerometer {
 private:
  Adafruit_BNO055 bno;
  unsigned long timeLastMeasure;
  double lastAcceleration;

 public:
  const uint16_t BNO055_SAMPLERATE_DELAY_MS = 100;
  /**
   * @brief Constructor of accelerometer, it sets up the id of the sensor and
   * the pin for the communication (I2C is the default).
   * @param id The id of the accelerometer (needed for library purposes).
   * @param pin The pin of the accelerometer.
   */
  Accelerometer(uint32_t id = ACCELEROMETER_DEFAULT_ID, uint8_t pin = 0x28);

  /**
   * @brief Gets the module of the acceleration measured by the sensor.
   * This operation can be done only at a certain sample rate: if the function
   * is called and the sample rate has not elapsed, this function returns the
   * last measurement.
   * @return The measured acceleration.
   */
  double getAcceleration();

  /**
   * @brief This function sets up the sensor. It MUST be called when setupping
   * the board.
   */
  void setup();
};

#endif  // SENSORS_ACCELEROMETER_H_