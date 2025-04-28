async function debugAttack() {
    try {
        // Step 1: Fetch current players
        const gameDataResponse = await fetch('/get_game_data');
        const gameData = await gameDataResponse.json();

        const players = gameData.players;
        const playerIds = Object.keys(players);

        if (playerIds.length === 0) {
            console.error('No players available to attack.');
            return;
        }

        // Step 2: Pick a random player
        const randomIndex = Math.floor(Math.random() * playerIds.length);
        const targetId = playerIds[randomIndex];

        console.log(`Randomly selected player for attack: ${targetId}`);

        // Step 3: Send attack command
        const attackResponse = await fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: `attack ${targetId}`
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
