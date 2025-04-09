// Sensor pins
#define sensorPower 7
#define sensorPin A5
#define LED_PIN 10
#define pinSemnalSenzor 12

// Value for storing water level
int val = 0;
int next_water_reading_frequency=2500;
static unsigned long next_water_reading=0;
bool toggle;
bool inundatieDetectata;
bool hot;

void setup() {

	pinMode(sensorPower, OUTPUT);
  pinMode(LED_PIN,OUTPUT);
	
	//WATER
	  digitalWrite(sensorPower, LOW);
  	digitalWrite(LED_PIN, HIGH);
    toggle=false;
    inundatieDetectata=false;
    hot=false;

  //Photo Senson
  pinMode(pinSemnalSenzor, INPUT);
	
	Serial.begin(115200);
}

void loop() {
	//get the reading from the function below and print it
  if(millis()>next_water_reading)
  {
    int level = readSensor();
    if(level>200 && inundatieDetectata==false)
    {
      Serial.write("W");
      digitalWrite(LED_PIN,toggle);
      toggle=!toggle;
      inundatieDetectata=true;
    }
    else if(level<200 && inundatieDetectata==true)
    {
        inundatieDetectata=false;
    }
    next_water_reading=next_water_reading_frequency+millis();
  }
  
  int stareSenzor = digitalRead(pinSemnalSenzor);
  if(stareSenzor==0 && hot==false)
  {
    Serial.write("H");
    hot=true;
  }
  else if(stareSenzor==1 && hot==true)
  {
    hot=false;
  }


}

//This is a function used to get the reading
int readSensor() {
	digitalWrite(sensorPower, HIGH);	// Turn the sensor ON
	delay(10);							// wait 10 milliseconds
	val = analogRead(sensorPin);		// Read the analog value form sensor
  delay(10);
	digitalWrite(sensorPower, LOW);		// Turn the sensor OFF
	return val;							// send current reading
}