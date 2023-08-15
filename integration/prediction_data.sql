WITH base AS (
    SELECT
        s.id,
        b.timeId,
        s.cityId,
        s.latitude,
        s.longitude
    FROM
        (
            SELECT * FROM stations WHERE id = ${stationId}
        ) s
        CROSS JOIN 
        (
            SELECT DISTINCT timeId FROM bikes WHERE timeId >= ${timeId - 40}
        ) b 
), main AS (
    SELECT 
        base.*, 
        w.temp, 
        w.feelsLikeTemp, 
        w.isDay, 
        w.description, 
        w.cloud, 
        w.wind, 
        w.gust, 
        COALESCE(e."group", 0) AS "group", 
        COALESCE(n, 0) AS nBikes 
    FROM 
        base 
    LEFT JOIN 
        ( SELECT timeId, COUNT(id) AS n FROM bikes WHERE stationId = ${stationId} AND timeId >= ${timeId - 40} GROUP BY timeId) sInfo ON 
    base.timeId = sInfo.timeId JOIN weather w ON w.cityId = base.cityId AND base.timeId = w.timeId LEFT OUTER JOIN events e ON
    TO_DAYS(e."date") = TO_DAYS(FROM_UNIXTIME(base.timeId * 180)) )

SELECT
    main.*, 
    b2.nBikes AS 't-6', 
    b5.nBikes AS 't-15', 
    b10.nBikes AS 't-30', 
    b20.nBikes AS 't-60', 
    b40.nBikes AS 't-120'
FROM 
    main
JOIN main b2 ON main.timeId = b2.timeId + 2 
JOIN main b5 ON main.timeId = b5.timeId + 5 
JOIN main b10 ON main.timeId = b10.timeId + 10 
JOIN main b20 ON main.timeId = b20.timeId + 20 
JOIN main b40 ON main.timeId = b40.timeId + 40