import os

import imageio.v2 as imageio
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import config

type_to_color = {
    "SENSOR": "lightgreen",
    "INNER": "lightblue",
    "ACTION": "orange",
}
BARRIER_COLOR = 'black'
SPECIMEN_COLOR = {
    True: 'red',
    False: "yellow"
}
food_cmap = plt.cm.Greens
norm = mcolors.Normalize(vmin=0, vmax=config.FOOD_PER_SOURCE_MAX)


def visualize_neural_network(graph: nx.MultiDiGraph):
    node_colors = [type_to_color.get(data['n_type']) for node, data in graph.nodes(data=True)]
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    edge_colors = ["red" if data['weight'] >= 0 else "blue" for _, _, data in graph.edges(data=True)]
    # positions of nodes in layers
    pos = nx.multipartite_layout(graph, subset_key="n_type", scale=-1)

    plt.figure(figsize=(12, 8))

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=700)
    nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=20, edge_color=edge_colors)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color="black", font_weight="bold")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8, font_color="red")

    plt.axis("off")
    plt.show()
    plt.close()


def plot_world(barriers, food_data, pop, save_path_name: str):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.clear()
    ax.set_xticks(np.arange(-0.5, config.DIM, 1))
    ax.set_yticks(np.arange(-0.5, config.DIM, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlim(-0.5, config.DIM - 0.5)
    ax.set_ylim(-0.5, config.DIM - 0.5)
    ax.margins(0)

    for loc in barriers:
        ax.add_patch(plt.Rectangle((loc[0] - 0.5, loc[1] - 0.5), 1, 1, color=BARRIER_COLOR))

    for loc in food_data:
        food_level = food_data.get(loc)
        food_color = food_cmap(norm(food_level))
        ax.add_patch(plt.Rectangle((loc[0] - 0.5, loc[1] - 0.5), 1, 1, color=food_color))

    for specimen in pop[1:]:
        ax.plot(specimen.location.x, specimen.location.y, 'o', color=SPECIMEN_COLOR.get(specimen.alive))

    plt.tight_layout()
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(save_path_name)
    plt.close()

    return


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
            os.remove(filename)

    return


def make_simple_plot(p_matrix: np.array, p_folder_name: str, p_plot_name: str) -> str:
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
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelright=False, labelleft=False)

    name = os.path.join(p_folder_name, f'{p_plot_name}.png')

    plt.savefig(name)
    plt.close()

    return name
