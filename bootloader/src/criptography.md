# Modulo `criptography` — Speck 32/64 in modalità CTR

## Scopo
Cifrare/decifrare i dati di pagina scambiati tra toolchain (PC) e bootloader.
Sostituisce il precedente **XOR a chiave ripetuta** (debole) con un vero cifrario
a blocchi leggero, mantenendo l'occupazione di flash compatibile con la boot
section da 4 KB dell'ATmega32U4.

## File coinvolti
- `criptography.h` / `criptography.c` — implementazione C (bootloader).
- `Password.h` — chiave segreta `SPECK_KEY[4]` (64 bit), **condivisa** col PC.
- `toolchain/bootloader_handler.py` — gemello Python (funzioni `encrypt`/`decrypt`).
- `process_functions.c` — unico chiamante lato firmware (`PF_write_memory_page`).

## Cifrario
- **Speck 32/64**: blocco 32 bit (due parole da 16 bit), chiave 64 bit (quattro
  parole da 16 bit), **22 round**, rotazioni `alpha=7`, `beta=2`.
- Scelto perché lavora su parole da **16 bit** → su AVR8 genera molto meno codice
  delle varianti a 32/64 bit, pur restando un cifrario reale.

## Modalità CTR
Si cifra un "blocco contatore" e lo si mette in **XOR** con i dati:
- blocco contatore = `(x = nonce, y = contatore_di_blocco)`;
- **cifrare e decifrare sono la stessa operazione** → un'unica `CRI_crypt()`.

### Nonce = indirizzo di pagina
Il nonce è l'**indirizzo della pagina flash**:
- diverso per ogni pagina → keystream diverso tra pagine (sparisce la debolezza
  "pagine uguali → cifrato uguale" dell'XOR);
- il contatore di blocco varia entro la pagina → nessun riuso di keystream;
- il nonce è **pubblico** per definizione del CTR: per questo l'indirizzo viaggia
  **in chiaro** (vedi sotto).

## Funzioni principali (`criptography.c`)
- `rotr16_7(x)` / `rotl16_2(x)`: rotazioni specializzate per le costanti di Speck,
  scritte per generare poco codice su AVR (`rotr 7 = rotl1(swap_byte(x))`).
- `speck_keystream_block(out_x, out_y, nonce, counter)`: genera un blocco di
  keystream. Il **key schedule è calcolato "al volo"** dentro lo stesso loop di
  cifratura (niente array `rk[22]`, niente secondo loop) e usa uno **shift-register
  di 3 parole** al posto di `l[i % 3]` (il modulo su AVR è costoso).
- `CRI_crypt(data, len, nonce)`: applica il keystream a `data[0..len)` in-place.
  Ordine byte del keystream: `x_hi, x_lo, y_hi, y_lo` (deve combaciare col Python).

## Protocollo: cosa è cambiato
**Prima:** l'intero payload `[addr_hi, addr_lo, *dati(128)]` era cifrato in XOR.
**Ora:** l'indirizzo (primi 2 byte) viaggia **in chiaro** (fa da nonce) e si cifra
solo il blocco dati da 128 byte. La lunghezza on-wire resta invariata (130 byte).

Lato Python la convenzione è incapsulata in `encrypt`/`decrypt`:
- payload ≤ 2 byte (es. eco indirizzo nelle risposte): **passthrough** (non cifrato);
- payload > 2 byte: primi 2 byte in chiaro, CTR sul resto con `nonce = (b0<<8)|b1`.

Grazie a questa convenzione **`operations.py` non è stato toccato** (il round-trip
`decrypt(packet)` → `encrypt(payload)` continua a produrre gli stessi byte on-wire).

## Chiave (`Password.h`)
- `SPECK_KEY[4]` = `{ k0, l0, l1, l2 }` (ordine atteso dal key schedule Speck).
- Riletta dal PC con `read_numbers_from_h_file` → i due lati restano allineati.
- **È un segreto:** va sostituita con valori casuali propri e non pubblicata.

## Verifica (fatta)
Cross-validazione automatica (host gcc + Python):
1. **Test vector ufficiale Speck32/64** — key `1918 1110 0908 0100`, pt `6574 694c`
   → ct `a868 42f2`: ✅ confermato dal Python.
2. **C ↔ Python byte-per-byte** su keystream/ciphertext con la chiave reale: ✅
   identici (`5aa2e744…541c`).
3. **Round-trip** `decrypt(encrypt(x)) == x`, con indirizzo in chiaro e dati cifrati: ✅.

## Vincoli / note
- **Compatibilità:** il formato cambia. Vanno aggiornati **insieme** bootloader e
  toolchain, e va **ri-generato `application.fw`** (i vecchi file non sono compatibili).
- **Robustezza:** Speck garantisce riservatezza; NON garantisce autenticità. Per un
  update "sicuro" servirebbe una firma/MAC (fuori scope attuale).
- Il file non dipende dall'hardware AVR: si compila anche su PC per i test.
