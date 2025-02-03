#include "WeightSensor.h"

#define DEBUG_WEIGHT false

double lastWeight = 0;


WeightSensor::WeightSensor(int preset, byte dout, byte sck)
: loadcell(dout,sck), preset(preset){}


void WeightSensor::setup(){
    loadcell.begin();
    unsigned long stabilizing_time = 2000;
    loadcell.start(stabilizing_time);
    if (DEBUG_WEIGHT && (loadcell.getTareTimeoutFlag() || loadcell.getSignalTimeoutFlag())){
        Serial.println("Error wiring problem");
    }
    if(DEBUG_WEIGHT) {Serial.println("Weight Setup complete");}

    loadcell.setCalFactor(loadCellCalFactors[preset]);
    loadcell.setTareOffset(loadCellTareOffsets[preset]);
    tared=false;
}



void WeightSensor::calc_tare_offset(){
    loadcell.update();
    loadcell.tareNoDelay();
    if(DEBUG_WEIGHT){Serial.println("calibrating");}
    while(!loadcell.getTareStatus()){
        loadcell.update();
    }
    if(DEBUG_WEIGHT){Serial.println("calibration complete");}
    Serial.println(String(loadcell.getTareOffset()));
}

int WeightSensor::getWeight(){
    if(loadcell.update() > 0){
        lastWeight = round(loadcell.getData());
        if (lastWeight < 0) lastWeight = 0;
        return lastWeight;
    }
    if(DEBUG_WEIGHT) Serial.println("Sensor weight not updated");
    return lastWeight;
}