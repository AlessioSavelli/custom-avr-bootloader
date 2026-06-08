#include <LUFA/Drivers/USB/USB.h>

#include "Descriptors.h"
#include "usb_manager.h"
#include "command_processor.h"
// #include "leds.h"

/** Contains the current baud rate and other settings of the first virtual serial port. This must be retained as some
 *  operating systems will not open the port unless the settings can be set successfully.
 */
static CDC_LineEncoding_t LineEncoding = {.BaudRateBPS = 0,
                                          .CharFormat = CDC_LINEENCODING_OneStopBit,
                                          .ParityType = CDC_PARITY_None,
                                          .DataBits = 8};

/** Event handler for the USB_ConfigurationChanged event. This configures the device's endpoints ready
 *  to relay data to and from the attached USB host.
 */
void EVENT_USB_Device_ConfigurationChanged(void)
{
    /* Setup CDC Notification, Rx and Tx Endpoints */
    Endpoint_ConfigureEndpoint(CDC_NOTIFICATION_EPNUM, EP_TYPE_INTERRUPT,
                               ENDPOINT_DIR_IN, CDC_NOTIFICATION_EPSIZE,
                               ENDPOINT_BANK_SINGLE);

    Endpoint_ConfigureEndpoint(CDC_TX_EPNUM, EP_TYPE_BULK,
                               ENDPOINT_DIR_IN, CDC_TXRX_EPSIZE,
                               ENDPOINT_BANK_SINGLE);

    Endpoint_ConfigureEndpoint(CDC_RX_EPNUM, EP_TYPE_BULK,
                               ENDPOINT_DIR_OUT, CDC_TXRX_EPSIZE,
                               ENDPOINT_BANK_SINGLE);
}

/** Event handler for the USB_ControlRequest event. This is used to catch and process control requests sent to
 *  the device from the USB host before passing along unhandled control requests to the library for processing
 *  internally.
 */
void EVENT_USB_Device_ControlRequest(void)
{
    /* Ignore any requests that aren't directed to the CDC interface */
    if ((USB_ControlRequest.bmRequestType & (CONTROL_REQTYPE_TYPE | CONTROL_REQTYPE_RECIPIENT)) !=
        (REQTYPE_CLASS | REQREC_INTERFACE))
    {
        return;
    }

    /* Process CDC specific control requests */
    switch (USB_ControlRequest.bRequest)
    {
    case CDC_REQ_GetLineEncoding:
        if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE))
        {
            Endpoint_ClearSETUP();

            /* Write the line coding data to the control endpoint */
            Endpoint_Write_Control_Stream_LE(&LineEncoding, sizeof(CDC_LineEncoding_t));
            Endpoint_ClearOUT();
        }

        break;
    case CDC_REQ_SetLineEncoding:
        if (USB_ControlRequest.bmRequestType == (REQDIR_HOSTTODEVICE | REQTYPE_CLASS | REQREC_INTERFACE))
        {
            Endpoint_ClearSETUP();

            /* Read the line coding data in from the host into the global struct */
            Endpoint_Read_Control_Stream_LE(&LineEncoding, sizeof(CDC_LineEncoding_t));
            Endpoint_ClearIN();
        }

        break;
    }
}

/** Retrieves the next byte from the host in the CDC data OUT endpoint, and clears the endpoint bank if needed
 *  to allow reception of the next data packet from the host.
 *
 *  \return Next received byte from the host in the CDC data OUT endpoint
 */
uint8_t USB_FetchNextCommandByte(void)
{
    /* Select the OUT endpoint so that the next data byte can be read */
    Endpoint_SelectEndpoint(CDC_RX_EPNUM);

    /* If OUT endpoint empty, clear it and wait for the next packet from the host */
    while (!(Endpoint_IsReadWriteAllowed()))
    {
        Endpoint_ClearOUT();

        while (!(Endpoint_IsOUTReceived()))
        {
            if (USB_DeviceState == DEVICE_STATE_Unattached)
                return 0;
        }
    }

    // leds(LED_RX, LED_ON);

    /* Fetch the next byte from the OUT endpoint */
    return Endpoint_Read_8();
}

/** Writes the next response byte to the CDC data IN endpoint, and sends the endpoint back if needed to free up the
 *  bank when full ready for the next byte in the packet to the host.
 *
 *  \param[in] Response  Next response byte to send to the host
 */
void USB_WriteNextResponseByte(const uint8_t Response)
{
    /* Select the IN endpoint so that the next data byte can be written */
    Endpoint_SelectEndpoint(CDC_TX_EPNUM);

    /* If IN endpoint full, clear it and wait until ready for the next packet to the host */
    if (!(Endpoint_IsReadWriteAllowed()))
    {
        Endpoint_ClearIN();

        while (!(Endpoint_IsINReady()))
        {
            if (USB_DeviceState == DEVICE_STATE_Unattached)
                return;
        }
    }

    // leds(LED_TX, LED_ON);

    /* Write the next byte to the IN endpoint */
    Endpoint_Write_8(Response);
}

/** Task to read in AVR910 commands from the CDC data OUT endpoint, process them, perform the required actions
 *  and send the appropriate response back to the host.
 */
void CDC_Task(void)
{

    /* Select the OUT endpoint */
    Endpoint_SelectEndpoint(CDC_RX_EPNUM);

    /* Check if endpoint has a command in it sent from the host */
    if (!(Endpoint_IsOUTReceived()))
        return;

    CMDP_main();

    /* Select the IN endpoint */
    Endpoint_SelectEndpoint(CDC_TX_EPNUM);

    /* Remember if the endpoint is completely full before clearing it */
    bool IsEndpointFull = !(Endpoint_IsReadWriteAllowed());

    /* Send the endpoint data to the host */
    Endpoint_ClearIN();

    /* If a full endpoint's worth of data was sent, we need to send an empty packet afterwards to signal end of transfer */
    if (IsEndpointFull)
    {
        while (!(Endpoint_IsINReady()))
        {
            if (USB_DeviceState == DEVICE_STATE_Unattached)
                return;
        }

        Endpoint_ClearIN();
    }

    /* Wait until the data has been sent to the host */
    while (!(Endpoint_IsINReady()))
    {
        if (USB_DeviceState == DEVICE_STATE_Unattached)
            return;
    }

    /* Select the OUT endpoint */
    Endpoint_SelectEndpoint(CDC_RX_EPNUM);

    /* Acknowledge the command from the host */
    Endpoint_ClearOUT();
}

void USB_setup(void)
{
    CMDP_rx_point_set(USB_FetchNextCommandByte);
    CMDP_tx_point_set(USB_WriteNextResponseByte);
    USB_Init();
}

void USB_loop(void)
{
    CDC_Task();
    USB_USBTask();
}

void USB_teardown(void)
{
    USB_Disable();
    // USB_Detach();
}
