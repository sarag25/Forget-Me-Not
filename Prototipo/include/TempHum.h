#ifndef TEMP_HUM_H_
#define TEMP_HUM_H_
#include <DHT.h>

class TempHum {
 private:
  DHT dht;
  const unsigned long DHT11_SAMPLERATE_DELAY_MS = 2000;
  unsigned long timeLastMeasureTemp, timeLastMeasureHum;
  double measureTemp, measureHum;

 public:
  /**
    * @brief Constructor of temperature and humidity sensor, 
      it sets up the pin for the communication
      @param OUT The pin of the temperature and humidity sensor
   */
  TempHum(byte OUT = 7);

  /**
   * @brief This function sets up the sensor. It MUST be called when setupping
   * the board.
   */
  void setup();

  /**
   * @brief Gets the temperature read by the sensor
   */
  float readTemp();

  /**
   * @brief Gets the humidity read by the sensor
   */
  float readHum();
};

#endif // TEMP_HUM_H_