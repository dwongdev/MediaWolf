import { socket } from './socket_script.js';

export class SettingsPage {
    init() {
        document.getElementById("save-settings-button").addEventListener("click", (event) => {
            event.preventDefault();
            this.saveSettings();
        });
    }
    saveSettings() {
        let formData = {};
        document.querySelectorAll("#settings-form input").forEach(input => {
            if (input.type === "number") {
                formData[input.id] = parseFloat(input.value);
            } else {
                formData[input.id] = input.value;
            }
        });
        socket.emit("save_settings", formData);
    }
}


