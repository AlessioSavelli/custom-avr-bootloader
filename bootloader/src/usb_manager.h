#ifndef USB_MANAGER_H
#define USB_MANAGER_H

#include <stdint.h>

uint8_t USB_FetchNextCommandByte(void);
void USB_WriteNextResponseByte(const uint8_t Response);

void USB_setup(void);
void USB_loop(void);
void USB_teardown(void);

#endif // USB_MANAGER_H