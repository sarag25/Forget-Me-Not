#include <Arduino.h>

#define IS_LIGHT_VERSION false

#define DEBUG_MAIN true
#define DEBUG_SETUP false
#define DEBUG_INCOMING_MESSAGES false
#define DEBUG_ALERT true
#define DEBUG_STATUS true
#define DEBUG_RFID true

#include "PacketManager.h"
#include "RFIDReader.h"
#include "WeightSensor.h"

#if !IS_LIGHT_VERSION
#include "Accelerometer.h"
#include "Buzzer.h"
#include "TempHum.h"
#endif

#if !IS_LIGHT_VERSION
const int ID = 1;
#else
const int ID = 2;
#endif

const int STATUS_SEND_RATE = 5000;
const int WEIGHT_SENSOR_SAMPLING_RATE = 1000;
const int RFID_SENSOR_SAMPLING_RATE = 1000;

#if !IS_LIGHT_VERSION
const int TEMPHUM_SENSOR_SAMPLING_RATE = 1000;
const int BUZZER_SENSOR_SAMPLING_RATE = 1000;
#endif

// TODO threshold
int weightSensorThreshold = 2000;
int tare = 15;

#if !IS_LIGHT_VERSION
float tempminSensorThreshold = 0;
float tempmaxSensorThreshold = 50;
float humSensorThreshold = 100;
double accelerometerThreshold = 100.0;
#endif

#if !IS_LIGHT_VERSION
bool isBuzzerPlaying = true;
bool findMe = false;
#endif

bool errorWeight = false;
#if !IS_LIGHT_VERSION
bool errorTemp = false;
bool errorHum = false;
bool errorBump = false;
#endif

SoftwareSerial bl(5, 6);
PacketManager pm(bl);
PacketManager::Packet packet;
RFIDReader rfid;
#if !IS_LIGHT_VERSION
WeightSensor w(0, 4, 2);
#else
WeightSensor w(1, 4, 2);
#endif

#if !IS_LIGHT_VERSION
Accelerometer a;
TempHum th;
Buzzer b;
#endif

unsigned long time_rfid;
unsigned long time_weight;
unsigned long time_status;

#if !IS_LIGHT_VERSION
unsigned long time_accel;
unsigned long time_temphum;
unsigned long time_buzzer;
#endif

void sendStatus() {
  uint32_t status[5] = {0};
/*
  status[0]: error bool
  status[1]: temperature int
  status[2]: humidity int
  status[3]: acceleration int
  status[4]: weight int
*/
#if !IS_LIGHT_VERSION
  status[0] = errorBump || errorHum || errorTemp || errorWeight;
  status[1] = (int32_t)th.readTemp();
  status[2] = (uint32_t)th.readHum();
  status[3] = (uint32_t)a.getAcceleration();
  status[4] = (int32_t)w.getWeight();
#else
  status[0] = errorWeight;
  status[1] = 22;
  status[2] = 25;
  status[3] = 0;
  status[4] = (int32_t)w.getWeight();
#endif

  packet.mtype = PacketManager::STATUS;
  packet.length = sizeof(*status) * 5;
  packet.payload = (byte*)status;

  pm.sendPacket(packet);

  if (DEBUG_MAIN && DEBUG_STATUS) Serial.println("send STATUS");

  if (DEBUG_MAIN && DEBUG_STATUS) {
    Serial.println("STATUS:\n\terror: " + String(status[0]) + "\n\ttemp: " +
                   String(status[1]) + "\n\thumidity: " + String(status[2]) +
                   "\n\tacceleration: " + String(status[3]) +
                   "\n\tweigth: " + String(status[4]));
  }
}

void setup() {
  if (DEBUG_MAIN) Serial.begin(9600);
  delay(10);
  if (DEBUG_MAIN && DEBUG_SETUP) Serial.println("Setup...");

  // WEIGHT SENSOR
  w.setup();
  if (DEBUG_MAIN && DEBUG_SETUP)
    Serial.println("WEIGHT SENSOR setup completed.");

  bl.begin(9600);

  // RFID
  rfid.setup();
  if (DEBUG_MAIN && DEBUG_SETUP) Serial.println("RFID setup completed.");

#if !IS_LIGHT_VERSION
  // ACCELEROMETER
  a.setup();
  if (DEBUG_MAIN && DEBUG_SETUP)
    Serial.println("ACCELEROMETER setup completed.");

  // TEMP & HUM
  th.setup();
  if (DEBUG_MAIN && DEBUG_SETUP) Serial.println("TEMPHUM setup completed.");

  // BUZZER
  b.setup();
  if (DEBUG_MAIN && DEBUG_SETUP) Serial.println("BUZZER setup completed.");

  // LED
  pinMode(3, OUTPUT);
  if (DEBUG_MAIN && DEBUG_SETUP) Serial.println("LED setup completed.");
#endif

  time_weight = millis();
  time_rfid = time_weight;
  time_status = time_weight;

#if !IS_LIGHT_VERSION
  time_accel = time_weight;
  time_temphum = time_weight;
  time_buzzer = time_weight;
#endif

  packet.payload = nullptr;

  if (DEBUG_MAIN) Serial.println("Setup completed.");
}

