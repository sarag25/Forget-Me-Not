#ifndef SENSORS_PACKET_MANAGER_H_
#define SENSORS_PACKET_MANAGER_H_

#include <Arduino.h>
#include <SoftwareSerial.h>
//#include "CommModule.h"

class PacketManager{
    private:
        SoftwareSerial &cm;
        unsigned long connection_start;
        const unsigned long CONNECTION_TIMEOUT = 1000;

        bool checkTimeout();
    public:
        /**
         * @brief Constructor of packet manager.
         * @param cm reference to a communication module class instance.
         */
        PacketManager(SoftwareSerial &cm);

        /**
         * @brief definition of the different message types.
         */
        enum MessageType{
            NOT_VALID = 0,  // A message having this code should be discarded

            /* THRESHOLDS */
            WEIGHT = 1,
            BUMP,
            TEMP,
            HUM,

            /* ALERT MESSAGES */
            ALERT_WEIGHT,
            ALERT_BUMP,
            ALERT_TEMP,
            ALERT_HUM,

            /* OBJECT IN/OUT */
            OBJ,

            /* MAKE AND STOP SOUND */
            FIND_ME,
            STOP_FIND_ME,

            /* BOX STATUS */
            STATUS,

            /* TARE BOX */
            TARE,

            /* ID EXCHANGE */
            ID_REQUEST,
            ID_ANSWER
        };
        
        /**
         * @brief Definition of packet structure.
         */
        struct Packet{
            MessageType mtype;
            int length;
            byte* payload;
        };

        /**
         * @brief Function for reading an incoming packet.
         * @return True if read was successful.
         */
        bool readPacket(Packet& pk);

        /**
         * @brief Function for sending a packet.
         */
        void sendPacket(const Packet& pk);
};

#endif //SENSORS_PACKET_MANAGER_H_