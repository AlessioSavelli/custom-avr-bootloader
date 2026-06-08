#ifndef LEDS_H
#define LEDS_H

#include <stdbool.h>

typedef enum
{
    LED_ON = 0,
    LED_OFF = 1,
    LED_TOGGLE = 2,
} led_action_t;

typedef enum
{
    LED_TX = 0,
    LED_RX = 1,
    LED_1 = 2,
    LED_2 = 3,

    LED_COUNT
} led_id_t;

void leds_setup(void);
void leds_teardown(void);
void leds(led_id_t id, led_action_t action);
#endif // LEDS_H