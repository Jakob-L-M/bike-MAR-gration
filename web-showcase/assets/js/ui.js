let current = 'map_view'

function show_page(group) {
    $(`.${current}`).toggleClass('hidden')
    $(`.${group}`).toggleClass('hidden')
    current = group

}

function update_trip_info() {
    $.getJSON(`/api/trips_since`, (data) => {
        document.getElementById('trips_1h').innerHTML = data[0]
        document.getElementById('trips_8h').innerHTML = data[1]
        document.getElementById('trips_24h').innerHTML = data[2]
    })
}