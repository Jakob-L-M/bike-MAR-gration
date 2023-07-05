let current = 'map_view'

function show_page(group) {
    $(`.${current}`).toggleClass('hidden')
    $(`.${group}`).toggleClass('hidden')
    current = group
    tripMap.invalidateSize();
}

function update_trip_info() {
    $.getJSON(`/api/trips_since`, (data) => {
        document.getElementById('trips_1h').innerHTML = data[0]
        document.getElementById('trips_8h').innerHTML = data[1]
        document.getElementById('trips_24h').innerHTML = data[2]
    })
}

function fill_dropdown(stations) {
    let tripsFrom = document.getElementById('stationFrom')
    let tripsTo = document.getElementById('stationTo')
    for (s of stations) {
        let opt = document.createElement('option')
        opt.text = s.name
        opt.value = s.id
        tripsFrom.add(opt)

        opt = document.createElement('option')
        opt.text = s.name
        opt.value = s.id
        tripsTo.add(opt)
    }
}