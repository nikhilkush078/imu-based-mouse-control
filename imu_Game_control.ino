#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define MPU_ADDR 0x68

// ============================================================
// BUTTONS
// ============================================================

#define BUTTON1 D5
#define BUTTON2 D6


// ============================================================
// WIFI
// ============================================================

const char* ssid = "Airtel_kaml_0228";
const char* password = "Passward@078078";

const char* laptopIP = "192.168.1.14";
const unsigned int port = 4210;

WiFiUDP udp;


// ============================================================
// READ MPU REGISTER
// ============================================================

int16_t read16(byte reg)
{
    Wire.beginTransmission(MPU_ADDR);

    Wire.write(reg);

    Wire.endTransmission(false);

    Wire.requestFrom(MPU_ADDR, (uint8_t)2);

    int16_t value = ((int16_t)Wire.read() << 8);

    value |= Wire.read();

    return value;
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    Wire.begin(D2, D1);

    // Wake MPU-6500
    Wire.beginTransmission(MPU_ADDR);

    Wire.write(0x6B);
    Wire.write(0x00);

    Wire.endTransmission();

    delay(100);


    // Buttons
    pinMode(BUTTON1, INPUT_PULLUP);
    pinMode(BUTTON2, INPUT_PULLUP);


    Serial.println();
    Serial.println("MPU-6500 started!");


    // WiFi
    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);

        Serial.print(".");
    }

    Serial.println();

    Serial.println("WiFi connected!");

    Serial.print("NodeMCU IP: ");

    Serial.println(WiFi.localIP());
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
    // --------------------------------------------------------
    // Read accelerometer
    // --------------------------------------------------------

    int16_t ax = read16(0x3B);
    int16_t ay = read16(0x3D);
    int16_t az = read16(0x3F);


    // --------------------------------------------------------
    // Read buttons
    //
    // INPUT_PULLUP:
    //
    // Not pressed = HIGH
    // Pressed     = LOW
    // --------------------------------------------------------

    int button1 = !digitalRead(BUTTON1);
    int button2 = !digitalRead(BUTTON2);


    // --------------------------------------------------------
    // Create packet
    // --------------------------------------------------------

    String data =
        String(ax) + "," +
        String(ay) + "," +
        String(az) + "," +
        String(button1) + "," +
        String(button2);


    // --------------------------------------------------------
    // Send UDP packet
    // --------------------------------------------------------

    udp.beginPacket(laptopIP, port);

    udp.print(data);

    udp.endPacket();


    // Debug
    Serial.println(data);


    // Approximately 50 packets/sec
    delay(20);
}
