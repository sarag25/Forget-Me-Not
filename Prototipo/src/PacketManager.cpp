#include "PacketManager.h"

#define DEBUG_PM true

PacketManager::PacketManager(SoftwareSerial& cm)
: cm(cm), connection_start(0) {}

bool PacketManager::checkTimeout() {
  return millis() - connection_start > CONNECTION_TIMEOUT;
}

bool PacketManager::readPacket(Packet& pk) {
  int firstByte = cm.read();
  // INITIATING SEQUENCE CHECK
  if (firstByte != 0xfe) {
    //if(DEBUG_PM) Serial.println("No starting byte [0xfe] found.");
    return false;
  }

  // TIMEOUT IF PACKET TRASMISSION IS TOO LONG
  connection_start = millis();

  // EXTRACT THE HEADER
  while (cm.available() < 2 && !checkTimeout());
  if (checkTimeout()) {
    // IF TIMEOUT OCCURRED SIGNAL ERROR
    if (DEBUG_PM) Serial.println("PACKET CORRUPTION: connection terminated abnormally - header.");
    return false;
  }

  int length = cm.read();
  int messageType = cm.read();

  // BEGIN PACKET FORMATTING
  pk.mtype = (MessageType)messageType;
  pk.length = length;

  // EXTRACTING PAYLOAD AND TERMINATING SEQUENCE
  while (cm.available() < pk.length + 1 && !checkTimeout());
  if (checkTimeout()) {
    if(DEBUG_PM) Serial.println("PACKET CORRUPTION: connection terminated abnormally - body.");
    return false;
  }

  // MEMORY ALLOCATION OF THE PACKET PAYLOAD
  pk.payload = new byte[pk.length];

  for (int i = 0; i < pk.length; i++) {
    byte b = cm.read();
    pk.payload[i] = b;
  }

  int terminator = cm.read();
  
  // TERMINATING SEQUENCE CHECK
  if (terminator != 0xff) {
    delete[] pk.payload;
    if (DEBUG_PM) Serial.println("PACKET CORRUPTION: No terminator [0xff] found after reaching packet length.");
    return false;
  }

  return true;
}

void PacketManager::sendPacket(const Packet& pk) { 
  cm.write(0xfe);
  cm.write((byte)pk.length);
  cm.write((byte)pk.mtype);
  for (int i = 0; i < pk.length; i++){
      cm.write(pk.payload[i]);
  }
  cm.write(0xff);
}