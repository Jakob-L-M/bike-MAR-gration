var tripMap = L.map('tripMap')

tripMap.on("load", function () {
    setTimeout(() => {
        tripMap.invalidateSize();
    }, 2000);
}); // ensuring proper map display
// https://stackoverflow.com/questions/38832273/leafletjs-not-loading-all-tiles-until-moving-map

tripMap.setView([50.805, 8.769], 13);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(tripMap);
