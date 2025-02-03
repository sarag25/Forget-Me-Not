#include "RFIDReader.h"

#define DEBUG_RFID false

RFIDReader::RFIDReader(byte SDA, byte RST) : rfid(SDA, RST) {}

void RFIDReader::setup() {
  SPI.begin();
  rfid.PCD_Init();
}

String RFIDReader::readUID() {
  if (rfid.PICC_IsNewCardPresent()) {
    if (rfid.PICC_ReadCardSerial()) {
      String uid = getUID();
      if (DEBUG_RFID) {
        Serial.println("RFID ID: " + uid);
      }
      return uid;
    }
  }
  return "";
}

String RFIDReader::getUID() {
  String uid = "";
  for (int i = 0; i < rfid.uid.size; i++) {
    uid += rfid.uid.uidByte[i] < 0x10 ? "0" : "";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  rfid.PICC_HaltA();
  return uid;
}