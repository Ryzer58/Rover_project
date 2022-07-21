/*Basic Lipo battery monitor - TODO
 * Using the Arduino Analog pins with a reference voltage of 3.3V
 * To bring voltages outputted from the upper cells to voltages suitabe to the analog pins
 * a voltage divider will be implemented so that the output is no greater than 3.3V
 * Check Datasheet for the state minimum and adjust accordingly, realistically the SBC
 * should be configure to shut itself down before reaching critical levels
 * Control bits in status byte are bit 3 and 2
 * 
*/

/*
#define BATT_TEMP A0
#define CELL_A A1
#define CELL_B A2
#define CELL_C A3
int a_volt; //store the Cell voltage
int b_volt;
int c_volt;
int temp;

#define CELL_HIGH 4200  //Lipo batteries tend to be around 4.2V when fully charged
#define CELL_LOW 3200   //Warn the host SBC if the battery is low
#define CELL_CRIT 3000  //If the SBC has not yet shutdown, alert it to.
#define HGH_TEMP 50     //Warn if the battery is getting to hot
#define OFFSET_A 1      //Adjust according to resistor values used (3.3V reference value used)
#define OFFSET_B 2
#define OFFSET_C 3

int batt_check(){
  int a_raw;
  int b_raw;
  int c_raw;
  int temp_raw;
  int raw_val[]={a_raw, b_raw, c_raw};
  int battery[]={CELL_A, CELL_B, CELL_C};
  
  
  for(int j; j<3;j++){
    raw_val[j]=analogRead(battery[j]);
    //Need to include a conversion calculate from raw value into a proportional value 3/1024
  }

  temp_raw = analogRead(BATT_TEMP);
  //convert raw value into proportional the check againts predefined limits
}

*/
