#ifndef RFID_READER_H_
#define RFID_READER_H_
#include "Arduino.h"
#include <MFRC522.h>

class RFIDReader {
 private:
  MFRC522 rfid;

 public:
  /**
   * @brief Constructor of RFID sensor,
     it sets up the pin for the communication
     @param SDA The pin of the RFID sensor
     @param RST The pin of the RFID sensor
   */
  RFIDReader(byte SDA = 10, byte RST = 9);

  /**
   * @brief Gets the string of the card read by the sensor
   */
  String readUID();

  /**
   * @brief Gets the string of the card read by the sensor
   */
  String getUID();

  /**
   * @brief This function sets up the sensor. It MUST be called when setupping
   * the board.
   */
  void setup();
};

#endif  // RFID_READER_H_