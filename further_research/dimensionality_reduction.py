from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd


def parse_hovers(docs):
    hovers = []

    for doc in docs:
        new_doc = ""
        current_line = ""
        for word in doc.split():
            if len(current_line) + len(word) > 100:
                new_doc += current_line + '<br>'
                current_line = ""
            current_line += ' ' + word
        if current_line:
            new_doc += current_line + '<br>'
        hovers.append(new_doc)
    return hovers


def dimensionality_reduction(vectors, labels, docs):
    pca = PCA(n_components=3)
    pca.fit(vectors)
    reduced_vectors = pca.transform(vectors)
    hovers = parse_hovers(docs.values())

    df = pd.DataFrame(data={
        'x': reduced_vectors[:, 0],
        'y': reduced_vectors[:, 1],
        'z': reduced_vectors[:, 2],
        'labels': [str(label) for label in labels],
        'hover': hovers
    })

    fig = px.scatter_3d(df,
                        x='x',
                        y='y',
                        z='z',
                        color='labels',
                        custom_data=['hover'],
                        color_discrete_map={
                            "0": 'rgb(255, 150, 150)',
                            "1": 'rgb(150, 255, 150)',
                            "2": 'rgb(150, 150, 255)',
                            "3": "red",
                            "4": "green",
                            "5": "blue"})

    fig.update_layout(
        hoverlabel=dict(
            font_size=12
        ),
        title='Further research clustering',
        showlegend=False
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}",
        marker_size=4
    )

    fig.show()
