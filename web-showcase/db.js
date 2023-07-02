async function get_bike_distribution(timeId, DB) {
    sql = `SELECT id, name, latitude, longitude, COALESCE(numBikes, 0) as n FROM (SELECT * FROM stations WHERE firstSeen <= ${timeId} AND lastSeen >= ${timeId}) s LEFT OUTER JOIN (SELECT stationId, COUNT(id) as numBikes from bikes WHERE timeId = ${timeId} GROUP BY stationId) b 
    ON s.id = b.stationId;`

    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                res(result)
            }
        })

    }))
}

async function get_rented_bike_info(timeId, DB) {
    sql = `SELECT timeId, COUNT(DISTINCT id) as numBikes FROM bikes WHERE timeId BETWEEN ${timeId - 29} AND ${timeId} GROUP BY timeId`

    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                res(result)
            }
        })

    }))
}

async function get_prediction_data(timeId, stationId, DB) {
    sql = `WITH base AS( SELECT s.id, b.timeId, s.cityId, s.latitude, s.longitude FROM ( SELECT * FROM stations WHERE id = ${stationId}) s CROSS JOIN 
    ( SELECT DISTINCT timeId FROM bikes WHERE timeId >= ${timeId - 40} ) b ), main AS 
    ( SELECT base.*, w.temp, w.feelsLikeTemp, w.isDay, w.description, w.cloud, w.wind, w.gust, COALESCE(e.\`group\`, 0) AS \`group\`, COALESCE(n, 0) AS nBikes FROM base LEFT JOIN 
    ( SELECT timeId, COUNT(id) AS n FROM bikes WHERE stationId = ${stationId} AND timeId >= ${timeId - 40} GROUP BY timeId) sInfo ON 
    base.timeId = sInfo.timeId JOIN weather w ON w.cityId = base.cityId AND base.timeId = w.timeId LEFT OUTER JOIN events e ON
    TO_DAYS(e.\`date\`) = TO_DAYS(FROM_UNIXTIME(base.timeId * 180)) )
    SELECT main.*, b2.nBikes AS 't-6', b5.nBikes AS 't-15', b10.nBikes AS 't-30', b20.nBikes AS 't-60', b40.nBikes AS 't-120'
    FROM main JOIN main b2 ON main.timeId = b2.timeId + 2 JOIN main b5 ON main.timeId = b5.timeId + 5 
    JOIN main b10 ON main.timeId = b10.timeId + 10 JOIN main b20 ON main.timeId = b20.timeId + 20 JOIN main b40 ON main.timeId = b40.timeId + 40`

    let possibilities = ["Sunny", "Clear", "Partly cloudy", "Mist", "Cloudy", "Overcast", "Fog", "Patchy light drizzle", "Patchy rain possible", "Patchy light rain", "Light rain shower", "Light drizzle", "Light rain", "Freezing fog", "Moderate rain at times", "Patchy snow possible", "Patchy light snow", "Patchy sleet possible", "Light snow showers", "Light sleet showers", "Light snow", "Light freezing rain", "Light sleet", "Moderate rain", "Patchy light rain with thunder", "Patchy moderate snow", "Moderate snow", "Patchy heavy snow", "Thundery outbreaks possible", "Thunder outbreaks possible", "Moderate or heavy rain shower", "Moderate or heavy snow showers", "Heavy rain at times", "Moderate or heavy sleet", "Heavy snow", "Moderate or heavy rain with thunder", "Blizzard"]
    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                if (result.length < 1) {
                    res([NaN])
                } else {
                    console.log(result)
                    let r = result[0]
                    let d = new Date(r.timeId * 180 * 1000)
                    let wd = d.getDay()
                    let time_float = (d.getHours()/24 + d.getMinutes()/1440) * 2 * Math.PI
                    res([(wd & 4)>>2, (wd & 2)>>1, wd & 1, // weekdays
                        Math.sin(time_float), Math.cos(time_float), // timeX/Y
                        r.latitude, r.longitude, r.temp, r.feelsLikeTemp,
                        possibilities.indexOf(r.description)/possibilities.length,
                        r.cloud, r.wind, r.gust, r.group, r.nBikes,
                        r['t-6'], r['t-15'], r['t-30'], r['t-60'], r['t-120']
                    ])
                }
            }
        })

    }))
}


async function get_station_history(timeId, stationId, DB) {
    sql = `SELECT t.timeId, COALESCE(b.n, 0) as n FROM (SELECT id FROM stations WHERE id = ${stationId}) s CROSS JOIN (SELECT DISTINCT timeId FROM bikes WHERE timeId > ${timeId-10}) t LEFT JOIN 
    (SELECT timeId, COUNT(id) AS n FROM bikes WHERE timeId >= ${timeId-10} AND stationId = ${stationId} GROUP BY timeId) b ON t.timeId = b.timeId ORDER BY t.timeId`

    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                res(result)
            }
        })

    }))
}

