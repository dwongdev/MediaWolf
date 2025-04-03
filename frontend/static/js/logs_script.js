import { socket } from './socket_script.js';

export class LogsPage {
    constructor() {
        socket.on("refreshed_logs", (logs) => {
            let refreshButton = document.getElementById('refreshLogs');
            const logContent = document.getElementById('logContent');
            logContent.innerText = logs;
            refreshButton.disabled = false;
            logContent.scrollTop = logContent.scrollHeight;
            window.scrollTo(0, document.body.scrollHeight);
        });
    }

    init() {
        let refreshButton = document.getElementById('refreshLogs');
        refreshButton.addEventListener('click', () => this.fetchLogs(refreshButton));
        window.scrollTo(0, document.body.scrollHeight);
    }

    fetchLogs(refreshButton) {
        refreshButton.disabled = true;
        socket.emit("refresh_logs");
    }
}

