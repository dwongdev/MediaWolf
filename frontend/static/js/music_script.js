import { socket } from './socket_script.js';

export class MusicPage {
    constructor() {
        this.tabs = {
            search: new MusicSearchTab(),
            recommendations: new MusicRecommendationsTab(),
            lidarr: new LidarrWantedTab(),
        };
    }

    init() {
        this.initTabs();
        this.restoreLastActiveTab();
    }

    initTabs() {
        Object.keys(this.tabs).forEach(tabName => {
            const tabElement = document.getElementById(`pills-music-${tabName}-tab`);
            if (tabElement) {
                tabElement.addEventListener('shown.bs.tab', () => {
                    this.tabs[tabName].setup();
                    this.storeActiveTab(tabElement.id);
                });
            }
        });
    }

    storeActiveTab(tabId) {
        localStorage.setItem('lastActiveMusicTab', tabId);
    }

    restoreLastActiveTab() {
        const lastTab = localStorage.getItem('lastActiveMusicTab');
        let activeTabName = 'search';

        if (lastTab && document.getElementById(lastTab)) {
            activeTabName = lastTab.replace('pills-music-', '').replace('-tab', '');
            new bootstrap.Tab(document.getElementById(lastTab)).show();
        }

        if (this.tabs[activeTabName] && typeof this.tabs[activeTabName].setup === 'function') {
            this.tabs[activeTabName].setup();
        }
    }
}


class MusicSearchTab {
    constructor() {
        this.selectedType = "track";

        socket.on('spotify_search_results', (data) => {
            this.changeUI("ready");
            this.showSpotifySearchResults(data);
        });
    }

    setup() {
        const searchButton = document.getElementById('music-search-button');
        const searchInput = document.getElementById('music-search-input');

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
        const query = document.getElementById('music-search-input').value.trim();

        if (query) {
            socket.emit('search_spotify', { query, type: this.selectedType });
        }
    }

    showSpotifySearchResults(data) {
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = '';

        if (data && data.results) {
            for (let category in data.results) {
                let items = data.results[category];

                if (Array.isArray(items) && items.length > 0) {
                    items.forEach(item => {
                        this.populateSpotifyTemplate(item.type, item);
                    });
                } else {
                    const noResultsMessage = document.createElement('p');
                    noResultsMessage.textContent = 'No results found';
                    resultsSection.appendChild(noResultsMessage);
                }
            }
        }
    }

    populateSpotifyTemplate(type, data) {
        let templateId;
        let element;

        if (type === 'track') {
            templateId = 'spotify-track-item-template';
        } else if (type === 'album') {
            templateId = 'spotify-album-item-template';
        } else if (type === 'artist') {
            templateId = 'spotify-artist-item-template';
        } else if (type === 'playlist') {
            templateId = 'spotify-playlist-item-template';
        }

        const template = document.getElementById(templateId);
        const clone = document.importNode(template.content, true);

        const downloadButton = clone.querySelector('.download');

        if (type === 'track') {
            clone.querySelector('.track-img').src = data.image || 'https://picsum.photos/300';
            clone.querySelector('.name').textContent = data.name;
            clone.querySelector('.artist').textContent = data.artist;
            clone.querySelector('.download').href = data.url;
            clone.querySelector('.download').setAttribute('data-url', data.url);
        } else if (type === 'album') {
            clone.querySelector('.album-img').src = data.image || 'https://picsum.photos/300';
            clone.querySelector('.name').textContent = data.name;
            clone.querySelector('.artist').textContent = data.artist;
            clone.querySelector('.download').href = data.url;
            clone.querySelector('.download').setAttribute('data-url', data.url);
        } else if (type === 'artist') {
            clone.querySelector('.artist-img').src = data.image || 'https://picsum.photos/300';
            clone.querySelector('.name').textContent = data.name;
            clone.querySelector('.followers').textContent = `${data.followers} Followers`;
            clone.querySelector('.download').href = data.url;
            clone.querySelector('.download').setAttribute('data-url', data.url);
        } else if (type === 'playlist') {
            clone.querySelector('.playlist-img').src = data.image || 'https://picsum.photos/300';
            clone.querySelector('.name').textContent = data.name;
            clone.querySelector('.owner').textContent = data.owner;
            clone.querySelector('.download').href = data.url;
            clone.querySelector('.download').setAttribute('data-url', data.url);
        }

        element = document.getElementById('results-section');
        element.appendChild(clone);

        downloadButton.addEventListener('click', (event) => {
            event.preventDefault();
            this.handleDownloadClick(event);
        });
    }

