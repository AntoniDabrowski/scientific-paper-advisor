var Plotly = require('plotly.js-strict-dist')

export function create_graph_on_scholar_result(divid, json) {
    Plotly.newPlot(divid,
};

/*
export function create_graph_on_scholar_result(divid, json) {
    Plotly.newPlot(divid, [{
            x: x,
            y: y,
            text: ['A<br>size: 40', 'B<br>size: 60', 'C<br>size: 80', 'D<br>size: 100', 'E<br>size: 80'],
            mode: 'markers',
            marker: {
                size: [400, 600, 800, 1000, 800],
                sizemode: 'area'
            }
        },
            {
                x: x,
                y: y,
            }
        ],
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
*/


export function purge_graph(divid) {
    Plotly.purge(divid)
}

