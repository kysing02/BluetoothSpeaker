// Group 1 - DotSpeaker Project.
// This is the main process which should include whole functions.
/*--------------------------------MODULES---------------------------------*/
// LED Matrix 
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include <ESP32-VirtualMatrixPanel-I2S-DMA.h>
#include <Fonts/Org_01.h>

// LED Matrix and Canvas
MatrixPanel_I2S_DMA *dma_display = nullptr;
GFXcanvas16 *canvas = nullptr;

// Clock
// #include <WiFi.h>
#include <TimeLib.h>

// Aurora
#include <FastLED.h>
#include "Effects.h"
Effects effects;
#include "Drawable.h"
#include "Playlist.h"
#include "Patterns.h"
Patterns patterns;

// File System
#include <SPIFFS.h>
#include <FS.h>

// GIFs
#include <AnimatedGIF.h>

/*--------------------------MATRIX PANEL CONFIG---------------------------*/
#define PANEL_RES_X 64
#define PANEL_RES_Y 32
#define PANEL_CHAIN 1

/*-------------------------------VARIABLES--------------------------------*/
// Morphing
#define NUM_FRAMES 30

// Wi-Fi
// const char* ssid = "Kys";
// const char* password = "kys20021110";

// Bluetooth connection
bool bluetooth_connected = false;

// Clock
// const char* ntpServer = "pool.ntp.org";

// Predefined color
uint16_t myBLACK = dma_display->color565(0, 0, 0);
uint16_t myWHITE = dma_display->color565(255, 255, 255);
uint16_t myRED = dma_display->color565(255, 0, 0);
uint16_t myGREEN = dma_display->color565(0, 255, 0);
uint16_t myBLUE = dma_display->color565(0, 0, 255);

// Aurora
unsigned long fps = 0, fps_timer;                 // fps (this is NOT a matrix refresh rate!)
unsigned int default_fps = 30, pattern_fps = 30;  // default fps limit (this is not a matrix refresh counter!)
unsigned long ms_animation_max_duration = 20000;  // 20 seconds
unsigned long last_frame=0, ms_previous=0;

// GIFs
AnimatedGIF gif;
File f;
int x_offset, y_offset;
unsigned long start_tick = 0;
String gifDir = "/gifs";                // play all GIFs in this directory
char filePath[256] = { 0 };
File root, gifFile;
bool lastGIFhasEnded = true;
unsigned long previousGIFmillis = 0;

// Song Infos
uint8_t *imgData = NULL;
uint16_t *bitmap = (uint16_t *)malloc(32 * 32 * sizeof(uint16_t));
String image_data;
uint16_t *image_array = (uint16_t *)malloc(32 * 32 * sizeof(uint16_t));
String title = "No Song Played";
String artist = "N/A";

// Pause and play bitmap array
const uint8_t pauseBitmap[] = {
  B10010000,
  B10010000,
  B10010000,
  B10010000,
  B10010000,
  B10010000,
  B10010000
};
const uint8_t playBitmap[] = {
  B10000000,
  B11000000,
  B11100000,
  B11110000,
  B11100000,
  B11000000,
  B10000000
};

// Morphing
const unsigned long frameDelay = 10;
unsigned long previousMorphingMillis = 0;
int frame = 0;
String playbackStatus = "stop";

// Scrolling
const unsigned long scrollDelay = 100;
const unsigned long resetDelay = 1000;
unsigned long previousScrollMillis = 0;
int xPos = 32;
bool resetting = false;
bool currentScrollingSwitch = 0;        // 0 - Scrolling Title, 1 - Scrolling Artist

// Status manager
enum StatusEnum {SLEEP, CLOCK, WALLPAPER_CLOCK, MUSIC};
StatusEnum currentStatus = CLOCK;

