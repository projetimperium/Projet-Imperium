#include <SoftwareSerial.h>
#include <FreqMeasure.h>

#define VoltagePin 0 // A0
#define CurrentPin 1 // A1

#define RelayPin 13
boolean relayOn = true;

#define DEBUG 1 // 1- serial debug, 0- debug off

// Mesurement interval
long mInterval_Power = 5000; // measure power every (ms)
int mTimer_Power = 0;

int tickInterval = 1000; // delay in ms between arduino cycle (adjust depending on intervals)

// number of measurements to take for average
int measurement_num = 1000;

// Xbee Serial Config
SoftwareSerial xbeeSerial(9, 10); // RX, TX
const String moduleName = "wattmetre";
String cmdPrefix = "<PI|" + moduleName + "|";

// LCD
SoftwareSerial LCDSerial(-1,11); // pin 11 = TX

void setup() {
  Serial.begin(9600);
  xbeeSerial.begin(9600);
  FreqMeasure.begin();


  delay(500); // attend pour que la LCD boot

  pinMode(RelayPin, OUTPUT);

  if(relayOn) {
    digitalWrite (RelayPin, HIGH);
  }

  //delay(100);
  getPower();
}

void loop() {
  if(xbeeSerial.available()){
    processCommand();
  }

  if (mTimer_Power >= mInterval_Power) {
    getPower();
    mTimer_Power = 0;
  }

  mTimer_Power += tickInterval;
  delay(tickInterval);
}



void getPower() {
  int input_Voltage = 0;
  int input_Current = 0;

  float power_average = 0;
  float power_apparent = 0;
  float power_active = 0;
  float power_factor = 0;

  float Vrms = 0;
  float Irms = 0;

  float current_sum = 0;
  float voltage_sum = 0;
  float power_sum = 0;

  float input_CurrentMod = 0;

  float average_div = (float)measurement_num;

  for(int i=0; i<measurement_num; i++) {
    // Voltage
    input_Voltage = analogRead(VoltagePin);

    input_Voltage = map( input_Voltage, 394 , 649 , 60 , -60);
    voltage_sum += input_Voltage*input_Voltage/average_div;

    // Current
    input_Current = analogRead(CurrentPin);
    input_CurrentMod = input_Current;
    input_CurrentMod = map( input_Current, 508 , 519 , -150 , 150);
    input_Current = map( input_Current, 517 , 559 , 0 , 415);
    current_sum += pow((float)input_Current, 2);

    // Power
    power_sum += (float)((input_CurrentMod/average_div)*input_Voltage);
  }

  Vrms = sqrt(voltage_sum);

  float current_average = current_sum/average_div;
  float current_rms_temp = sqrt(current_average);

  Irms = map( current_rms_temp, 14 , 530 , 0.0 , 1500.0); // remap to RMS value

  power_apparent = (Irms/average_div)*Vrms;

  power_active = abs(power_sum/average_div);

  power_factor = power_active/power_apparent;
  if(power_factor > 1) {
    power_factor = 1;
  }
  if(DEBUG){
    Serial.println(" V = ");
    Serial.println(Vrms);
    Serial.println(" I = ");
    Serial.println(Irms);
    Serial.println(" S = ");
    Serial.println(power_apparent);
    Serial.println(" P = ");
    Serial.println(power_active);
    Serial.println(" Facteur de Puissance = ");
    Serial.println(power_factor);
  }

  if(xbeeSerial.available() > 0){
    processCommand();
  }
  sendPowerData(Vrms, Irms, power_apparent, power_active, power_factor);

}

float getFrequence() {
  double sum = 0.0;
  int count = 0;
  float frequency = 0.0;

  unsigned long lastFreq = millis();

  while(count != 30) {

    if(xbeeSerial.available() > 0){
      processCommand();
    }

    if (FreqMeasure.available()) {
      sum += FreqMeasure.read();
      count += 1;
      lastFreq = millis();
    }else {
      if(millis() - lastFreq > 1000) {
        Serial.println( "Frequence = Erreur de mesure, 0.0");
        return -1;
      }
    }
  }


  frequency = F_CPU / (sum / count);

  if(DEBUG) {
    Serial.println(" Frequence = ");
    Serial.println(frequency);
  }

  return frequency;
}


