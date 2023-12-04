// Omzetting van PLC LREAL (8 bytes) naar arduino float (4 bytes) inclusief swap van big endian naar little endian
//
// https://babbage.cs.qc.cuny.edu/IEEE-754.old/32bit.html
// **************************
// Aansluitingen voor UNO
// 5 V  -> 5 V
// GND  -> GND
// MISO -> 12
// MOSI -> 11
// SCS  -> 10 Vergeet vooral de Chip Select niet!!
// SCLK -> 13
// **************************

// PLC-side:
// Project tree: rechtsklik projectnaam > properties > Protection > V Support simulation during block compilation
// datablock GLBS: (properties => attributes => ontvink Optimized block access)
// GLBS.Hoek = -258.0

// Hoe gebruik je deze software?
// Zet het IP-adres van je PLC in deze arduino-file: wijzig X1 in 11, 21, .. 101, .., 121
// Maak een server aan in de PLC met %M0.0 aan TSEND_C.REQ. Maak een LREAL aan in GLBS, bijv. Hoek = -258.0 en
// koppel deze aan TSEND_C.DATA. Download naar een echte PLC of naar PLCSim Advanced.
// Upload 2023-ServerPLC-ArduinoClientLREAL.ino naar een Arduino en start de Serial Monitor.
// Zet op de PLC in een splitscreen met het brilletje <Main> en <GLBS> aan.
// Toggle %M0.0 op de PLC in Main > Tsend_C > REQ. Dan wordt de LReal GLBS.Hoek naar de Uno gestuurd en
// getoond op de Serial Monitor. Dubbelklik in de oranje cel van Hoek en kijk of andere hoeken ook correct
// verstuurd worden. Gebruik in de arduino de real om een servo mee aan te sturen.

#include <SPI.h>
#include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xDE };
IPAddress ipW5500(192, 168, 0, 177);                 // IP address van de W5500
// Let op: IP-adres (192, 168, 0, 1) kan wel eens problemen geven bij simulatie
IPAddress ipPLCserver(192, 168, 0, X1);              // IP address van de PLC-server
int serverPoort = 2000;                              // Poortnummer van de PLC-server
EthernetClient clientW5500;

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ;                                                // wait for serial port to connect.

  // Setup W5500
  pinMode(53, OUTPUT);                               // pen 53 wordt output (alleen MEGA2560)
  Ethernet.init(10);                                 // SPI-CS: Chip Select op pen 10
  Ethernet.begin(mac, ipW5500);                      // start the Ethernet connection
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("HW not found.");
    for (;;)
      ;
  }
  while (Ethernet.linkStatus() == LinkOFF) {
    Serial.println("Ethernet cable is not connected.");
    delay(500);
  }
  delay(1000);                                       // 1000 ms voor initialisatie van de WizNet W5500

  Serial.println("connecting...");
  if (clientW5500.connect(ipPLCserver, serverPoort)) Serial.println("connected");  // to server
  else Serial.println("connection failed");                                        // no connection to server
}

uint8_t bytes[8];                                    // ruimte voor de 8 bytes van de LREAL van de PLC
unsigned long longint, hoekL;                        // Long heeft maar 4 bytes
float hoek;                                          // De LREAL wordt omgezet naar deze REAL of FLOAT

void loop() {
  delay(100);
  int i = 0;
  while (clientW5500.available()) {                  // Als er iets ontvangen is van de PLC
    byte c = clientW5500.read();                     // 1 van de 8 bytes van de LREAL wordt ingelezen
    bytes[7-i]=c;                                    // vul array met de 8 ontvangen bytes en swap wegens
    i += 1;                                          // little endian/big endian
  }
  if (i == 8) {
    // Maak van een LReal van 8 bytes een Real (float in Arduino) van 4 bytes omdat in Arduino
    // de LReal (double in Arduino) hetzelfde is als de Real of de float, dus ook maar 4 bytes  
    memcpy (&longint, &bytes[4], 4);                 // Kopieer de eerste 4 bytes van de LREAL
    hoekL = (longint & 0x80000000L) | (((longint & 0x7FFFFFFFL) - 0x38000000L) << 3) | long((bytes[3] >> 5));
    memcpy(&hoek, &hoekL, 4);                        // Kopieer de nieuwe REAL naar float hoek
    Serial.println(hoek);                            // Gebruik hoek om de servo aan te sturen
    i = 0;
  }
  // if the server is disconnected, stop the client:
  if (!clientW5500.connected()) {
    Serial.println();
    Serial.println("disconnecting.");
    clientW5500.stop();
    for (;;)
      ;  // End of program
  }
}