/*-----------------------------MAIN FUNCTIONS-----------------------------*/
void setup() {
  // Starts serial connection (Serial Monitor)
  Serial.begin(38400);

  // Module configuration
  HUB75_I2S_CFG mxconfig(
    PANEL_RES_X,   // module width
    PANEL_RES_Y,   // module height
    PANEL_CHAIN    // Chain length
  );

  // Initialize display
  dma_display = new MatrixPanel_I2S_DMA(mxconfig);
  dma_display->begin();
  dma_display->setBrightness8(90);        // 0-255
  dma_display->clearScreen();

  // Initialize canvas
  canvas = new GFXcanvas16(64, 32);
  canvas->setTextWrap(false);

  // Power on idle screen
  dma_display->setFont(&Org_01);
  dma_display->setTextSize(1);
  dma_display->setTextColor(myGREEN);
  dma_display->setCursor(1, 18);
  dma_display->println("DOT.SPEAKER");
  
  // Connect to WiFi
  // WiFi.begin(ssid, password);
  // while (WiFi.status() != WL_CONNECTED) {
  //   delay(1000);
  //   Serial.println("Connecting to WiFi...");
  // }
  // Serial.println("Connected to WiFi");

  while (!bluetooth_connected) {
    delay(1000);
    decodeCommands();
  }

  // Initialize NTP
  //configTime(9 * 3600, 0, ntpServer);
  //setTime(12, 0, 0, 1, 1, 1970);          // set initial time (time before NTP time is get)
  //updateClock();

  // Initialize Aurora
  effects.Setup();
  patterns.listPatterns();
  patterns.moveRandom(1);                 // start from a random pattern
  Serial.print("Pattern set: ");
  Serial.println(patterns.getCurrentPatternName());
  ms_previous = millis();
  fps_timer = millis();

  // Start filesystem
  Serial.println(" * Loading SPIFFS");
  if(!SPIFFS.begin()){
    Serial.println("SPIFFS Mount Failed");
  }

  // Initialize GIF
  gif.begin(LITTLE_ENDIAN_PIXELS);
  root = SPIFFS.open(gifDir);

  // Open the cover art bmp file from SPIFFS
  String imgDir = "/cover.bmp";
  File file = SPIFFS.open(imgDir, "r");
  if (SPIFFS.exists("/cover.bmp")) {
    Serial.println("/cover.bmp File does exist");
  }

  // Read the cover art image data into bitmap variable
  size_t fileSize = file.size();
  Serial.println(fileSize);
  imgData = (uint8_t *)malloc(fileSize);
  file.read(imgData, fileSize);
  file.close();
  convertRGB888toRGB565(imgData + 54, bitmap, 32, 32);       // TODO: Hardcoded image header info
  free(imgData);

  // Copy values from bitmap to image_array (default image)
  copyBitmapToImageArray();

  // Clear screen
  dma_display->setTextColor(myWHITE);
  dma_display->fillScreen(myBLACK);
}

void loop() {
//  if (currentStatus != CLOCK){          // only permit clock since aurora need fps control
//    canvas->fillScreen(myBLACK);
//  }
  decodeCommands();
  if (currentStatus == MUSIC){
    if (!bluetooth_connected) {
      dma_display->setFont(&Org_01);
      dma_display->setTextSize(1);
      dma_display->setTextColor(myRED);
      dma_display->setCursor(1, 18);
      dma_display->println("Bluetooth");
      dma_display->setCursor(32, 26);
      dma_display->println("OFF");
    }
    else {
      scrollText();
      showPlayPauseButton();
      canvas->drawRGBBitmap(0, 0, image_array, 32, 32);
    }
  }
  else if (currentStatus == CLOCK){
    playAuroraPattern();
  }
  else if (currentStatus == WALLPAPER_CLOCK){
    ShowGIF();
    drawClock();
  }
  dma_display->drawRGBBitmap(0, 0, canvas->getBuffer(), 64, 32);
}

/*----------------------------OTHER FUNCTIONS-----------------------------*/

/**
 * @brief Synchronize clock using NTP Time.
 * 
 */
// void updateClock() {
//   // Fetch NTP time
//   time_t currentTime = time(nullptr);
//   struct tm* timeInfo;
//   timeInfo = localtime(&currentTime);
//   // Update the internal time
//   setTime(timeInfo->tm_hour, timeInfo->tm_min, timeInfo->tm_sec,
//           timeInfo->tm_mday, timeInfo->tm_mon + 1, timeInfo->tm_year + 1900);
// }

/**
 * @brief Draw clock on the GFX Canvas. Automatically synchronize NTP time every hour.
 * 
 */
