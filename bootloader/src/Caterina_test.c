
#include <avr/io.h>
#include <avr/interrupt.h>

#include <stdint.h>

static uint32_t timer = 0;

ISR(TIMER0_OVF_vect)
{
    timer++;
}

ISR(BADISR_vect)
{
}

static const uint32_t LARGE_NUMBER = (500 * (16 * 1000 * 1000));

void lose_time()
{
    PORTD ^= (1 << 5);

    for (uint32_t i = 0; i < LARGE_NUMBER; i++)
    {
    }
    for (uint32_t i = 0; i < LARGE_NUMBER; i++)
    {
    }
    for (uint32_t i = 0; i < LARGE_NUMBER; i++)
    {
    }
    for (uint32_t i = 0; i < LARGE_NUMBER; i++)
    {
    }
}

void move_interrupt_vector_to_boot_section(void)
{
    uint8_t x;

    __asm__ volatile(
        "ldi %[x], 0b01 \n\t"               // x = 1 << IVCE (enable interrupt vector change)
        "out %[mcucr], %[x] \n\t"           // MCUCR = x
        "ldi %[x], 0b10 \n\t"               // x = 1 << IVSEL (move interrupt vector to start of boot section)
        "out %[mcucr], %[x] \n\t"           // MCUCR = x
        :                                   // No output operands
        : [x] "r"(x),                       // first input operand: uint8_t x
          [mcucr] "I" _SFR_IO_ADDR(MCUCR)); // second input operand: MCUCR register
}

void wait(uint32_t milliseconds)
{
    uint32_t end = timer + milliseconds;
    while (timer < end)
    {
    }
}

int main(void)
{
    cli();

    // clock_prescale_set(clock_div_1);

    move_interrupt_vector_to_boot_section();

    TCCR0A = 0;
    TCCR0B = 0b11;
    TCNT0 = 0;
    TIMSK0 = 0b1;

    DDRD |= (1 << 5);
    DDRB |= (1 << 0);

    if (MCUCR & 0b10)
    {
        PORTB |= (1 << 0);
    }

    sei();

    while (1)
    {
        uint32_t a = timer;
        // lose_time();
        wait(500);
        if (timer != a)
        {
            PORTB ^= (1 << 0);
        }
    }

    return (0);
}