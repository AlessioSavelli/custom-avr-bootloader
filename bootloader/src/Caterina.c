#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/boot.h>
#include <avr/eeprom.h>
#include <avr/power.h>
#include <avr/interrupt.h>

#include "bootloader_globals.h"
#include "bootloader_timer.h"
#include "command_processor.h"
// #include "leds.h"
#include "usb_manager.h"

#include "compiler_macros.h"

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

void move_interrupt_vector_to_application_section(void)
{
    uint8_t x;

    __asm__ volatile(
        "ldi %[x], 0b01 \n\t"               // x = 1 << IVCE (enable interrupt vector change)
        "out %[mcucr], %[x] \n\t"           // MCUCR = x
        "ldi %[x], 0b00 \n\t"               // x = 0 (move interrupt vector to start of application section)
        "out %[mcucr], %[x] \n\t"           // MCUCR = x
        :                                   // No output operands
        : [x] "r"(x),                       // first input operand: uint8_t x
          [mcucr] "I" _SFR_IO_ADDR(MCUCR)); // second input operand: MCUCR register
}

static void bootloader_setup(void)
{
    MCUSR = 0;     // clear all reset flags
    wdt_disable(); // disable watchdog

    clock_prescale_set(clock_div_1); // Disable clock division

    move_interrupt_vector_to_boot_section();

    BT_setup();
    
    USB_setup();

    sei(); // Enable global interrupts

}

static void bootloader_loop(void)
{
    static BT_time_ms_t led_timer = 0;
    if (BT_timer_expired(&led_timer, 100))
    {
        BT_timer_start(&led_timer);
    }

    USB_loop();
}

static void bootloader_teardown(void)
{
    USB_teardown();
    BT_teardown();

    // clear (disable) interrupts
    cli();

    move_interrupt_vector_to_application_section();
}

int main(void)
{
    bootloader_setup();
    while (!BT_timer_expired(&bootloader_timer, BOOTLOADER_TIMEOUT))
    {
        bootloader_loop();
    }
    bootloader_teardown();

    /* jump to beginning of application space */
    __asm__ volatile("jmp 0x0000");
}

ISR(BADISR_vect)
{
}
