// Start/Sit Optimizer JavaScript

let currentUser = null;
let currentLeagueId = null;
let currentUserId = null;

// Connect Sleeper Account
document.getElementById('connectBtn').addEventListener('click', async () => {
    const username = document.getElementById('sleeperUsername').value.trim();
    const btn = document.getElementById('connectBtn');
    const messageDiv = document.getElementById('connectionMessage');

    if (!username) {
        showMessage(messageDiv, 'Please enter your Sleeper username', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Connecting...';

    try {
        const response = await fetch(`/api/sleeper/user/${username}`);
        const data = await response.json();

        if (data.success) {
            currentUser = data.user;
            showMessage(messageDiv, `Connected as ${data.user.display_name || username}`, 'success');
            loadLeagues(data.user.user_id);
        } else {
            showMessage(messageDiv, data.error || 'User not found', 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Failed to connect. Please try again.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Connect Account';
    }
});

// Load user leagues
async function loadLeagues(userId) {
    const leagueSection = document.getElementById('leagueSection');
    const leaguesList = document.getElementById('leaguesList');

    leaguesList.innerHTML = '<div class="loading-message"><div class="spinner-large"></div><p>Loading your leagues...</p></div>';
    leagueSection.style.display = 'block';

    try {
        // Try 2025 season first (2025-2026 NFL season)
        let response = await fetch(`/api/sleeper/user/${userId}/leagues?season=2025`);
        let data = await response.json();

        // If no leagues found, try 2024
        if (data.success && data.leagues.length === 0) {
            response = await fetch(`/api/sleeper/user/${userId}/leagues?season=2024`);
            data = await response.json();
        }

        if (data.success && data.leagues.length > 0) {
            currentUserId = userId;
            displayLeagues(data.leagues);
        } else {
            leaguesList.innerHTML = '<div class="no-results">No leagues found for 2024-2025 season. Please check your username.</div>';
        }
    } catch (error) {
        leaguesList.innerHTML = '<div class="error-message">Failed to load leagues. Please try again.</div>';
    }
}

// Display leagues
function displayLeagues(leagues) {
    const leaguesList = document.getElementById('leaguesList');

    const html = `
        <div class="leagues-grid">
            ${leagues.map(league => `
                <div class="league-card" onclick="selectLeague('${league.league_id}', '${league.name}', '${league.scoring_settings?.rec || 0}')">
                    <h3>${league.name}</h3>
                    <div class="league-details">
                        <span class="badge">${league.total_rosters} Teams</span>
                        <span class="badge">${getScoringType(league.scoring_settings)}</span>
                    </div>
                    <button class="btn-small">Select League →</button>
                </div>
            `).join('')}
        </div>
    `;

    leaguesList.innerHTML = html;
}

// Get scoring type from settings
function getScoringType(scoring) {
    if (!scoring) return 'Standard';
    const rec = parseFloat(scoring.rec || 0);
    if (rec === 1) return 'PPR';
    if (rec === 0.5) return 'Half PPR';
    return 'Standard';
}

// Select league
async function selectLeague(leagueId, leagueName, recPoints) {
    currentLeagueId = leagueId;

    const optimizerSection = document.getElementById('optimizerSection');
    const leagueInfo = document.getElementById('leagueInfo');

    document.getElementById('leagueName').textContent = leagueName;

    // Set scoring format based on league settings
    const scoringSelect = document.getElementById('scoringFormatOptimizer');
    if (recPoints == 1) {
        scoringSelect.value = 'PPR';
    } else if (recPoints == 0.5) {
        scoringSelect.value = 'HALF_PPR';
    } else {
        scoringSelect.value = 'STANDARD';
    }

    document.getElementById('leagueScoring').textContent = getScoringType({ rec: recPoints });

    // Get user roster info
    try {
        const response = await fetch(`/api/sleeper/league/${leagueId}/roster/${currentUserId}`);
        const data = await response.json();

        if (data.success) {
            const roster = data.roster;
            const wins = roster.settings?.wins || 0;
            const losses = roster.settings?.losses || 0;
            const ties = roster.settings?.ties || 0;
            document.getElementById('userRecord').textContent = `${wins}-${losses}${ties > 0 ? `-${ties}` : ''}`;
        }
    } catch (error) {
        document.getElementById('userRecord').textContent = '-';
    }

    leagueInfo.style.display = 'flex';
    optimizerSection.style.display = 'block';

    // Scroll to optimizer section
    optimizerSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Optimize lineup
document.getElementById('optimizeBtn').addEventListener('click', async () => {
    const btn = document.getElementById('optimizeBtn');
    const resultsDiv = document.getElementById('optimizationResults');
    const scoringFormat = document.getElementById('scoringFormatOptimizer').value;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Optimizing...';

    resultsDiv.innerHTML = '<div class="loading-message"><div class="spinner-large"></div><p>Analyzing your roster...</p></div>';

    try {
        const response = await fetch('/api/sleeper/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                league_id: currentLeagueId,
                user_id: currentUserId,
                scoring_format: scoringFormat
            })
        });

        const data = await response.json();

        if (data.success) {
            displayOptimization(data.optimization);
        } else {
            resultsDiv.innerHTML = `<div class="error-message">${data.error || 'Optimization failed'}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error-message">Failed to optimize lineup. Please try again.</div>';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🔍 Optimize Lineup</span>';
    }
});

// Display optimization results
function displayOptimization(optimization) {
    const resultsDiv = document.getElementById('optimizationResults');

    const html = `
        <div class="optimization-results">
            <!-- Total Projection -->
            <div class="stats-bar" style="margin-bottom: 30px;">
                <div class="stat-item">
                    <span class="stat-label">Projected Points:</span>
                    <span class="stat-value" style="font-size: 1.5rem;">${optimization.total_projection}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Format:</span>
                    <span class="stat-value">${optimization.scoring_format}</span>
                </div>
            </div>

            <!-- Recommendations -->
            ${optimization.recommendations.length > 0 ? `
                <div class="recommendations-section">
                    <h3 style="color: var(--primary-color); margin-bottom: 20px;">💡 Start/Sit Recommendations</h3>
                    <div class="recommendations-list">
                        ${optimization.recommendations.map((rec, index) => `
                            <div class="recommendation-card">
                                <div class="rec-header">
                                    <span class="rec-number">#${index + 1}</span>
                                    <span class="rec-gain">+${rec.projected_gain} pts</span>
                                </div>
                                <div class="rec-swap">
                                    <div class="rec-action">
                                        <span class="action-label">START</span>
                                        <span class="player-name">${rec.bench_player}</span>
                                        <span class="player-proj">${rec.bench_projection.toFixed(1)} pts</span>
                                    </div>
                                    <div class="swap-arrow">⇄</div>
                                    <div class="rec-action sit">
                                        <span class="action-label">SIT</span>
                                        <span class="player-name">${rec.starter_player}</span>
                                        <span class="player-proj">${rec.starter_projection.toFixed(1)} pts</span>
                                    </div>
                                </div>
                                <div class="rec-position">
                                    <span class="position-badge ${rec.position}">${rec.position}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : `
                <div class="welcome-message">
                    <h2>✅ Your Lineup is Optimal!</h2>
                    <p>No recommended changes. You're starting your best players.</p>
                </div>
            `}

            <!-- Starters -->
            <div class="lineup-section">
                <h3 style="color: var(--primary-color); margin-bottom: 20px;">Starting Lineup</h3>
                ${Object.entries(optimization.starters).map(([position, players]) => {
                    if (players.length === 0) return '';
                    return `
                        <div class="position-group">
                            <h4 class="position-header">
                                <span class="position-badge ${position}">${position}</span>
                            </h4>
                            <div class="players-list">
                                ${players.map(player => `
                                    <div class="player-card starter">
                                        <div class="player-info">
                                            <span class="player-name">${player.name}</span>
                                            ${player.injury_status ? `<span class="injury-badge">${player.injury_status}</span>` : ''}
                                        </div>
                                        <span class="player-projection">${player.projection.toFixed(1)} pts</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>

            <!-- Bench -->
            ${optimization.bench.length > 0 ? `
                <div class="lineup-section">
                    <h3 style="color: var(--text-secondary); margin-bottom: 20px;">Bench</h3>
                    <div class="players-list">
                        ${optimization.bench.map(player => `
                            <div class="player-card bench">
                                <div class="player-info">
                                    <span class="position-badge ${player.position}">${player.position}</span>
                                    <span class="player-name">${player.name}</span>
                                    ${player.injury_status ? `<span class="injury-badge">${player.injury_status}</span>` : ''}
                                </div>
                                <span class="player-projection">${player.projection.toFixed(1)} pts</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    resultsDiv.innerHTML = html;
}

// Helper function to show messages
function showMessage(element, message, type) {
    element.className = type === 'error' ? 'error-message' : 'welcome-message';
    element.innerHTML = `<p>${message}</p>`;
    element.style.display = 'block';

    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}
