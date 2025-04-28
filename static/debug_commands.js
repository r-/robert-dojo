async function debugGiveFlag() {
    try {
        // Step 1: Fetch current players
        const gameDataResponse = await fetch('/get_game_data');
        const gameData = await gameDataResponse.json();

        const players = gameData.players;
        const playerIds = Object.keys(players);

        if (playerIds.length === 0) {
            console.error('No players available to give a flag.');
            return;
        }

        // Step 2: Pick a random player to give the flag
        const randomIndex = Math.floor(Math.random() * playerIds.length);
        const targetId = playerIds[randomIndex];

        console.log(`Randomly selected player to receive the flag: ${targetId}`);

        // Step 3: Send the command to the server to give the flag
        const flagResponse = await fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: `take_flag ${targetId}`
            })
        });

        const flagResult = await flagResponse.json();
        console.log('Server response:', flagResult);

        if (!flagResponse.ok) {
            console.error('Failed to give flag:', flagResult.message);
        } else {
            console.log(`Flag successfully given to player ${targetId}`);
        }
    } catch (error) {
        console.error('Error during debugGiveFlag:', error);
    }
}

async function debugAttack() {
    try {
        // Step 1: Fetch current players
        const gameDataResponse = await fetch('/get_game_data');
        const gameData = await gameDataResponse.json();

        const players = gameData.players;
        const playerIds = Object.keys(players);

        if (playerIds.length < 2) {
            console.error('Not enough players to perform an attack.');
            return;
        }

        // Step 2: Pick a random attacker
        const randomAttackerIndex = Math.floor(Math.random() * playerIds.length);
        const attackerId = playerIds[randomAttackerIndex];

        // Step 3: Pick a random target (ensure the target is not the attacker)
        let targetId;
        do {
            const randomTargetIndex = Math.floor(Math.random() * playerIds.length);
            targetId = playerIds[randomTargetIndex];
        } while (targetId === attackerId); // Ensure attacker does not attack themselves

        // Get attacking player’s IP
        const attackingPlayerIp = players[attackerId].ip;

        console.log(`Randomly selected attacker: ${attackerId}`);
        console.log(`Attacker's IP: ${attackingPlayerIp}`);
        console.log(`Randomly selected target for attack: ${targetId}`);

        // Step 4: Send attack command
        const attackResponse = await fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: `attack ${targetId} ${attackingPlayerIp}`
            })
        });

        const attackResult = await attackResponse.json();
        console.log('Server response:', attackResult);

        if (!attackResponse.ok) {
            console.error('Attack failed:', attackResult.message);
        } else {
            console.log('Attack successful:', attackResult.message);
        }
    } catch (error) {
        console.error('Error during debugAttack:', error);
    }
}
