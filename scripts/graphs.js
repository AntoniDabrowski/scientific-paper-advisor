var Plotly = require('plotly.js-strict-dist')

export function create_graph_on_scholar_result(divid, x, y) {
    Plotly.newPlot(divid, [{
            type: 'parcoords',
            line: {
                color: 'blue'
            },

            dimensions: [{
                range: [1, 5],
                constraintrange: [1, 2],
                label: 'A',
                values: [1, 4]
            }, {
                range: [1, 5],
                label: 'B',
                values: [3, 1.5],
                tickvals: [1.5, 3, 4.5]
            }, {
                range: [1, 5],
                label: 'C',
                values: [2, 4],
                tickvals: [1, 2, 4, 5],
                ticktext: ['text 1', 'text 2', 'text 4', 'text 5']
            }, {
                range: [1, 5],
                label: 'D',
                values: [4, 2]
            }]
        }],
        {
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

export function purge_graph(divid) {
    Plotly.purge(divid)
}

