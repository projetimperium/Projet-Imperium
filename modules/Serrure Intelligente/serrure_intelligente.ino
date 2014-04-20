  /*
    Si ceci est votre premier setup, veuillez vous assurer que le byte 512
    de votre EEPROM est à 0 avec la fonction EEPROM.write(512,0); Sans oublier
    la librairie #include <EEPROM.h>
  */

#include <PN532mod.h>
#include <SPI.h>
#include <EEPROM.h>
#include <SoftwareSerial.h>

// Librairie pour le Serial du XBEE
SoftwareSerial mySerial(2, 3); // RX, TX

// Declaration des Pins
int pin_doorControl = 4;
int pin_led1 = 5;
int pin_led2 = 6;
int pin_buzzer = 7;

// constantes
const int OPEN_DOOR_TIME = 2500; // ms
const String moduleName = "porte";

String cmdPrefix = "<PI|" + moduleName + "|";
// cmdPrefix -> <PI|porte|<cmd>|<param>

// Declaration NFC
#define PN532_CS 10
PN532 nfc(PN532_CS);

const int tagSize = 17;

/*
  Premier 16 byte -> Tag ID
  Dernier byte -> Tag active (1- active, 0-déactiver)
*/
uint8_t tag1_init[tagSize] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1};
uint8_t tag2_init[tagSize] = {15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,1};
uint8_t tag3_init[tagSize] = {5,0,6,8,6,6,0,8,5,0,1,9,9,2,0,2,1};
uint8_t tag4_init[tagSize] = {1,3,5,7,9,11,13,15,0,2,4,6,8,10,12,14,1};

uint8_t tag1[tagSize];
uint8_t tag2[tagSize];
uint8_t tag3[tagSize];
uint8_t tag4[tagSize];


void setup() {
  mySerial.begin(9600);

  /*
    First run setup
  */
  if (EEPROM.read(512) == 0) {
    writeTag(tag1_init, 1);
    writeTag(tag2_init, 2);
    writeTag(tag3_init, 3);
    writeTag(tag4_init, 4);
    EEPROM.write(512,1);
 }

  /*
    Get tag data from EEPROM
  */
  readTag(tag1, 1);
  readTag(tag2, 2);
  readTag(tag3, 3);
  readTag(tag4, 4);


  pinMode(pin_doorControl, OUTPUT);
  pinMode(pin_led1, OUTPUT);
  pinMode(pin_led2, OUTPUT);
  pinMode(pin_buzzer, OUTPUT);

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) { while (1); } // halt

  nfc.SAMConfig(); // configurer à lire les étiquettes et cartes RFID
}


/*
  Main loop
*/
void loop() {

  if(mySerial.available() > 0){
    processCommand();
  }

  uint32_t id = readRFID();
  if (id != 0){
    processRFID(id);
  }

}
/* ------------------------------- */


/*
-------------------------------
  Envoyer et recevoir des commandes
-------------------------------
*/
String readCommand() {
  String command = readStringSerial();
  command.replace(cmdPrefix, "");
  return command;
}

void processCommand() {
  String command = readCommand();
  if(command == "unlock"){
    return openDoor();

  }else if(command.startsWith("kill|")){
    String tag = command.substring(5);
    killTag(tag);

  }else if(command.startsWith("restore|")){
    String tag = command.substring(8);
    restoreTag(tag);
  }
}

void sendCommand(String cmd) {
  String sendCmd = cmdPrefix;
  sendCmd.concat(cmd);
  mySerial.print(sendCmd);
}

/*
-------------------------------
  Fonctions de NFC - Porte
-------------------------------
*/

/*
  Ouvrir la porte
*/
void openDoor() {
  digitalWrite(pin_led2, HIGH);
  digitalWrite(pin_doorControl, HIGH);
  delay(OPEN_DOOR_TIME);
  digitalWrite(pin_doorControl, LOW);
  digitalWrite(pin_led2, LOW);
  delay(500);
}

