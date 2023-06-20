var icons = []

for (let i = 0; i <= 10; i++) {
    icons.push(L.icon({
        iconUrl: `/assets/img/m${i}.png`,
    
        iconSize:     [32, 32], // size of the icon
        iconAnchor:   [16, 16], // point of the icon which will correspond to marker's location
    }))
}