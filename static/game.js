
async function updateGameData() {
    try {
        const response = await fetch('/get_game_data');
        const data = await response.json();

        const playersList = document.getElementById('players-list');
        const logsContainer = document.getElementById('logs-container');
        const redScore = document.getElementById('red-score');
        const blueScore = document.getElementById('blue-score');

        redScore.innerHTML = `Red Score: ${data.score["1"]}`
        blueScore.innerHTML = `Blue Score: ${data.score["0"]}`

        // Update Players List
        playersList.innerHTML = data.players && Object.keys(data.players).length
            ? Object.values(data.players).map(createPlayerItem).join('')
            : '<li class="no-players">No players are currently connected.</li>';

        // Update Logs
        logsContainer.innerHTML = data.logs && data.logs.length
            ? data.logs.map(createLogEntry).join('')
            : '<p class="no-logs">No logs available.</p>';

    } catch (error) {
        console.error('Failed to update game data:', error);
        document.getElementById('logs-container').innerHTML = '<p class="error">Error loading game data.</p>';
    }
}

// Fetch and update the game data every second
setInterval(updateGameData, 1000);

function createLogEntry(log) {
    return `<p class="log-entry">${log}</p>`;
}

function reset()
{

    fetch('/restart', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            //alert(`Player ${playerId} has joined the ${team} team!`);
            updateGameData(); // Refresh player list
        } else {
            alert(`Failed to assign team: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error changing team:', error);
        alert('Error changing team. Please try again.');
    });    
}

