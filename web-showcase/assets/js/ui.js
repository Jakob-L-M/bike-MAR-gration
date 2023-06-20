let current = 'live_analytics'

function show_page(group) {
    $(`.${current}`).hide()
    $(`.${group}`).show()
    current = group

}

show_page('map_view')

function update_trip_info() {
    $.getJSON(`/api/trips_since`, (data) => {
        console.log('ui', data)
        document.getElementById('trips_1h').innerHTML = data[0]
        document.getElementById('trips_8h').innerHTML = data[1]
        document.getElementById('trips_24h').innerHTML = data[2]
    })
}

update_trip_info()