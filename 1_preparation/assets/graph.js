function display_rented_info() {

    $.getJSON('/api/rented_info', (data) => {

        console.log(data)
        let timeId = data[0]
        let total = data[1]
        let values = data[2]
        // label array
        let l = []
        let v = []

        for (let i = timeId - 59; i <= timeId; i++) {
            // there exists a value for the given timeId
            if (i in values) {
                v.push(total - values[i])
                l.push(new Date((i * 180 - 60*(new Date().getTimezoneOffset())) * 1000).toISOString().substring(11, 16))
            } else {
                v.push(NaN)
                l.push(new Date((i * 180 - 60*(new Date().getTimezoneOffset())) * 1000).toISOString().substring(11, 16))
            }
        }
            let d = [{
                backgroundColor: "#4c51bf",
                borderColor: "#4c51bf",
                data: v,
                fill: false,
                spanGaps: true
            }]

        document.getElementById('current_bikes').innerHTML = d[d.length - 1].data[d[d.length - 1].data.length - 1]
        
        var config = {
            type: "line",
            data: {
                labels: l,
                datasets: d
            },
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
        var ctx = document.getElementById("rented-chart").getContext("2d");
        window.myLine = new Chart(ctx, config);
    })
}

display_rented_info()