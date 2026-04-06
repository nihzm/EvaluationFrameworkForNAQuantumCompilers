from ast import List, Tuple
from cProfile import label
import pdb
from .utils import *
import pandas as pd
import seaborn as sns
import numpy as np
from .utils import *
import matplotlib.pyplot as plt
from .utils import COLUMN_FIGSIZE
from matplotlib import gridspec
from itertools import cycle, product


def line_plot_better(data, x, y, xlabel='XLabel', ylabel='YLabel', legend:str|list[str]=None, show_legend=True, title=None):

    fig = plt.figure(figsize=COLUMN_FIGSIZE)
    nrows = 1
    ncols = 1
    gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)
    ax = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)][0]

    sns.set_theme()
    sns.set_style("whitegrid")
    colors = sns.color_palette("pastel")
    #colors = sns.color_palette("deep")
    ax.grid(True)

    for i, data_i in enumerate(data):
        ax = sns.lineplot(data_i, x=x, y=y, marker=line_markers[i], color=colors[i], dashes=False, label=legend[i] if legend != None else None)

    ax.set_xlabel(xlabel, color='black')
    ax.set_ylabel(ylabel, color='black')
    
    if title != None:
        ax.set_title(title, fontweight='bold')
    return fig




def line_plot(data, x, y, xlabel='XLabel', ylabel='YLabel', legend:str|list[str]=None, show_legend=True, axis=None, save=False, title=None):
    
    if axis == None:
        fig = plt.figure(figsize=COLUMN_FIGSIZE)
        nrows = 1
        ncols = 1
        gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)
        ax = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)][0]
    else:
        ax = axis

    sns.set_theme()
    sns.set_style("whitegrid")
    ax.grid(True)

    if isinstance(y, list) or isinstance(y, np.ndarray):
        line_data = pd.DataFrame()
        line_data['x'] = x
        line_data.set_index('x', inplace=True)
        colors = sns.color_palette("deep")
        ax.set_xlabel(xlabel, color='black')
        ax.set_ylabel(ylabel, color='black')

        for i in range(len(y)):
            if legend == None:
                sns.lineplot(x=x, y=y[i], ax=ax, marker=line_markers[i], color=colors[i], dashes=False)
            else:
                sns.lineplot(x=x, y=y[i], ax=ax, marker=line_markers[i], color=colors[i], label=legend[i], dashes=False, legend=False if not show_legend else True)

    else:
        line_data = pd.DataFrame()
        line_data['x'] = x
        sns.set_theme()
        sns.set_style("whitegrid")
        colors = sns.color_palette("pastel")
        line_data['y'] = y
        fig, ax1 = plt.subplots()
        sns.lineplot(data=line_data, x='x', y='y', ax=ax1, label=ylabel, marker='o', color=colors[1])
        yticks = np.arange(min(y), max(y), (max(y)-min(y))/10)
        ax1.set_yticks(yticks)
        ax1.legend(loc='upper left')
        ax1.set_ylabel(ylabel, color='black')
        ax1.set_xlabel(xlabel, color='black')

    if title != None:
        ax.set_title(title, fontweight='bold')    

    if axis == None or save:
        return fig



def bar_plot(
    y: np.ndarray,
    bar_labels: list[str],
    colors: list[str] | None = None,
    hatches: list[str] | None = None,
    spacing: float = 2,
    zorder: int = 2000,
    filename: str = None,
    y_integer: bool = False,
    text=None,
    text_pos:tuple=None
    ):
    if colors is None:
        colors = sns.color_palette("pastel")

    #assert len(y.shape) == len(yerr.shape) == 2
    #assert len(y.shape) == 2
    #assert y.shape == yerr.shape

    num_bars = len(y)
    x = np.arange(num_bars)

    fig, ax = plt.subplots()

    color, hatch = colors[:len(y)], hatches[:len(y)]

    bar_width = spacing / (num_bars)

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

    save_figure(fig, filename)
    plt.close()


def grouped_bar_plot(data, figure=None, xcol='x', ycol='y', groups_label=None, bar_labels=None, ylabel=None, title=None, xlabel=None, bar_width=2, figsize=(15,4)):

    colors = sns.color_palette("pastel")

    #pdb.set_trace()
    ax = sns.barplot(data=data, x=xlabel, y=ylabel, hue=groups_label, palette=colors, edgecolor='black', linewidth=1.5)

    for bars, hatch in zip(ax.containers, hatches):
        for bar in bars:
            bar.set_hatch(hatch)

    plt.title(title, fontweight='bold')
    plt.tight_layout()
    plt.xlabel(xlabel, color='black')
    plt.ylabel(ylabel, color='black')
    #ax.legend(loc='upper left')
    plt.legend(bbox_to_anchor=(0.5, -0.2), loc="upper center", borderaxespad=0., ncol=2)
    return plt.gcf()


def stacked_grouped_bar_plot(data:pd.DataFrame, value_labels:list[str], groups, group_labels=None, bar_labels=None, ylabel=None, title=None, xlabel=None, bar_width=2):

    ax = plt.subplots()
    colors = sns.color_palette('pastel')

    #xticks = [len(bar_labels)//len(groups)//2 + len(bar_labels)//len(groups)*i for i in range(len(groups))]
    #ax = data.plot.bar(x='groups', y=value_labels, rot=0, width=bar_width, stacked=True, edgecolor='black', linewidth=1.5, alpha=0.7, color=colors, xticks=xticks, figsize=figsize)
    ax = data.plot.bar(x='groups', y=value_labels, rot=0, stacked=True, edgecolor='black', linewidth=1.5, color=colors, figsize=COLUMN_FIGSIZE)

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
#
    ##ax = sns.barplot(x='groups', y=value_labels[1], data=data, hue='bar_labels', palette=colors[2:3], edgecolor='black', linewidth=2, alpha=1, legend=False, width=bar_width) 
    #ax = sns.barplot(x='groups', y='min', data=data, hue='bar_labels', palette=colors[3:4], edgecolor='black', linewidth=2, alpha=1, legend=False, width=bar_width)
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
    plt.xlabel(xlabel, color='black')
    plt.ylabel(ylabel, color='black')
    ax.legend(handles=[ax.patches[0], ax.patches[len(bar_labels)]], loc='upper left', labels=['Compilation Time', 'Execution Time'])
    return plt.gcf()