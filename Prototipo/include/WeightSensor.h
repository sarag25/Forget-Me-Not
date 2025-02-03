#ifndef WEIGHT_SENSOR_H_
#define WEIGHT_SENSOR_H
#include <HX711_ADC.h>

class WeightSensor {
 private:
  const float loadCellCalFactors[2] = {20.5, - 26.5};
  const long int loadCellTareOffsets[2] = {8491809, 8443168};
  HX711_ADC loadcell;
  int preset;

 public:
  bool tared;
  /**
   * @brief Constructor of weight sensor
   * @param preset select the preset for calibrating the sensor
   * @param dout The dout of the weight sensor (needed for library purposes)
   * @param sck The sck of the weight sensor
   */
  WeightSensor(int preset, byte dout = 4, byte sck = 2);

  /**
   * @brief This function sets up the sensor. It MUST be called when setupping
   * the board.
   */
  void setup();

  /**
   * @brief Function that defines the starting weight.
   */
  void tare();
  void calc_tare_offset();
  /**
   * @brief Gets the module of the weight measured by the sensor.
   * This operation can be done only at a certain sample rate: if the function
   * is called and the sample rate has not elapsed, this function returns the
   * last measurement.
   * @return The measured weight
   */
  int getWeight();
};
#endif