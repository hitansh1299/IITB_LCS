// Declare the chart dimensions and margins.

async function get_data(url) {
    const response = await fetch("/getchartingdata?" + url)
    const data = await response.json();
    console.log(data);
    return data
}

async function get_regression_data() {
    const response = await fetch("/getregressiondata")
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
                if (pm == 'timestamp') continue;
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
    $('.nsewdrag').attr('style', 'fill: rgba(212,212,212,0.175); stroke-width: 0; pointer-events: all;');
}

export async function create_regression_plot() {
    console.log("regression plot")
    const rawdata = await get_regression_data()
    var chart = []
    var shapes = []

    //Purple Air Flex II
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_purpleair'],
        mode: 'markers',
        type: 'scatter',
        name: 'Purple Air Flex II<br>R^2 Score: ' + Math.round((rawdata['params']['purpleair']['r2_score'] + Number.EPSILON)*100)/100 + '<br>',
        marker: { color: 'blue' }
    })
    shapes.push({
        x0: rawdata['params']['purpleair']['x'][0],
        y0: rawdata['params']['purpleair']['y'][0],
        x1: rawdata['params']['purpleair']['x'][1],
        y1: rawdata['params']['purpleair']['y'][1],
        type: 'line',
        name: 'Purple Air Flex II',
        line: { color: 'blue' }
    })
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_purpleair_corrected'],
        mode: 'markers',
        type: 'scatter',
        name: 'Purple Air Flex II Corrected <br>R^2 Score: ' + Math.round((rawdata['params']['purpleair_corrected']['r2_score'] + Number.EPSILON)*100)/100 + '<br>',
        marker: { color: 'Cyan' }
    })
    shapes.push({
        x0: rawdata['params']['purpleair_corrected']['x'][0],
        y0: rawdata['params']['purpleair_corrected']['y'][0],
        x1: rawdata['params']['purpleair_corrected']['x'][1],
        y1: rawdata['params']['purpleair_corrected']['y'][1],
        type: 'line',
        name: 'Purple Air Flex II Corrected',
        line: { color: 'Cyan' }
    })

    //AlphaSense OPC N3
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_n3'],
        mode: 'markers',
        type: 'scatter',
        name: 'OPC N3<br>R^2 Score: ' + Math.round((rawdata['params']['n3']['r2_score'] + Number.EPSILON)*100)/100 + '<br>',
        marker: { color: 'red' }
    })
    shapes.push({
        x0: rawdata['params']['n3']['x'][0],
        y0: rawdata['params']['n3']['y'][0],
        x1: rawdata['params']['n3']['x'][1],
        y1: rawdata['params']['n3']['y'][1],
        type: 'line',
        name: 'AlphaSense OPC N3',
        line: { color: 'red' }
    })
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_n3_corrected'],
        mode: 'markers',
        type: 'scatter',
        name: 'OPC N3 Corrected<br>R^2 Score: ' + (Math.round((rawdata['params']['n3_corrected']['r2_score'] + Number.EPSILON)*100)/100) + '<br>',
        marker: { color: 'HotPink' }
    })
    shapes.push({
        x0: rawdata['params']['n3_corrected']['x'][0],
        y0: rawdata['params']['n3_corrected']['y'][0],
        x1: rawdata['params']['n3_corrected']['x'][1],
        y1: rawdata['params']['n3_corrected']['y'][1],
        type: 'line',
        name: 'AlphaSense OPC N3 Corrected',
        line: { color: 'HotPink' }
    })

    //Atmos
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_atmos'],
        mode: 'markers',
        type: 'scatter',
        name: 'Atmos<br>R^2 Score: ' + (Math.round((rawdata['params']['atmos']['r2_score'] + Number.EPSILON)*100)/100) + '<br>',
        marker: { color: 'green' }
    })
    shapes.push({
        x0: rawdata['params']['atmos']['x'][0],
        y0: rawdata['params']['atmos']['y'][0],
        x1: rawdata['params']['atmos']['x'][1],
        y1: rawdata['params']['atmos']['y'][1],
        type: 'line',
        name: 'Atmos',
        line: { color: 'green' }
    })
    chart.push({
        x: rawdata['pm2.5_grimm'],
        y: rawdata['pm2.5_atmos_corrected'],
        mode: 'markers',
        type: 'scatter',
        name: 'Atmos Corrected<br>R^2 Score: ' + (Math.round((rawdata['params']['atmos_corrected']['r2_score'] + Number.EPSILON)*100)/100) + '<br>',
        marker: { color: 'LimeGreen' }
    })
    shapes.push({
        x0: rawdata['params']['atmos_corrected']['x'][0],
        y0: rawdata['params']['atmos_corrected']['y'][0],
        x1: rawdata['params']['atmos_corrected']['x'][1],
        y1: rawdata['params']['atmos_corrected']['y'][1],
        type: 'line',
        name: 'Atmos Corrected',
        line: { color: 'LimeGreen' }
    })

    var OFFSET = 1
    chart.push({
        x: [Math.min(...rawdata['pm2.5_grimm']) - OFFSET, Math.max(...rawdata['pm2.5_grimm']) + OFFSET],
        y: [Math.min(...rawdata['pm2.5_grimm']) - OFFSET, Math.max(...rawdata['pm2.5_grimm']) + OFFSET],
        mode: 'line',
        type: 'scatter',
        name: '1:1 Line',
        line: { color: 'black' }
    })

    var layout = {
        font: { size: 12 },
        autosize: true,
        width: 900,
        height: 600,
        xaxis: { title: 'GRIMM OPC N3 PM2.5' },
        yaxis: { title: 'LCS PM2.5' },
        shapes: shapes,
        margin: {
            t: 50, //top margin
            l: 50, //left margin
            r: 50, //right margin
            b: 50 //bottom margin
        }
    };

    var config = { responsive: true }
    // config = {}
    Plotly.newPlot('chartcontainer', chart, layout, config);
    $('.nsewdrag').attr('style', 'fill: rgba(212,212,212,0.175); stroke-width: 0; pointer-events: all;');
}