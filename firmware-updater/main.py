import sys
from resource_path import resource_path
sys.path.append(resource_path('lib'))

import webview
import serial.tools.list_ports

import math

import bootloader_handler_lite as bhl

class Api:

    def load_file(self):
        window = webview.windows[0]
        file_paths = window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=('All files (*.*)', 'Text files (*.txt)')
        )
        file = file_paths[0]
        return file

    def update_ports(self):
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append({
                "port": p.device,
                "id": p.hwid,
                "description": p.description
            })
        return ports
    
    def start_update(self, port, file):
        payloads = bhl.unpack_fw_file(file)
        bhl.setup(port)
        count: int = 0

        self.backend_event('status LOADING')

        # write all memory pages
        for i, payload in enumerate(payloads):
            count += 1
            bhl.send(
                bhl.Request(
                    identifier=count,
                    command=bhl.Command.WRITE_MEMORY_PAGE,
                    payload_length=len(payload),
                    payload=payload,
                )
            )
            bhl.receive().simple_check()

            # keep alive occasionally
            if count % 10 == 0:
                count += 1
                bhl.send(
                    bhl.Request(
                        identifier=count,
                        command=bhl.Command.KEEP_ALIVE,
                        payload_length=0,
                        payload=[],
                    )
                )
                bhl.receive().simple_check()
            
            percentage = 100 * i / len(payloads)
            self.backend_event(f'progress {percentage}')
        
        self.backend_event(f'progress 100')

        # enable application
        count += 1
        bhl.send(
            bhl.Request(
                identifier=count,
                command=bhl.Command.APPLICATION_ENABLE,
                payload_length=0,
                payload=[],
            )
        )
        bhl.receive().simple_check()

        count += 1
        bhl.send(
            bhl.Request(
                identifier=count,
                command=bhl.Command.START_SKETCH,
                payload_length=0,
                payload=[],
            )
        )
        bhl.receive().simple_check()

        self.backend_event(f'progress 100')
        self.backend_event('status SUCCESS')
        self.backend_event(f'end')

        bhl.teardown()
        return "ok"

    def start_application(self, port):
        bhl.setup(port)
        bhl.send(
            bhl.Request(
                identifier=0,
                command=bhl.Command.START_SKETCH,
                payload_length=0,
                payload=[],
            )
        )
        bhl.teardown()
        return "ok"

    def request_bootloader(self, port):
        bhl.setup(port)
        bhl.request_reset()
        bhl.teardown()
        return "ok"
    
    def backend_event(self, message):
        window = webview.windows[0]
        window.evaluate_js(f"onBackendEvent('{message}')")



if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        "Device Management",
        resource_path("gui/index.html"),
        js_api=api,
        )
    window.events.loaded += lambda: api.backend_event('start')
    webview.start(
        # debug=True
        )

