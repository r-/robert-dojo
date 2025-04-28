// Function to kick a player
function kickPlayer(playerId) {
    const formData = new FormData();
    formData.append('player_id', playerId);

    fetch('/kick', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`${playerId} has been kicked!`);
            updateGameData();  // Refresh the player list after kicking
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error kicking player:', error);
    });
}

function createPlayerItem(player)
{
    return `
     <li class="table-row" data-player-id="${player.id}">
        <div>${player.id}</div>
        <div>${player.ip}</div>
        <div>${player.health}</div>
        <div>${player.score}</div>
        <div>${player.deaths}</div>
        <div>${player.team}</div>
        <div class="player-actions">
            <button class="blue-team-button" onclick="newTeam('${player.id}', 'Blue')">Blue</button>
            <button class="red-team-button" onclick="newTeam('${player.id}', 'Red')">Red</button>
            <button class="kick-button" onclick="kickPlayer('${player.id}')">Kick</button>
        </div>
    </li>
`;
}


// Function to make player join a team
function newTeam(playerId, team) {
    const formData = new FormData();
    formData.append('player_id', playerId);
    formData.append('player_team', team);

    fetch('/newTeam', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`Player ${playerId} has joined the ${team} team!`);
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