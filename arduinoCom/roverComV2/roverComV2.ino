/* RoverCom V2
 * Controller code for Arduino working with a host SBC such as the Pcduino or Raspberry pi 
 * through serial communication. Remember to ensure that if changing the buadrate on the host
 * side, change it hear as well.
 *
 */

#include <Servo.h>
#include <NewPing.h>
// #include <Wire.h> // Needed for BNO055 DOF (Not yet implemented)

/* Serial communication handling */
//uint8_t control = 0;
bool serRead = false;
const byte numChars = 24;
char receivedChars[numChars];
char tempChars[numChars];

uint8_t func = 0;
uint8_t prev_func = 0;
uint8_t data1 = 0;
uint8_t data2 = 0;
uint8_t data3 = 0;
uint8_t data4 = 0;

/* Vellemen KA04 motor shield configuration - A stackable dual motor driver shield based 
 * around the L298P. For each of the two channels two pins are requied, one for direction
 * and the other for setting PWM output. Pins are selected by place a jumper on the
 * header which corresponds to the desired pins. See the mapping below.
 * 
 */
// Motor channel A:
const uint8_t MOTA_DIR = 4; //7,2 - Alternative avaliable pins via jumper DIRA
const uint8_t MOTA_PWM = 5; //3,6 - PWMA
// Motor channel B:
// const uint8_t MOTB_DIR = 8; //12,13 - DIRB
// const uint8_t MOTB_PWM = 9; //10,11 - PWMB

// Motor throttle range - create a default range which we can adjust from SBC side via a command

uint8_t MIN_THROTTLE = 75;
const uint8_t MAX_THROTTLE = 255;
uint8_t throttle;
bool dir;


/*------------------------------------------------------------------------------------------
 * SG995 Servo configuration - Ensure that the servo arc does not exceed the physical
 * constraints of the chasis to avoid damage the servo. Depending on the servo is positoned
 * in relation to the steering mechanism. The movement may be inverted to what we expect in
 * which case we can either swap the values here or on the python side. 
 * 
 */

Servo str;              
const uint8_t CENTRE = 30;
const uint8_t MAX_LEFT = 0;    
const uint8_t MAX_RIGHT = 60;
const uint8_t angle = CENTRE;

//Camera positioning (if used) - not yet implemented:
//Servo cam;
//uint8_t CENTRE = 90;
//uint8_t PAN_LEFT = 45;
//uint8_t PAN_RIGHT = 135;


/*------------------------------------------------------------------------------------------
 * HC-SR04 - Ultrasonic sensor configuration - These are currently our only method for detecting 
 * objects. They are ideal for indoors but no great for going outside, further alterations will
 * most likely need to made to the structure before outdoor exploration is attempted. In total 6 sensors
 * can be mounted to the Rover. An array of 3 at the front with the remaining form an array at the
 * rear. 
 * 
 */
 
#define ARRAY_NUM     2
#define SONAR_NUM     3     // Number or sensors attached to an array
#define MAX_DISTANCE 200    // Maximum distance (in cm) to ping.
uint8_t act_sensor = 0;     // Keeps track of which sensor is active.
bool senRead;


/*------------------------------------------------------------------------------------------
 * BNO055 configuration - TODO
 * 
 */

void setup() {

  pinMode(MOTA_DIR, OUTPUT);
  pinMode(MOTA_PWM, OUTPUT);
  digitalWrite(MOTA_DIR, HIGH); //Default to driving forward position
  analogWrite(MOTA_PWM, 0);
  
  str.attach(9);
  str.write(angle);

  /*intialise_sensors(); 
   * Only used of interrupt driven using Timer 2, may not be necceasry so
   * disable for now. This is subject to how well the next stage of 
   * testing goes with simple using millis() as point of reference for 
   * sampling the sensors.
   * 
   */
  
  Serial.begin(19200);
  
  while(!Serial);
  /* For Lenardo board and similiar we need to force a wait for incoming serial */

  /* Once we recieve command for the SBC we then send the basic Rover configuration.
   * start with stating how many motors attached and how they are setup by passing a 
   * configuration number. followed by repeating this for the servo(s).
   * 
   * Motor configuration options:
   * 0 = straight drive 
   * 1 = differential drive right motor
   * 2 = differential drive left motor
   * 
   * Servo configuration options:
   * 
   * 0 = rack and pinion steering
   * 1 = camera panning servo
   * 2 = camera tilting servo
   *  
   */

  char profile[5] = {1,0,1,0};

  for (int x = 0; x < 4; x++){
  
    Serial.print(profile[x]);

  }

  //inboundData();
  Serial.print("Rover intialized: ");
  Serial.print(MIN_THROTTLE);
  Serial.print(",");
  Serial.print(MAX_THROTTLE);
  
}

