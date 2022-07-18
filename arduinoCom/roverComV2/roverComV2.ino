/* RoverCom V2
 * To communicate with the Pcduino or Raspberry pi using through
 * serial/uart (/dev/ttyACM0). Currently designed around an Uno at 19200
 * Motor controller/shield used is the motor shield by Velleman
 * Generic DC Motor rated at 4.5V - 6V
 * MG995 Servo
 * 3 Cell Lipo battery
 * DC Buck converter
 * Optional Adafruit servo shield
 * More updates to come later...
 * 
 */

#include <Servo.h>
#include <NewPing.h>


/*Vellemen motor shield configuration - requires two pins output pins, one digital pin for
* control the direction and a PWM for controlling the speed.
*/
#define MOTA_DIR 4 //7,2 - Alternative avaliable pins via jumper DIRA
#define MOTA_PWM 5 //3,6
//Uncomment if using the second B channel motor output
//#define MOTB_DIR = 8,12,13
//#define MOTB_PWM = 9,10,11

#define MIN_REVERSE 5 //Mapped PWM Duty cycle below in the range of 75 - 255.
#define MAX_REVERSE 185
#define MIN_FORWARD 190
#define MAX_FORWARD 370
#define STATIONARY 0

int vel;
int throttle;
int cur_throttle;
//------------------------------------------------------------------------------------------


/*SG995 configuration - ensure that the movement of the servo is kept within the physical
* constraints of the frame to avoid potentially damaging the servo 
*/
Servo str;
#define CENTRE 30
#define MAX_LEFT 0           //Left and Right may need to swapped based on the orientation
#define MAX_RIGHT 60         //of the servo
int cur_ang = CENTRE;        //Start at center point
const int pivot_time = 12 ;  //Time taken to reached the next position from current
//ideally in future at least add another servo to move the camera
//------------------------------------------------------------------------------------------

#define MAIN_LAMPS 13
//#define RIGHT_IND = 12
//#define LEFT_IND = 11
//#define REV_LAMPS = 10

//------------------------------------------------------------------------------------------

//HC04 - Ultrasonic distance measuring sensor
#define SONAR_NUM     2   // Number or sensors.
#define MAX_DISTANCE 200  // Maximum distance (in cm) to ping.
#define MIN_DISTANCE 10   //Closest permissable distance to object
#define PING_INTERVAL 35  // Milliseconds between sensor pings (29ms is about the min to 
//avoid cross-sensor echo).

unsigned long pingTimer[SONAR_NUM]; // Holds the times when the next ping should happen 
//for each sensor.
unsigned int cm[SONAR_NUM];         // Where the ping distances are stored.
uint8_t currentSensor = 0;          // Keeps track of which sensor is active.

NewPing sonar[SONAR_NUM] = {        // Sensor object array.
  NewPing(12, 11, MAX_DISTANCE),    // Each sensor's trigger pin, echo pin,
  NewPing(8, 7,  MAX_DISTANCE)      //and max distance to ping.
};

//------------------------------------------------------------------------------------------
void setup() {

  pinMode(MOTA_DIR, OUTPUT);
  pinMode(MOTA_PWM, OUTPUT);
  digitalWrite(MOTA_DIR, HIGH); //Default to driving forward position
  analogWrite(MOTA_PWM, 0);
  
  str.attach(9);
  str.write(cur_ang);

  pinMode(MAIN_LAMPS, OUTPUT);

  intialise_sensors();
  
  Serial.begin(19200);
  Serial.print("Motor: ");
  Serial.print(MIN_REVERSE); Serial.print(","); //Send values to the pi so it is full aware of what it is
  Serial.print(MAX_REVERSE); Serial.print(",");//working with.
  Serial.print(MIN_FORWARD); Serial.print(",");
  Serial.println(MAX_FORWARD);

  Serial.print("Servo: ");
  Serial.print(CENTRE); Serial.print(",");
  Serial.print(MAX_LEFT); Serial.print(",");
  Serial.println(MAX_RIGHT);
}

void loop() {

  while(Serial.available() > 0){
    
    //sent in format: in_velocity, inAng, inFunc
    int in_vel = Serial.parseInt(); //Input velocity, combining speed and direction as in the variables defined above
    int in_ang = Serial.parseInt(); //Input angle for the steering servo
    int in_func = Serial.parseInt(); //Reserved for later use

    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
      
      if (in_vel != vel){ //Only attempt to write out a value if there is a change
        
        bool way = true;
      
        if (in_vel >= MIN_FORWARD and in_vel <= MAX_FORWARD){
           
           way = true;
           update_velocity(way, in_vel);
        }
        else if (in_vel >= MIN_REVERSE and in_vel <= MAX_REVERSE){
          
          way = false;
          update_velocity(way, in_vel);
        }
        
        else{
          
          halt(); //Stop the motors, either if intentional or a value outside of the
                  //speed vectors is specified
        } 
        cur_throttle = throttle;
        vel = in_vel;
      }
      
      if (in_ang != cur_ang){
      
        if (in_ang <= MAX_RIGHT and in_ang >= MAX_LEFT){
          update_steering(in_ang);
          cur_ang = in_ang;
        }
        
        else{
            Serial.println("Requested angle beyond constraints");          
        }  
      }
      if (in_func <= 10){
        //Basic light control fuctions
        int lit_status = digitalRead(MAIN_LAMPS);
        if (lit_status == LOW){
          digitalWrite(MAIN_LAMPS, HIGH);     
        }
        else{
          digitalWrite(MAIN_LAMPS, LOW);
        }
      }

      if (in_func > 10 and in_func <= 20){
        //Read from the sensors then print the values
        scanning();
      }
    }
  }
}

int update_velocity(bool dir, int accel){
  const int throt_min = 75; //Minimum pwm value at which the motor will still crawl at
  const int throt_max = 255;
  
  if (dir == true){
    throttle = map(accel, MIN_FORWARD, MAX_FORWARD, throt_min, throt_max);
    digitalWrite(MOTA_DIR, HIGH);
    Serial.print("Driving forward at: ");
    Serial.println(throttle);
    analogWrite(MOTA_PWM, throttle);
  }

  else{
    throttle = map(accel, MIN_REVERSE, MAX_REVERSE, throt_min, throt_max);
    digitalWrite(MOTA_DIR, LOW);
    Serial.print("Driving in reverse at: ");
    Serial.println(throttle);
    analogWrite(MOTA_PWM, throttle);
  }
}

int update_steering(int pos){ 

  if (pos <= MAX_RIGHT and pos > CENTRE){
        
    Serial.print("right at ");
    Serial.println(pos);
  }
  else if (pos >= MAX_LEFT and pos < CENTRE){
        
    Serial.print("left at ");
    Serial.println(pos);   
  }
  else{
    Serial.print("Centring steering \n");
  }
  str.write(pos);
  
  return pivot_time;
  
}

void halt(){
  analogWrite(MOTA_PWM, 0);
  Serial.println("Stopping");
  
}
