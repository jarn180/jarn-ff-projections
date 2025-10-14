// Fantasy Football Projections Web App
// Main JavaScript file

let currentProjections = [];
let currentFormat = 'PPR';
let currentPosition = 'ALL';

// DOM Elements
const formatSelect = document.getElementById('formatSelect');
const searchInput = document.getElementById('searchInput');
const projectionsContainer = document.getElementById('projectionsContainer');
const projectionsTable = document.getElementById('projectionsTable');
const loadingMessage = document.getElementById('loadingMessage');
const errorMessage = document.getElementById('errorMessage');
const statsBar = document.getElementById('statsBar');
const positionTabs = document.getElementById('positionTabs');

// Event Listeners
formatSelect.addEventListener('change', handleFormatChange);
searchInput.addEventListener('input', handleSearch);

// Auto-load data on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchProjections();
});

// Position tab click handlers
document.querySelectorAll('.position-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Update active tab
        document.querySelectorAll('.position-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        // Update current position
        currentPosition = this.dataset.position;

        // Re-render projections
        if (currentProjections.length > 0) {
            renderProjections();
        }
    });
});

// Fetch projections from cache
async function fetchProjections() {
    try {
        showLoading();
        hideError();

        const response = await fetch('/api/projections');
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load projections');
        }

        currentProjections = data.projections;

        hideLoading();
        showStats(data.total_players, data.last_updated);
        showPositionTabs();
        renderProjections();

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Render projections table
function renderProjections() {
    const format = formatSelect.value === 'all' ? null : formatSelect.value;
    const searchTerm = searchInput.value.toLowerCase();

    // Filter projections
    let filteredProjections = currentProjections.filter(proj => {
        const matchesSearch = proj.player.toLowerCase().includes(searchTerm);
        const matchesFormat = !format || proj.format === format;

        // Handle FLEX position (RB, WR, TE combined)
        let matchesPosition;
        if (currentPosition === 'FLEX') {
            matchesPosition = ['RB', 'WR', 'TE'].includes(proj.position);
        } else {
            matchesPosition = currentPosition === 'ALL' || proj.position === currentPosition;
        }

        return matchesSearch && matchesFormat && matchesPosition;
    });

    if (filteredProjections.length === 0) {
        projectionsTable.innerHTML = '<div class="no-results">No players found matching your criteria.</div>';
        return;
    }

    // Group by player if showing all formats
    if (format === null || format === 'all') {
        renderMultiFormatTable(filteredProjections);
    } else {
        renderSingleFormatTable(filteredProjections);
    }
}

// Render table with all formats
function renderMultiFormatTable(projections) {
    // Group by player
    const playerMap = {};
    projections.forEach(proj => {
        if (!playerMap[proj.player]) {
            playerMap[proj.player] = {
                position: proj.position,
                week: proj.week,
                matchup: proj.matchup,
                formats: {}
            };
        }
        playerMap[proj.player].formats[proj.format] = proj;
    });

    let html = '<table class="data-table">';
    html += '<thead><tr>';
    html += '<th>Rank</th>';
    html += '<th>Pos</th>';
    html += '<th class="player-name">Player</th>';
    html += '<th>Week</th>';
    html += '<th>Matchup</th>';
    html += '<th>PPR</th>';
    html += '<th>Half PPR</th>';
    html += '<th>Standard</th>';
    html += '<th>Actions</th>';
    html += '</tr></thead><tbody>';

    // Sort by PPR points
    const players = Object.entries(playerMap).sort((a, b) => {
        const aPoints = a[1].formats['PPR']?.total_points || 0;
        const bPoints = b[1].formats['PPR']?.total_points || 0;
        return bPoints - aPoints;
    });

    players.forEach(([playerName, data], index) => {
        html += '<tr>';
        html += `<td class="rank">${index + 1}</td>`;
        html += `<td><span class="position-badge ${data.position}">${data.position}</span></td>`;
        html += `<td class="player-name">${playerName}</td>`;
        html += `<td>${data.week || 'TBD'}</td>`;
        html += `<td style="font-size: 0.85rem;">${data.matchup || 'TBD'}</td>`;
        html += `<td class="points">${data.formats['PPR']?.total_points.toFixed(2) || '-'}</td>`;
        html += `<td class="points">${data.formats['HALF_PPR']?.total_points.toFixed(2) || '-'}</td>`;
        html += `<td class="points">${data.formats['STANDARD']?.total_points.toFixed(2) || '-'}</td>`;
        html += `<td><button class="btn-small" onclick="showPlayerDetails('${playerName}')">Details</button></td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    projectionsTable.innerHTML = html;
}

// Render table with single format
function renderSingleFormatTable(projections) {
    let html = '<table class="data-table">';
    html += '<thead><tr>';
    html += '<th>Rank</th>';
    html += '<th>Pos</th>';
    html += '<th class="player-name">Player</th>';
    html += '<th>Week</th>';
    html += '<th>Matchup</th>';
    html += '<th>Total Points</th>';
    html += '<th>Pass</th>';
    html += '<th>Rush</th>';
    html += '<th>Rec</th>';
    html += '<th>Actions</th>';
    html += '</tr></thead><tbody>';

    projections.forEach((proj, index) => {
        html += '<tr>';
        html += `<td class="rank">${index + 1}</td>`;
        html += `<td><span class="position-badge ${proj.position}">${proj.position}</span></td>`;
        html += `<td class="player-name">${proj.player}</td>`;
        html += `<td>${proj.week || 'TBD'}</td>`;
        html += `<td style="font-size: 0.85rem;">${proj.matchup || 'TBD'}</td>`;
        html += `<td class="points total-points">${proj.total_points.toFixed(2)}</td>`;
        html += `<td class="points">${proj.breakdown.passing.toFixed(1)}</td>`;
        html += `<td class="points">${proj.breakdown.rushing.toFixed(1)}</td>`;
        html += `<td class="points">${proj.breakdown.receiving.toFixed(1)}</td>`;
        html += `<td><button class="btn-small" onclick="showPlayerDetails('${proj.player}')">Details</button></td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    projectionsTable.innerHTML = html;
}

// Show player details in modal/popup
function showPlayerDetails(playerName) {
    const playerProjections = currentProjections.filter(p => p.player === playerName);

    if (playerProjections.length === 0) return;

    let detailsHtml = `<div class="modal-overlay" onclick="closeModal()">`;
    detailsHtml += `<div class="modal" onclick="event.stopPropagation()">`;
    detailsHtml += `<div class="modal-header">`;
    detailsHtml += `<h2>${playerName}</h2>`;
    detailsHtml += `<button class="close-btn" onclick="closeModal()">&times;</button>`;
    detailsHtml += `</div>`;
    detailsHtml += `<div class="modal-body">`;

    playerProjections.forEach(proj => {
        detailsHtml += `<div class="detail-section">`;
        detailsHtml += `<h3>${proj.format}</h3>`;
        detailsHtml += `<p class="total-points-large">${proj.total_points.toFixed(2)} points</p>`;
        detailsHtml += `<div class="breakdown">`;
        detailsHtml += `<div class="breakdown-item">`;
        detailsHtml += `<span class="label">Passing:</span>`;
        detailsHtml += `<span class="value">${proj.breakdown.passing.toFixed(2)}</span>`;
        detailsHtml += `</div>`;
        detailsHtml += `<div class="breakdown-item">`;
        detailsHtml += `<span class="label">Rushing:</span>`;
        detailsHtml += `<span class="value">${proj.breakdown.rushing.toFixed(2)}</span>`;
        detailsHtml += `</div>`;
        detailsHtml += `<div class="breakdown-item">`;
        detailsHtml += `<span class="label">Receiving:</span>`;
        detailsHtml += `<span class="value">${proj.breakdown.receiving.toFixed(2)}</span>`;
        detailsHtml += `</div>`;
        if (proj.breakdown.fumbles !== 0) {
            detailsHtml += `<div class="breakdown-item">`;
            detailsHtml += `<span class="label">Fumbles:</span>`;
            detailsHtml += `<span class="value">${proj.breakdown.fumbles.toFixed(2)}</span>`;
            detailsHtml += `</div>`;
        }
        detailsHtml += `</div>`;

        if (Object.keys(proj.stats).length > 0) {
            detailsHtml += `<h4>Projected Stats</h4>`;
            detailsHtml += `<div class="stats-grid">`;
            for (const [stat, value] of Object.entries(proj.stats)) {
                const statLabel = stat.replace('player_', '').replace(/_/g, ' ');
                detailsHtml += `<div class="stat-item">`;
                detailsHtml += `<span class="stat-label">${statLabel}:</span>`;
                detailsHtml += `<span class="stat-value">${value.toFixed(2)}</span>`;
                detailsHtml += `</div>`;
            }
            detailsHtml += `</div>`;
        }
        detailsHtml += `</div>`;
    });

    detailsHtml += `</div></div></div>`;

    const modalContainer = document.createElement('div');
    modalContainer.id = 'modalContainer';
    modalContainer.innerHTML = detailsHtml;
    document.body.appendChild(modalContainer);
}

// Close modal
function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (modalContainer) {
        modalContainer.remove();
    }
}

// Handle format change
function handleFormatChange() {
    if (currentProjections.length > 0) {
        renderProjections();
    }
}

// Handle search
function handleSearch() {
    if (currentProjections.length > 0) {
        renderProjections();
    }
}

// UI Helper Functions
function showLoading() {
    loadingMessage.style.display = 'block';
}

function hideLoading() {
    loadingMessage.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}


function showStats(totalPlayers, lastUpdated) {
    document.getElementById('totalPlayers').textContent = totalPlayers;
    document.getElementById('lastUpdated').textContent = lastUpdated || 'Unknown';
}

function showPositionTabs() {
    positionTabs.style.display = 'flex';
}

// Make functions globally accessible
window.showPlayerDetails = showPlayerDetails;
window.closeModal = closeModal;