void drawClock() {
  // Synchronize NTP time every seconds
  // if (millis() % (1000) == 0) {
  //   canvas->fillScreen(myBLACK);
  //   updateClock();
  // }

  // Get current time
  int currentHour = hourFormat12();
  int currentMinute = minute();
  int currentSecond = second();

  // Create strings for the clock display
  char timeStr[6];
  sprintf(timeStr, "%02d:%02d", currentHour, currentMinute);

  int currentDay = day();
  int currentMonth = month();

  char dayStr[25];
  sprintf(dayStr, "%s %02d/%02d", dayShortStr(weekday()), currentMonth, currentDay);

  // String dayStrJap;
  // if (dayStr == "Sun"){
  //   dayStrJap = "日";
  // }
  // else if (dayStr == "Mon"){
  //   dayStrJap = "月";
  // }
  // else if (dayStr == "Tue"){
  //   dayStrJap = "火";
  // }
  // else if (dayStr == "Wed"){
  //   dayStrJap = "水";
  // }
  // else if (dayStr == "Thu"){
  //   dayStrJap = "木";
  // }
  // else if (dayStr == "Fri"){
  //   dayStrJap = "金";
  // }
  // else if (dayStr == "Sat"){
  //   dayStrJap = "土";
  //}

  // Draw the hour:minutes in the center
  int textSize = 2;
  int xOffsetHour = 1;
  int yOffsetHour = 2;
  int xPosition = (PANEL_RES_X - strlen(timeStr) * (6 * textSize)) / 2 + xOffsetHour;
  int yPosition = (PANEL_RES_Y - 16 * textSize) / 2 + yOffsetHour;
  canvas->setCursor(xPosition, yPosition);
  canvas->setTextSize(textSize);
  canvas->setFont();
  canvas->setTextColor(myWHITE);
  canvas->print(timeStr);

  // Draw the weekday at the bottom left
  int textSizeSmall = 1;
  canvas->setCursor(2, PANEL_RES_Y - 8 * textSizeSmall);
  canvas->setTextSize(textSizeSmall);
  canvas->setFont();
  canvas->setTextColor(dma_display->color565(221, 240, 226));
  for (int i = 0; i < strlen(dayStr); ++i) {      
    dayStr[i] = toupper(dayStr[i]);           // Capitalize the weekday string
  }
  canvas->print(dayStr);
}

/**
 * @brief Play a single aurora pattern frame.
 * 
 */
void playAuroraPattern() {
  // If current pattern has exceed max animation duration, change pattern
  if ( (millis() - ms_previous) > ms_animation_max_duration ) 
  {
    patterns.stop();
    patterns.moveRandom(1);
    patterns.start();
    
    Serial.print("Changing pattern to:  ");
    Serial.println(patterns.getCurrentPatternName());
    
    ms_previous = millis();

    //effects.RandomPalette();          // select a random palette as well
  }

  // Draw a single pattern frame (?)
  if ( 1000 / pattern_fps + last_frame < millis()){
    last_frame = millis();
    pattern_fps = patterns.drawFrame();
    if (!pattern_fps)
      pattern_fps = default_fps;
    ++fps;
    drawClock();
  }
  // Use this for dirty workaround
//  last_frame = millis();
//  pattern_fps = patterns.drawFrame();
//  if (!pattern_fps)
//    pattern_fps = default_fps;
//  ++fps;

  // Show effect fps every second
  if (fps_timer + 1000 < millis()){
    Serial.printf_P(PSTR("Effect fps: %ld\n"), fps);
    fps_timer = millis();
    fps = 0;
  }
}

/**
 * @brief Draw a line of image directly on the LED Matrix.
 * // Parse the received time string (assuming the format is HH:MM:SS)
  sscanf(receivedData.c_str(), "%d:%d:%d", &hours, &minutes, &seconds);

 */
