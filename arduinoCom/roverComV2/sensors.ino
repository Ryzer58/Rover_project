/*The Main detection mechanism is two ultrasonic sensors, one positoned at the the front and
*the other at the rear. Later I plan to use two arrays of 3 sensors. One array postioned at the
*front and the other at the back, to reduce, pin count the recieve pins will be multiplexed
*reducing the pin count from 12 to 8.
*
*/


/*

unsigned long pingTimer[SONAR_NUM]; // Holds the times when the next ping should happen

NewPing sonar[SONAR_NUM] = {       // Sensor object array.
  NewPing(12, 8, MAX_DISTANCE),    //Front facing sensor
  NewPing(6, 7,  MAX_DISTANCE)     //Rear facing sensor.
//Potential pins to use later for additional modules
//NewPing(11, 8, MAX_DISTANCE)     //Front right    
//NewPing(10, 8, MAX_DISTANCE)     //Front left
//NewPing(3, 7, MAX_DISTANCE)      //Rear right
//NewPing(2, 7, MAX_DISTANCE)      //Rear left



};                                  
void intialise_sensors(){                 //Carried out during setup phase
  pingTimer[0] = millis() + 75;           // First ping starts at 75ms, gives time for the Arduino to chill before starting.
  for (uint8_t i = 1; i < SONAR_NUM; i++) // Set the starting time for each sensor.
    pingTimer[i] = pingTimer[i - 1] + PING_INTERVAL;
}

//-----------------------------------------------------------------------------------------------------------------------------

int scanning(bool dir){

  //unsigned long pingTimer[SONAR_NUM]; // Holds the times when the next ping should happen (not currently needed)
  //for each sensor.
  unsigned int cm[SONAR_NUM];           // Where the ping distances are stored.
  uint8_t act_sensor = 0;                // Keeps track of which sensor is active.
  uint8_t half_sen = SONAR_NUM / 2;
  uint8_t i = 0;

  if (dir == true){ //Use forward facing sonar(s)

    act_sensor = 0;

    //i = 0 //reserved for later use
 
  }

  else{ //Use rear facing sonars

    act_sensor = 1;
    //i = 3
        
  }
  
  sonar[act_sensor].ping_timer(echoCheck(act_sensor)); // Do the ping (processing continues, interrupt will call echoCheck to look for echo).
  //array(i)

}
  

 * 
 * uint8_t array(uint8_t i){
  
  for (uint8_t i = 0; i < half_sen; i++) { // Loop through all the sensors.
    if (millis() >= pingTimer[i]) {         // Is it this sensor's time to ping?
      pingTimer[i] += PING_INTERVAL * SONAR_NUM;  // Set next time this sensor will be pinged.
      if (i == 0 && currentSensor == SONAR_NUM - 1) clusterCycle(); // Sensor ping cycle complete, do something with the results.
      sonar[currentSensor].timer_stop();          // Make sure previous timer is canceled before starting a new ping (insurance).
      currentSensor = i;                          // Sensor being accessed.
      cm[currentSensor] = 0;                      // Make distance zero in case there's no ping echo for this sensor.
      sonar[currentSensor].ping_timer(echoCheck(currentSensor)); // Do the ping (processing continues, interrupt will call echoCheck to look for echo).
    }
  }

}
  // The rest of your code would go here.



uint8_t echoCheck(uint8_t act_sensor, unsigned int cm[act_sensor]) { // If ping received, set the sensor distance to array.
  if (sonar[act_Sensor].check_timer())
    cm[act_sensor] = sonar[act_sensor].ping_result / US_ROUNDTRIP_CM;
}

void clusterCycle() { // Sensor ping cycle complete, do something with the results.
  for (uint8_t i = 0; i < SONAR_NUM; i++) {
    Serial.print(i); //Todo remove print states and send value back to main array
    Serial.print("=");
    Serial.print(cm[i]);
    Serial.print("cm ");
  }
  Serial.println();
}

*/

//TODO - Add in section for BNO055 9DOF module
