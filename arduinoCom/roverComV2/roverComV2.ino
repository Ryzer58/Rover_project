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

/* Vellemen KA04 motor shield configuration - A stackable dual motor shield. It requires two pins 
 * to drive a single motor, one for direction and the other for PWM output. Their are
 * jumpers on the board give some flexibility in choosing the output pins used on either
 * channel A or B. Remember to amend sketch based on jumper positions
 * 
 */

// Motor channel A:
#define MOTA_DIR 4 //7,2 - Alternative avaliable pins via jumper DIRA
#define MOTA_PWM 5 //3,6 - PWMA
// Motor channel B:
// #define MOTB_DIR = 8,12,13 - DIRB
// #define MOTB_PWM = 9,10,11 - PWMB
#define MIN_REVERSE 5    // Both the speed and direction are combined into a single velocity
#define MAX_REVERSE 185  // value. It is mapped out below to set the direction based on
#define MIN_FORWARD 190  // the give range then set the duty cycle realative to its
#define MAX_FORWARD 370  // position in the the range of 75 - 255
#define STATIONARY 0

uint8_t vel;
bool dir;
bool new_data;


/*------------------------------------------------------------------------------------------
 * SG995 Servo configuration - Ensure that the servo arc does not exceed the physical
 * constraints of the frame to any damaging the servo. In future I may add an addtional 
 * servo to act as pan mechanism for the camera used on the SBC
 * 
 */

Servo str;               //Main steering servo,
#define CENTRE 30
#define MAX_LEFT 0       //Left and Right may need to swapped based on the orientation
#define MAX_RIGHT 60     //of the servo
uint8_t cur_ang = CENTRE;    //Start at center point
#define pivot_time = 12; //Time taken for servo to do a an arc of 60 degrees in nanoseconds


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
  Serial.print(MIN_REVERSE); Serial.print(","); // Send values to the pi so it is full aware of what it is
  Serial.print(MAX_REVERSE); Serial.print(","); // working with.
  Serial.print(MIN_FORWARD); Serial.print(","); // maybe it would be better to combine to a single string
  Serial.println(MAX_FORWARD);

  Serial.print("Servo: ");
  Serial.print(CENTRE); Serial.print(",");
  Serial.print(MAX_LEFT); Serial.print(",");
  Serial.println(MAX_RIGHT);
  
}

void loop() {

  while(Serial.available() > 0){
    
    //sent in format: in_velocity, inAng, inFunc
    uint8_t in_vel = Serial.parseInt();  // Input velocity, combining speed and direction as in the variables defined above
    uint8_t in_ang = Serial.parseInt();  // Input angle for the steering servo
    uint8_t in_func = Serial.parseInt(); // Reserved for later use

    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
      
      uint8_t motion = 0;
      
      if (in_vel != vel){ // Only attempt to write out a value if there is a change
      
        if (in_vel >= MIN_FORWARD and in_vel <= MAX_FORWARD){
           
          dir = true;
          motion = update_velocity(in_vel);
          bitSet(control, 6); // 1100 0000 (192) - set motion and direction bit to 1
          bitSet(control, 7);
        }
        else if (in_vel >= MIN_REVERSE and in_vel <= MAX_REVERSE){
          
          dir = false;
          motion = update_velocity(in_vel);
          bitClear(control, 6); // 1000 0000 (128) set motion to 1 and drive to 0
          bitSet(control, 7);
        }
        
        else{
          
          halt(); // Stop the motors, either if intentional or if an invalid velocity is specified
          motion = 0;
          bitClear(control, 7); //set motion bit to 0
          

        } 
        vel = in_vel;

        act_sensor = 0;

        new_data = true;

      }
      
      if (in_ang != cur_ang){
      
        if (in_ang <= MAX_RIGHT and in_ang >= MAX_LEFT){
          cur_ang = update_steering(in_ang);
          
        }
        
        else{
          
          bitClear(control, 5); // set turning bit bit to 0
          str.write(CENTRE);    // if an invalid value is sent then default back to center          
        }

        act_sensor = 0;

        new_data = true;  
      }
      
      transmit(control, motion, cur_ang);
      
    }
  }

  scanning();  // Currently only supports single sensor in either direction
  //batt_check(); // Currently disabled

}

int update_velocity(int accel){
  const uint8_t throt_min = 75; // Minimum pwm value at which the motor will still crawl at
  const uint8_t throt_max = 255;
  uint8_t throttle;
  
  if (dir == true){
    throttle = map(accel, MIN_FORWARD, MAX_FORWARD, throt_min, throt_max);
    digitalWrite(MOTA_DIR, HIGH);
    //Serial.print("Driving forward at: ");
    //Serial.println(throttle);

  }

  else{
    throttle = map(accel, MIN_REVERSE, MAX_REVERSE, throt_min, throt_max);
    digitalWrite(MOTA_DIR, LOW);
    //Serial.print("Driving in reverse at: ");
    //Serial.println(throttle);
    
  }
  analogWrite(MOTA_PWM, throttle);
  return throttle;
}

int update_steering(uint8_t pos){ 

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
  
}
