# Analisi memoria del bootloader (ATmega32U4)

> Documento di analisi preliminare. Misure ottenute compilando con la toolchain
> locale (`avr-gcc 7.3.0`) il target `Caterina` così com'è nel repo.

## 1. Vincolo hardware (il muro da rispettare)

- **MCU:** ATmega32U4 — 32 KB di Flash totali, 2,5 KB di SRAM.
- **Sezione bootloader:** `BOOT_SECTION_SIZE_KB = 4` → start a `0x7000`.
  - **4096 byte è il massimo assoluto** della boot section sul 32U4
    (fuse BOOTSZ, 2048 word). **Non si può allargare.** O si sta dentro 4 KB, o niente.

## 2. Occupazione attuale (baseline)

```
Program:  4076 byte  (su 4096 disponibili → 99,5%)   <-- 20 byte liberi
Data:      308 byte  (su 2560 → 12%)                  <-- RAM tranquilla
```

**Il collo di bottiglia è il FLASH, non la RAM.** Servono ~20 byte liberi: per
reintegrare i LED e/o irrobustire la cifratura bisogna **prima liberare spazio**.

## 3. Dove va il Flash (simboli realmente linkati nell'ELF)

| Byte | Simbolo | Origine | Note |
|-----:|---------|---------|------|
| 592 | `CMDP_main` | command_processor.c | include inline `receive/execute/give_response` |
| 502 | `USB_Device_ProcessControlRequest` | LUFA core | enumerazione USB standard |
| 354 | `__vector_10` (USB_GEN) | LUFA core | gestione eventi/reset USB |
| 208 | `PF_write_memory_page` | process_functions.c | scrittura pagina Flash (necessaria) |
| 178 | `Endpoint_Write_Control_Stream_LE` | LUFA core | usata da GetLineEncoding |
| 134 | `crc8` | command_processor.c | CRC bitwise |
| 128 | `PASSWORD` | Password.h | **chiave XOR di 128 byte in .data** |
| 118 | `USB_ResetInterface` | LUFA core | |
| 114 | `main` | Caterina.c | |
| 114 | `Endpoint_Read_Control_Stream_LE` | LUFA core | usata da SetLineEncoding |
| 100 | `CDC_Task` | usb_manager.c | |
| 100 | `CALLBACK_USB_GetDescriptor` | Descriptors.c | |
|  ~92 | `EVENT_USB_Device_ControlRequest` | usb_manager.c | Get/SetLineEncoding |

> Lo "stack" USB di LUFA (CDC seriale) pesa complessivamente **~1,5 KB** ed è la
> parte che "si mangia la memoria", come da intuizione. L'`HIDParser` (2 KB nei
> `.o`) e gran parte di `EndpointStream` vengono già scartati da `--gc-sections`.

## 4. Opportunità di riduzione (stima, dalla più sicura alla più invasiva)

