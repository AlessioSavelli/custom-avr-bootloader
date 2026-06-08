
// -----------------------------------------------------------------------------
// Periodic Events
// -----------------------------------------------------------------------------

async function updatePorts() {
    let ports = []
    try {
        ports = await window.pywebview.api.update_ports();
    } catch (err) {
        ports = []
    }
    ports.unshift({
        port: '',
        id: '',
        description: 'Select a port',
    })

    const select = document.getElementById('select-port');
    let select_is_up_to_date = (ports.length == select.options.length);
    for (opt of select.options) {
        let found = false;
        for (p of ports) {
            if (p.port == opt.value) {
                found = true;
                break;
            }
        }
        if (!found) {
            select_is_up_to_date = false;
            break;
        }
    }

    if (!select_is_up_to_date) {
        select.innerHTML = '';
        for (p of ports) {
            const opt = document.createElement('option');
            opt.value = p.port;
            opt.textContent = renderPort(p);
            select.appendChild(opt);
        }
    }

}

function renderPort(p) {
    /**
     * Example:
     * p = {
     *   port: 'COM8',
     *   description: 'USB-SERIAL CH340 (COM8)',
     *   id: 'USB VID:PID=1A86:7523 SER=123456 LOCATION=1-3.2:x.0'
     * }
     * Output: "COM8 - USB-SERIAL CH340 (123456)"
     */

    // get the main description
    const descMatch = p.description.match(/^(.*?)\s*\(.*\)$/);
    const shortDesc = descMatch ? descMatch[1] : p.description;

    // extract the serial number from the id
    const serMatch = p.id.match(/SER=([^\s]+)/i);
    const serial = serMatch ? serMatch[1] : "";

    return `${p.port} - ${shortDesc} (${serial})`;
}



// -----------------------------------------------------------------------------
// Frontend Events
// -----------------------------------------------------------------------------

async function loadFile() {
    const path = await window.pywebview.api.load_file();
    const handle = document.getElementById("text-file-path");
    if (handle) {
        if (path) {
            handle.innerText = path;
            showSection('step-select-port');
        } else {
            handle.innerText = "No file selected";
        }
    }
}

async function portSelected() {
    const port = document.getElementById('select-port').value;
    if ('' != port) {
        enableButton('button-start');
    }
}

async function startUpdate() {
    const port = document.getElementById('select-port').value;
    const file = document.getElementById('text-file-path').innerText;
    if (!port) {
        alert('Select a COM port before continuing');
        return;
    }
    if (!file) {
        alert('Select a file before continuing');
        return;
    }
    showSection('step-progress')
    await window.pywebview.api.start_update(port, file);
}

async function restart() {
    showSection('step-load-file');
    resetFilePath();

    resetPortSelection();
    disableButton('button-start');

    updateProgress(['0']);
    updateStatus(['']);
    disableButton('button-restart');
}

// -----------------------------------------------------------------------------
// Backend Events
// -----------------------------------------------------------------------------

const handlers = {
    start: startLogic,
    progress: updateProgress,
    status: updateStatus,
    end: completeUpdate,
};

function onBackendEvent(message) {
    const [cmd, ...args] = message.split(" ");
    const handler = handlers[cmd];
    if (handler) {
        handler(args);
    }
}

async function startLogic(args) {
    await updatePorts();
    restart();
    setInterval(updatePorts, 1000);
}

function updateProgress(args) {
    const progress_bar = document.getElementById('progress-bar');
    const progress_value = document.getElementById('progress-value');

    let percentage = args[0];
    percentage = Number(percentage);
    progress_bar.value = percentage;

    percentage = Math.floor(percentage * 10) / 10;
    progress_value.innerText = `${percentage}`;
}

function updateStatus(args) {
    const status_message = document.getElementById('status-message');
    status_message.innerText = args.join(' ');
}

function completeUpdate(args) {
    enableButton('button-restart');
}

// -----------------------------------------------------------------------------
// GUI basic functions
// -----------------------------------------------------------------------------

function showSection(sectionId) {
    const sections = document.getElementsByClassName('section');
    for (const section of sections) {
        section.hidden = true
        if (sectionId == section.id) {
            section.hidden = false
        }
    }
}

function enableButton(buttonId) {
    const button = document.getElementById(buttonId);
    button.disabled = false
}

function disableButton(buttonId) {
    const button = document.getElementById(buttonId);
    button.disabled = true
}

function resetFilePath() {
    const text = document.getElementById('text-file-path');
    text.innerText = 'No file selected'
}

function resetPortSelection() {
    const select = document.getElementById('select-port');
    select.selectedIndex = 0;
}
