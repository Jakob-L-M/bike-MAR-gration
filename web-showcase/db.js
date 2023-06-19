async function get_bike_distribution(timeId, DB) {
    sql = `SELECT name, latitude, longitude, COALESCE(numBikes, 0) as n FROM (SELECT * FROM stations WHERE firstSeen <= ${timeId} AND lastSeen >= ${timeId}) s LEFT OUTER JOIN (SELECT stationId, COUNT(id) as numBikes from bikes WHERE timeId = ${timeId} GROUP BY stationId) b 
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
    sql = `SELECT timeId, COUNT(DISTINCT id) as numBikes FROM bikes WHERE timeId BETWEEN ${timeId - 59} AND ${timeId} GROUP BY timeId`

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
    DB.query("SELECT id, startTime FROM (SELECT DISTINCT id FROM bikes WHERE timeId >= (SELECT MAX(timeId) FROM bikes)) b LEFT JOIN ( SELECT bikeId, MAX(startTime) as startTime FROM trips GROUP BY bikeId) t ON b.id = t.bikeId;", async (err, res) => {
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
        DB.query(`SELECT * FROM bikes WHERE id = ${bike_id} AND timeId >= ${start} ORDER BY timeId`, async (err, res) => {
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
                                    has_next ? next_station[0].timeId : null])

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
    update_trips
}