function copyToClipboard() {
    const ipField = document.getElementById('server-ip');
    ipField.select();
     // Select the text field
     ipField.select();
     ipField.setSelectionRange(0, 99999); // For mobile devices

    // Copy the text inside the text field
    navigator.clipboard.writeText(copyText.value);

    /*
    navigator.clipboard.writeText(ipField.value)
        .then(() => {
            console.log('Text successfully copied to clipboard!');
        })
        .catch((error) => {
            console.error('Error copying text to clipboard: ', error);
        });**/
}
