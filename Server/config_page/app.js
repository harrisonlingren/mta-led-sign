let stations = [];

function makeConfig() {
    const provider = document.getElementById("provider").value;
    const ssid = document.getElementById("ssid").value;
    const pass = document.getElementById("pass").value;
    const direction = document.getElementById("direction").value;

    const selectedStations = Array.from(document.querySelectorAll('input[name="station"]:checked'));
    if (!provider || !ssid || !pass || selectedStations.length === 0 || !direction) {
        console.error("Missing some values in form, can't save config");
        document.getElementById("warning").hidden = false;
        return false;
    }

    let stationIds = [];
    let selectedLines = [];

    selectedStations.forEach(stationCheckbox => {
        const stationId = stationCheckbox.value;
        stationIds.push(stationId);
        const lines = Array.from(document.querySelectorAll(`input[name="line_${stationId}"]:checked`))
                           .map(input => input.value);
        selectedLines = selectedLines.concat(lines);
    });
    
    // Remove duplicate lines that might be selected from different station complexes
    selectedLines = [...new Set(selectedLines)];

    if (selectedLines.length === 0) {
        console.error("No lines selected for the station(s)");
        document.getElementById("warning").hidden = false;
        return false;
    }

    let outputContent = `secrets = {
    'ssid': '${ssid}',
    'password': '${pass}',
    'timezone' : 'America/New_York',
    'mta_station': '${stationIds.join(',')}',
    'mta_train_direction': '${direction}',
    'mta_api_url': '${provider}',
    'debug': False,
    'mta_train_lines': '${selectedLines.join(',')}'
}`;

    const outputFile = new Blob([outputContent], {type: "text/x-python"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(outputFile);
    link.download = "secrets.py";
    link.click();
    URL.revokeObjectURL(link.href);
}

function searchStations(input) {
    if (input === '') {
        return [];
    }
    const regex = new RegExp(input.toLowerCase(), 'i');
    return stations.filter(station => station.name.toLowerCase().match(regex));
}

function showResults(search) {
    const res = document.getElementById("results");
    res.innerHTML = '';
    const resultsList = searchStations(search);
    
    resultsList.forEach(result => {
        const stationId = result.stop_ids.join(',');
        let stationDiv = document.createElement('div');
        stationDiv.innerHTML = `
            <input type="checkbox" id="station_${stationId}" name="station" value="${stationId}">
            <label for="station_${stationId}">${result.name} (${result.lines.join(', ')})</label>
        `;
        
        let linesDiv = document.createElement('div');
        linesDiv.style.marginLeft = "20px";
        result.lines.forEach(line => {
            linesDiv.innerHTML += `
                <input type="checkbox" id="line_${stationId}_${line}" name="line_${stationId}" value="${line}">
                <label for="line_${stationId}_${line}">${line}</label>
            `;
        });
        stationDiv.appendChild(linesDiv);
        res.appendChild(stationDiv);
    });
}

document.getElementById("provider").defaultValue = window.location.host;

fetch("/api/station")
    .then(response => response.json())
    .then(stationList => {
        stations = stationList;
    });