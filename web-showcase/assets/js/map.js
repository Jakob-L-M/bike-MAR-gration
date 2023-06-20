var map = L.map('map').setView([50.805, 8.769], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var stationMarkers = L.layerGroup().addTo(map);
var stations = []

const radius = 200

function update_stations() {
    
    stationMarkers.clearLayers();

    $.getJSON(`/api/stations`, (data) => {

        stations = data

        for (let station of data) {
            let m = L.marker([station.lat, station.lon])
            m.bindTooltip(`${station.n}`, { permanent: true, offset: [0, 0], clickable: false });
            m.addTo(stationMarkers)
        }
        setTimeout(update_stations, 60000); // update every minute to ensure up-to-date data
    })

    // also auto update trip info
    update_trip_info()
    
}

update_stations()

map.on('click', function(e) {
    // remove all current divs
    $("div.station-pred").remove();

    let click_lat = e.latlng.lat
    let click_lng = e.latlng.lng
    for (let station of stations) {
        if (meter_dist(click_lat, click_lng, station.lat, station.lon) < radius) {
            console.log(station.name)
            create_station_prediction(station.name)
        }
    }
});