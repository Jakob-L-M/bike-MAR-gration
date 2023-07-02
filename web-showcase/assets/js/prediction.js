var model;
tf.loadGraphModel('/assets/model/model.json').then((m) => {model = m})

function print_model() {
    console.log(model)
}

function predict(stationId) {
    var y;
    $.getJSON(`/api/prediction_data?stationId=${stationId}`, (data) => {
        let x = tf.tensor([data])
        y = model.predict(x).dataSync().map((x) => Math.round(x))
    })
    return y
}