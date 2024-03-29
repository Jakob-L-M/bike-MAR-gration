const express = require('express');
const dotenv = require('dotenv');
const fetch = (...args) =>
    import ('node-fetch').then(({ default: fetch }) => fetch(...args));
var mysql = require('mysql');
const db_functions = require('./db')

const scrapeSettings = { method: "Get" };

dotenv.config({ path: './.env' });
const conf = dotenv.config().parsed

const DB_CONNECTION = mysql.createConnection({
    host: conf.MYSQL_HOST,
    user: conf.MYSQL_USER,
    password: conf.MYSQL_PASSWORD,
    database: conf.MYSQL_DATABASE,
});

const app = express();

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
    db_functions.get_number_of_trips(DB_CONNECTION, 20)
});

app.get('/assets/*', (req, res) => {
    console.log('sending asset', req.url)
    res.sendFile(__dirname + req.url);
});

app.get('/api/trips_since', async function(req, res) {
    console.log('db request', req.url)
    var result = []
    result.push(await db_functions.get_number_of_trips(DB_CONNECTION, 20)) //1h
    result.push(await db_functions.get_number_of_trips(DB_CONNECTION, 160)) //8h
    result.push(await db_functions.get_number_of_trips(DB_CONNECTION, 480)) //24h
    res.send(result) // list so its not interpreted as status
})

app.get('/api/stations', async function(req, res) {
    console.log('db request', req.url)
    let timestamp = Date.now()

    let timeId = Math.floor(timestamp / (180 * 1000))

    let t = await db_functions.get_bike_distribution(timeId, DB_CONNECTION)

    result = []

    for (let s of t) {
        // only stations that still exist
        result.push({ 'name': s.name, 'lat': s.latitude, 'lon': s.longitude, 'n': s.n, 'id': s.id})
    }
    res.send(result)


})

app.get('/api/trip_details', async function(req, res) {
    console.log('db request', req.url)
    
    if (req.query.origins === undefined || req.query.destinations === undefined
        || req.query.since === undefined || req.query.resSize === undefined) {
            res.send(null)
            return
        }

    res.send((await db_functions.get_trip_details(req.query.origins, req.query.destinations, req.query.since, req.query.resSize, DB_CONNECTION)))
})

app.get('/api/rented_info', async function(req, res) {
    console.log('db request', req.url)
    let timestamp = Date.now()
    let timeId = Math.floor(timestamp / (180 * 1000))

    let total = (await db_functions.get_num_bikes(timeId, DB_CONNECTION))[0].numBikes

    let result = {}
    let bike_info = await db_functions.get_rented_bike_info(timeId, DB_CONNECTION)
    for (i of bike_info) {
        result[i.timeId] = i.numBikes
    }
    res.send([timeId, total, result])
})

app.get('/api/station_history', async function(req, res) {
    console.log('db request', req.url, req.query)
    let timestamp = Date.now()
    let timeId = Math.floor(timestamp / (180 * 1000))

    let stationId = Number(req.query.stationId)
    if (!isNaN(stationId)) {
        res.send(await db_functions.get_station_history(timeId, stationId, DB_CONNECTION))
    } else {
        res.send(null)
        console.log('invalid station id')
    }

})

app.get('/api/prediction_data', async function(req, res) {
    console.log('db request', req.url, req.query)
    let timestamp = Date.now()
    let timeId = Math.floor(timestamp / (180 * 1000))

    let stationId = Number(req.query.stationId)
    if (!isNaN(stationId)) {
        res.send(await db_functions.get_prediction_data(timeId, stationId, DB_CONNECTION))
    } else {
        res.send(null)
        console.log('invalid station id')
    }

})


app.get(`/${conf.SCRAPE_TRIGGER}`, async(req, res) => {
    console.log('Start Scraping')
    let timestamp = Date.now()

    let timeId = Math.round(timestamp / (180 * 1000))

    try {
        await fetch(`http://api.weatherapi.com/v1/current.json?key=${conf.WEATHER_KEY}&q=Marburg&aqi=no`, scrapeSettings)
            .then(res => res.json())
            .then((json) => {
                let cur = json.current

                var sql = `INSERT INTO weather (timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust)
            VALUES (${timeId}, 1, ${cur.temp_c}, ${cur.feelslike_c}, ${cur.is_day}, '${cur.condition.text}', ${cur.cloud}, ${cur.wind_kph}, ${cur.gust_kph})`

                DB_CONNECTION.query(sql, (err, res) => {
                    if (err) console.log(err)
                    else console.log('Pushed weather')
                })
            });

    } catch (e) {
        console.log(e)
    }

    try {
        await fetch(`https://maps.nextbike.net/maps/nextbike-live.json?city=438&domains=nm&list_cities=0&bikes=0`, scrapeSettings)
            .then(res => res.json())
            .then(async(json) => {
                let stations = json.countries[0].cities[0].places
                for (let station of stations) {

                    if (!station.bike) { // station is a bike
                        var sql = `INSERT INTO stations (id, name, latitude, longitude, firstSeen, lastSeen, cityId)
                VALUES (${station.uid}, '${station.name}', ${station.lat}, ${station.lng}, ${timeId}, ${timeId}, 1)
                ON DUPLICATE KEY UPDATE
                firstSeen = CASE WHEN firstSeen < VALUES(firstSeen) THEN firstSeen ELSE VALUES(firstSeen) END,
                lastSeen = CASE WHEN lastSeen > VALUES(lastSeen) THEN lastSeen ELSE VALUES(lastSeen) END;`

                        DB_CONNECTION.query(sql, (err, res) => {
                            if (err) console.log(err)
                        })

                        for (let bike of station.bike_numbers) {
                            var sql = `INSERT INTO bikes (id, timeId, stationId, latitude, longitude)
                    VALUES (${bike}, ${timeId}, ${station.uid}, NULL, NULL)`
                            DB_CONNECTION.query(sql, (err, res) => {
                                if (err) console.log(err)
                            })
                        }
                    } else { // station less bike
                        var sql = `INSERT INTO bikes (id, timeId, stationId, latitude, longitude)
                    VALUES (${station.bike_numbers[0]}, ${timeId}, NULL, ${station.lat}, ${station.lng})`

                        DB_CONNECTION.query(sql, (err, res) => {
                            if (err) console.log(err)
                        })
                    }

                }
            })
    } catch (e) {
        console.log(e)
    }
    await db_functions.update_trips(DB_CONNECTION)

    res.send('Done')
})

var http = require('http');

/**
 * Get port from environment and store in Express.
 */

var port = normalizePort(process.env.PORT || '3000');
app.set('port', port);

/**
 * Create HTTP server.
 */

var server = http.createServer(app);

/**
 * Listen on provided port, on all network interfaces.
 */

server.listen(port);

server.on('listening', onListening);

/**
 * Normalize a port into a number, string, or false.
 */

function normalizePort(val) {
    var port = parseInt(val, 10);

    if (isNaN(port)) {
        // named pipe
        return val;
    }

    if (port >= 0) {
        // port number
        return port;
    }

    return false;
}

function onListening() {
    var addr = server.address();
    var bind = typeof addr === 'string' ?
        'pipe ' + addr :
        'port ' + addr.port;
    console.log('Listening on ' + bind);
}

async() => {
    let response = await pusher.devices();

    console.log(response)
}