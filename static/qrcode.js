function copyToClipboard() {
    const ipField = document.getElementById('server-ip');
    ipField.select();
    navigator.clipboard.writeText(ipField.value)
        .then(() => {
            console.log('Text successfully copied to clipboard!');
        })
        .catch((error) => {
            console.error('Error copying text to clipboard: ', error);
        });
}

function generateQRCode() {
    const qrModal = document.getElementById("qr-modal");
    const qrImg = document.getElementById("qr-modal-img");
    qrModal.style.display = "block"; // Show modal
    qrImg.src = `/generate_qrcodes`;  // Set the image source to the generated QR code
}

function closeModal() {
    const qrModal = document.getElementById("qr-modal");
    qrModal.style.display = "none";
}

function printQRCode() {
    const qrImg = document.getElementById("qr-modal-img");

    if (!qrImg || !qrImg.src) {
        console.error("QR code image not found.");
        return;
    }

    const printWindow = window.open('', '', 'height=400,width=600');
    const printDocument = printWindow.document;

    // Create the HTML structure as a string
    const htmlContent = `
        <html>
            <head>
                <title>Print QR Code</title>
            </head>
            <body>
                <img src="${qrImg.src}" style="max-width: 100%; height: auto;" />
            </body>
        </html>
    `;

    // Write the content to the new window
    printDocument.open();
    printDocument.write(htmlContent);
    printDocument.close();

    // Wait for the window to load and then trigger printing
    printWindow.onload = function () {
        printWindow.focus(); // Focus the print window to ensure print dialog opens
        printWindow.print();  // Open the print dialog
    };

    // Optionally close the window after the user is done printing (with a small delay)
    setTimeout(() => {
        printWindow.close();
    }, 1000); // 1 second delay before closing the print window after print dialog is triggered
}


// Function to copy the QR code image to clipboard
function copyQRCode() {
    const qrImg = document.getElementById("qr-modal-img");

    if (!qrImg || !qrImg.src) {
        console.error("QR code image not found.");
        return;
    }

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.width = qrImg.width;
    canvas.height = qrImg.height;
    
    // Draw the image onto the canvas
    context.drawImage(qrImg, 0, 0);

    // Convert the canvas content to a Blob (image)
    canvas.toBlob(function (blob) {
        if (blob) {
            // Create a ClipboardItem with the image
            const item = new ClipboardItem({
                "image/png": blob
            });

            // Write the item to the clipboard
            navigator.clipboard.write([item])
                .then(() => {
                    alert("QR Code copied to clipboard!");
                })
                .catch((err) => {
                    console.error("Error copying QR Code to clipboard: ", err);
                    alert("Failed to copy QR Code to clipboard.");
                });
        }
    }, "image/png");
}


// Function to update the connected players and logs
function updateGameData() {
    fetch('/get_game_data')
        .then(response => response.json())
        .then(data => {
            // Update Players List
            const playersList = document.getElementById('players-list');
            playersList.innerHTML = ''; // Clear current list
            if (data.players && Object.keys(data.players).length > 0) {
                Object.values(data.players).forEach(player => {
                    const li = document.createElement('li');
                    li.innerHTML = `${player.id} - Score: ${player.score} | Health: ${player.health}
                                    <button onclick="generateQRCode('${player.id}')">Generate QR Code</button>
                                    <button onclick="kickPlayer('${player.id}')">Kick Player</button>`;
                    playersList.appendChild(li);
                });
            } else {
                playersList.innerHTML = '<li>No players are currently connected.</li>';
            }

            // Update Logs
            const logsContainer = document.getElementById('logs-container');
            logsContainer.textContent = ''; // Clear current logs
            if (data.logs && data.logs.length > 0) {
                data.logs.forEach(log => {
                    const p = document.createElement('p');
                    p.textContent = log;
                    logsContainer.appendChild(p);
                });
            } else {
                logsContainer.textContent = 'No logs available.';
            }
        })
        .catch(error => {
            console.error('Error fetching game data:', error);
        });
}

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

// Fetch and update the game data every second
setInterval(updateGameData, 1000);