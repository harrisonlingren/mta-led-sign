stations = [];
stationMap = {
    "A": "ACE", "B": "BDFM", "C": "ACE",
    "D": "BDFM", "E": "ACE", "F": "BDFM",
    "G": "G", "J": "JZ", "L": "L",
    "M": "BDFM", "N": "NQRW", "Q": "NQRW",
    "R": "NQRW", "W": "NQRW", "1": "123",
    "2": "123", "3": "123", "4": "456",
    "5": "456", "6": "456", "7": "7"
}

function makeConfig(e) {
    let provider = document.getElementById("provider").value;
    let ssid = document.getElementById("ssid").value;
    let pass = document.getElementById("pass").value;
    let station = document.getElementById("station").value;
    let direction = document.getElementById("direction").value;

    if (!provider || !ssid || !pass || !station || !direction) {
        console.error("Missing some values in form, can't save config");
        document.getElementById("warning").hidden = false;
        return false;
    }

    let outputHeaders = "text/x-python"
    let outputContent = `secrets = {
    'ssid': '${ssid}',
    'password': '${pass}',
    'timezone' : 'America/New_York',
    'mta_station': '${station}',
    'mta_train_direction': '${direction}',
    'mta_api_url': '${provider}'
}`;

    let outputFile = new Blob([outputContent], {type: outputHeaders});
    let link = document.createElement("a");
    link.href = URL.createObjectURL(outputFile);
    link.download = "secrets.py";
    link.click();
    URL.revokeObjectURL(link.href);

    return false;
}

function searchStations(input) {
    if (input === '') {
        return [];
    }

    const regex = new RegExp(input.toLowerCase());
    return stations.filter((station) => station.name.toLowerCase().match(regex));
}

function showResults(search) {
    res = document.getElementById("results");
    res.innerHTML = '';
    let resultsList = '';
    searchStations(search).forEach(result => {
        resultsList += `<option value="${result.id}">${result.name} (${result.line})</option>`;
    });
    res.innerHTML = `${resultsList}`;
}

document.getElementById("provider").defaultValue = document.URL.replace('/config/', '/api');

const stationIdRegex = "^[01234567ABCDEFGJLMNQRWZ]{3}$"
fetch("/api/station")
    .then((response) => response.json())
    .then((stations) => {
        return Object.values(stations).filter(station => station['stop_id'].match(stationIdRegex));
    })
    .then((stations) => Object.values(stations).map((station) => (
        { 'id': station['stop_id'], 'name': station['stop_name'], 'line': stationMap[station['stop_id'][0]] }
    )))
    .then((stationList) => { stations = stationList; });

