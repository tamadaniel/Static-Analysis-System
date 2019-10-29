///////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////// https://github.com/mathworks/thingspeak-particle ///////////////////

#include <ThingSpeak.h>
#include <WiFi.h>
 
char ssid[] = "ASUS";//"NETGEAR80"; //"320063FF";//"ASUS"; //your network SSID (name)
char pass[] ="kawalab211";//"qwer1234"; // "0332154160";//"kawalab211";// your network password

WiFiClient client;
//TCPClient client;
 
unsigned long myChannelNumber = 000000; //update
const char * myWriteAPIKey = "PTZELOZ3PCLE3Q17"; //update right

struct Button {
  const uint8_t PIN;
  uint32_t numberKeyPresses;
  bool pressed;
};
unsigned long dt;
unsigned long interval1;
unsigned long interval2;

unsigned long off1;
unsigned long on1;
unsigned long t1[4];
unsigned long t2[4];

unsigned long off2;
unsigned long on2;

int ref;
uint32_t before1=0;
uint32_t before2=0;

Button button1 = {4, 0, false};
Button button2 = {14, 0, false};

void IRAM_ATTR isr1() {
  if(millis()-interval1>300){
    interval1=millis();
    t1[button1.numberKeyPresses%4]=interval1;
    button1.numberKeyPresses += 1;
  }
}

void IRAM_ATTR isr2() {
  if(millis()-interval2>300){
    interval2=millis();
    t2[button2.numberKeyPresses%4]=interval2;
    button2.numberKeyPresses += 1;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(button1.PIN, INPUT);
  pinMode(button2.PIN, INPUT);
  attachInterrupt(button1.PIN, isr1, CHANGE);
  attachInterrupt(button2.PIN, isr2, CHANGE);

  dt=millis(); 
  WiFi.mode(WIFI_STA);
  btStop(); // turn off bluetooth
  ThingSpeak.begin(client); // Initialize ThingSpeak 
}

void thingspeak(long value[]){
  // Write to ThingSpeak. There are up to 8 fields in a channel, allowing you to store up to 8 different
  // pieces of information in a channel.
  for (int field=0;field<sizeof(value);field++){
    ThingSpeak.setField(field+1, value[field]);
  }
 
  // write to the ThingSpeak channel
  int x = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
  if(x == 200){
    Serial.println("Channel update successful.");
  }else{
    Serial.println("Problem updating channel. HTTP error code " + String(x));
  }  
}

void loop() {
//   Connect or reconnect to WiFi
  if(WiFi.status() != WL_CONNECTED){
    Serial.print("Attempting to connect to SSID: ");
    
    while(WiFi.status() != WL_CONNECTED){
      WiFi.begin(ssid, pass); // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      //Serial.print(".");
      delay(5000);
    }
    //Serial.println("\nConnected.");
    dt=millis(); 
  }
  
  if (millis()-dt>=1000){// && before1!=button1.numberKeyPresses && before2!=button2.numberKeyPresses){
    before1=button1.numberKeyPresses;
    before2=button2.numberKeyPresses;
    //////////////////////  button1 ///////////////////////////////
    ref=-1;
      ref=(button1.numberKeyPresses-1)%4;
      
      switch (ref){
        case 0:
            off1=t1[0]-t1[3];
            on1=t1[3]-t1[2];
          break;
        case 1:
            off1=t1[0]-t1[3];
            on1=t1[1]-t1[0];          
          break;
        case 2:
            off1=t1[2]-t1[1];
            on1=t1[1]-t1[0];            
          break;
        case 3:
            off1=t1[2]-t1[1];
            on1=t1[3]-t1[2];          
          break;     
      }

    //////////////////////  button2 ///////////////////////////////
    ref=-1;
      ref=(button2.numberKeyPresses-1)%4;
      Serial.printf("ref %u \n", ref);
      switch (ref){
        case 0:
            off2=t2[0]-t2[3];
            on2=t2[3]-t2[2];            
          break;
        case 1:
            off2=t2[0]-t2[3];
            on2=t2[1]-t2[0];          
          break;
        case 2:
            off2=t2[2]-t2[1];
            on2=t2[1]-t2[0];
          break;
        case 3:
            off2=t2[2]-t2[1];
            on2=t2[3]-t2[2];          
          break;     
      }

    Serial.printf("on1 %u \n", on1);
    Serial.printf("off1 %u \n", off1);
    Serial.printf("on2 %u \n", on2);
    Serial.printf("off2 %u \n", off2);
    long value[]={off1,on1,off2,on2};
    thingspeak(value);
    dt=millis();  
    }
}
