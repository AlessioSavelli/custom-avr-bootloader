#include <stdint.h>
#include <stddef.h>

#include "Password.h"

static void xor_cypher(uint8_t *data, size_t data_len, const uint8_t *key, size_t key_len)
{
    for (size_t i = 0; i < data_len; i++)
    {
        data[i] ^= key[i % key_len];
    }
}

static const size_t PASSWORD_SIZE = sizeof(PASSWORD);

void CRI_encrypt(uint8_t *data, size_t data_len)
{
    xor_cypher(data, data_len, PASSWORD, PASSWORD_SIZE);
}

void CRI_decrypt(uint8_t *data, size_t data_len)
{
    xor_cypher(data, data_len, PASSWORD, PASSWORD_SIZE);
}