    changeUI(state) {
        ['music-search-button', 'music-search-input', 'music-search-dropdown'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.disabled = state === "busy";
        });

        const spinner = document.getElementById('music-spinner-border');
        if (spinner) spinner.style.display = state === "busy" ? 'inline-block' : 'none';
    }

    updateSearchType(option) {
        this.selectedType = option.toLowerCase();
        document.getElementById("music-search-button").innerText = `Search for ${option}`;
    }

    handleDownloadClick(event) {
        const button = event.target;

        button.disabled = true;
        button.classList.remove('btn-primary');
        button.classList.add('btn-secondary');
        button.classList.add('disabled');
        button.innerText = 'Added';

        const trackUrl = button.getAttribute('data-url');
        const card = button.closest('.card');

        if (!trackUrl) {
            alert('No URL found!');
            return;
        }

        const itemData = {
            type: card.querySelector('.type')?.textContent.trim().toLowerCase(),
            name: card.querySelector('.name')?.textContent.trim(),
            artist: card.querySelector('.artist')?.textContent.trim() || null,
            url: trackUrl
        };

        socket.emit('spotify_download_item', itemData);
    }
}


class MusicRecommendationsTab {
    constructor() {
        socket.on('music_recommendations', (data) => {
            const artistRow = document.getElementById('artist-row');
            artistRow.innerHTML = "";
            this.appendArtists(data.data);
        });
    }

    setup() {
        socket.emit("load_music_recommendations");
        document.getElementById('get-recommendations-button').addEventListener('click', () => this.getRecommendations());

        setTimeout(() => {
            ["min-listeners", "min-play-count"].forEach(id => {
                let element = document.getElementById(id);
                if (element) {
                    element.addEventListener("input", (event) => {
                        this.updateStep(event.target);
                    });
                }
            });
        }, 500);
    }

    addToLidarr(artistName) {
        if (socket.connected) {
            socket.emit('add_artist_to_lidarr', encodeURIComponent(artistName));
        }
        else {
            showToast("Connection Lost", "Please reload to continue.");
        }
    }

    appendArtists(artists) {
        var artistRow = document.getElementById('artist-row');
        var template = document.getElementById('artist-template');

        artists.forEach((artist) => {
            var clone = document.importNode(template.content, true);
            var artistCol = clone.querySelector('#artist-column');

            artistCol.querySelector('.card-title').textContent = artist.name;
            artistCol.querySelector('.genre').textContent = artist.genre;
            artistCol.querySelector('.card-img-top').src = artist.image;
            artistCol.querySelector('.card-img-top').alt = artist.name;
            artistCol.querySelector('.add-to-lidarr-btn').addEventListener('click', () => {
                this.addToLidarr(artist.name);
            });
            artistCol.querySelector('.get-overview-btn').addEventListener('click', () => {
                this.overviewReq(artist);
            });
            artistCol.querySelector('.dismiss-artist-btn').addEventListener('click', (event) => {
                this.dismissArtist(event, artist);
            });
            artistCol.querySelector('.listeners').textContent = artist.listeners;
            artistCol.querySelector('.play-count').textContent = artist.play_count;

            var addButton = artistCol.querySelector('.add-to-lidarr-btn');
            if (artist.status === "Added" || artist.status === "Already in Lidarr") {
                artistCol.querySelector('.card-body').classList.add('status-green');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-secondary');
                addButton.disabled = true;
                addButton.textContent = artist.status;
            } else if (artist.status === "Failed to Add" || artist.status === "Invalid Path") {
                artistCol.querySelector('.card-body').classList.add('status-red');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-danger');
                addButton.disabled = true;
                addButton.textContent = artist.status;
            } else {
                artistCol.querySelector('.card-body').classList.add('status-blue');
            }
            artistRow.appendChild(clone);
        });
    }

    getRecommendations() {
        const data = {
            selected_artist: document.getElementById("artist-select").value || "all",
            sort_by: document.getElementById("sort-select").value || "random",
            min_play_count: parseInt(document.getElementById("min-play-count").value) || null,
            min_listeners: parseInt(document.getElementById("min-listeners").value) || null,
            num_results: 10,
        };

        socket.emit("refresh_music_recommendations", data);
    }

