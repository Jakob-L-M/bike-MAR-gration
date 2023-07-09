var tripMap = L.map('tripMap')


tripMap.setView([50.805, 8.769], 14);

var tripLines = L.layerGroup().addTo(tripMap);

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

    // console.log(fromStr, toStr, timeInfo.value, resultSize.value)

    // call api
    $.getJSON(`/api/trip_details?origins=${fromStr}&destinations=${toStr}&since=${timeInfo.value}&resSize=${resultSize.value}`, (data) => {
        //console.log(data)
        
        // clear current table
        $('#tripTable tbody tr').remove()
        // clear trip map
        tripLines.clearLayers()

        // display result
        var table = $('#tripTable tbody')
        for (let trip of data) {
            // console.log(trip)

            let origin = stations[inverted_station_index[trip.stationFrom]]
            let destination = stations[inverted_station_index[trip.stationTo]]

            let row = `<tr
                class="border-b transition duration-300 ease-in-out hover:bg-blue-300"
                id = _${origin.id}_${destination.id}>
                <td class="whitespace-nowrap px-6 py-4 font-medium">${trip.numTrips}</td>
                <td class="whitespace-nowrap px-6 py-4">${origin.name}</td>
                <td class="whitespace-nowrap px-6 py-4">${destination.name}</td>
                </tr>`
            table.append(row)

            var line = L.polyline([[origin.lat, origin.lon], [destination.lat, destination.lon]], {color: '#ea580c',className: `_${origin.id}_${destination.id}`}).arrowheads({
                yawn: 40,
                fill: true,
                size: '20px',
                color: '#ea580c' // orange-600
              });
            line.addTo(tripLines)

            // #22d3ee cyan-400
            $(`#_${origin.id}_${destination.id}`).on('mouseover', (e) => {
                let hoverId = e.currentTarget.id
                
                for (let i of $(`.${hoverId}`)) {
                    i.style.stroke = '#22d3ee'
                    i.style.fill = '#22d3ee'
                    i.style.zIndex = '10000'
                }

                // ensuring visibility
                moveUp($(`.${hoverId}`))
            })

            $(`#_${origin.id}_${destination.id}`).on('mouseout', (e) => {
                let hoverId = e.currentTarget.id
                
                for (let i of $(`.${hoverId}`)) {
                    i.style.stroke = '#ea580c'
                    i.style.fill = '#ea580c'
                    i.style.zIndex = '-1'
                }
            })

        }

    })

}

// helper function for zIndex enforcement on svg elements
function moveUp(thisObject){
    thisObject.appendTo(thisObject.parents('svg>g'));
}
