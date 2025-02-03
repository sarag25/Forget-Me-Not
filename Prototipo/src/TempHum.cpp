#include "TempHum.h"

#define DEBUG_TEMPHUM false

TempHum::TempHum(byte OUT) : dht(OUT, DHT11) {
    timeLastMeasureTemp = 0;
    timeLastMeasureHum = 0;
    measureTemp = 0.0;
    measureHum = 0.0;
}

void TempHum::setup() {
  dht.begin();
  if (DEBUG_TEMPHUM) Serial.println("Setup");
}

float TempHum::readTemp() {
  if (DEBUG_TEMPHUM) Serial.println("Reading Temperature");
  if (timeLastMeasureTemp == 0 ||
      millis() - timeLastMeasureTemp > DHT11_SAMPLERATE_DELAY_MS) {  
    timeLastMeasureTemp = millis();
    measureTemp = dht.readTemperature(); 
  }
  return measureTemp;
}

float TempHum::readHum() {
  if (DEBUG_TEMPHUM) Serial.println("Reading Humidity");
  if (timeLastMeasureHum == 0 ||
      millis() - timeLastMeasureHum > DHT11_SAMPLERATE_DELAY_MS) {  
    timeLastMeasureHum = millis();
    measureHum = dht.readHumidity(); 
  }
  return measureHum;
}