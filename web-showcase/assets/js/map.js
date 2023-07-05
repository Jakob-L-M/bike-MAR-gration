var map = L.map('map').setView([50.805, 8.769], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    minZoom: 11,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var stationMarkers = L.layerGroup().addTo(map);
var stations = []

const radius = 100
var firstLoad = true

function update_stations() {

    stationMarkers.clearLayers();

    $.getJSON(`/api/stations`, (data) => {

        stations = data

        for (let station of data) {
            let m = L.marker([station.lat, station.lon], { 'icon': getIcon(station.n) })
            m.addTo(stationMarkers)
        }
        setTimeout(update_stations, 60000); // update every minute to ensure up-to-date data
    })

    if (firstLoad) {
        fill_dropdown(stations)
    }

    firstLoad = false

    // also auto update trip info
    update_trip_info()

}
update_stations()

map.on('click', async (e) => {
    // remove all current divs
    $("div.station-pred").remove();

    let click_lat = e.latlng.lat
    let click_lng = e.latlng.lng
    let temp = []
    for (let station of stations) {
        if (meter_dist(click_lat, click_lng, station.lat, station.lon) < radius) {
            temp.push(station)
            create_station_div(station.name, station.id)
        }
    }
    await new Promise(r => setTimeout(r, 400));
    for (let station of temp) {
        create_station_graphs(station.id)
    }
});