function submitForm() {
    var formData = new FormData(document.querySelector('form'));
    var urlEncodedData = new URLSearchParams(formData).toString();

    // Send AJAX request to start the simulation and update the table and graph
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/updateTable", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);

                if (response.status && response.status === 'running') {
                    // Display a message indicating the simulation is running
                    document.getElementById("resultContainer").innerHTML = "<p>Simulation running, please wait...</p>";
                    document.querySelector('.container.mt-5 table').innerHTML = '';
                    var graphContainer = document.getElementById("graphContainer");
                    if (graphContainer) {
                        graphContainer.style.display = "none";
                    }
                    // Start polling to check for simulation status
                    checkSimulationStatus();
                } else {
                    // Update the UI with the results
                    updateUIWithResults(response);
                }
            } else {
                console.error("Failed to fetch data from the server. Status: " + xhr.status);
            }
        }
    };

    // Send the form data to the server
    xhr.send(urlEncodedData);
}

function checkSimulationStatus() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/check-simulation-status", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.status && response.status === 'complete') {
                // Simulation is complete, update the UI with the results
                updateUIWithResults(response);
            } else {
                // Simulation is not complete, check again after some time
                setTimeout(checkSimulationStatus, 5000); // Check every 5 seconds
            }
        }
    };
    xhr.send();
}

function updateUIWithResults(response) {
    var resultContainer = document.getElementById("resultContainer");
    var tableContainer = document.querySelector('.container.mt-5 table');

    // Clear the "Simulation running" message
    resultContainer.innerHTML = '<img id="graphContainer" src="" alt="Constraint Yield Graphs" style="display: none;">';
    var graphContainer = document.getElementById("graphContainer");

    if (tableContainer && 'tableHtml' in response) {
        // Update the table with the new results
        tableContainer.innerHTML = response.tableHtml;

        // Center-align table headers
        var tableHeaders = tableContainer.querySelectorAll('th');
        tableHeaders.forEach(function (header) {
            header.style.textAlign = 'center';
        });

        // Left-align Constraint column cells
        var constraintHeader = tableContainer.querySelector('th:first-child');
        if (constraintHeader) {
            var headerWidth = constraintHeader.offsetWidth;
            var rows = tableContainer.querySelectorAll('tr');
            rows.forEach(function (row) {
                var firstCell = row.querySelector('td:first-child');
                if (firstCell) {
                    firstCell.style.textAlign = 'left';
                    firstCell.style.paddingLeft = (headerWidth / 2) + 'px';
                }
            });
        }
    }

    if ('graphData' in response) {
        graphContainer.src = response.graphData;
        graphContainer.style.display = 'block';
    } else {
        graphContainer.style.display = 'none';
    }
}