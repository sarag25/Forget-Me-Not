#include "Buzzer.h"
# define DEBUG_MODE false

Buzzer::Buzzer(byte OUT) { this->OUT = OUT; }

void Buzzer::setup() { pinMode(OUT, OUTPUT); }

void Buzzer::soundON() { digitalWrite(OUT, HIGH); }

void Buzzer::soundOFF() { digitalWrite(OUT, LOW); }