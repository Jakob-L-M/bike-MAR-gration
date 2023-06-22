var config = {
    type: "line",
    options: {
        maintainAspectRatio: false,
        responsive: true,
        title: {
            display: false,
            text: "Sales Charts",
            fontColor: "white"
        },
        legend: {
            display: false
        },
        tooltips: {
            mode: "index",
            intersect: false
        },
        hover: {
            mode: "nearest",
            intersect: true
        },
        scales: {
            xAxes: [{
                ticks: {
                    fontColor: "rgba(0,0,0,.7)"
                },
                display: true,
                scaleLabel: {
                    display: false,
                    labelString: "Month",
                    fontColor: "black"
                },
                gridLines: {
                    display: false,
                    borderDash: [2],
                    borderDashOffset: [2],
                    color: "rgba(33, 37, 41, 0.3)",
                    zeroLineColor: "rgba(0, 0, 0, 0)",
                    zeroLineBorderDash: [2],
                    zeroLineBorderDashOffset: [2]
                }
            }],
            yAxes: [{
                ticks: {
                    fontColor: "rgba(0,0,0,.7)"
                },
                display: true,
                scaleLabel: {
                    display: false,
                    labelString: "Value",
                    fontColor: "white"
                },
                gridLines: {
                    borderDash: [3],
                    borderDashOffset: [3],
                    drawBorder: false,
                    color: "rgba(0, 0, 0, 0.15)",
                    zeroLineColor: "rgba(33, 37, 41, 0)",
                    zeroLineBorderDash: [2],
                    zeroLineBorderDashOffset: [2]
                }
            }]
        }
    }
};

function display_rented_info() {

    $.getJSON('/api/rented_info', (data) => {

        let timeId = data[0]
        let total = data[1]
        let values = data[2]
            // label array
        let l = []
        let v = []

        for (let i = timeId - 29; i <= timeId; i++) {
            // there exists a value for the given timeId
            if (i in values) {
                v.push(total - values[i])
                l.push(new Date((i * 180 - 60 * (new Date().getTimezoneOffset())) * 1000).toISOString().substring(11, 16))
            } else {
                v.push(NaN)
                l.push(new Date((i * 180 - 60 * (new Date().getTimezoneOffset())) * 1000).toISOString().substring(11, 16))
            }
        }
        let d = {
            backgroundColor: "#ea580c",
            borderColor: "#ea580c",
            data: v,
            fill: false,
            spanGaps: true
        }

        document.getElementById('current_bikes').innerHTML = d.data[d.data.length - 1]


        let ctx = document.getElementById("rented-chart").getContext("2d");
        let temp = {...config}
        temp['data'] = {
            labels: l,
            datasets: [d]
        }
        window.myLine = new Chart(ctx, temp);
    })
}

display_rented_info()

function create_station_div(name, id) {
    $('#map-predictions').append(`
    <div class="w-full xl:w-6/12 mb-12 xl:mb-0 px-4 station-pred">
        <div class="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded bg-white">
            <div class="rounded-t mb-0 px-4 py-3 bg-transparent">
                <div class="flex flex-wrap items-center">
                    <div class="relative w-full max-w-full flex-grow flex-1">
                        <h6 class="uppercase text-blueGray-100 mb-1 text-xs font-semibold">
                            Station Prediction
                        </h6>
                        <h2 class="text-blueGray-100 text-xl font-semibold">
                            ${name}
                        </h2>
                    </div>
                </div>
            </div>
            <div class="p-4 flex-auto">
                <!-- Chart -->
                <div class="relative chart">
                    <canvas id="_${id}-line-chart"></canvas>
                </div>
            </div>
        </div>
    </div>
    `)
}

function create_station_graphs(name, id) {
    $.getJSON(`/api/station_history?stationId=${id}`, (data) => {

        console.log(data)

        let l = []
        let v = []

        for (let i = data.length-1; i >= 0; i -= 10) {
            v.push(data[i].n)
            l.push(new Date((data[i].timeId * 180 - 60 * (new Date().getTimezoneOffset())) * 1000).toISOString().substring(11, 16))
        }
        l[l.length - 1] = 'now'
        let d = {
            backgroundColor: "#ea580c",
            borderColor: "#ea580c",
            data: v,
            fill: false,
            spanGaps: true
        }
        console.log(d, l, name, id)

        let temp = {...config}
        temp['data'] = {
            labels: l,
            datasets: [d]
        }
        window.myLine = new Chart(document.getElementById(`_${id}-line-chart`).getContext("2d"), temp);
    })
}