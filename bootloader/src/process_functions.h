#ifndef PROCESS_FUNCTIONS_H
#define PROCESS_FUNCTIONS_H

#include "command_processor.h"

typedef CP_status_t process_function_t(message_s *message);

CP_status_t PF_bootloader_version(message_s *message);
CP_status_t PF_keep_alive(message_s *message);
CP_status_t PF_application_enable(message_s *message);
CP_status_t PF_write_memory_page(message_s *message);
CP_status_t PF_start_sketch(message_s *message);

#endif // PROCESS_FUNCTIONS_H