#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

int demo_mode = 1;
static const int max_animation_index = 8;
int current_animation_index = 0;

// Reference state
int ref_eye_height = 40;
int ref_eye_width = 40;
int ref_space_between_eye = 10;
int ref_corner_radius = 10;

// Current eye state
int left_eye_height = ref_eye_height;
int left_eye_width = ref_eye_width;
int left_eye_x = 32;
int left_eye_y = 32;
int right_eye_x = 32 + ref_eye_width + ref_space_between_eye;
int right_eye_y = 32;
int right_eye_height = ref_eye_height;
int right_eye_width = ref_eye_width;

void draw_eyes(bool update = true) {
  display.clearDisplay();
  int x = int(left_eye_x - left_eye_width / 2);
  int y = int(left_eye_y - left_eye_height / 2);
  display.fillRoundRect(x, y, left_eye_width, left_eye_height, ref_corner_radius, SSD1306_WHITE);
  x = int(right_eye_x - right_eye_width / 2);
  y = int(right_eye_y - right_eye_height / 2);
  display.fillRoundRect(x, y, right_eye_width, right_eye_height, ref_corner_radius, SSD1306_WHITE);
  if (update) display.display();
}

void center_eyes(bool update = true) {
  left_eye_height = ref_eye_height;
  left_eye_width = ref_eye_width;
  right_eye_height = ref_eye_height;
  right_eye_width = ref_eye_width;

  left_eye_x = SCREEN_WIDTH / 2 - ref_eye_width / 2 - ref_space_between_eye / 2;
  left_eye_y = SCREEN_HEIGHT / 2;
  right_eye_x = SCREEN_WIDTH / 2 + ref_eye_width / 2 + ref_space_between_eye / 2;
  right_eye_y = SCREEN_HEIGHT / 2;

  draw_eyes(update);
}

void blink(int speed = 12) {
  draw_eyes();
  for (int i = 0; i < 3; i++) {
    left_eye_height -= speed;
    right_eye_height -= speed;
    draw_eyes();
    delay(1);
  }
  for (int i = 0; i < 3; i++) {
    left_eye_height += speed;
    right_eye_height += speed;
    draw_eyes();
    delay(1);
  }
}

void sleep() {
  left_eye_height = 2;
  right_eye_height = 2;
  draw_eyes(true);
}

void wakeup() {
  sleep();
  for (int h = 0; h <= ref_eye_height; h += 2) {
    left_eye_height = h;
    right_eye_height = h;
    draw_eyes(true);
  }
}

void happy_eye() {
  center_eyes(false);
  int offset = ref_eye_height / 2;
  for (int i = 0; i < 10; i++) {
    display.fillTriangle(left_eye_x - left_eye_width / 2 - 1, left_eye_y + offset,
                         left_eye_x + left_eye_width / 2 + 1, left_eye_y + 5 + offset,
                         left_eye_x - left_eye_width / 2 - 1, left_eye_y + left_eye_height + offset, SSD1306_BLACK);

    display.fillTriangle(right_eye_x + right_eye_width / 2 + 1, right_eye_y + offset,
                         right_eye_x - left_eye_width / 2 - 1, right_eye_y + 5 + offset,
                         right_eye_x + right_eye_width / 2 + 1, right_eye_y + right_eye_height + offset, SSD1306_BLACK);
    offset -= 2;
    display.display();
    delay(1);
  }
  display.display();
  delay(1000);
}

void saccade(int direction_x, int direction_y) {
  int dx = 8;
  int dy = 6;
  int blink_amt = 8;

  left_eye_x += dx * direction_x;
  right_eye_x += dx * direction_x;
  left_eye_y += dy * direction_y;
  right_eye_y += dy * direction_y;
  left_eye_height -= blink_amt;
  right_eye_height -= blink_amt;
  draw_eyes();
  delay(1);

  left_eye_x += dx * direction_x;
  right_eye_x += dx * direction_x;
  left_eye_y += dy * direction_y;
  right_eye_y += dy * direction_y;
  left_eye_height += blink_amt;
  right_eye_height += blink_amt;
  draw_eyes();
  delay(1);
}

void move_big_eye(int direction) {
  int oversize = 1;
  int dx = 2;
  int blink_amt = 5;

  for (int i = 0; i < 3; i++) {
    left_eye_x += dx * direction;
    right_eye_x += dx * direction;
    left_eye_height -= blink_amt;
    right_eye_height -= blink_amt;
    if (direction > 0) {
      right_eye_height += oversize;
      right_eye_width += oversize;
    } else {
      left_eye_height += oversize;
      left_eye_width += oversize;
    }
    draw_eyes();
    delay(1);
  }

  for (int i = 0; i < 3; i++) {
    left_eye_x += dx * direction;
    right_eye_x += dx * direction;
    left_eye_height += blink_amt;
    right_eye_height += blink_amt;
    if (direction > 0) {
      right_eye_height += oversize;
      right_eye_width += oversize;
    } else {
      left_eye_height += oversize;
      left_eye_width += oversize;
    }
    draw_eyes();
    delay(1);
  }

  delay(1000);

  for (int i = 0; i < 3; i++) {
    left_eye_x -= dx * direction;
    right_eye_x -= dx * direction;
    left_eye_height -= blink_amt;
    right_eye_height -= blink_amt;
    if (direction > 0) {
      right_eye_height -= oversize;
      right_eye_width -= oversize;
    } else {
      left_eye_height -= oversize;
      left_eye_width -= oversize;
    }
    draw_eyes();
    delay(1);
  }

  for (int i = 0; i < 3; i++) {
    left_eye_x -= dx * direction;
    right_eye_x -= dx * direction;
    left_eye_height += blink_amt;
    right_eye_height += blink_amt;
    if (direction > 0) {
      right_eye_height -= oversize;
      right_eye_width -= oversize;
    } else {
      left_eye_height -= oversize;
      left_eye_width -= oversize;
    }
    draw_eyes();
    delay(1);
  }

  center_eyes();
}

void move_right_big_eye() { move_big_eye(1); }
void move_left_big_eye() { move_big_eye(-1); }

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  Serial.begin(115200);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Eye Bot Starting...");
  display.display();
  delay(1000);
  center_eyes();
}

void loop() {
  blink(6);
  delay(1000);
  saccade(1, 0);  // look right
  delay(1000);
  saccade(-1, 0); // look left
  delay(1000);
  happy_eye();
  delay(1000);
  sleep();
  delay(1000);
  wakeup();
  delay(1000);
  move_left_big_eye();
  delay(1000);
  move_right_big_eye();
  delay(1000);
}
