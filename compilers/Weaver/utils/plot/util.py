import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib import gridspec
import os
import pdb
import typing
from matplotlib.ticker import StrMethodFormatter
from itertools import cycle


FONTSIZE = 12
HIGHERISBETTER = "Higher is better ↑"
LOWERISBETTER = "Lower is better ↓"
ISBETTER_FONTSIZE = FONTSIZE + 2
WIDE_FIGSIZE = (13, 2.8)
COLUMN_FIGSIZE = (6.5, 3.4)
COLUMN_FIGSIZE_2 = (7.5, 4)

hatches = [
            "/",
            "\\",
            "//",
            "\\\\",
            "x",
            ".",
            ",",
            "*",
            "o",
            "O",
            "+",
            "X",
            "s",
            "S",
            "d",
            "D",
            "^",
            "v",
            "<",
            ">",
            "p",
            "P",
            "$",
            "#",
            "%",
        ]

plt.rcParams.update({"font.size": FONTSIZE})

def stacked_grouped_bar_plot(ax, data:pd.DataFrame, value_labels:list[str], groups, group_labels=None, bar_labels=None, ylabel=None, title=None, xlabel=None, bar_width=2):

    colors = sns.color_palette('pastel')

    #xticks = [len(bar_labels)//len(groups)//2 + len(bar_labels)//len(groups)*i for i in range(len(groups))]
    #ax = data.plot.bar(x='groups', y=value_labels, rot=0, width=bar_width, stacked=True, edgecolor='black', linewidth=1.5, alpha=0.7, color=colors, xticks=xticks, figsize=figsize)
    ax = data.plot.bar(x='n_variables', y=value_labels, rot=0, stacked=True, edgecolor='black', linewidth=1.5, color=colors, figsize=COLUMN_FIGSIZE)

    ##ax = sns.barplot(x='groups', y='max', data=data, hue='bar_labels', palette=colors, edgecolor='black', linewidth=2, alpha=0.7, legend=False, width=bar_width)
    #ax = sns.barplot(x='groups', y='max', data=data, hue='bar_labels', palette=colors[2:3], edgecolor='black', linewidth=2, alpha=1, legend=False, width=bar_width)
    ##ax = sns.barplot(x='groups', y=value_labels[0], data=data, hue='bar_labels', palette=colors[3:4], edgecolor='black', linewidth=2, alpha=0.7, legend=False, width=bar_width)
    ##ax = sns.barplot(x='groups', y='min', data=data, hue='bar_labels', palette=colors[len(groups):], edgecolor='black', linewidth=2, alpha=0.7, legend=False, width=bar_width)
#
    ##for i in ax.containers:
    ##    ax.bar_label(i, label_type='center', fmt='%.2f', fontweight='bold')

    #pdb.set_trace()

    #top_labels = [bar_labels[i] for i in range(len(bar_labels)) for _ in groups]
#
    #for bar, lab in zip(ax.patches[:len(bar_labels)], bar_labels):
    #    plt.text(bar.get_x() + bar.get_width() / 2., 0, '%d' % int(lab), ha='center', va='bottom', fontweight='bold', color='black')

    pdb.set_trace()
#
    ##ax = sns.barplot(x='groups', y=value_labels[1], data=data, hue='bar_labels', palette=colors[2:3], edgecolor='black', linewidth=2, alpha=1, legend=False, width=bar_width) 
    #ax = sns.barplot(x='System', y=value_labels, data=data, hue='n_variables', palette=colors[3:4], edgecolor='black', linewidth=2, alpha=1, legend=False, width=bar_width)
    ##for i in ax.containers:
    ##ax.bar_label(i, label_type='center', labels=groups)
    ##ax.bar_label(ax.containers[1], label_type='center', padding=2)
#
    ##ax = sns.barplot(x='groups', y='min', data=data, hue='bar_labels', palette=colors, edgecolor='black', linewidth=2, alpha=1)
#
    ##sns.set_color_codes('muted')
    ##colors = sns.color_palette("pastel")
    ##ax = sns.barplot(x='bar_labels', y='x2', hue='groups', data=data, label= palette=colors, edgecolor='black', linewidth=1.5)
