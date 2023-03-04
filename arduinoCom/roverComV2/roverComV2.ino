/* RoverCom V2
 * To communicate with the Pcduino or Raspberry pi using through
 * serial/uart (/dev/ttyACM0). Currently designed around an Uno at 19200
 * Motor controller/shield used is the motor shield by Velleman
 * Generic DC Motor rated at 4.5V - 6V
 * MG995 Servo
 * 3 Cell Lipo battery
 * DC Buck converter
 * Optional Adafruit servo shield
 * HC-SR04 Ultrasonic sensors x 6
 * More updates to come later...
 * 
 */

#include <Servo.h>
#include <NewPing.h>
//#include <Wire.h> //TODO BNO055


uint8_t control = 0;
uint8_t func;

/* Vellemen KA04 motor shield configuration - A stackable dual motor shield. It requires two pins 
 * to drive a single motor, one for setting the direction and the other to drive PWM output.
 * Arduino pins used are configured by jumpers placed on the board headers. Each of the pins
 * avaliable to control channel A or B are listed below.
 * 
 */

// Motor channel A:
const uint8_t MOTA_DIR = 4; //7,2 - Alternative avaliable pins via jumper DIRA
const uint8_t MOTA_PWM = 5; //3,6 - PWMA
// Motor channel B:
// #define MOTB_DIR = 8,12,13 - DIRB
// #define MOTB_PWM = 9,10,11 - PWMB

const uint8_t MIN_THROTTLE = 75;  // duty cycle range in which the motor actually moves
const uint8_t MAX_THROTTLE = 255;  // Tweak according to the motor actually used

uint8_t throttle;
bool dir;
bool incoming_data;
bool new_data;


/*------------------------------------------------------------------------------------------
 * SG995 Servo configuration - Ensure that the servo arc does not exceed the physical
 * constraints of the frame to any damaging the servo. In future I may add an addtional 
 * servo to act as pan mechanism for the camera used on the SBC
 * 
 */

Servo str;               //Main steering servo,
const uint8_t CENTRE = 30;
const uint8_t MAX_LEFT = 0;       //Left and Right may need to swapped based on the orientation
const uint8_t MAX_RIGHT = 60;     //of the servo
uint8_t cur_ang = CENTRE;    //Start at center point
//#define pivot_time = 12; //Time taken for servo to do a an arc of 60 degrees in nanoseconds


/*------------------------------------------------------------------------------------------
 * HC-SR04 - Ultrasonic sensor configuration - To use will carry out inital tests while
 * indoors. See sensors tab for more detailed configuration.
 * surrounding environment. The end goal is to use 6 sensor, an array of 3 forward and back
 * 
 * 
 * 
 */
 
#define SONAR_NUM     3   // Number or sensors.
#define MAX_DISTANCE 200  // Maximum distance (in cm) to ping.
#define MIN_UPPER 5       //Define a band at which to stop
#define MIN_LOWER 2
uint8_t act_sensor = 0;               // Keeps track of which sensor is active.


/*------------------------------------------------------------------------------------------
 * BNO055 configuration - TODO
 * 
 * 
 */

void setup() {

  pinMode(MOTA_DIR, OUTPUT);
  pinMode(MOTA_PWM, OUTPUT);
  digitalWrite(MOTA_DIR, HIGH); //Default to driving forward position
  analogWrite(MOTA_PWM, 0);
  
  str.attach(9);
  str.write(cur_ang);

  //intialise_sensors(); //TODO - to be used when working with a sensor array
  
  Serial.begin(19200);
  //while(!Serial){
  //  //needed for leonardo or similiar  
  //}
  
  Serial.print("Motor: ");
  Serial.print(MIN_THROTTLE); Serial.print(","); // Inform the SBC what the operating parameters are
  Serial.print(MAX_THROTTLE); 

  Serial.print("; Servo: ");
  Serial.print(CENTRE); Serial.print(",");
  Serial.print(MAX_LEFT); Serial.print(",");
  Serial.println(MAX_RIGHT);
  
}

void loop() {

  while(Serial.available() > 0){
    
    //sent in format: inFunc, in_velocity, inAng - TODO communications need a major reworking 
    uint8_t in_func = Serial.parseInt(); // Input functiom, for now just repurpose as directional control rather than being unused
    uint8_t in_throttle = Serial.parseInt();  // Input velocity, combining speed and direction as in the variables defined above
    uint8_t in_ang = Serial.parseInt();  // Input angle for the steering servo
    

    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
      
      uint8_t motion = 0;

      act_sensor = 0;

      if(in_func != func){

        
        if (in_func == 0){

          dir = false;
          halt(); //stop the motor before changing direction
          digitalWrite(MOTA_DIR, LOW);
          bitClear(control, 6);

        }

        if (in_func == 1){

          dir = true;
          halt();
          digitalWrite(MOTA_DIR, HIGH);
          bitSet(control, 6);

        }

        //function code 10 - sensor related operations - TODO

        //function code 20 - bno related operations

        func = in_func;
        new_data = true;
        
      }
      
      if (in_throttle != throttle){ // Only attempt to write out a value if there is a change
      
        if (in_throttle >= MIN_THROTTLE and in_throttle <= MAX_THROTTLE){
           
          
          motion = update_velocity(in_throttle);
          throttle = motion;
           
        }
        
        else{
          
          halt(); // Stop the motors, either if intentional or if an invalid throttle is specified
          throttle = 0;
          motion = 0;
          bitClear(control, 7); //set motion bit to 0
          
        } 
        
        new_data = true;

      }
      
      if (in_ang != cur_ang){
      
        if (in_ang <= MAX_RIGHT and in_ang >= MAX_LEFT){
          cur_ang = update_steering(in_ang);
          
        }
        
        else{
          
          bitClear(control, 5); // set turning bit bit to 0
          str.write(CENTRE);    // if an invalid value is sent then default back to center
          cur_ang = CENTRE;          
        }

        new_data = true;

      }

      if (new_data == true){

        transmit(control, motion, cur_ang);
        new_data = false;

      }
      
      incoming_data = true; 
      
    }
  }

  scanning();  // Currently only supports single sensor in either direction
  //batt_check(); // Currently disabled

}

uint8_t update_velocity(uint8_t accel){
  
  analogWrite(MOTA_PWM, accel);
  bitSet(control, 7);// 1100 0000 (192) - set motion bit to 1
  
  return accel;

}

uint8_t update_steering(uint8_t pos){ 

  if (pos <= MAX_RIGHT and pos > CENTRE){

    bitSet(control, 5); // 00100000 - set turning bit to 1   
    bitSet(control, 4); // 00110000 (48) - Angle bit = 1
  }
  else if (pos >= MAX_LEFT and pos < CENTRE){
        
    bitSet(control, 5); // 00100000 - set turning bit to 1
    bitClear(control, 4); // 00100000 (32) - Angle bit = 0   
  }
  else{
    //Serial.print("Centring steering \n");
    bitClear(control, 5); // set turning bit bit to 0
  }
  //Serial.println(pos);
  str.write(pos);
  
  return pos;
  
}

void transmit(uint8_t results, uint8_t throttle, uint8_t pos){ //TODO rework serial communications to make them more streamlined/efficient

  Serial.print(results); Serial.print(",");
  Serial.print(throttle);Serial.print(",");
  Serial.println(pos);
}

void halt(){
  
  analogWrite(MOTA_PWM, 0);
  bitClear(control, 7); // set motion bit to 0 to signify that the Rover is now idle
  throttle = 0;
  
}
