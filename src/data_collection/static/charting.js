import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// Declare the chart dimensions and margins.

async function get_data(start, end, sensor) {
    const response = await fetch('/getData/' + new URLSearchParams({
        'start': start,
        'end': end,
        'sensor': sensor
    }).toString())
    const data = await response.json();
    console.log(data);
}

/*
@params:
start: the start date and time
end: the end date and time
y: an object of datas, ie {opc: [], purpleair:[]...}
*/
function chart(start, end, y_) {
    const width = 1920;
    const height = 600;
    const marginTop = 20;
    const marginRight = 20;
    const marginBottom = 30;
    const marginLeft = 40;

    // Declare the x (horizontal position) scale.
    const x = d3.scaleUtc()
        .domain([new Date("2023-01-01"), new Date("2024-01-01")])
        .range([marginLeft, width - marginRight]);

    // Declare the y (vertical position) scale.
    const y = d3.scaleLinear()
        .domain([0, 100])
        .range([height - marginBottom, marginTop]);

    // Create the SVG container.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height);

    // Add the x-axis.
    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x));

    // Add the y-axis.
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y));

    // Append the SVG element.
    chartcontainer.append(svg.node());
}

chart(null, null, null);