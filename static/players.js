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
function createPlayerItem(player) {
    let teamClass = 'default-team'; // Default class
    if (player.team === 'Blue') {
        teamClass = 'team-blue'; // Muted blue team
    } else if (player.team === 'Red') {
        teamClass = 'team-red'; // Muted red team
    }

    return `
     <li class="table-row ${teamClass}" data-player-id="${player.id}">
        <div>${player.id}</div>
        <div>${player.ip}</div>
        <div>${player.health}</div>
        <div>${player.score}</div>
        <div>${player.deaths}</div>
        <div>${player.team}</div>
        <div>${player.flag}</div>
        <div class="player-actions">
            <button class="blue-team-button" onclick="newTeam('${player.id}', 0)">Blue, 0</button>
            <button class="red-team-button" onclick="newTeam('${player.id}', 1)">Red, 1</button>
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

    console.log(team)

    fetch('/newTeam', {
        method: 'POST',
        body: formData
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