    dismissArtist(event, artist) {
        if (socket.connected) {
            socket.emit('dismiss_artist', encodeURIComponent(artist.name));
            const artistColumn = event.currentTarget.closest('#artist-column');

            if (artistColumn) {
                artistColumn.style.transition = 'opacity 1.5s';
                artistColumn.style.opacity = '0';

                setTimeout(() => artistColumn.remove(), 1500);
            }
        }
        else {
            showToast("Connection Lost", "Please reload to continue.");
        }
    }

    updateStep(input) {
        let value = parseInt(input.value);
        input.step = value >= 10_000_000 ? 1_000_000 :
            value >= 1_000_000 ? 100_000 :
                value >= 100_000 ? 10_000 : 1_000;
    }

    overviewReq(artist) {
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        document.body.style.overflow = 'hidden';
        document.body.style.paddingRight = `${scrollbarWidth}px`;

        var modalTitle = document.getElementById('bio-modal-title');
        var modalBody = document.getElementById('modal-body');
        modalTitle.textContent = artist.name;
        modalBody.innerHTML = DOMPurify.sanitize(artist.overview || "No overview available.");


        var modal = new bootstrap.Modal(document.getElementById('bio-modal'));
        modal.show();

        modal._element.addEventListener('hidden.bs.modal', function () {
            document.body.style.overflow = 'auto';
            document.body.style.paddingRight = '0';
        });
    }
}

class LidarrWantedTab {
    constructor() {
        socket.on("lidarr_update", (response) => this.lidarrUpdate(response));
    }

    setup() {
        this.lidarrSpinner = document.getElementById('lidarr-spinner');
        this.lidarrTable = document.getElementById('lidarr-table').getElementsByTagName('tbody')[0];
        this.lidarrGetWantedButton = document.getElementById('get-lidarr-wanted-btn');
        this.selectAllCheckbox = document.getElementById("select-all-checkbox");

        this.lidarrGetWantedButton.replaceWith(this.lidarrGetWantedButton.cloneNode(true));
        this.selectAllCheckbox.replaceWith(this.selectAllCheckbox.cloneNode(true));

        this.lidarrGetWantedButton = document.getElementById('get-lidarr-wanted-btn');
        this.selectAllCheckbox = document.getElementById("select-all-checkbox");

        this.selectAllCheckbox.addEventListener("change", (e) => {
            const isChecked = e.target.checked;
            document.querySelectorAll('input[name="lidarr_item"]').forEach(checkbox => {
                checkbox.checked = isChecked;
            });
        });

        this.lidarrGetWantedButton.addEventListener('click', () => {
            this.lidarrGetWantedButton.disabled = true;
            this.lidarrSpinner.classList.remove('d-none');
            this.lidarrTable.innerHTML = '';
            socket.emit("lidarr_get_wanted");
        });
    }

    lidarrUpdate(response) {
        this.lidarrTable.innerHTML = '';
        let allChecked = true;

        if (response.status === "busy") {
            this.lidarrGetWantedButton.disabled = true;
            this.lidarrSpinner.classList.remove('d-none');
        } else {
            this.lidarrGetWantedButton.disabled = false;
            this.lidarrSpinner.classList.add('d-none');
        }

        this.selectAllCheckbox.style.display = "block";
        this.selectAllCheckbox.checked = false;

        response.data.forEach((item, i) => {
            if (!item.checked) allChecked = false;

            const row = this.lidarrTable.insertRow();
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.className = "form-check-input";
            checkbox.id = `lidarr_${i}`;
            checkbox.name = "lidarr_item";
            checkbox.checked = item.checked;
            checkbox.addEventListener("change", () => this.checkIfAllTrue());

            const label = document.createElement("label");
            label.className = "form-check-label";
            label.htmlFor = `lidarr_${i}`;
            label.textContent = `${item.artist} - ${item.album_name}`;

            row.insertCell(0).appendChild(checkbox);
            row.insertCell(1).appendChild(label);
            row.insertCell(2).textContent = `${item.missing_count}/${item.track_count}`;
            row.cells[2].classList.add("text-center");
        });

        this.selectAllCheckbox.checked = allChecked;
    }

    checkIfAllTrue() {
        const checkboxes = document.querySelectorAll('input[name="lidarr_item"]');
        this.selectAllCheckbox.checked = [...checkboxes].every(cb => cb.checked);
    }
}
