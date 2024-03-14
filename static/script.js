function submitForm() {
    var inputTemp = document.getElementById("inputTemp").value;
    inputTemp = parseInt(inputTemp);

    if (inputTemp < 10 || inputTemp > 500 || isNaN(inputTemp)) {
        alert("Please enter a valid value between 10 and 500.");
        return;
    }

    // Send AJAX request to update the table
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/updateTable", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                // Parse the JSON response
                var response = JSON.parse(xhr.responseText);

                // Check if the expected property exists
                if ('tableHtml' in response) {
                    // Update the result container
                    var resultContainer = document.getElementById("resultContainer");
                    resultContainer.innerHTML = "You entered: " + inputTemp;

                    // Show the result container
                    resultContainer.style.display = "block";

                    // Update only the content inside the table
                    var tableContainer = document.querySelector('.container.mt-5 table');
                    tableContainer.innerHTML = response.tableHtml;
                } else {
                    console.error("Expected property 'tableHtml' not found in the JSON response.");
                }
            } else {
                console.error("Failed to fetch data from the server. Status: " + xhr.status);
            }
        }
    };

    // Send the user input to the server
    xhr.send("inputTemp=" + inputTemp);
}