void sendPowerData(float Vrms, float Irms, float power_apparent, float power_active, float power_factor) {

  if(isnan(Vrms)) Vrms = 0;
  if(isnan(Irms)) Irms = 0;
  if(isnan(power_apparent)) power_apparent = 0;
  if(isnan(power_active)) power_active = 0;
  if(isnan(power_factor)) power_factor = 0;

  String data = "power|";
  char buffer[10];

  float freq = getFrequence();

  if(freq == -1 || (freq > 0 && freq < 10)) { // frequence pas normal, envoye des 0
    freq = 0;
    Vrms = 0;
    Irms = 0;
    power_apparent = 0;
    power_active = 0;
    power_factor = 0;
  }
  if(power_active <= 0) {
    power_apparent = 0;
  }

  dtostrf(Vrms, 2, 2, buffer);
  data.concat(String(buffer) + "|");
  dtostrf(Irms, 2, 2, buffer);
  data.concat(String(buffer) + "|");
  dtostrf(power_apparent, 2, 2, buffer);
  data.concat(String(buffer) + "|");
  dtostrf(power_active, 2, 2, buffer);
  data.concat(String(buffer) + "|");
  dtostrf(power_factor, 2, 3, buffer);
  data.concat(String(buffer) + "|");
  dtostrf(freq, 2, 2, buffer);
  data.concat(String(buffer));


  LCDWrite(Vrms, Irms, power_apparent, power_active, power_factor);
  sendCommand(data);

}

void LCDWrite(float Vrms, float Irms, float power_apparent, float power_active, float power_factor) {

  xbeeSerial.end();
  LCDSerial.begin(9600);

  LCDClear();

  String line1 = "";
  String line2 = "";
  char buffer[10];

  line1.concat("S=");
  dtostrf(power_apparent, 2, 2, buffer);
  line1.concat(String(buffer));

  line1.concat(" P=");
  dtostrf(power_active, 2, 2, buffer);
  line1.concat(String(buffer));

  line2.concat("cos = ");
  dtostrf(power_factor, 2, 2, buffer);
  line2.concat(String(buffer));


  LCDMoveCursor(0,0);
  LCDSerial.print(line1);

  LCDMoveCursor(1,0);
  LCDSerial.print(line2);

  LCDSerial.end();
  xbeeSerial.begin(9600);

}

void sendCommand(String cmd) {
  String sendCmd = cmdPrefix;
  sendCmd.concat(cmd);
  delay(100);
}


String readCommand() {
  String command = readStringSerial();

  command.replace(cmdPrefix, "");
  return command;
}

void processCommand() {
  Serial.println("COMMAND: ");
  String command = readCommand();


  if(command == "off") {
    return closeRelay();
  }else if(command == "on") {
    return openRelay();
  }
}


void closeRelay() {
  digitalWrite(RelayPin, LOW);
}
void openRelay() {
  digitalWrite(RelayPin, HIGH);
}


String readStringSerial() {
    String content = "";
    char character;

    while(xbeeSerial.available() > 0) {
        character = xbeeSerial.read();
        content.concat(character);
    }
    return content;
}


/*
position 0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
line 0   128   129   130   131   132   133   134   135   136   137   138   139   140   141   142   143
line 1   192   193   194   195   196   197   198   199   200   201   202   203   204   205   206   207
*/
void LCDMoveCursor(int line, int index) {
  LCDSerial.write(254); // dit au LCD qu'on veut modifier le cursor
  if(line == 0){
    LCDSerial.write(128 + index);
  }else if(line == 1){
    LCDSerial.write(192 + index);
  }

  return;
}

void LCDClear() {
  LCDMoveCursor(0,0);
  LCDSerial.write("                ");
  LCDSerial.write("                ");
  LCDMoveCursor(0,0);
  return;
}
