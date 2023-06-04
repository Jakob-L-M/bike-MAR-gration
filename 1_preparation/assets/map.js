var map = L.map('map').setView([50.805, 8.769], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let stations = $.getJSON(`/api/stations`, (data) => {
    console.log(data)
    update_stations(data)
})

function update_stations(stations) {
    for (s of stations) {
        L.marker([s.lat, s.lon]).addTo(map)
    }
}