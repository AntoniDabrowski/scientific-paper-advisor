from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE


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


def remove_outliers(reduced_vectors, labels, hovers):
    center = reduced_vectors.mean(axis=0)

    MSE = [np.mean((center - vector) ** 2) for vector in reduced_vectors]

    avg_MSE = np.mean(MSE)
    std_MSE = np.std(MSE)

    new_vectors = []
    new_labels = []
    new_hovers = []

    for vector, label, hover, MSE_single in zip(reduced_vectors, labels, hovers, MSE):
        if MSE_single < avg_MSE + 2 * std_MSE:
            new_vectors.append(vector)
            new_labels.append(label)
            new_hovers.append(hover)

    return np.array(new_vectors), new_labels, new_hovers


def dimensionality_reduction(vectors, labels, docs, alg='t-SNE', cut_outliers=False):
    if alg == 'PCA':
        pca = PCA(n_components=3)
        pca.fit(vectors)
        reduced_vectors = pca.transform(vectors)
    elif alg == 't-SNE':
        tsne = TSNE(n_components=3, learning_rate='auto', init='random', perplexity=3)
        reduced_vectors = tsne.fit_transform(vectors)
    else:
        raise ValueError(f"Dimensionality reduction can be only performed with algorithm PCA or t-SNE, not {alg}")

    hovers = docs.values()
    if cut_outliers:
        reduced_vectors, labels, hovers = remove_outliers(reduced_vectors, labels, hovers)
    hovers = parse_hovers(hovers)

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
