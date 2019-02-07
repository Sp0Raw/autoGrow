#include "Adafruit_Sensor.h"
#include "Adafruit_AM2320.h"
#include <OneWire.h>
OneWire  ds(13);  // on pin 13 (a 4.7K resistor is necessary)

Adafruit_AM2320 am2320 = Adafruit_AM2320();
int num_temp;
int val; // Задаем переменную val для отслеживания нажатия клавиши
int ledpin = 13; // задаем цифровой интерфейс ввода/вывода 13 - это наш светодиод

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    delay(10); // hang out until serial port opens
  }
  /*  */
  Serial.println("Hard is ready...");
  Serial.println("Press H or ? to help.");
  am2320.begin();
}

void loop() {
  int sel_sens = 0;
  val = Serial.read (); // Считываем команду посланную с компьютера через консоль IDE Arduino
  if (val == 'R'){ // Задаем букву условие на букву "R", при нажатии которой в консоли будет зажигался светодиод и появится строка "Hello World!"
   get_term(1);} 
  else if (val == 'G'){
    Serial.print("{\"num_sens\": 0,\"sens_type\" : \"AM2320\", \"sens_id\" : \"none\",\"sens_Val\": { \"temp\":"+String(am2320.readTemperature())+", \"hum\":"+String(am2320.readHumidity())+"}}"); 
    delay(2000);
  } 
  else if (val == 'H' || val == '?'){
  Serial.println("Проверим русскую кодировку!");
  Serial.println("Hard is ready...");
  Serial.println("Press H or ? to help.");
  Serial.println("Press S for scan OneWire line");
  Serial.println("Press R for read DS18B20");
  Serial.println("Press G for read AM2320");    
  }else if (val == 'S'){
    Serial.println("START SCAN.");
    byte sc_res=10;
    while (sc_res!=0) {
    sc_res = scanner_wire1(sel_sens);
    sel_sens++;
  }
  Serial.println("END OF SCAN.");  
  sel_sens=0;
  }
}

/* Получить данные с температурных датчиков DS18B20 */
void get_term(int code){
  byte addr[8];
  float celsius, fahrenheit;
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];

  if (num_temp == 0 ) {
    Serial.print("{");
  }

  if ( !ds.search(addr)) {
    Serial.println("}");
    num_temp = 0;
    ds.reset_search();
    delay(250);
    return;
    if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return;
    }

  }
  Serial.print("\"num_sens\": ");  Serial.print(num_temp); Serial.print(",");
  num_temp++;
  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x10:
      Serial.print("\"sens_type\" : \"DS18S20\"");  type_s = 1; break; // or old DS1820
    case 0x28:
      Serial.print("\"sens_type\" : \"DS18B2\""); type_s = 0; break;
    case 0x22:
      Serial.print("\"sens_type\" : \"DS1822\""); type_s = 0; break;
    default:
      Serial.print("\"sens_type\" : \"NOT_DEVICE\""); return;
  }

  Serial.print(", \"sens_id\" : \" ");
  for ( i = 0; i < 8; i++) {
    if (i != 0) {
      Serial.write(':');
    }
    if (addr[i] < 16) {
      Serial.print("0");
    }
    Serial.print(addr[i], HEX);
  }
  Serial.print("\",");
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end

  //  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.

  present = ds.reset();
  ds.select(addr);
  ds.write(0xBE);         // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  celsius = (float)raw / 16.0;
  fahrenheit = celsius * 1.8 + 32.0;
  Serial.print("\"sens_Val\": [{ \"temp\":");
  //
  Serial.print(celsius);
  Serial.print("}],");
  delay(1000);
  //}  
  }

/* сканнер датчиков температуры DS18B20 */
byte scanner_wire1(int code) {
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];
  
  if ( !ds.search(addr)) {
    ds.reset_search();
    return 0;
  }
  Serial.print(" SENS_NUMBER ="+String(code));
  Serial.print(" ROM =");
  for( i = 0; i < 8; i++) {
    Serial.write(' ');
    if ( addr[i]<16) {
      Serial.print("0");
    }
    Serial.print(addr[i], HEX);
  }

  if (OneWire::crc8(addr, 7) != addr[7]) {
    Serial.println("CRC is not valid!");
    return 2;
  }
  Serial.print(" CHIP FAMILY ");
  Serial.print(addr[0],HEX);
  // the first ROM byte indicates which chip
  Serial.print(" =  ");
  switch (addr[0]) {

  case 0x01:
    Serial.println(" DS1990 DS2401");  // 
    return 1;
    break;
  case 0x02:
    Serial.println(" DS1991");  // 
    return 1;
    break;
  case 0x04:
    Serial.println(" DS1994");  // 
    return 1;
    break;
  case 0x05:
    Serial.println(" DS2405");  // 
    return 1;
    break;
  case 0x06:
    Serial.println(" DS1992");  // 
    return 1;
    break;
  case 0x08:
    Serial.println(" DS1993");  // 
    return 1;
    break;
  case 0x0B:
    Serial.println(" DS1985");
    return 1;
    break;
  case 0x10:
    Serial.println(" DS1820 DS18S20 DS1920");
    return 1;  
    break;
  case 0x12:
    Serial.println(" DS2406");
    return 1;  
    break;
  case 0x21:
    Serial.println(" DS1921");
    return 1;
    break;
  case 0x22:
    Serial.println(" DS1822");
    return 1;
    break;
  case 0x24:
    Serial.println(" DS1904");
    return 1;
    break;
  case 0x28:
    Serial.println(" DS18B20");
    return 1;
    break;
  case 0x29:
    Serial.println(" DS2408");
    return 1;  
    break;
  case 0x36:
    Serial.println(" DS2740");
    return 1;  
    break;
  case 0x3B:
    Serial.println(" DS1825");
    return 1;  
    break;
  case 0x41:
    Serial.println(" DS1923");
    return 1;  
    break;
//Serial.println("------41-------");
  default:
    Serial.println(" is not listed.");
//Serial.println("------5--------");
    return 1;
  } 

}
