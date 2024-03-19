function submitForm() {
    var formData = new FormData(document.querySelector('form'));
    var urlEncodedData = new URLSearchParams(formData).toString();

    // Send AJAX request to update the table and graph
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/updateTable", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                // Parse the JSON response
                var response = JSON.parse(xhr.responseText);

                // Check if the expected properties exist
                if ('tableHtml' in response) {
                    // Update the result container
                    var tableContainer = document.querySelector('.container.mt-5 table');
                    tableContainer.innerHTML = response.tableHtml;

                    // Center-align table headers
                    var tableHeaders = tableContainer.querySelectorAll('th');
                    tableHeaders.forEach(function(header) {
                        header.style.textAlign = 'center';
                    });
                } else {
                    console.error("Expected property 'tableHtml' not found in the JSON response.");
                }

                if ('graphData' in response) {
                    // Update the graph image
                    var graphContainer = document.getElementById("graphContainer");
                    graphContainer.src = response.graphData;
                    graphContainer.style.display = "block";
                } else {
                    console.error("Expected property 'graphData' not found in the JSON response.");
                }
            } else {
                console.error("Failed to fetch data from the server. Status: " + xhr.status);
            }
        }
    };

    // Send the form data to the server
    xhr.send(urlEncodedData);
}
