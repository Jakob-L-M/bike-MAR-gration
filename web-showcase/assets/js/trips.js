var tripMap = L.map('tripMap')


tripMap.setView([50.805, 8.769], 14);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    minZoom: 11,
    maxZoom: 18,
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(tripMap);

function update_trip_details() {

    // read inputs
    let stationFrom = document.getElementById('stationFrom')
    let stationTo = document.getElementById('stationTo')
    let timeInfo = document.getElementById('tripTime')
    let resultSize = document.getElementById('tripRes')

    var selectedOrigins = []
    var selectedDestinations = []

    for (o of stationFrom.options) {
        if (o.selected) selectedOrigins.push(o.value)
    }

    for (o of stationTo.options) {
        if (o.selected) selectedDestinations.push(o.value)
    }

    // require some origin and some destination to be selected
    if (selectedOrigins.length == 0 || selectedDestinations.length == 0) return

    let fromStr = '(' + selectedOrigins.toString() + ')'
    let toStr = '(' + selectedDestinations.toString() + ')'

    console.log(fromStr, toStr, timeInfo.value, resultSize.value)

    // call api
    $.getJSON(`/api/trip_details?origins=${fromStr}&destinations=${toStr}&since=${timeInfo.value}&resSize=${resultSize.value}`, (data) => {
        console.log(data)
    })

    // display result
}
