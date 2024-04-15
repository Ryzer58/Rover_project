
//unsigned long pingTimer[SONAR_NUM]; // Holds the times when the next ping should happen
//unsigned int cm[SONAR_NUM];         // Where the ping distances are stored.

unsigned long last_ping;
unsigned long time_since;
unsigned long ping_time = 50;         //Minimum interval between pings to account for cross echo
unsigned long last_scan;              //Used in test program to moderate the sampling time to 500 ms
unsigned long check_time;
unsigned long scan_now = 500;

uint8_t array_pos[3]={};

bool colAlert;
bool out_range;

NewPing for_array[ARRAY_NUM][SONAR_NUM] = {{ NewPing(12, 12, MAX_DISTANCE), NewPing(10, 10, MAX_DISTANCE), NewPing(8, 8, MAX_DISTANCE) },
                                          {NewPing(6, 6, MAX_DISTANCE), NewPing(3, 3, MAX_DISTANCE), NewPing(2, 2, MAX_DISTANCE)}};


/*
NewPing rear_array[SONAR_NUM] = {     //Rear facing sensors
  NewPing(6, 6, MAX_DISTANCE),     
  NewPing(3, 3, MAX_DISTANCE),      
  NewPing(2, 2, MAX_DISTANCE),      
};

*/


/*
 * Reserved for possible future use, have yet to test with timer 2
 *
 * void intialise_sensors(){                 // Carried out during setup phase
 *  pingTimer[0] = millis() + 75;           // First ping starts at 75ms, gives time for the Arduino to chill before starting.
 *   for (uint8_t i = 1; i < SONAR_NUM; i++) // Set the starting time for each sensor.
 *    pingTimer[i] = pingTimer[i - 1] + PING_INTERVAL;
 *}
 *
 */

//-----------------------------------------------------------------------------------------------------------------------------

void scanning(){
 
  if(act_sensor < 3){

    time_since = millis();

    if(time_since - last_ping >= ping_time){

      array_pos[act_sensor] = for_array[dir][act_sensor].ping_cm(); // Use direction to correctly probe the corresponding array

      /* if(array_pos[act_sensor] <= MIN_UPPER and array_pos[act_sensor] >= MIN_LOWER){
       *
       *
       *   colAlert = true; //Doesnt currently do anything but the plan is that this acts as a fail safe
       *                //should the SBC stop fail to send the stop command
       * 
       *}
       */

      if (array_pos[act_sensor] == 0){

        out_range = true;
        array_pos[act_sensor] = MAX_DISTANCE;

        }

      else{

        out_range = false;

      }  

      act_sensor++;

      last_ping = time_since;
    }

  }

  /*
   * Broadcast the sensor readings back to the SBC but be cautious not to flood the serial port as general diagnostics data to 
   * cap this we add in time for how often data is relay back.
   * 
   */

  if(senRead  == true){

    check_time = millis();

    if(check_time - last_scan >= scan_now)
    {

      transmit(array_pos[0], array_pos[1], array_pos[2]);
      senRead = false;

      last_scan = check_time;

    }
  }
}

//TODO - BNO055 9DOF module data processing for advance decision
/**
 * @brief Two options of encoder or bno055 to calculate speed
 * 
 */

