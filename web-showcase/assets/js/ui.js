let current = 'live_analytics'

function show_page(group) {
    $(`.${current}`).hide()
    $(`.${group}`).show()
    current = group

}
    
show_page('map_view')