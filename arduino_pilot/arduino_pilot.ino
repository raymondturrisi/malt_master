//Include libraries
#include "DHT.h"
#include <OneWire.h> 

//Define pin literals/tokens
////actuators
#define gj_Pin 6
#define kFan_Pin 7
#define k_LA_pwmPin 4
#define g_LA_pwmPin 5
#define k_motor_Pin 22
#define g_motor_Pin 24
#define k_heat_Pin 26
#define g_filter_Pin 28
#define g_mister_Pin 30
#define g_flood_Pin 32
#define g_drain_Pin 34
#define g_o2_Pin 36
#define g_LA_2_Pin 23
#define g_LA_1_Pin 25
#define k_LA_2_Pin 27
#define k_LA_1_Pin 29
#define wp_temp_sensor 42
#define echoPin 45
#define trigPin 44

////sensors
#define DHTPIN 43     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
//Define other tokens

#define OPEN 1
#define CLOSE 0
int kilnFlap = 1;
int gateValve = 0;
DHT dht(DHTPIN, DHTTYPE);
OneWire ds(wp_temp_sensor);  // on digital pin 2

long duration; // variable for the duration of sound wave travel
int distance; // variable for the distance measurement

void setup() {
  Serial.begin(115200);
  //Serial.println("Program loading..");
  //create variables, set pin modes, etc..
  pinMode(gj_Pin,OUTPUT);
  pinMode(kFan_Pin,OUTPUT);
  pinMode(k_LA_pwmPin,OUTPUT);
  pinMode(g_LA_pwmPin,OUTPUT);
  pinMode(k_motor_Pin,OUTPUT);
  pinMode(g_motor_Pin,OUTPUT);
  pinMode(k_heat_Pin,OUTPUT);
  pinMode(g_filter_Pin,OUTPUT);
  pinMode(g_mister_Pin,OUTPUT);
  pinMode(g_flood_Pin,OUTPUT);
  pinMode(g_drain_Pin,OUTPUT);
  pinMode(g_o2_Pin,OUTPUT);
  pinMode(g_LA_2_Pin,OUTPUT);
  pinMode(g_LA_1_Pin,OUTPUT);
  pinMode(k_LA_2_Pin,OUTPUT);
  pinMode(k_LA_1_Pin,OUTPUT);
  
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT); // Sets the echoPin as an INPUT
  
  //If there is something waiting in the serial bus, parse it, else proceed
  //Serial.println("kiln heater (0 or 1), kiln fan (0, or 128-255), kiln motor (0 or 1), gs motor (0 or 1), kiln flap (0 or 1), gate valve (0 or 1), germ jogger (0, or 200-255), o2 valve (0 or 1), flood valve (0 or 1), mister (0 or 1), drain (0 or 1)");
  
  dht.begin();
  delay(5000);
  //Serial.println("Program set..");
  //Serial.println("temp, hum");
}

unsigned long int kiln_th_time = 0;

//forward declare functions
void linearActuator(int actuator, int state);
void get_kiln_th(float &kiln_temp, float &kiln_humidity);
float us_sensor();
float getTemp();


//main loop
int states[12];
char buffer1[100];
char buffer2[200];

int i = 0;

//controllable states
int k_motor = 0;
int k_fan = 0;
int k_heater = 0;
int k_flap = 0;


int g_motor = 0;
int o2 = 0;
int flood = 0;
int mist = 0;
int filter = 0;
int gj_motor = 0;
int drain = 0;
int err_code = 0;

float k_temp = 0.00;
float k_hum = 0.00;

