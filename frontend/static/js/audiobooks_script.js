import { socket } from './socket_script.js';

export class AudiobookPage {
    constructor() {
        this.tabs = {
            search: new AudiobookSearchTab(),
            recommendations: new AudiobookRecommendationsTab(),
            readarr: new ReadarrWantedTab(),
        };
    }

    init() {
        this.restoreLastActiveTab();
        this.initTabs();
    }

    initTabs() {
        Object.keys(this.tabs).forEach(tabName => {
            const tabElement = document.getElementById(`pills-audiobooks-${tabName}-tab`);
            if (tabElement) {
                tabElement.addEventListener('shown.bs.tab', () => {
                    this.switchTab(tabName);
                });
            }
        });
    }

    switchTab(tabName) {
        this.activeTab = tabName;
        this.storeActiveTab(tabName);
        this.tabs[tabName].setup();
    }

    storeActiveTab(tabName) {
        localStorage.setItem('lastActiveAudiobookTab', tabName);
    }

    restoreLastActiveTab() {
        const lastTab = localStorage.getItem('lastActiveAudiobookTab') || 'search';
        new bootstrap.Tab(document.getElementById(`pills-audiobooks-${lastTab}-tab`)).show();
        this.switchTab(lastTab);
    }
}

class AudiobookSearchTab {
    constructor() {
        socket.on('audiobook_search_results', (data) => {
            this.changeUI("ready");
            this.showAudiobookSearchResults(data);
        });
    }

    setup() {
        const searchButton = document.getElementById('audiobooks-search-button');
        const searchInput = document.getElementById('audiobooks-search-input');

        searchButton.addEventListener('click', () => this.initiateSearch());
        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                this.initiateSearch();
            }
        });
    }

    initiateSearch() {
        this.changeUI("busy");
        const query = document.getElementById('audiobooks-search-input').value.trim();

        if (query) {
            socket.emit('audiobook_search', query);
        }
        else {
            this.changeUI("ready");
        }
    }

    showAudiobookSearchResults(data) {
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = '';

        if (data && data.results) {
            for (let category in data.results) {
                let items = data.results[category];

                if (Array.isArray(items) && items.length > 0) {
                    items.forEach(item => {
                        this.populateAudiobookTemplate(item);
                    });
                } else {
                    const noResultsMessage = document.createElement('p');
                    noResultsMessage.textContent = 'No results found';
                    resultsSection.appendChild(noResultsMessage);
                }
            }
        }
    }

    populateAudiobookTemplate(data) {
        const template = document.getElementById("spotify-audiobook-item-template");
        const clone = document.importNode(template.content, true);

        clone.querySelector('.audiobook-img').src = data.image || 'https://picsum.photos/300';
        clone.querySelector('.name').textContent = data.name;
        clone.querySelector('.author').textContent = data.author;

        clone.querySelector('.add-to-readarr-btn').addEventListener('click', (event) => {
            const button = event.target;
            button.disabled = true;
            this.addToReadarr(data);
        });
        clone.querySelector('.get-overview-btn').addEventListener('click', () => {
            this.overviewReq(data);
        });
        clone.querySelector('.download').addEventListener('click', (event) => {
            this.handleDownloadClick(event, data);
        });

        let element = document.getElementById('results-section');
        element.appendChild(clone);
    }

    changeUI(state) {
        ['audiobooks-search-button', 'audiobooks-search-input'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.disabled = state === "busy";
        });

        const spinner = document.getElementById('audiobooks-spinner-border');
        if (spinner) spinner.style.display = state === "busy" ? 'inline-block' : 'none';
    }

    overviewReq(audiobook) {
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        document.body.style.overflow = 'hidden';
        document.body.style.paddingRight = `${scrollbarWidth}px`;

        var modalTitle = document.getElementById('overview-modal-title');
        var modalBody = document.getElementById('modal-body');
        modalTitle.textContent = audiobook.name;
        modalBody.innerHTML = DOMPurify.sanitize(audiobook.overview || "No overview available.");

        var modal = new bootstrap.Modal(document.getElementById('overview-modal'));
        modal.show();

        modal._element.addEventListener('hidden.bs.modal', function () {
            document.body.style.overflow = 'auto';
            document.body.style.paddingRight = '0';
        });
    }

    addToReadarr(data) {
        console.log(data);
    }

    handleDownloadClick(event, data) {
        event.preventDefault();
        const button = event.target;
        button.disabled = true;
        button.classList.remove('btn-primary');
        button.classList.add('btn-secondary');
        button.classList.add('disabled');
        button.innerText = 'Downloaded';
        console.log(data);
    }
}

class AudiobookRecommendationsTab {
    setup() { }
}
class ReadarrWantedTab {
    setup() { }
}