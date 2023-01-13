var Plotly = require('plotly.js-strict-dist')

function create_text_for_graph(nodes) {
    let result = [];

    for (let i = 0; i < nodes.length; i++) {
        let node_dict = nodes[i]
        result.push(`<a href="${node_dict['url']}">${node_dict['title']}</a>` +
            `<br>Authors: ${node_dict['authors']}<br>#citations: ${node_dict['num_publications']}`)
    }

    return result;
}

export function create_graph_on_scholar_result(divid, json) {
    console.debug(json)
    let x = [];
    let y = [];
    let point_size = [];
    for (let key in json.layout) {
        x.push(json.layout[key][0])
        y.push(json.layout[key][1])
    }
    for (let i = 0; i < json.nodes.length; i++) {
        point_size.push(json.nodes[i]['num_publications'])
    }

    const text = create_text_for_graph(json.nodes)

    console.debug(x)
    console.debug(y)
    console.debug(point_size)


    Plotly.newPlot(divid, [{
        x: x,
        y: y,
        text: text,
        mode: 'markers',
        marker: {
            size: point_size,
            sizemode: 'area'
        }
    }])
}

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

