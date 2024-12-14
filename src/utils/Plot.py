import os

import imageio.v2 as imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def visualize_neural_network(graph: nx.MultiDiGraph):
    type_to_color = {
        "SENSOR": "lightgreen",
        "INNER": "lightblue",
        "ACTION": "orange",
    }
    node_colors = [type_to_color.get(data['n_type']) for node, data in graph.nodes(data=True)]
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    edge_colors = ["red" if data['weight'] >= 0 else "blue" for _, _, data in graph.edges(data=True)]
    pos = nx.multipartite_layout(graph, subset_key="n_type")

    plt.figure(figsize=(12, 8))

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=700)
    nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=20, edge_color=edge_colors)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color="black", font_weight="bold")

    # Draw edge labels for weights
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8, font_color="red")

    plt.title("Neural Network Visualization")
    plt.axis("off")
    plt.show()


def make_plot(p_matrix: np.array, p_folder_name: str, p_plot_name: str) -> str:
    """ creates color map of passed matrix and saves it in specified folder with specified name """

    assert isinstance(p_matrix, np.ndarray)
    assert isinstance(p_folder_name, str)
    assert isinstance(p_plot_name, str)

    if not os.path.exists(p_folder_name):
        os.mkdir(p_folder_name)

    field_to_color = np.rot90(np.ma.masked_where(p_matrix == 0, p_matrix), 1)

    fig, ax = plt.subplots()
    cmap = mpl.colormaps['gray']
    cmap.set_bad(color='white')
    ax.matshow(field_to_color, interpolation=None, cmap=cmap)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False,
                   labeltop=False, labelright=False,
                   labelleft=False)

    name = os.path.join(p_folder_name, f'{p_plot_name}.png')

    plt.savefig(name)
    plt.close()

    return name


def to_gif(p_target_name: str, p_filenames: list[str]) -> None:
    """ composes pictures of specified filenames into one animated .gif file """

    assert isinstance(p_target_name, str)
    assert isinstance(p_filenames, list)
    for filename in p_filenames:
        assert isinstance(filename, str)

    with imageio.get_writer(f'{p_target_name}.gif', mode='I') as writer:
        for filename in p_filenames:
            image = imageio.imread(filename)
            writer.append_data(image)

    return
