async function get_bike_distribution(timeId, DB) {
    sql = `SELECT * FROM stations;`

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
    get_bike_distribution
}