async function get_number_of_trips(DB, since) {
    // since is the number of 3min intervals
    sql = `SELECT COUNT(*) AS n FROM trips
    WHERE ROUND(UNIX_TIMESTAMP(CURTIME(4))/180) - endTime <= ${since}
    AND nextStartTime IS NOT NULL`

    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                res(result[0].n)
            }
        })

    }))
}

async function get_num_bikes(timeId, DB) {
    sql = `SELECT COUNT(DISTINCT id) as numBikes FROM bikes WHERE timeId BETWEEN ${timeId - 120} AND ${timeId}`

    return await (new Promise((res, rej) => {
        DB.query(sql, (err, result) => {
            if (err) {
                console.log(err)
                rej(err)
            } else {
                res(result)
            }
        })

    }))
}

async function update_trips(DB) {
    DB.query("SELECT id, startTime FROM (SELECT DISTINCT id FROM bikes WHERE timeId = (SELECT MAX(timeId) FROM bikes)) b LEFT JOIN ( SELECT bikeId, MAX(startTime) as startTime FROM trips GROUP BY bikeId) t ON b.id = t.bikeId;", async(err, res) => {
        if (err) {
            console.log(err);
            return
        }

        for (let bike of res) {
            await update_bike_trips(DB, bike.id, bike.startTime)
        }
    })
}

async function update_bike_trips(DB, bike_id, start) {
    if (start === undefined) start = 0

    await new Promise((main_res, main_rej) => {
        DB.query(`SELECT * FROM bikes WHERE id = ${bike_id} AND timeId >= ${start} ORDER BY timeId`, async(err, res) => {
            if (err) {
                console.log(err);
                return
            }

            let next_known = start
            let trips = []

            for (let record of res) {
                if (record.timeId >= next_known) {
                    // find the end of the trip aka next station
                    stationId = record.stationId != null ? record.stationId : 'NULL'
                    lat = record.latitude != null ? record.latitude : 'NULL'
                    lon = record.longitude != null ? record.longitude : 'NULL'

                    await new Promise((res, rej) => {
                        DB.query(`SELECT * FROM bikes WHERE id = ${bike_id} AND timeId > ${record.timeId} AND NOT (stationId <=> ${stationId} AND latitude <=> ${lat} AND longitude <=> ${lon}) ORDER BY timeId LIMIT 1;`, (err, next_station) => {
                            if (err) {
                                console.log(err);
                                rej(err)
                                return
                            }
                            let sql = ""
                            let has_next = next_station.length > 0
                            if (!has_next) {
                                sql = `SELECT id, stationId, latitude, longitude, MIN(timeId) AS start, MAX(timeId) AS end FROM bikes WHERE id = ${bike_id} AND timeId >= ${record.timeId} GROUP BY id, stationId, latitude, longitude`
                            } else {
                                sql = `SELECT id, stationId, latitude, longitude, MIN(timeId) AS start, MAX(timeId) AS end FROM bikes WHERE id = ${bike_id} AND timeId BETWEEN ${record.timeId} AND ${next_station[0].timeId} GROUP BY id, stationId, latitude, longitude`
                            }
                            DB.query(sql, (err, trip) => {
                                if (err) {
                                    console.log(err);
                                    rej(err)
                                    return
                                }
                                let t = trip[0]
                                trips.push([bike_id, t.start, t.end, t.stationId, t.latitude, t.longitude,
                                    has_next ? next_station[0].stationId : null,
                                    has_next ? next_station[0].timeId : null
                                ])

                                next_known = t.end + 1
                                res(next_station)
                            })
                        })
                    })
                }
            }
            q = 'REPLACE INTO `trips` VALUES \n'
            for (let t of trips) {
                sql = t.toString().replaceAll(',,', ',NULL,').replaceAll(',,', ',NULL,')
                if (sql.slice(-1) == ',') {
                    sql = sql + 'NULL'
                }
                sql = '(' + sql + '),'
                q += sql
            }
            q = q.substring(0, q.length - 1) + ';'
            DB.query(q, (err, res) => {
                if (err) console.log(err)
            })


            main_res(true)
        })
    })
}

module.exports = {
    get_bike_distribution,
    get_rented_bike_info,
    get_num_bikes,
    get_number_of_trips,
    update_trips,
    get_station_history,
    get_prediction_data
}