#
    ##sns.set_color_codes('muted')
    ##colors = sns.color_palette("muted")
    ##ax = sns.barplot(x='bar_labels', y='x1', hue='groups', data=data, palette=colors, edgecolor='black', linewidth=1.5)

    containers_groups1 = [ax.patches[i*(len(bar_labels)//len(groups)):(i+1)*(len(bar_labels)//len(groups))] for i in range(len(groups))]
    containers_groups2 = [ax.patches[len(bar_labels)+i*(len(bar_labels)//len(groups)):len(bar_labels)+(i+1)*(len(bar_labels)//len(groups))] for i in range(len(groups))]

    #for container,hatch,color in zip(containers_groups1, hatches, cycle(colors[:2])):
    #    for bar in container:
    #        bar.set_hatch(hatch)
    #        bar.set_facecolor(color)
#
    #for container,hatch,color in zip(containers_groups2, hatches, cycle(colors[2:4])):
    #    for bar in container:
    #        bar.set_hatch(hatch)
    #        bar.set_facecolor(color)

    for bars, hatch in zip(ax.containers, hatches):
        for bar in bars:
            bar.set_hatch(hatch)

    #plt.bar_label(fo)
            
    
    plt.title(title, fontweight='bold')
    #ax.set_xticklabels(groups)
    #plt.xlabel(xlabel, color='black')
    #plt.ylabel(ylabel, color='black')
    #ax.legend(handles=[ax.patches[0], ax.patches[len(bar_labels)]], loc='upper left', labels=['Compilation Time', 'Execution Time'])
    return ax

def grouped_bar_plot(
    ax: plt.Axes,
    y: np.ndarray,
    yerr: np.ndarray=None,
    bar_labels: list[str] = None,
    group_labels: list[str] = None,
    colors: list[str] | None = None,
    hatches: list[str] | None = None,
    show_average_text: bool = False,
    average_text_position: float = 1.05,
    spacing: float = 0.95,
    zorder: int = 2000,
    bar_width: float = None
):
    if colors is None:
        colors = sns.color_palette("pastel")
    if hatches is None:
        hatches = hatches = [
            "/",
            "\\",
            "//",
            "\\\\",
            "x",
            ".",
            ",",
            "*",
            "o",
            "O",
            "+",
            "X",
            "s",
            "S",
            "d",
            "D",
            "^",
            "v",
            "<",
            ">",
            "p",
            "P",
            "$",
            "#",
            "%",
        ]

    #assert len(y.shape) == len(yerr.shape) == 2
    #assert len(y.shape) == 2
    #assert y.shape == yerr.shape

    num_groups, num_bars = y.shape
    print(num_groups, len(bar_labels), num_bars)
 
    assert len(bar_labels) == num_bars

    if bar_width == None:
        bar_width = spacing / (num_bars + 1)

    bar_width = bar_width * 1.1
    
    x = np.arange(num_groups)

    #plt.text((i+2)//num_groups + (i * bar_width), 0, "X", ha='center', va='bottom')
    #Set X on nan values

    for i in range(num_bars):
        y_bars = y[:, i]
        #yerr_bars = yerr[:, i]

        color, hatch = colors[i % len(colors)], hatches[i % len(hatches)]

        # if it is the last group of bars add distance of 1.5

        ax.bar(
            x + (i * bar_width),
            y_bars,
            bar_width,
            hatch=hatch,
            label=bar_labels[i],
            #yerr=yerr_bars,
            color=color,
            edgecolor="black",
            linewidth=1.5,
            error_kw=dict(lw=2, capsize=3),
            zorder=zorder,
        )

    #5000 for fidelity plot
    #67 for compilation time plot
    #1.3 for npulses plot
    #2.6
    #x position 2.8
    
    #nan_n = 3
    #for j in range(num_groups):
    #    if np.isnan(y[j][nan_n]):
    #        ax.text((nan_n+j*num_groups-1)//num_groups+nan_n*bar_width, 10**-1.31, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')
    #
    ax.set_xticks(x + ((num_bars - 1) / 2) * bar_width)
    ax.set_xticklabels(group_labels)

    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}')) # 2 decimal places

    if show_average_text:
        for i, x_pos in enumerate(ax.get_xticks()):
            ax.get_yticks()
            y_avg = np.average(y[i])
            #y_avg = y[i].prod()**(1/len(y[i]))
            text = f"{y_avg:.2f}"
            print(text)
            #text0 = f"{y[i][0]:.2f}"
            #text1 = f"{(y[i][1] - y[i][0])/y[i][0]*100:.1f}%"
            #text2 = f"{(y[i][2] - y[i][0])/y[i][0]*100:.1f}%"
            text0 = f"{y[i][0]:.2f}"
            text1 = f"{((y[i][1] - y[i][0])/y[i][0])*100:.1f}%"
            text2 = f"{((y[i][2] - y[i][0])/y[i][0])*100:.1f}%"

            text1 = f'+{text1}' if y[i][1] > y[i][0] else text1
            text2 = f'+{text2}' if y[i][2] > y[i][0] else text2
            #ax.text(x_pos, average_text_position, text, ha="center")
            #ax.text(x_pos-bar_width, average_text_position+(y[i][0]/ax.get_ylim()[1]), text0, ha="center", fontsize=10)
            #ax.text(x_pos+bar_width, average_text_position+(y[i][1]/ax.get_ylim()[1]), text2, ha="center", fontsize=10)
            #ax.text(x_pos, average_text_position+(y[i][2]/ax.get_ylim()[1]), text1, ha="center", fontsize=10)

            ax.text(x_pos-bar_width+0.01, average_text_position+y[i][0], text0, ha="center", fontsize=7)
            ax.text(x_pos, average_text_position+y[i][1], text1, ha="center", fontsize=7, color='green' if y[i][1] > y[i][0] else 'red')
            ax.text(x_pos+bar_width+0.01, average_text_position+y[i][2], text2, ha="center", fontsize=7, color='green' if y[i][2] > y[i][0] else 'red')

def grouped_bar_plot_lowerGood(
    ax: plt.Axes,
    y: np.ndarray,
    yerr: np.ndarray=None,
    bar_labels: list[str] = None,
    group_labels: list[str] = None,
    colors: list[str] | None = None,
    hatches: list[str] | None = None,
    show_average_text: bool = False,
    average_text_position: float = 1.05,
    spacing: float = 0.95,
    zorder: int = 2000,
    bar_width: float = None
):
    if colors is None:
        colors = sns.color_palette("pastel")
    if hatches is None:
        hatches = hatches = [
            "/",
            "\\",
            "//",
            "\\\\",
            "x",
            ".",
            ",",
            "*",
            "o",
            "O",
            "+",
            "X",
            "s",
            "S",
            "d",
            "D",
            "^",
            "v",
            "<",
            ">",
            "p",
            "P",
            "$",
            "#",
            "%",
        ]

    #assert len(y.shape) == len(yerr.shape) == 2
    #assert len(y.shape) == 2
    #assert y.shape == yerr.shape

    num_groups, num_bars = y.shape
    print(num_groups, len(bar_labels), num_bars)
 
    assert len(bar_labels) == num_bars

    if bar_width == None:
        bar_width = spacing / (num_bars + 1)

    bar_width = bar_width * 1.1
    
    x = np.arange(num_groups)

    for i in range(num_bars):
        y_bars = y[:, i]
        #yerr_bars = yerr[:, i]

        color, hatch = colors[i % len(colors)], hatches[i % len(hatches)]

        #print(color)

        ax.bar(
            x + (i * bar_width),
            y_bars,
            bar_width,
            hatch=hatch,
            label=bar_labels[i],
            #yerr=yerr_bars,
            color=color,
            edgecolor="black",
            linewidth=1.5,
            error_kw=dict(lw=2, capsize=3),
            zorder=zorder,
        )
    ax.set_xticks(x + ((num_bars - 1) / 2) * bar_width)
    ax.set_xticklabels(group_labels)

    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}')) # 2 decimal places

    if show_average_text:
        for i, x_pos in enumerate(ax.get_xticks()):
            ax.get_yticks()
            y_avg = np.average(y[i])
            #y_avg = y[i].prod()**(1/len(y[i]))
            text = f"{y_avg:.2f}"
            print(text)
            #text0 = f"{y[i][0]:.2f}"
            #text1 = f"{(y[i][1] - y[i][0])/y[i][0]*100:.1f}%"
            #text2 = f"{(y[i][2] - y[i][0])/y[i][0]*100:.1f}%"
            text0 = f"{y[i][0]:.2f}"
            text1 = f"{((y[i][1] - y[i][0])/y[i][0])*100:.1f}%"
            text2 = f"{((y[i][2] - y[i][0])/y[i][0])*100:.1f}%"

            text1 = f'+{text1}' if y[i][1] > y[i][0] else text1
            text2 = f'+{text2}' if y[i][2] > y[i][0] else text2
            #ax.text(x_pos, average_text_position, text, ha="center")
            #ax.text(x_pos-bar_width, average_text_position+(y[i][0]/ax.get_ylim()[1]), text0, ha="center", fontsize=10)
            #ax.text(x_pos+bar_width, average_text_position+(y[i][1]/ax.get_ylim()[1]), text2, ha="center", fontsize=10)
            #ax.text(x_pos, average_text_position+(y[i][2]/ax.get_ylim()[1]), text1, ha="center", fontsize=10)

            ax.text(x_pos-bar_width+0.01, average_text_position+y[i][0], text0, ha="center", fontsize=8)
            ax.text(x_pos, average_text_position+y[i][1], text1, ha="center", fontsize=8, color='red' if y[i][1] > y[i][0] else 'green')
            ax.text(x_pos+bar_width+0.01, average_text_position+y[i][2], text2, ha="center", fontsize=8, color='red' if y[i][2] > y[i][0] else 'green')

#Different number of bars in each group
def uneven_grouped_bar_plot(
    ax: plt.Axes,
    y: np.ndarray,
    yerr: np.ndarray=None,
    bar_labels: list[str] = None,
    group_labels: list[str] = None,
    colors: list[str] | None = None,
    hatches: list[str] | None = None,
    show_average_text: bool = False,
    average_text_position: float = 1.05,
    spacing: float = 0.95,
    zorder: int = 2000,
    bar_width: float = None,
):
    if colors is None:
        colors = sns.color_palette("pastel")
    if hatches is None:
        hatches = hatches = [
            "/",
            "\\",
            "//",
            "\\\\",
            "x",
            ".",
            ",",
            "*",
            "o",
            "O",
            "+",
            "X",
            "s",
            "S",
            "d",
            "D",
            "^",
            "v",
            "<",
            ">",
            "p",
            "P",
            "$",
            "#",
            "%",
        ]

    #assert len(y.shape) == len(yerr.shape) == 2
    #assert len(y.shape) == 2
    #assert y.shape == yerr.shape

    #pdb.set_trace()

    num_groups = len(y)
    num_bars = sum([len(y[i]) for i in range(num_groups)])

    print(num_groups, len(bar_labels), num_bars)

    group_size_percentages = [len(y[i]) / num_bars for i in range(num_groups)]
    
    spacing_per_group = [spacing * group_size_percentages[i] for i in range(num_groups)]

    #pdb.set_trace()

    #if bar_width == None:
    #    bar_width = spacing / (num_bars + 1)
    
    for j in range(num_groups):
        for i in range(len(y[j])):
            x = np.arange(len(y[j]))

            group_num_bars = len(y[j])

            bar_width = spacing_per_group[j] / (group_num_bars + 1)

            y_bars = y[j][:, 2]

            color, hatch = colors[group_num_bars % len(colors)], hatches[group_num_bars % len(hatches)]

            group_bar_labels = bar_labels[:len(y[j])]

            ax.bar(
                x * (i+1 * bar_width) + sum(spacing_per_group[:j]),
                y_bars,
                bar_width,
                hatch=hatch,
                label=group_bar_labels,
                #yerr=yerr_bars,
                color=color,
                edgecolor="black",
                linewidth=1.5,
                error_kw=dict(lw=2, capsize=3),
                zorder=zorder,
            )
    
    #ax.set_xticks(x + ((num_groups - 1)) * bar_width)

    #ax.set_xticks(x + ((num_bars - 1) / 2) * bar_width)

    #ax.set_xticklabels(group_labels)

    #if show_average_text:
    #    for i, x_pos in enumerate(ax.get_xticks()):
    #        y_avg = np.average(y[i])
    #        #y_avg = y[i].prod()**(1/len(y[i]))
    #        text = f"{y_avg:.2f}"
    #        print(text)
    #        ax.text(x_pos, average_text_position, text, ha="center")

def bar_plot(
    ax: plt.Axes,
    y: np.ndarray,
    bar_labels: list[str],
    colors: list[str] | None = None,
    hatches: list[str] | None = None,
    spacing: float = 2,
    zorder: int = 2000,
    filename: str = None,
    y_integer: bool = False,
    text=None,
    text_pos:tuple=None,
    bar_width: float = None,
    ):
    if colors is None:
        colors = sns.color_palette("pastel")
    if hatches is None:
        hatches = hatches = [
            "/",
            "\\",
            "//",
            "\\\\",
            "x",
            ".",
            ",",
            "*",
            "o",
            "O",
            "+",
            "X",
            "s",
            "S",
            "d",
            "D",
            "^",
            "v",
            "<",
            ">",
            "p",    
            "P",
            "$",
            "#",
            "%",
        ]

    #assert len(y.shape) == len(yerr.shape) == 2
    #assert len(y.shape) == 2
    #assert y.shape == yerr.shape

    num_bars = len(y)
    x = np.arange(num_bars)

    #fig, ax = plt.subplots()

    color, hatch = colors[:len(y)], hatches[:len(y)]

    bar_width = spacing / (num_bars) * 2

    plt.xticks(rotation=45)

    ax.bar(
        x,
        y,
        bar_width,
        hatch=hatch,
        tick_label=bar_labels,
        #yerr=yerr_bars,
        color=color,
        edgecolor="black",
        linewidth=1.5,
        error_kw=dict(lw=2, capsize=3),
        zorder=zorder,
    )
    if text != None:
        plt.text(*text_pos, text)

    if y_integer:
        y_ticks_integer = np.arange(0, max(y) + 1, (max(y) // 10) + 1)
        ax.set_yticks(ticks=y_ticks_integer)

    #save_figure(fig, filename)

def index_dataframe_mean_std(
    df: pd.DataFrame,
    xkey: str,
    xvalues: np.ndarray,
    ykey: str,
) -> tuple[np.ndarray, np.ndarray]:
    df = (
        df.groupby(xkey)
        .agg({ykey: ["mean", "sem"]})
        .sort_values(by=[xkey])
        .reset_index()[[xkey, ykey]]
    )
    df = df.set_index(xkey)
    df = df.reindex(sorted(xvalues))
    df[ykey] = df[ykey].fillna(0.0)
    df = df.reset_index()
    return np.array(df[ykey]["mean"]), np.array(df[ykey]["sem"])


def data_frames_to_y_yerr(
    dataframes: list[pd.DataFrame],
    xkey: str,
    xvalues: np.ndarray,
    ykey: str,
    ykey_base: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    if ykey_base is not None:
        for df in dataframes:
            df[ykey] = df[ykey] / df[ykey_base]

    mean_data, std_data = [], []
    for df in dataframes:
        mean, std = index_dataframe_mean_std(df, xkey, xvalues, ykey)
        mean_data.append(mean)
        std_data.append(std)

    return np.array(mean_data), np.array(std_data)


def save_figure(fig: plt.Figure, exp_name: str):
    plt.tight_layout()
    fig.savefig(
        exp_name + ".pdf",
        bbox_inches="tight",
    )


# if __name__ == "__main__":
#     from data import NOISE_SCALE_KOLKATA

#     dfs = [pd.read_csv(file) for file in NOISE_SCALE_KOLKATA.values()]
#     labels = list(NOISE_SCALE_KOLKATA.keys())

#     print(
#         index_dataframe_mean_std(
#             dfs[0], "num_qubits", np.array([8, 10, 12]), "num_cnots_base"
# #         )
#     ) 

def plot_lines_2yaxis(xkey:str, xlabel: str, ykeys: list[str], labels: list[str], data: pd.DataFrame, filename: str):

    sns.set_theme()
    sns.set_style("whitegrid")

    fig, ax1 = plt.subplots()
    sns.lineplot(data=data, x=xkey, y=ykeys[0], ax=ax1, label=labels[0], markers='o')

    ax2 = ax1.twinx()

    sns.lineplot(data=data, x=xkey, y=ykeys[1], ax=ax2, label=labels[1], markers='o')

    ax1.set_ylabel(labels[0], color='b')
    ax2.set_ylabel(labels[1], color='r')
    ax1.set_xlabel(xlabel)
    
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    save_figure(fig, filename)

def prepare_dataframe(df: pd.DataFrame, key: str) -> pd.DataFrame:
    res_df = df.loc[df[key] > 0.0]
    res_df = (
        res_df.groupby("num_qubits")
        .agg({key: ["mean", "sem"]})
        .sort_values(by=["num_qubits"])
        .reset_index())
    return res_df

# def calculate_figure_size(num_rows, num_cols):
#     subplot_width_inches = 3.0  # Adjust this value based on your desired subplot width

#     # Define the number of columns and rows of subplots
#     num_cols = 2
#     num_rows = 3

#     # Calculate the total width and height based on the subplot width and number of columns and rows
#     fig_width_inches = subplot_width_inches * num_cols
#     fig_height_inches = fig_width_inches / 1.618 * num_rows  # Incorporate the golden ratio (1.618) for the height

#     return fig_width_inches, fig_height_inches

def plot_line(ax, xkey:str, xlabel: str, ykeys: list[str], labels: list[str], data: pd.DataFrame):

    sns.set_theme()
    sns.set_style("whitegrid")

    sns.lineplot(ax=ax, data=data, x=xkey, y=ykeys[0], label=labels[0], markers='o')

    ax.set_ylabel(labels[0], color='b')
    ax.set_xlabel(xlabel)
    
    ax.legend(loc='upper left')

def prepare_dataframe(df: pd.DataFrame, key: str) -> pd.DataFrame:
    res_df = df.loc[df[key] > 0.0]
    res_df = (
        res_df.groupby("num_qubits")
        .agg({key: ["mean", "sem"]})
        .sort_values(by=["num_qubits"])
        .reset_index())
    return res_df

# def calculate_figure_size(num_rows, num_cols):
#     subplot_width_inches = 3.0  # Adjust this value based on your desired subplot width

#     # Define the number of columns and rows of subplots
#     num_cols = 2
#     num_rows = 3

#     # Calculate the total width and height based on the subplot width and number of columns and rows
#     fig_width_inches = subplot_width_inches * num_cols
#     fig_height_inches = fig_width_inches / 1.618 * num_rows  # Incorporate the golden ratio (1.618) for the height

#     return fig_width_inches, fig_height_inches


if __name__ == "__main__":
    fig, ax = plt.subplots(1, figsize=COLUMN_FIGSIZE)

    x = np.array([15, 20, 25])
    y = np.array(
        [
            [0.5, 0.6],
            [0.4, 0.5],
            [0.3, 0.4],
        ]
    )
    yerr = np.array(
        [
            [0.5, 0.6],
            [0.4, 0.5],
            [0.3, 0.4],
        ]
    )
    ax.set_xticklabels(x)
    ax.grid(axis="y", linestyle="-", zorder=-1)
    grouped_bar_plot(ax, y, yerr, ["simtime", "knittime"])
    ax.legend(loc="upper right")
    save_figure(fig, "test")
