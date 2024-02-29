// Declare the chart dimensions and margins.

async function get_data(url) {
    const response = await fetch("/getchartingdata?" + url)
    const data = await response.json();
    console.log(data);
    return data
}

/*
@params:
start: the start date and time
end: the end date and time
y: an object of datas, ie {opc: [], purpleair:[]...}
*/
export async function chartData(serializedURL) {
    console.log(serializedURL)
    const rawdata = await get_data(serializedURL)

    console.log(rawdata)
    var chart = []
    for (let sensor in rawdata) {
        console.log(sensor)
        for (let series in rawdata[sensor]) {
            console.log(series)
            for (let pm in rawdata[sensor][series]) {
                if(pm == 'timestamp') continue;
                chart.push({
                    x: rawdata[sensor][series]['timestamp'],
                    y: rawdata[sensor][series][pm],
                    type: 'scatter',
                    name: sensor.split('_')[1].toUpperCase() + "_" + pm,
                })
            }
        }
    }

    var layout = {
        font: { size: 12 }
    };

    var config = { responsive: true }
    Plotly.newPlot('chartcontainer', chart, layout, config);
}