from __future__ import annotations
from typing import Union, Sequence, Tuple

import numpy as np

import matplotlib.colors
import matplotlib.pyplot as plt
from matplotlib.scale import ScaleBase


def plot_parcoords(
    values: Union[Sequence, np.ndarray],
    labels: Union[Sequence[str], np.ndarray[str]] = None,
    title: str = None,
    color_field: Union[str, int] = None,
    color="grey",
    scale: Union[
        Sequence[Tuple[Union[str, int], Union[str, ScaleBase]]],
        Sequence[Union[str, ScaleBase]],
        str,
    ] = None,
    figsize: Tuple[int, int] = None,
    cmap=plt.cm.viridis,
    y_limits: Union[Sequence, np.ndarray] = None,
    axs: np.ndarray[plt.Axes] = None,
) -> Tuple[plt.Figure, np.ndarray[plt.Axes]]:
    """Plotting function for parallel coordinate plots.

    :param values: 2-dimensional sequence or numpy-array containing
        row-vectors of the data to display. (required)
    :param labels: Sequence containing the column labels. (optional)
    :param title: Title of the figure. (optional)
    :param color_field: Either the label of the column (`labels` must be provided)
        or the column index used as basis for the coloring. If not
        provided, the `color` attribute will be used. (optional)
    :param color: Color of the edges when `color_field` attribute is not provided.
        (default: grey)
    :param scale: Sequence of scale types. Must be in one of the forms:
        [({field label/index}, {"linear", "log", ...}), ...] or
        [{"linear", "log", ...}, ...] or
        {"linear", "log", ...}.
        (optional, default: linear)
    :param figsize: Size of the figure. (optional)
    :param cmap: The colormap for the edge-colors (to be used together with
        `color_field`). (default: viridis)
    :param y_limits: The min- & max-limits for the axes. Must be in the form of:
        [(`min`, `max`), ...] for all axes. (optional)
    :param axs: An existing axes array, to be used when adding more datapoints.
        (optional)
    :return: The figure object and the axes (as ndarray).
    """
    # transpose row-vector to column-vector
    if not isinstance(values, np.ndarray):
        values = np.array(values, dtype="object")
    values = values.T

    no_of_cols = len(values)
    if axs is None:
        # initialize figure and axes
        fig, axs = plt.subplots(
            1,
            no_of_cols - 1,
            figsize=figsize,
            sharey="none",
        )
        axs = np.append(axs, axs[-1].twinx())

        # calculate limits from data & transform nominal columns
        ylims = []
        for i, (column, ax) in enumerate(zip(values, axs)):
            if not all(isinstance(item, (int, float)) for item in column):
                mappings, column = np.unique(column, return_inverse=True)
                values[i] = column
                ax.set_yticks(range(len(mappings)), labels=mappings)
            if y_limits is None:
                smallest = column.min(axis=0)
                largest = column.max(axis=0)
                ylims.append([smallest, largest])
        if y_limits is None:
            y_limits = ylims
    else:
        for i, (column, ax) in enumerate(zip(values, axs)):
            if not all(isinstance(item, (int, float)) for item in column):
                for x, value in enumerate(column):
                    if isinstance(value, str):
                        column[x] = {
                            text.get_text(): i
                            for i, text in enumerate(ax.get_yticklabels())
                        }[value]
                values[i] = column
        if y_limits is not None:
            print(
                "Warning: setting `y_limits` when using existing axes has no effect."
            )
            y_limits = None
        if scale is not None:
            print(
                "Warning: setting `scale` when using existing axes has no effect."
            )
            scale = None
        fig = axs[0].get_figure()

    if scale is not None:
        if isinstance(scale, str):
            [ax.set_yscale(scale) for ax in axs]
        elif (
            isinstance(scale, Sequence)
            and len(scale) > 0
            and all([isinstance(s, str) for s in scale])
        ):
            [ax.set_yscale(s) for ax, s in zip(axs, scale)]
        elif (
            isinstance(scale, Sequence)
            and len(scale) > 0
            and all(
                [
                    isinstance(s, Sequence)
                    and len(s) == 2
                    and isinstance(s[0], (int, str))
                    and isinstance(s[1], str)
                    for s in scale
                ]
            )
        ):
            for column, scale_type in scale:
                if isinstance(column, str):
                    column = labels.index(column)
                axs[column].set_yscale(scale_type)
        else:
            print(
                f"Warning: invalid value '{scale}' passed to `scale`. Attribute is ignored."
            )

    for i, ax in enumerate(axs):
        if i < len(axs) - 1:
            ax.set_xlim([i, i + 1])
        if y_limits is not None:
            ax.set_ylim(y_limits[i])
        ax.spines[["bottom", "top"]].set_visible(False)
        ax.get_xaxis().set_visible(False)
        if labels is not None:
            ax.text(
                0 if i < len(axs) - 1 else 1,
                1.07,
                labels[i],
                horizontalalignment="center",
                verticalalignment="center",
                rotation=0,
                transform=ax.transAxes,
            )

    color_by_index = None
    if color_field is not None:
        if isinstance(color_field, str) and labels is not None:
            color_by_index = labels.index(color_field)
        elif isinstance(color_field, int):
            color_by_index = color_field
        else:
            print(
                f"Warning: invalid value '{color_field}' passed to `color_field`. Attribute is ignored."
            )
    color_norm = False
    if color_by_index is not None:
        color_norm = matplotlib.colors.Normalize(
            vmin=values[color_by_index].min(axis=0),
            vmax=values[color_by_index].max(axis=0),
        )

    for i in range(len(values) - 1):
        for e, (y1, y2, c) in enumerate(
            zip(
                values[i],
                values[i + 1],
                values[color_by_index]
                if color_by_index
                else np.zeros(len(values[0])),
            )
        ):
            l_color = color
            if color_by_index:
                l_color = cmap(color_norm(c))
            axs[i].axline(
                [
                    0,
                    axs[i].transLimits.transform(
                        axs[i].transScale.transform([0, y1])
                    )[1],
                ],
                [
                    1,
                    axs[i + 1].transLimits.transform(
                        axs[i + 1].transScale.transform([1, y2])
                    )[1],
                ],
                c=l_color,
                transform=axs[i].transAxes,
            )

    if fig:
        fig.subplots_adjust(wspace=0)
        fig.subplots_adjust(top=0.85)
        if title is not None:
            fig.suptitle(title)

    return fig, axs
