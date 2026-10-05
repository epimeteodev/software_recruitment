#include "fakeArduino.hpp"
#include "MotorArduino.h"

#define PERIOD 100 // ms

class Servo {
	private:
	static const uint8_t LOW_ANGLE  = 240;
	static const uint8_t HIGH_ANGLE = 150;
	static const uint8_t MOVE_INSTRUCTION = 0x1E;

	static uint16_t encode_angle(uint8_t alpha) {
		return ((uint16_t)alpha * 0x3ff / 300);
	}

	public:
	static void start() {
		Serial.begin(19200);
	}

	static void end() {
		// Serial.close();
	}

	static void move(uint16_t fraction) {
		// LOW + (HIGH - LOW) * f
		int32_t angle = (int32_t)LOW_ANGLE + ((int32_t)HIGH_ANGLE - (int32_t)LOW_ANGLE) * (int32_t)fraction / (uint16_t)(-1);
		
		uint16_t encoded_angle = encode_angle(angle);
		// Little endian!
		uint8_t instruction[3] = {
			MOVE_INSTRUCTION,
			(uint8_t)(encoded_angle),	
			(uint8_t)(encoded_angle >> 8),
		};
		// printf("angle = %d, encoded = %d", angle, encoded_angle);

		Serial.write(instruction, 3);
	}
};

class Joystick {
	private:
	static const int PIN = A2;
	static const int MAX = 1023;
	static const int MIN = 0;

	public:
	static void start() {
		// assert(sizeof(int) >= 2); --> NOT a byte
		return;
	}

	static void end() {
		return;
	}

	static uint16_t read() {
		uint32_t res = analogRead(PIN);
		// printf("joystick= %d\n", res);
		res = res * ((1 << 16) - 1);
		res /= 1023;
		// printf("lel=%f\n", (float)res / (uint16_t)(-1));
		return (uint16_t) res;
	}
};

void loop_delay(uint64_t ms) {
	static uint64_t last_us = micros();

	uint64_t current_us = micros();
	uint64_t delta_ms = (current_us - last_us) / 1000;

	//printf("delta = %ld, ms = %ld\n", delta_ms, ms);
	if (delta_ms < ms) {
		delay(ms - delta_ms);
	}

	last_us = micros();
}

void setup() {
	Servo::start();
	Joystick::start();
	loop_delay(0); // init
}

void loop() {
	Servo::move(Joystick::read());
	loop_delay(PERIOD);
}