void GIFDraw(GIFDRAW *pDraw)
{
    uint8_t *s;
    uint16_t *d, *usPalette, usTemp[320];
    int x, y, iWidth;

  iWidth = pDraw->iWidth;
  if (iWidth > MATRIX_WIDTH)
      iWidth = MATRIX_WIDTH;

    usPalette = pDraw->pPalette;
    y = pDraw->iY + pDraw->y; // current line
    
    s = pDraw->pPixels;
    if (pDraw->ucDisposalMethod == 2) // restore to background color
    {
      for (x=0; x<iWidth; x++)
      {
        if (s[x] == pDraw->ucTransparent)
           s[x] = pDraw->ucBackground;
      }
      pDraw->ucHasTransparency = 0;
    }
    // Apply the new pixels to the main image
    if (pDraw->ucHasTransparency) // if transparency used
    {
      uint8_t *pEnd, c, ucTransparent = pDraw->ucTransparent;
      int x, iCount;
      pEnd = s + pDraw->iWidth;
      x = 0;
      iCount = 0; // count non-transparent pixels
      while(x < pDraw->iWidth)
      {
        c = ucTransparent-1;
        d = usTemp;
        while (c != ucTransparent && s < pEnd)
        {
          c = *s++;
          if (c == ucTransparent) // done, stop
          {
            s--; // back up to treat it like transparent
          }
          else // opaque
          {
             *d++ = usPalette[c];
             iCount++;
          }
        } // while looking for opaque pixels
        if (iCount) // any opaque pixels?
        {
          for(int xOffset = 0; xOffset < iCount; xOffset++ ){
            canvas->drawPixel(x + xOffset, y, usTemp[xOffset]); // 565 Color Format
          }
          x += iCount;
          iCount = 0;
        }
        // no, look for a run of transparent pixels
        c = ucTransparent;
        while (c == ucTransparent && s < pEnd)
        {
          c = *s++;
          if (c == ucTransparent)
             iCount++;
          else
             s--; 
        }
        if (iCount)
        {
          x += iCount; // skip these
          iCount = 0;
        }
      }
    }
    else // does not have transparency
    {
      s = pDraw->pPixels;
      // Translate the 8-bit pixels through the RGB565 palette (already byte reversed)
      for (x=0; x<pDraw->iWidth; x++)
      {
        canvas->drawPixel(x, y, usPalette[*s++]); // color 565
      }
    }
}

/**
 * @brief Open a GIF File.
 * 
 */
void * GIFOpenFile(const char *fname, int32_t *pSize)
{
  Serial.print("Playing gif: ");
  Serial.println(fname);
  f = SPIFFS.open(fname);
  if (f)
  {
    *pSize = f.size();
    return (void *)&f;
  }
  return NULL;
}

/**
 * @brief Close a GIF File.
 * 
 */
void GIFCloseFile(void *pHandle)
{
  File *f = static_cast<File *>(pHandle);
  if (f != NULL)
     f->close();
}

/**
 * @brief Read a GIF File.
 * 
 */
int32_t GIFReadFile(GIFFILE *pFile, uint8_t *pBuf, int32_t iLen)
{
    int32_t iBytesRead;
    iBytesRead = iLen;
    File *f = static_cast<File *>(pFile->fHandle);
    // Note: If you read a file all the way to the last byte, seek() stops working
    if ((pFile->iSize - pFile->iPos) < iLen)
       iBytesRead = pFile->iSize - pFile->iPos - 1; // <-- ugly work-around
    if (iBytesRead <= 0)
       return 0;
    iBytesRead = (int32_t)f->read(pBuf, iBytesRead);
    pFile->iPos = f->position();
    return iBytesRead;
}

/**
 * @brief Seek a GIF File.
 * 
 */
int32_t GIFSeekFile(GIFFILE *pFile, int32_t iPosition)
{ 
  int i = micros();
  File *f = static_cast<File *>(pFile->fHandle);
  f->seek(iPosition);
  pFile->iPos = (int32_t)f->position();
  i = micros() - i;
//  Serial.printf("Seek time = %d us\n", i);
  return pFile->iPos;
}

/**
 * @brief Show a GIF image. The operation is non-blocking.
 * 
 */
void ShowGIF()
{
  unsigned long currentMillis = millis();
  
  if (lastGIFhasEnded){
    gifFile.close();
    gifFile = root.openNextFile();
    if (!gifFile){
      root.close();
      root = SPIFFS.open(gifDir);
      gifFile = root.openNextFile();
    }
    if (!gifFile.isDirectory()){
      lastGIFhasEnded = false;
      memset(filePath, 0x0, sizeof(filePath));                
      strcpy(filePath, gifFile.path());
      if (gif.open(filePath, GIFOpenFile, GIFCloseFile, GIFReadFile, GIFSeekFile, GIFDraw)){
        x_offset = (MATRIX_WIDTH - gif.getCanvasWidth())/2;
        if (x_offset < 0) x_offset = 0;
        y_offset = (MATRIX_HEIGHT - gif.getCanvasHeight())/2;
        if (y_offset < 0) y_offset = 0;
        Serial.printf("Successfully opened GIF; Canvas size = %d x %d\n", gif.getCanvasWidth(), gif.getCanvasHeight());
        Serial.flush();
      }
    }
  }
  // Draw a single frame
  if (!gif.playFrame(true, NULL) || ((currentMillis - previousGIFmillis) > 8000)){
    previousGIFmillis = millis();
    gif.close();
    lastGIFhasEnded = true;
  }
}