/*
  Desactiver une tag
*/
void killTag(String tag) {
  if(tag == "tag1"){
    tag1[tagSize-1] = 0;
    writeTag(tag1,1);
  }else if(tag == "tag2"){
    tag2[tagSize-1] = 0;
    writeTag(tag2,2);
  }else if(tag == "tag3"){
    tag3[tagSize-1] = 0;
    writeTag(tag3,3);
  }else if(tag == "tag4"){
    tag4[tagSize-1] = 0;
    writeTag(tag4,4);
  }

  return;
}
/*
  Restorer une tag a sa valeur initial
*/
void restoreTag(String tag) {
  if(tag == "tag1"){
   writeTag(tag1_init, 1);
   readTag(tag1, 1);
  }else if(tag == "tag2"){
   writeTag(tag2_init, 2);
   readTag(tag2, 2);
  }else if(tag == "tag3"){
   writeTag(tag3_init, 3);
   readTag(tag3, 3);
  }else if(tag == "tag4"){
   writeTag(tag4_init, 4);
   readTag(tag4, 4);
  }

  return;
}

/*
  Lire ID du RFID tag
*/
uint32_t readRFID() {
  return nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A);
}

/*
  Verifier les ID des RFID tag
*/
void processRFID(uint32_t id) {
  uint8_t keys[]= { 0xFF,0xFF,0xFF,0xFF,0xFF,0xFF };
  if(nfc.authenticateBlock(1, id ,0x08,KEY_A,keys)) { //authenticate block 0x08
    uint8_t block[16];
    if(nfc.readMemoryBlock(1,0x08,block)) {

      // Verifier les tags
      if(verifier(block, tag1) && tag1[16] ){
        sendCommand("unlock|tag1");
        openDoor();
      }else if(verifier(block, tag2) && tag2[16]){
        sendCommand("unlock|tag2");
        openDoor();
      }else if(verifier(block, tag3) && tag3[16]){
        sendCommand("unlock|tag3");
        openDoor();
      }else if(verifier(block, tag4) && tag4[16]){
        sendCommand("unlock|tag4");
        openDoor();
      }else{
        // not a valid tag
        if(verifier(block, tag1))
        sendCommand("warning|UnauthorizedTag1");
        else if(verifier(block, tag2))
        sendCommand("warning|UnauthorizedTag2");
        else if(verifier(block, tag3))
        sendCommand("warning|UnauthorizedTag3");
        else if(verifier(block, tag4))
        sendCommand("warning|UnauthorizedTag4");
        digitalWrite(pin_led1, HIGH);
        delay(1000);
        digitalWrite(pin_led1, LOW);
      }

    }

    delay(500);
  }
}

// Verifier deux array
boolean verifier(uint8_t array1[], uint8_t array2[]) {
  for (int i = 0; i<16; i++) {
    if (array1[i] != array2[i]) {
      return false;
    }
  }

  return true;
}

// Lire string line du serial
String readStringSerial() {
    String content = "";
    char character;
    while(mySerial.available() > 0) {
        character = mySerial.read();
        content.concat(character);
    }
    return content;
}


/** Fonctions EEPROM **/

/*
  Ecrire tag a l'EEPROM
*/
void writeTag(uint8_t tagData[], int tagNum) {
  tagNum -= 1;
  int addrStart = tagNum * tagSize;
  int c = 0;

  for(int addr = addrStart; addr < addrStart+tagSize; addr++){
    EEPROM.write(addr, tagData[c]);
    c += 1;
  }
}


/*
  Lire du EEPROM, stoker dans tag
*/
void readTag(uint8_t * tag, int tagNum) {
  tagNum -= 1;
  int addrStart = tagNum * tagSize;
  int c = 0;

  for(int addr = addrStart; addr < addrStart+tagSize; addr++){
    tag[c] = EEPROM.read(addr);
    c += 1;
  }
}

/* Debug Print fonction */
void debugPrint(uint8_t arr[]) {
  for(int i=0; i<sizeof(arr); i++){
    mySerial.print(arr[i]);
  }
  mySerial.println("");
}
