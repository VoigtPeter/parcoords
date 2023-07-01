from typing import Union, Sequence

import numpy as np

import matplotlib.colors
import matplotlib.pyplot as plt
from matplotlib.scale import ScaleBase


def plot_parcoords(
        values: Union[Sequence, np.ndarray],
        labels: Union[Sequence[str], np.ndarray[str]] = None,
        color_field: Union[str, int] = None,
        color="grey",

        scale: Union[Sequence[Union[str, ScaleBase]], str] = None,
        figsize: tuple[int, int] = None,
        cmap=plt.cm.viridis,
        y_limits: Union[Sequence, np.ndarray] = None,
        fig: plt.Figure = None,
        axs: np.ndarray[plt.Axes] = None
) -> tuple[plt.Figure, np.ndarray[plt.Axes]]:
    """ Plotting function for parallel coordinate plots.
    :param values:
    :param labels:
    :param color_field:
    :param color:

    :param scale: Sequence of scale types, e.g.: [{"linear", "log", ...}, ...].
                  None defaults to "linear" for all axes.
    :param figsize:
    :param cmap:
    :param y_limits:
    :param fig:
    :param axs:
    :return:
    """
    # transpose row-vector to column-vector
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    values = values.T

    no_of_cols = len(values)
    if axs is None:
        # initialize figure and axes
        fig, axs = plt.subplots(1, no_of_cols - 1, figsize=figsize, sharey="none")
        axs = np.append(axs, axs[-1].twinx())

        # calculate limits from data & transform nominal columns
        if y_limits is None:
            y_limits = []
            for i, (column, ax) in enumerate(zip(values, axs)):
                if not all(isinstance(item, (int, float)) for item in column):
                    mappings, column = np.unique(column, return_inverse=True)
                    values[i] = column
                    ax.set_yticks(range(len(mappings)), labels=mappings)
                smallest = column.min(axis=0)
                largest = column.max(axis=0)
                y_limits.append([smallest, largest])
    else:
        if y_limits is not None:
            print("Warning: setting `y_limits` when using existing axes has no effect.")
            y_limits = None

    if scale is not None:
        if isinstance(scale, str):
            [ax.set_yscale(scale) for ax in axs]
        else:
            [ax.set_yscale(s) for ax, s in zip(axs, scale)]

    for i, ax in enumerate(axs):
        if i < len(axs) - 1:
            ax.set_xlim([i, i+1])
        if y_limits is not None:
            ax.set_ylim(y_limits[i])
        ax.spines[["bottom", "top"]].set_visible(False)
        ax.get_xaxis().set_visible(False)
        if labels is not None:
            ax.text(
                0 if i < len(axs) - 1 else 1, 1.07, labels[i],
                horizontalalignment="center",
                verticalalignment="center",
                rotation=0,
                transform=ax.transAxes
            )

    color_by_index = False
    if color_field is not None:
        if isinstance(color_field, str) and labels is not None:
            color_by_index = labels.index(color_field)
        elif isinstance(color_field, int):
            color_by_index = color_field
        else:
            print(f"Warning: invalid value '{color_field}' passed to `color_field`. Attribute is ignored.")
    color_norm = False
    if color_by_index:
        color_norm = matplotlib.colors.Normalize(
            vmin=values[color_by_index].min(axis=0),
            vmax=values[color_by_index].max(axis=0)
        )

    for i in range(len(values) - 1):
        for e, (y1, y2, c) in enumerate(zip(
                values[i],
                values[i+1],
                values[color_by_index] if color_by_index else np.zeros(len(values[0])))):
            l_color = color
            if color_by_index:
                l_color = cmap(color_norm(c))
            axs[i].axline(
                [0, axs[i].transLimits.transform(axs[i].transScale.transform([0,y1]))[1]],
                [1, axs[i+1].transLimits.transform(axs[i+1].transScale.transform([1,y2]))[1]],
                c=l_color,
                transform=axs[i].transAxes
            )

    if fig:
        fig.subplots_adjust(wspace=0)

    return fig, axs