/**
 * @brief Convert RGB888 to RGB565. (with inversion)
 * Red and Blue channel is swapped and whole image is vertically inverted.
 * For opening BMP files through SPIFFS.
 */
void convertRGB888toRGB565(const uint8_t* input, uint16_t* output, size_t width, size_t height) {
    for (size_t j = 0; j < height; j++) {
        for (size_t i = 0; i < width; i++) {
            uint8_t r = input[((height - 1 - j) * width + i) * 3 + 2];  // Adjust for vertical inversion
            uint8_t g = input[((height - 1 - j) * width + i) * 3 + 1];
            uint8_t b = input[((height - 1 - j) * width + i) * 3];

            // Convert to RGB565 format
            output[j * width + i] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
        }
    }
}

/**
 * @brief Convert RGB888 to RGB565. (without inversion)
 * For receiving image from Serial Communication.
 */
void convertRGB888toRGB565noInversion(const uint8_t* input, uint16_t* output, size_t width, size_t height) {
  for (size_t i = 0; i < width * height; i++) {
    uint8_t r = input[i * 3];
    uint8_t g = input[i * 3 + 1];
    uint8_t b = input[i * 3 + 2];

    // Convert to RGB565 format
    output[i] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
  }
}

/**
 * @brief Convert monochrome color (0 to 1) to RGB565.
 * 
 */
uint16_t convertMonochromeToRGB565(float monochrome) {
    // Ensure the monochrome value is within the valid range [0, 1]
    monochrome = std::max(0.0f, std::min(1.0f, monochrome));

    // Map monochrome value to 5-bit intensity for red channel
    uint8_t red = static_cast<uint8_t>(monochrome * 31);

    // Map monochrome value to 6-bit intensity for green channel
    uint8_t green = static_cast<uint8_t>(monochrome * 63);

    // Map monochrome value to 5-bit intensity for blue channel
    uint8_t blue = static_cast<uint8_t>(monochrome * 31);

    // Combine the color intensities into RGB565 format
    uint16_t rgb565 = (red << 11) | (green << 5) | blue;

    return rgb565;
}

/**
 * @brief Simple linear interpolation
 * 
 */
float interpolate(float start, float end_f, int frame, int numFrames) {
  return start + ((end_f - start) * frame) / numFrames;
}

/**
 * @brief Interpolate pixel values and display a single frame
 * 
 */
void interpolateAndDisplay(int start_x, int start_y, const uint8_t* bitmap1, const uint8_t* bitmap2, int frame, int numFrames, int width, int height) {
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      // Interpolate pixel values between the two bitmaps
      float pixel1 = ((bitmap1[y] >> (7 - x)) & 0x01) ? 1 : 0;
      float pixel2 = ((bitmap2[y] >> (7 - x)) & 0x01) ? 1 : 0;
      
      float pixel = interpolate(pixel1, pixel2, frame, numFrames);
      uint16_t color = convertMonochromeToRGB565(pixel);
      
      // Set the pixel on the screen
      canvas->drawPixel(start_x + x, start_y + y, color);
    }
  }
}

/**
 * @brief Show a frame of play or pause button based on current frame and playback status.
 * 
 */
void showPlayPauseButton(){
  unsigned long currentMillis = millis();
  canvas->fillRect(46, 20, 4, 7, myBLACK);

  if (playbackStatus == "pause") {
    if (frame < NUM_FRAMES) {
      if (currentMillis - previousMorphingMillis >= frameDelay) {
        frame++;
      }    
      interpolateAndDisplay(46, 20, pauseBitmap, playBitmap, frame, NUM_FRAMES, 4, 7);
    }
    else {
      canvas->drawBitmap(46, 20, playBitmap, 4, 7, myWHITE);
    }
  }
  else if (playbackStatus == "play") {
    if (frame < NUM_FRAMES) {
      if (currentMillis - previousMorphingMillis >= frameDelay) {
        frame++;
      }    
      interpolateAndDisplay(46, 20, playBitmap, pauseBitmap, frame, NUM_FRAMES, 4, 7);
    }
    else {
      canvas->drawBitmap(46, 20, pauseBitmap, 4, 7, myWHITE);
    }
  }
}