void loop() {

  inboundData();
  if(serRead == true) {
    strcpy(tempChars, receivedChars);
    // A temporary copy is required to protect the original data because
    // strtok() used in parseData() replaces the commas with \0
    parseData();
    serRead = false;
  }

  act_sensor = 0;

  if(func != prev_func){
        
    switch (func) {
      case 0: 

        // Set both the direction and throttle
        dir = data1;
        halt(); // stop the motor before changing direction
        digitalWrite(MOTA_DIR, dir);
        update_velocity(data2);
        //bitClear(control, 6);
        break;

      case 1:

        // Set just the throttle level
        update_velocity(data1);
        //throttle = update_velocity(in_throttle);
        //bitSet(control, 6);
        break;

      case 2:

        // Set both the speed and steering angle
        update_steering(data2);
        update_velocity(data1);
        break;

      case 3: 
      
        // Just set the steering angle
        update_steering(data1);
        break;
     

      case 4:
    
        // Adust the stall speed, if needed
        data1 = MIN_THROTTLE;
        break;

    }

    transmit(func, throttle, angle);
    
    prev_func = func;
    senRead = true;
        
  }
              
  scanning();
  // batt_check(); // Not yet implemented
  delay(10);

}

void inboundData(){
  static bool recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && serRead == false){
    rc = Serial.read();

    if (recvInProgress == true) {
      if(rc != endMarker){
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }

        else {
          receivedChars[ndx] = '\0'; //Terminate the end of the string
          recvInProgress = false;
          ndx = 0;
          serRead = true;
        }
      }

      else if (rc == startMarker) {
        recvInProgress = true;
      }
    }
  }
}

void parseData(){ //Split the data into its parseData

  char * strtokIndx; // This is used by strtok() as an index

  strtokIndx = strtok(tempChars, ","); // Get the first part from the string
  func = atoi(strtokIndx);

  strtokIndx = strtok(NULL, ","); // This continues from where the previous call left off
  data1 = atoi(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  data2 = atof(strtokIndx);

}


void update_velocity(uint8_t accel){
  
  if (throttle >= MIN_THROTTLE && throttle <= MAX_THROTTLE){

    analogWrite(MOTA_PWM, accel);
    //bitSet(control, 7); // 1100 0000 (192) - set motion bit to 1

  }

  else{
      
    Serial.print("Error invalid data");
      
  }

}

uint8_t update_steering(uint8_t pos){ 

  if (angle <= MAX_RIGHT and angle >= MAX_LEFT){

    str.write(angle);

  }

  else if(angle == CENTRE){
          
    //bitClear(control, 5); // set turning bit bit to 0
    str.write(CENTRE);    // if an invalid value is sent then default back to center

  }

  else{

  Serial.print("Error invalid data");

  }


  /*
  if (pos <= MAX_RIGHT and pos > CENTRE){

    bitSet(control, 5); // 00100000 - set turning bit to 1   
    bitSet(control, 4); // 00110000 (48) - Angle bit = 1
  }
  else if (pos >= MAX_LEFT and pos < CENTRE){
        
    bitSet(control, 5); // 00100000 - set turning bit to 1
    bitClear(control, 4); // 00100000 (32) - Angle bit = 0   
  }íí
  else{
    // Serial.print("Centring steering \n");
    bitClear(control, 5); // set turning bit bit to 0
  }
  // Serial.println(pos);
  str.write(pos);

  */
  
  return pos; 
}


void transmit(uint8_t results, uint8_t throttle, uint8_t pos){ // TODO rework serial communications to make them more streamlined/efficient

  Serial.print(results); Serial.print(",");
  Serial.print(throttle);Serial.print(",");
  Serial.println(pos);
}

void halt(){
  
  analogWrite(MOTA_PWM, 0);
  //bitClear(control, 7); // set motion bit to 0 to signify that the Rover is now idle
  
}
