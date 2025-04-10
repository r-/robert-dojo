
document.addEventListener('DOMContentLoaded', function () {
    // Handle form submission via AJAX
    const kickForms = document.querySelectorAll('form[action="/kick"]');

    kickForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the default form submission

            const playerId = form.querySelector('input[name="player_id"]').value;

            fetch('/kick', {
                method: 'POST',
                body: new URLSearchParams({ 'player_id': playerId }),
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message); // Show a success message
                        // Remove the player from the UI
                        form.closest('li').remove();
                    } else {
                        alert(data.message); // Show an error message
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});