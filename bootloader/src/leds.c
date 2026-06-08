#include "leds.h"
#include <avr/io.h>

// A single compact struct with the data for each LED
typedef struct
{
    volatile uint8_t *port;
    volatile uint8_t *ddr;
    uint8_t bit;
} led_t;

static const led_t leds_data[LED_COUNT] = {
    {&PORTD, &DDRD, 5}, // LED_TX
    {&PORTB, &DDRB, 0}, // LED_RX
    {&PORTE, &DDRE, 6}, // LED_1
    {&PORTB, &DDRB, 5}, // LED_2
};

void leds_setup(void)
{
    for (led_id_t i = 0; i < LED_COUNT; i++)
    {
        *leds_data[i].ddr |= (1 << leds_data[i].bit);
    }
}

void leds_teardown(void)
{
    for (led_id_t i = 0; i < LED_COUNT; i++)
    {
        *leds_data[i].ddr &= ~(1 << leds_data[i].bit);
    }
}

void leds(led_id_t id, led_action_t action)
{
    volatile uint8_t *port = leds_data[id].port;
    uint8_t bit = (1 << leds_data[id].bit);

    if (action == LED_ON)
    {
        *port |= bit;
    }
    else if (action == LED_OFF)
    {
        *port &= ~bit;
    }
    else
    { // LED_TOGGLE
        *port ^= bit;
    }
}