| # | Intervento | Risparmio stimato | Rischio |
|---|------------|------------------:|---------|
| A | **Chiave XOR 128→16 byte** (o keystream calcolato) | ~110 B Flash + ~110 B RAM | Nullo (con allineamento lato PC) |
| B | **Flag build**: `-mcall-prologues`, valutare `-flto` | 150–400 B | Basso/Medio (LTO da testare con ISR/asm) |
| C | **Snellire le control-request CDC**: GetLineEncoding fittizio / SetLineEncoding senza stream | ~250–300 B | Medio (va testato che l'OS apra ancora la porta) |
| D | **Refactor `CMDP_main`**: ridurre rami, NULL-check ridondanti, blocco "application detected" | 50–150 B | Basso |
| E | **Stringhe descrittori** più corte / Manufacturer rimosso | 30–60 B | Basso (cambia il nome mostrato) |
| F | **CRC8**: mantenere bitwise (la tabella costerebbe 256 B → da NON fare) | — | — |

Sommando A+B+D in modo conservativo si liberano **plausibilmente 300–600 byte**:
spazio sufficiente per **reintegrare i LED** e per una **cifratura più robusta**.

### 4.1 Risultati MISURATI (build con toolchain locale)

| Tentativo | Program | Liberi su 4096 | Esito |
|-----------|--------:|---------------:|-------|
| Baseline | 4076 B | 20 B | punto di partenza |
| `-mcall-prologues` | overflow +16 B | — | **peggiora** su codice piccolo → scartato |
| Micro-refactor C (NULL-check, `feedback_bit`) | 4076 B | 20 B | **0 byte** (gia' ottimizzato da `-Os`) |
| **`-flto` (LTO)** | **3944 B** | **152 B** | **-132 byte**, build pulita |

**Conclusione del passo conservativo:** gli interventi "gratis" non esistono.
L'unica leva a basso costo che funziona è **LTO** (152 B liberi), ma è una
trasformazione link-time aggressiva → **va validata sull'hardware** (c'è inline
asm per lo spostamento del vettore interrupt e ci sono ISR).
Le altre due leve vere restano: **chiave 128→16 B** (~112 B, legata alla nuova
crypto) e **snellimento control-request CDC** (~250 B, richiede test USB).

### 4.2 Risultato FINALE (Speck32/64-CTR robusto, senza LED)

Decisione presa: niente LED, cifrario robusto **Speck 32/64-CTR**, recupero byte
con ottimizzazioni C validabili (no asm, no modifiche USB).

| Passo | Program | Note |
|-------|--------:|------|
| Baseline (XOR debole) | 4076 B | 20 liberi |
| + LTO | 3944 B | 152 liberi |
| + Speck32/64-CTR (chiave 128→8 B) | overflow +198 | cifrario = 488 B |
| + rotazioni via byte-swap | overflow +198 | nessun effetto (gia' ottimizzate) |
| + key schedule "al volo" (no `rk[22]`) | overflow +158 | cifrario 488→444 B |
| + shift-register al posto di `l[i%3]` | overflow +144 | cifrario 444→408 B |
| **+ timer 32→16 bit** | **4088 B** | **8 liberi, BUILD OK** |

**Esito:** dove prima entrava a malapena un XOR debolissimo, ora entra un vero
cifrario a blocchi (Speck), restando nei 4 KB. Margine risicato (8 B): per più
respiro restano opzioni a basso rischio (stringhe descrittori ~40–60 B) o, con
cautela, riscrittura in **assembly** del cifrario (alto guadagno ma non validabile
in esecuzione senza hardware/simulatore).

> Tutte le misure: build con LTO attivo. **LTO e timer 16-bit vanno validati
> sull'hardware** (timing e enumerazione USB invariati nelle attese, ma da provare).

## 5. Reintegrazione LED

- `leds.c`/`leds.h` esistono già, ma sono **esclusi dalla build** (commentati nel
  Makefile) e tutte le chiamate `leds(...)` sono commentate in `usb_manager.c` e
  `Caterina.c`.
- Mappatura LED già definita: TX=PD5, RX=PB0, LED1=PE6, LED2=PB5
  (compatibile Leonardo/Micro).
- Costo stimato a reintegrarli: il modulo `leds` + chiamate ~ **100–200 B Flash**.
  Fattibile **solo dopo** aver liberato spazio (sez. 4).
- Uso minimo sensato: RX lampeggia in ricezione, TX in trasmissione, LED1 "alive"
  durante il timeout bootloader, LED2 errore. Si può tarare per costare poco.

## 6. Cifratura: stato e opzioni

### Stato attuale (debole)
- XOR a chiave ripetuta (Vigenère) con chiave = `0x00,0x01,...,0x7F`.
- Debolezze: chiave **non segreta di fatto** (pattern banale), `key[0]=0x00`
  lascia il primo byte in chiaro, nessuna diffusione, nessuna autenticità
  (il CRC8 non è crittografico). Identici plaintext → identici ciphertext.

### Opzioni proposte
1. **Keystream "a chiavi circolari" (rolling)** — XOR con keystream generato da un
   PRNG leggero (es. xorshift) inizializzato con **chiave segreta + nonce di pagina
   (indirizzo)**. Costo ~80–150 B. Robustezza: molto meglio dell'attuale, ma non
   forte contro attaccante esperto.
2. **Cifrario leggero (Speck 64/128 o XTEA) in modo CTR** — robustezza
   crittografica reale; in CTR serve solo la direzione "encrypt" del cifrario per
   cifrare e decifrare. Costo ~200–350 B. Richiede prima di liberare spazio.
3. **XOR ma con chiave segreta vera e più corta** — minimo sforzo, libera Flash,
   ma resta un XOR a chiave ripetuta (debole). Solo "meno imbarazzante".

> Nota di sicurezza: per un *update sicuro* vero servirebbe **autenticità**
> (firma o MAC), non solo riservatezza. È fuori dallo scope immediato ma va
> segnalato: oggi chiunque conosca/indovini lo schema può caricare firmware.

### Vincolo di simmetria PC↔MCU
Qualunque scelta va replicata in **`toolchain/bootloader_handler.py`**
(`encrypt`/`decrypt`/`xor_cypher`), che oggi legge la chiave direttamente da
`Password.h`.

## 7. Come si verifica

- **Flash:** `make clean && make all` → riga `Program: NNNN bytes`. Deve restare
  `< 4096` con margine.
- **Funzionale (richiede la board fisica):** enumerazione USB OK, la porta si apre
  dall'updater, un ciclo di scrittura pagina + rilettura coincide, l'app parte a
  fine timeout. Questi test li deve eseguire l'utente sull'hardware.
