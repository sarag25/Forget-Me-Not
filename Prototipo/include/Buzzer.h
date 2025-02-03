#ifndef BUZZER_H_
#define BUZZER_H_
#include <Arduino.h>

class Buzzer {
  private:
    byte OUT = 8;

  public:
    Buzzer(byte OUT = 8);

    void setup();

    void soundON();

    void soundOFF();

};

#endif  // BUZZER_H_