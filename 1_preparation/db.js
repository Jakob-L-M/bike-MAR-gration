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

module.exports = {
    get_bike_distribution,
    get_rented_bike_info,
    get_num_bikes
}