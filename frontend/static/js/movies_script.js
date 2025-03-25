import { socket } from './socket_script.js';

function addToRadarr(movieTitle, movieYear, tmdbId) {
    if (socket.connected) {
        socket.emit('add_movie_to_radarr', encodeURIComponent(movieTitle), movieYear, tmdbId);
    }
    else {
        showToast("Connection Lost", "Please reload to continue.");
    }
}

function overviewReq(movie) {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = `${scrollbarWidth}px`;

    var modalTitle = document.getElementById('overview-modal-title');
    var modalBody = document.getElementById('modal-body');
    modalTitle.textContent = movie.title;
    modalBody.innerHTML = DOMPurify.sanitize(movie.overview || "No overview available.");


    var modal = new bootstrap.Modal(document.getElementById('overview-modal'));
    modal.show();

    modal._element.addEventListener('hidden.bs.modal', function () {
        document.body.style.overflow = 'auto';
        document.body.style.paddingRight = '0';
    });
}

function updateMovieCard(movie) {
    var movieCards = document.querySelectorAll('#movie-column');
    movieCards.forEach(function (card) {
        var cardBody = card.querySelector('.card-body');
        var cardmovieTitle = cardBody.querySelector('.card-title').textContent.trim();

        if (cardmovieTitle === movie.title) {
            cardBody.classList.remove('status-green', 'status-red', 'status-blue');

            var addButton = cardBody.querySelector('.add-to-radarr-btn');

            if (movie.status === "Added" || movie.status === "Already in Radarr") {
                cardBody.classList.add('status-green');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-secondary');
                addButton.disabled = true;
                addButton.textContent = movie.status;
            } else if (movie.status === "Failed to Add" || movie.status === "Invalid Path") {
                cardBody.classList.add('status-red');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-danger');
                addButton.disabled = true;
                addButton.textContent = movie.status;
            } else {
                cardBody.classList.add('status-blue');
                addButton.disabled = false;
            }
            return;
        }
    });
}

export class MoviesPage {
    constructor() {
        this.tabs = {
            search: new MovieSearchTab(),
            recommendations: new MovieRecommendationsTab(),
        }
    }

    init() {
        this.restoreLastActiveTab();
        this.initTabs();
    }

    initTabs() {
        Object.keys(this.tabs).forEach(tabName => {
            const tabElement = document.getElementById(`pills-movie-${tabName}-tab`);
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
        localStorage.setItem('lastActiveMovieTab', tabName);
    }

    restoreLastActiveTab() {
        const lastTab = localStorage.getItem('lastActiveMovieTab') || 'search';
        new bootstrap.Tab(document.getElementById(`pills-movie-${lastTab}-tab`)).show();
        this.switchTab(lastTab);
    }
}

class MovieSearchTab {
    constructor() {
        socket.on('movie_search_results', (data) => {
            this.changeUI("ready");
            this.showMovieSearchResults(data);
        });
    }

    setup() {
        const searchButton = document.getElementById('movie-search-button');
        const searchInput = document.getElementById('movie-search-input');

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
        const query = document.getElementById('movie-search-input').value.trim();

        if (query) {
            socket.emit('movie_search', { query });
        }
        else {
            this.changeUI("ready");
        }
    }

    changeUI(state) {
        ['movie-search-button', 'movie-search-input'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.disabled = state === "busy";
        });

        const spinner = document.getElementById('movie-spinner-border');
        if (spinner) spinner.style.display = state === "busy" ? 'inline-block' : 'none';
    }

    showMovieSearchResults(data) {
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = '';

        if (data && data.results) {
            if (Array.isArray(data.results) && data.results.length > 0) {
                data.results.forEach(item => {
                    this.populateMovieSearchTemplate(item);
                });
            } else {
                const noResultsMessage = document.createElement('p');
                noResultsMessage.textContent = 'No results found';
                resultsSection.appendChild(noResultsMessage);
            }
        } else {
            const noResultsMessage = document.createElement('p');
            noResultsMessage.textContent = 'No results found';
            resultsSection.appendChild(noResultsMessage);
        }
    }

    populateMovieSearchTemplate(movie) {
        var template = document.getElementById('search-movie-template');
        const clone = document.importNode(template.content, true);

        const cardTitle = clone.querySelector('.card-title');
        const genre = clone.querySelector('.genre');
        const cardImgTop = clone.querySelector('.card-img-top');
        const addToRadarrBtn = clone.querySelector('.add-to-radarr-btn');
        const getOverviewBtn = clone.querySelector('.get-overview-btn');
        const averageVote = clone.querySelector('.vote-average');
        const popularity = clone.querySelector('.popularity');


        cardTitle.textContent = `${movie.title} - ${movie.year}`;
        genre.textContent = movie.genres;
        cardImgTop.src = movie.image;
        cardImgTop.alt = movie.title;

        addToRadarrBtn.addEventListener('click', () => {
            addToRadarrBtn.disabled = true;
            addToRadarrBtn.textContent = 'Adding...';
            addToRadarr(movie.title, movie.year, movie.tmdb_id);
        });

        getOverviewBtn.addEventListener('click', () => {
            overviewReq(movie);
        });

        averageVote.textContent = `Vote Average: ${movie.vote_average}`;
        popularity.textContent = `Popularity: ${movie.popularity}`;

        const element = document.getElementById('results-section');
        element.appendChild(clone);
    }
}

class MovieRecommendationsTab {
    constructor() {
        this.currentPage = 1;
        this.numResults = 10;
        this.loading = false;

        socket.on('movie_recommendations', (data) => {
            const movieRow = document.getElementById('movie-row');
            if (this.currentPage === 1) movieRow.innerHTML = "";
            this.appendMovies(data.data);
            this.loading = false;
        });

        socket.on("refresh_movie", (movie) => {
            updateMovieCard(movie);
        });
    }