/**
 * @brief Scroll text and prints song title and artist.
 * 
 */
void scrollText(){
  int16_t x_text, y_text;
  uint16_t w_text, h_text;
  
  unsigned long currentMillis = millis();

  if (resetting == true){
    // Print static text and wait for 1 second before scrolling next content
    if (currentMillis - previousScrollMillis >= resetDelay){
      previousScrollMillis = currentMillis;
      resetting = false;
      xPos = 32;
    }
    else if (currentScrollingSwitch == 0) {
      //canvas->getTextBounds(title, 32, 5, &x_text, &y_text, &w_text, &h_text);
      //canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      //canvas->getTextBounds(artist, 32, 13, &x_text, &y_text, &w_text, &h_text);
      //canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      canvas->fillRect(32, 0, 32, 16, myBLACK);
      
      canvas->setTextColor(myGREEN);
      canvas->setCursor(32, 5);
      canvas->println(title);
  
      canvas->setTextColor(myBLUE);
      canvas->setCursor(xPos, 13);
      canvas->println(artist);
    }
    else {
      //canvas->getTextBounds(title, 32, 5, &x_text, &y_text, &w_text, &h_text);
      //canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      //canvas->getTextBounds(artist, 32, 13, &x_text, &y_text, &w_text, &h_text);
      //canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      canvas->fillRect(32, 0, 32, 16, myBLACK);
      
      canvas->setTextColor(myGREEN);
      canvas->setCursor(xPos, 5);
      canvas->println(title);
  
      canvas->setTextColor(myBLUE);
      canvas->setCursor(32, 13);
      canvas->println(artist);
    }
  }
  else if (currentScrollingSwitch == 0) {
    // Scroll Ttile
    // If scrolling time interval has passed
    if (currentMillis - previousScrollMillis >= scrollDelay){
      previousScrollMillis = currentMillis;
      canvas->getTextBounds(title, xPos, 5, &x_text, &y_text, &w_text, &h_text);
      // If there is still text to scroll
      if (xPos >= 32 - (w_text - 32)) { // initialPosition - (textWidth - textBoundaryWidth)
        // Clear the display
        canvas->fillRect(x_text, y_text, w_text, h_text, myBLACK);
        canvas->getTextBounds(artist, 32, 13, &x_text, &y_text, &w_text, &h_text);
        canvas->fillRect(x_text, y_text, w_text, h_text, myBLACK);

        canvas->setFont(&Org_01);
        canvas->setTextSize(1);
          
        canvas->setTextColor(myGREEN);
        // Display the text at the current position
        canvas->setCursor(xPos, 5);
        canvas->println(title);

        canvas->setTextColor(myBLUE);
        canvas->setCursor(32, 13);
        canvas->println(artist);
        
        // Move the text to the left for scrolling effect
        xPos--;
      }
      // If the text reaches the end, restart the scrolling after a delay
      else {
        resetting = true;
        currentScrollingSwitch = 1;
        canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      }
    }
  }
  else {
    // Scroll Artist
    // If scrolling time interval has passed
    if (currentMillis - previousScrollMillis >= scrollDelay){
      previousScrollMillis = currentMillis;
      canvas->getTextBounds(artist, xPos, 13, &x_text, &y_text, &w_text, &h_text);
      // If there is still text to scroll
      if (xPos >= 32 - (w_text - 32)) { // initialPosition - (textWidth - textBoundaryWidth)
        // Clear the display
        canvas->fillRect(x_text, y_text, w_text, h_text, myBLACK);
        canvas->getTextBounds(title, 32, 5, &x_text, &y_text, &w_text, &h_text);
        canvas->fillRect(x_text, y_text, w_text, h_text, myBLACK);

        canvas->setFont(&Org_01);
        canvas->setTextSize(1);
        
        canvas->setTextColor(myBLUE);
        // Display the text at the current position
        canvas->setCursor(xPos, 13);
        canvas->println(artist);
  
        canvas->setTextColor(myGREEN);
        canvas->setCursor(32, 5);
        canvas->println(title);
        
        // Move the text to the left for scrolling effect
        xPos--;
      }
      // If the text reaches the end, restart the scrolling after a delay
      else {
        resetting = true;
        currentScrollingSwitch = 0;
        canvas->fillRect(x_text - 1, y_text - 1, w_text + 2, h_text + 2, myBLACK);
      }
    }
  }
}

