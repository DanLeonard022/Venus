#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Mata config
const int eyeWidth = 35;
const int eyeHeight = 34;
const int eyeRadius = 7;

const int leftEyeX = 20;
const int rightEyeX = 82;
const int eyeY = 25;

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.display();
  delay(500);
}

void loop() {
  wakeUpAnimation();
  blinkEyes(2, 200);
  lookEyes("left");
  delay(300);
  lookEyes("right");
  delay(300);
  lookEyes("center");
  delay(3000);
  smileEyes();
  delay(2000);
}

void drawEyes(int shrinkY = 0, int shiftX = 0) {
  display.clearDisplay();

  int newHeight = max(2, eyeHeight - shrinkY);  // prevent 0 height
  int yOffset = shrinkY / 2;

  display.fillRoundRect(leftEyeX + shiftX, eyeY + yOffset, eyeWidth, newHeight, eyeRadius, SSD1306_WHITE);
  display.fillRoundRect(rightEyeX + shiftX, eyeY + yOffset, eyeWidth, newHeight, eyeRadius, SSD1306_WHITE);

  display.display();
}

void blinkEyes(int times, int speed) {
  for (int i = 0; i < times; i++) {
    drawEyes(eyeHeight - 2);  // Almost closed (line)
    delay(speed);
    drawEyes(0);              // Open
    delay(speed);
  }
}

void lookEyes(String dir) {
  int shift = 0;
  if (dir == "left") shift = -4;
  else if (dir == "right") shift = 4;
  drawEyes(0, shift);
}

void smileEyes() {
  drawEyes(eyeHeight - 8);  // semi-closed smile shape
}

void wakeUpAnimation() {
  drawEyes(0);
  delay(500);
}