    setup() {
        this.loading = true;

        socket.emit("load_movie_recommendations");
        document.getElementById('get-recommendations-button').addEventListener('click', () => {
            const movieRow = document.getElementById('movie-row');
            movieRow.innerHTML = "";
            this.getRecommendations();
        });

        setTimeout(() => {
            this.initInfiniteScroll();
        }, 500);

        setTimeout(() => {
            this.loading = false;
        }, 5000);
    }

    appendMovies(movies) {
        var movieRow = document.getElementById('movie-row');
        var template = document.getElementById('movie-template');

        movies.forEach((movie) => {
            var clone = document.importNode(template.content, true);
            var movieCol = clone.querySelector('#movie-column');

            movieCol.querySelector('.card-title').textContent = `${movie.title} - ${movie.year}`;
            movieCol.querySelector('.genre').textContent = movie.genre;
            movieCol.querySelector('.card-img-top').src = movie.image;
            movieCol.querySelector('.card-img-top').alt = movie.title;
            movieCol.querySelector('.add-to-radarr-btn').addEventListener('click', () => {
                const addButton = movieCol.querySelector('.add-to-radarr-btn');
                addButton.disabled = true;
                addButton.textContent = 'Adding...';
                addToRadarr(movie.title, movie.year, movie.tmdb_id);
            });
            movieCol.querySelector('.get-overview-btn').addEventListener('click', () => {
                overviewReq(movie);
            });
            movieCol.querySelector('.dismiss-movie-btn').addEventListener('click', (event) => {
                this.dismissMovie(event, movie);
            });
            movieCol.querySelector('.vote-average').textContent = `Vote Average: ${movie.vote_average}`;
            movieCol.querySelector('.popularity').textContent = `Popularity: ${movie.popularity}`;

            var addButton = movieCol.querySelector('.add-to-radarr-btn');
            if (movie.status === "Added" || movie.status === "Already in Radarr") {
                movieCol.querySelector('.card-body').classList.add('status-green');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-secondary');
                addButton.disabled = true;
                addButton.textContent = movie.status;
            } else if (movie.status === "Failed to Add" || movie.status === "Invalid Path") {
                movieCol.querySelector('.card-body').classList.add('status-red');
                addButton.classList.remove('btn-primary');
                addButton.classList.add('btn-danger');
                addButton.disabled = true;
                addButton.textContent = movie.status;
            } else {
                movieCol.querySelector('.card-body').classList.add('status-blue');
            }
            movieRow.appendChild(clone);
        });
    }

    getRecommendations(loadMore = false) {
        if (!loadMore) {
            this.currentPage = 1;
        } else {
            this.currentPage++;
        }

        if (this.loading) return;
        this.loading = true;

        const data = {
            selected_movie: document.getElementById("movie-select").value || "all",
            sort_by: document.getElementById("sort-select").value || "random",
            min_popularity: parseFloat(document.getElementById("min-popularity").value) || null,
            min_vote_average: parseFloat(document.getElementById("min-vote-average").value) || null,
            num_results: this.numResults,
            page: this.currentPage,
        };

        socket.emit("refresh_movie_recommendations", data);
    }

    initInfiniteScroll() {
        const sentinel = document.getElementById('scroll-sentinel');
        const observer = new IntersectionObserver((entries) => {
            const entry = entries[0];

            const movieSelected = document.getElementById("movie-select").value && document.getElementById("movie-select").value !== "all";
            if (!movieSelected && entry.isIntersecting && !this.loading) {
                this.getRecommendations(true);
            }
        });

        observer.observe(sentinel);
    }

    dismissMovie(event, movie) {
        if (socket.connected) {
            socket.emit('dismiss_movie', encodeURIComponent(movie.title));
            const movieColumn = event.currentTarget.closest('#movie-column');

            if (movieColumn) {
                movieColumn.style.transition = 'opacity 1.5s';
                movieColumn.style.opacity = '0';

                setTimeout(() => movieColumn.remove(), 1500);
            }
        }
        else {
            showToast("Connection Lost", "Please reload to continue.");
        }
    }
}
