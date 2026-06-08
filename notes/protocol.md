REQUEST

1 start = 0x55
1 identifier
1 command
1 payload_length = N
N payload
1 crc (identifier, command, payload length, payload)



RESPONSE

1 start = 0x55
1 identifier
1 status
1 payload_length = N
N payload
1 crc (identifier, command, payload length, payload)
