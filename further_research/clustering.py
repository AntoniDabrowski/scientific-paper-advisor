from sklearn.cluster import KMeans


def get_centroids(current_labels, dists):
    current_labels[dists[:, 0].argmin()] = 3
    current_labels[dists[:, 1].argmin()] = 4
    current_labels[dists[:, 2].argmin()] = 5


def process_labels(current_labels):
    names = {0: 'A', 1: 'B', 2: 'C',
             3: 'A_centroid',
             4: 'B_centroid',
             5: 'C_centroid'}
    return [names[label] for label in current_labels]


def k_centroids(vectors, k=3):
    k_means = KMeans(n_clusters=k).fit(vectors)
    dists = k_means.transform(vectors)
    get_centroids(k_means.labels_, dists)

    return process_labels(k_means.labels_)