String allStates = "";
int error_code
String buff, tempstr;
void loop() {
  //Serial.println("waiting..");
  //If there is something waiting in the serial bus, parse it, else proceed
  //Serial.println("kiln heater (0 or 1), kiln fan (0, or 128-255), kiln motor (0 or 1), gs motor (0 or 1), kiln flap (0 or 1), gate valve (0 or 1), germ jogger (0, or 200-255), o2 valve (0 or 1), flood valve (0 or 1), mister (0 or 1), drain (0 or 1)");
  if(Serial.available()){
    i = 0;
    buff = Serial.readStringUntil('\n');
    for(int k = 0; k <=11; k++) {
      i = buff.indexOf(',');
      tempstr = buff.substring(0,i);
      states[k] = tempstr.toInt();
      buff.remove(0,i+1);
      //Serial.print(k+1);
      //Serial.print(": ");
      //Serial.println(states[k]);
    }
    /*
      arduino parser 
      while(Serial.available()) {
      Serial.println(Serial.peek());
      states[i] = Serial.parseInt();
      Serial.print(i+1);
      Serial.print(": ");
      Serial.println(states[i]);
      i++;
    }
    if(i!=12) {
      //Serial.println(i);
      Serial.println("Full command not received\nMust pass 11 comma separated arguments..");
      //Serial.println("kiln heater (0 or 1), kiln fan (0, or 128-255), kiln motor (0 or 1), gs motor (0 or 1), kiln flap (0 or 1), gate valve (0 or 1), germ jogger (0, or 200-255), o2 valve (0 or 1), flood valve (0 or 1), mister (0 or 1), drain (0 or 1), filter (0 or 1)");
      for(int j = 0; j < sizeof(states)/sizeof(int); j++) {
        states[j] = 0;
      }
    */
    digitalWrite(k_heat_Pin, states[0]);
    analogWrite(kFan_Pin, states[1]);
    digitalWrite(k_motor_Pin, states[2]);
    digitalWrite(g_motor_Pin, states[3]);
    linearActuator(kilnFlap, states[4]);
    linearActuator(gateValve, states[5]);
    analogWrite(gj_Pin, states[6]);
    digitalWrite(g_o2_Pin, states[7]);
    digitalWrite(g_flood_Pin, states[8]);
    digitalWrite(g_mister_Pin, states[9]);
    digitalWrite(g_drain_Pin, states[10]);
    digitalWrite(g_filter_Pin, states[11]);
  }
  allStates = "";
  for(int j = 0; j < sizeof(states)/sizeof(int); j++) {
        allStates = allStates + String(states[j]);
        if(j != sizeof(states)/sizeof(int)) {
          allStates +=", ";
        }
  }
  //sprintf(buffer1, "");
  //Serial.println(allStates);
  delay(500);
  get_kiln_th(k_temp, k_hum);
  String message = String(err_code) + ", " + String(millis()) + ", " + String(k_temp) + ", " + String(k_hum) + ", " + String(us_sensor()) + ", " + String(getTemp()) +"\n";
  Serial.print(message);
}


//UDEF_FUNC


void linearActuator(int actuator, int state) {
  if(kilnFlap == actuator) {
    if(state == OPEN) {
      digitalWrite(k_LA_2_Pin, HIGH);
      digitalWrite(k_LA_1_Pin, LOW);
      analogWrite(k_LA_pwmPin, 255);
    } else {
      digitalWrite(k_LA_2_Pin, LOW);
      digitalWrite(k_LA_1_Pin, HIGH);
      analogWrite(k_LA_pwmPin, 255);
    }
  } else {
    if(state == OPEN) {
      digitalWrite(g_LA_2_Pin, HIGH);
      digitalWrite(g_LA_1_Pin, LOW);
      analogWrite(g_LA_pwmPin, 255);
    } else {
      digitalWrite(g_LA_2_Pin, LOW);
      digitalWrite(g_LA_1_Pin, HIGH);
      analogWrite(g_LA_pwmPin, 255);
    }
  }
  
}

void get_kiln_th(float &kiln_temp, float &kiln_humidity) {
  if(kiln_th_time <= (millis()+2250)) {
    kiln_th_time+=2250;

    //code from adafruit {
    kiln_humidity = dht.readHumidity();
    // Read temperature as Celsius (the default)
    float t = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    kiln_temp = dht.readTemperature(true);
    
    // Check if any reads failed and exit early (to try again).
    if (isnan(kiln_humidity) || isnan(t) || isnan(kiln_temp)) {
      kiln_humidity = 999;
      kiln_temp = 999;
      //Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }
    //Serial.println(kiln_humidity);
    //Serial.println(kiln_temp);
    // Compute heat index in Fahrenheit (the default)
    //float hif = dht.computeHeatIndex(f, h);
    // Compute heat index in Celsius (isFahreheit = false)
    //float hic = dht.computeHeatIndex(t, h, false);
    //}
  }
}

float us_sensor() {
  // Clears the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  return distance;
}

float getTemp(){
  //returns the temperature from one DS18S20 in DEG Celsius

  byte data[12];
  byte addr[8];

  if ( !ds.search(addr)) {
      //no more sensors on chain, reset search
      ds.reset_search();
      return -1000;
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return -1000;
  }

  if ( addr[0] != 0x10 && addr[0] != 0x28) {
      Serial.print("Device is not recognized");
      return -1000;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1); // start conversion, with parasite power on at the end

  byte present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE); // Read Scratchpad

  for (int i = 0; i < 9; i++) { // we need 9 bytes
    data[i] = ds.read();
  }

  ds.reset_search();

  byte MSB = data[1];
  byte LSB = data[0];

  float tempRead = ((MSB << 8) | LSB); //using two's compliment
  float TemperatureSum = tempRead / 16;

  return (TemperatureSum * 18 + 5)/10 + 32;
}