/**
 * @brief Convert string received from serial communication into bitmap uint8_t array.
 * The converted array is then ready to be used to be drawn onto LED Matrix.
 */
void convertStringToImage(String image_data){
  // Remove square brackets and spaces
  image_data.remove(0, 1);
  image_data.remove(image_data.length() - 1, 1);
  image_data.trim();

  // Tokenize the string by commas
  int count = 0;
  while (image_data.length() > 0) {
    int commaIndex = image_data.indexOf(',');
    if (commaIndex == -1) {
      commaIndex = image_data.length();
    }

    // Extract the substring until the comma
    String valueStr = image_data.substring(0, commaIndex);

    // Convert the substring to uint16_t and store it in the array
    image_array[count] = valueStr.toInt();

    // Remove the processed part from the string
    image_data.remove(0, commaIndex + 1);
    image_data.trim();

    count++;
  }

  Serial.println("Converted uint16_t array:");
  for (int i = 0; i < sizeof(image_array) / sizeof(image_array[0]); i++) {
    Serial.print(image_array[i]);
    Serial.print(" ");
  }
}

/**
 * @brief Copy every single bit of bitmap into image array.
 * 
 */
void copyBitmapToImageArray() {
  for (int i = 0; i < 32 * 32; ++i) {
        image_array[i] = bitmap[i];
    }
}

void parseTime(String timeinfo) {
  int month, day, year, hour, min, sec;       //  01/30/24:14:17:25

  // Parse the received time string
  sscanf(timeinfo.c_str(), "%d/%d/%d:%d:%d:%d", &month, &day, &year, &hour, &min, &sec);

  setTime(hour, min, sec, day, month, year);
}

/**
 * @brief Check serial inputs and decode commands.
 * 
 */
void decodeCommands(){
  if (Serial.available()){
    char command = Serial.read();
    if(command == 'A'){
      // Change status CLOCK
      currentStatus = CLOCK;
      canvas->fillScreen(myBLACK);
    }
    else if(command == 'B'){
      // Change status WALLPAPER_CLOCK
      currentStatus = WALLPAPER_CLOCK;
      canvas->fillScreen(myBLACK);
    }
    else if(command == 'C'){
      // Change status MUSIC
      currentStatus = MUSIC;
      canvas->fillScreen(myBLACK);
    }
    else if(command == '1'){
      // Bluetooth connection status
      char bt_connection;
      bt_connection = Serial.readStringUntil('\n')[0];
      if (bt_connection == '0'){
        bluetooth_connected = false;
      }
      else if (bt_connection == '1'){
        bluetooth_connected = true;
      }
    }
    else if(command == '2'){
      // AVRCP - Pause
      if (playbackStatus == "play") frame = NUM_FRAMES - frame;   // Reset frame
      playbackStatus = "pause";
    }
    else if(command == '3'){
      // AVRCP - Play
      if (playbackStatus == "pause") frame = NUM_FRAMES - frame;  // Reset frame
      playbackStatus = "play";
    }
    else if(command == '4'){
      // AVRCP - Stop
      frame = 0;                                                  // Reset frame
      playbackStatus = "stop";
      title = "No Song Played";                                   // Delete song infos
      artist = "N/A";
      copyBitmapToImageArray();                                   // Use default covert art
      xPos = 32;
      resetting = true;
      currentScrollingSwitch = 0;
      previousScrollMillis = millis();
    }
    else if(command == '5'){
      // AVRCP - Update song title
      title = Serial.readStringUntil('\n');                       // Reset scrolling
      xPos = 32;
      resetting = true;
      currentScrollingSwitch = 0;
      previousScrollMillis = millis();
    }
    else if(command == '6'){
      // AVRCP - Update song artist
      artist = Serial.readStringUntil('\n');                      // Reset scrolling
      xPos = 32;
      resetting = true;
      currentScrollingSwitch = 0;
      previousScrollMillis = millis();
    }
    else if(command == '7'){
      // AVRCP - Update song cover
      image_data = Serial.readStringUntil('\n');
      if (image_data == NULL || image_data == "" || image_data.length() < 1000) {
        copyBitmapToImageArray();
      }
      else {
        convertStringToImage(image_data);
      }
    }
    else if(command == '8'){
      String timeinfo;
      timeinfo = Serial.readStringUntil('\n');
      parseTime(timeinfo);
    }
    else {
      Serial.print("Error: unknown command :");
      Serial.println(command);
    }
  }
}
