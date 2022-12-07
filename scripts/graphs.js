var Plotly = require('plotly.js-strict-dist')

export function create_graph_on_scholar_result(divid, x, y) {
    Plotly.newPlot(divid, [{
        x: x,
        y: y
    }], {
        sliders: [{
            pad: {t: 30},
            currentvalue: {
                xanchor: 'right',
                prefix: 'color: ',
                font: {
                    color: '#888',
                    size: 20
                }
            },
            steps: [{
                label: 'red',
                method: 'restyle',
                args: ['line.color', 'red']
            }, {
                label: 'green',
                method: 'restyle',
                args: ['line.color', 'green']
            }, {
                label: 'blue',
                method: 'restyle',
                args: ['line.color', 'blue']
            }]
        }]
    });
}