void loop() {
  if (pm.readPacket(packet) == true) {
    if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
      Serial.println("One packet received");
    typedef PacketManager::MessageType ptype;
    switch (packet.mtype) {
      case ptype::WEIGHT:
        weightSensorThreshold = *(int32_t*)packet.payload;
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New weight threshold: ") +
                         weightSensorThreshold);
        break;

      case ptype::TARE:
        tare = *(int32_t*)packet.payload;
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New tare received: ") + tare);
        break;

      case ptype::ID_REQUEST:
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("ID REQUEST received: ") + tare);
        packet.mtype = ptype::ID_ANSWER;
        packet.length = 4;
        packet.payload = (byte*)&ID;
        pm.sendPacket(packet);
        packet.payload = nullptr;

#if !IS_LIGHT_VERSION
      case ptype::BUMP:
        accelerometerThreshold = *(int32_t*)packet.payload;
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New bump threshold: ") +
                         accelerometerThreshold);
        break;
      case ptype::TEMP:
        tempminSensorThreshold = *(int32_t*)packet.payload;
        tempmaxSensorThreshold = *(int32_t*)(packet.payload + 4);
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New tempmin threshold: ") +
                         tempminSensorThreshold);
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New tempmax threshold: ") +
                         tempmaxSensorThreshold);
        break;
      case ptype::HUM:
        humSensorThreshold = *(int32_t*)packet.payload;
        if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
          Serial.println(String("New humidity threshold: ") +
                         humSensorThreshold);
        break;

      case ptype::FIND_ME:
        if (!findMe) {
          findMe = true;
          if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES) Serial.println("FIND ME");
        }
        break;
      case ptype::STOP_FIND_ME:
        if (findMe) {
          findMe = false;
          if (DEBUG_MAIN && DEBUG_INCOMING_MESSAGES)
            Serial.println("STOP FIND ME");
        }
        break;
#endif

      default:
        break;
    }

    // deallocate memory
    if (packet.payload != nullptr) {
      delete[] packet.payload;
      packet.payload = nullptr;
    }
  }

  if (millis() - time_weight >= WEIGHT_SENSOR_SAMPLING_RATE) {
    int32_t weight = w.getWeight();
    if (weight >= weightSensorThreshold) {
      errorWeight = true;
      packet.mtype = PacketManager::ALERT_WEIGHT;
      packet.length = 4;
      packet.payload = (byte*)&weight;

      pm.sendPacket(packet);
      sendStatus();

      if (DEBUG_MAIN && DEBUG_ALERT)
        Serial.println("Peso eccessivo rilevato: " +
                       String(w.getWeight() / 1000.0) + " kg");
    } else {
      errorWeight = false;
    }

    time_weight = millis();
  }

  if (millis() - time_rfid >= RFID_SENSOR_SAMPLING_RATE) {
    String uuid = rfid.readUID();
    if (uuid.length() > 1) {
      packet.mtype = PacketManager::OBJ;
      packet.length = uuid.length();
      packet.payload = (byte*)uuid.c_str();

      pm.sendPacket(packet);
      sendStatus();
      if (DEBUG_MAIN && DEBUG_RFID)
        Serial.println("Oggetto rilevato. UUID: " + uuid);
    }

    time_rfid = millis();
  }

#if !IS_LIGHT_VERSION
  if (millis() - time_accel >= a.BNO055_SAMPLERATE_DELAY_MS) {
    if (a.getAcceleration() >= accelerometerThreshold) {
      errorBump = true;
      packet.mtype = PacketManager::ALERT_BUMP;
      packet.length = 0;
      packet.payload = nullptr;
      pm.sendPacket(packet);
      sendStatus();

      if (DEBUG_MAIN && DEBUG_ALERT) Serial.println("Bump rilevato.");
    } else {
      errorBump = false;
    }

    time_accel = millis();
  }

  if (millis() - time_temphum >= TEMPHUM_SENSOR_SAMPLING_RATE) {
    if (th.readHum() >= humSensorThreshold) {
      errorHum = true;
      packet.mtype = PacketManager::ALERT_HUM;
      packet.length = 0;
      packet.payload = nullptr;

      pm.sendPacket(packet);
      sendStatus();
      if (DEBUG_MAIN && DEBUG_ALERT) Serial.println("Umidità eccessiva.");
    } else {
      errorHum = false;
    }

    int32_t temp = th.readTemp();

    if (temp <= tempminSensorThreshold || temp >= tempmaxSensorThreshold) {
      errorTemp = true;

      packet.mtype = PacketManager::ALERT_TEMP;
      packet.length = 4;
      packet.payload = (byte*)&temp;

      pm.sendPacket(packet);
      sendStatus();

      if (DEBUG_MAIN && DEBUG_ALERT)
        Serial.println(String("Temperatura anormale: ") + String(temp));
    } else {
      errorTemp = false;
    }

    time_temphum = millis();
  }

  if (millis() - time_buzzer >= BUZZER_SENSOR_SAMPLING_RATE) {
    if (isBuzzerPlaying && findMe) {
      b.soundON();
      isBuzzerPlaying = false;
    } else {
      b.soundOFF();
      isBuzzerPlaying = true;
    }
    time_buzzer = millis();
  }

  if (errorWeight || errorBump || errorHum || errorTemp) {
    digitalWrite(3, HIGH);
  } else {
    digitalWrite(3, LOW);
  }
#endif

  if (millis() - time_status > STATUS_SEND_RATE) {
    sendStatus();
    time_status = millis();
  }
}