#ifndef BOOTLOADER_TIMER_H
#define BOOTLOADER_TIMER_H

#include <stdint.h>
#include <stdbool.h>

typedef int32_t BT_time_ms_t;

extern volatile BT_time_ms_t bootloader_timer;

void BT_setup(void);
void BT_teardown(void);

void BT_timer_start(BT_time_ms_t *timer);
bool BT_timer_expired(BT_time_ms_t *timer, BT_time_ms_t timeout);

#endif // BOOTLOADER_TIMER_H