from scipy.stats import gmean
from scipy.stats import iqr
from benchmarks.plot.util import *
#from plot.plot import line_plot
#from benchmarks.plot.plot import line_plot
import seaborn as sns
from matplotlib.ticker import StrMethodFormatter



FONTSIZE = 12
ISBETTER_FONTSIZE = FONTSIZE + 2
HIGHERISBETTER = "Higher is better ↑"
LOWERISBETTER = "Lower is better ↓"

#from get_average import get_average
#from util import calculate_figure_size, plot_lines, grouped_bar_plot, data_frames_to_y_yerr
#from data import SWAP_REDUCE_DATA, DEP_MIN_DATA, NOISE_SCALE_ALGIERS_DATA, SCALE_SIM_TIME, SCALE_SIM_MEMORY


sns.set_theme(style="whitegrid", color_codes=True)
colors = sns.color_palette("deep")
plt.rcParams.update({"font.size": 12})

def insert_column(df):
    df['total_runtime'] = df['run_time'] + df['knit_time']

    return df

def dataframe_out_of_columns(dfs, lines, columns):
    merged_df = pd.DataFrame()

    merged_df["num_qubits"] = dfs[0]["num_qubits"].copy()
    merged_df.set_index("num_qubits")

    for i,f in enumerate(dfs):
        merged_df[lines[i]] = f[columns].copy()

    #merged_df.reset_index(drop = True, inplace = True)
    merged_df.set_index("num_qubits", inplace = True)

    return merged_df
'''
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
'''

hatches = [
    "/",
	"\\",
	"//",
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
def custom_plot_multiprogramming(	
	titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "multi_programming.pdf",
) -> None:
	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	x = np.array([59, 74, 88])

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylim(0, 1)

	y = np.array(
		[
			[0.81, 0.88, 0.94],
			[0.68, 0.83, 0.945],
			[0.53, 0.78, 0.92]
		]
	)

	yerr = np.array(
		[
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0]
		]
	)
	
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)	
	grouped_bar_plot(axis[0], y, yerr, ["No M/P", "Random M/P", "QOS M/P"])
	axis[0].legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=3)

	#axis[0].set_yticks(np.logspace(1, 5, base=10, num=5, dtype='int'))
	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 1, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	#os.makedirs(os.path.dirname(output_file), exist_ok=True)
	#plt.tight_layout(pad=1)
	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_multiprogramming_relative(titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "multi_programming_relative.pdf",):

	fig = plt.figure(figsize=WIDE_FIGSIZE)

	x = np.array([59, 74, 88])

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylim(0, 1.1)

	y = np.array(
		[
			[0.98, 0.933, 0.94, 0.97, 0.98, 0.9456, 0.943, 0.96, 0.9452],
			[0.945, 0.914, 0.92, 0.951, 0.967, 0.929, 0.918, 0.948, 0.923],
			[0.913, 0.905, 0.903, 0.934, 0.938, 0.905, 0.897, 0.93, 0.901]
		]
	)

	yerr = np.array(
		[
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		]
	)

	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y, yerr, ["W-State", "QSV", "TL-1", "HS-1", "HS-2", "VQE-1", "VQE-2", "QAOA-B", "QAOA-2"], show_average_text=True, average_text_position=2)

	axis[0].axhline(1, color="red", linestyle="-", linewidth=2)

	#axis[0].legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=3)
	handles, labels = axis[0].get_legend_handles_labels()

	fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.2),
        ncol=9,
        frameon=False,
    )

	#axis[0].set_yticks(np.logspace(1, 5, base=10, num=5, dtype='int'))
	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 1, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	#os.makedirs(os.path.dirname(output_file), exist_ok=True)
	#plt.tight_layout(pad=1)
	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_large_circuit_fidelities(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "scalability_results.pdf"):

	fig = plt.figure(figsize=WIDE_FIGSIZE)

	x = np.array([4, 8, 12, 16, 20, 24])
	#x = dataframes[0]["bench_name"]

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylim(0, 1.1)

	y = np.array(
		[
			df["fidelity"] for df in dataframes
		]
	)

	yerr = np.array(
		[
			df["fidelity_std"] for df in dataframes
		]
	)
	

	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y, yerr, ["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, average_text_position=1.03)

	handles, labels = axis[0].get_legend_handles_labels()

	fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.2),
        ncol=9,
        frameon=False,
    )

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 1, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	#os.makedirs(os.path.dirname(output_file), exist_ok=True)
	#plt.tight_layout(pad=1)
	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_small_circuit_relative_fidelities(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "scalability_proposal.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE_2)

	x = np.array(["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])
	#x = dataframes[0]["bench_name"]

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	axis[0].set_yscale("log", base=2)
	axis[0].set_ylim(1, 32)

	#ytick_locations = [1e0, 1e1, 1e2, 1e3, 1e4, 1e5]
	ytick_labels = ['0', '1', '2', '4', '8', '16', '32']
	axis[0].set_yticklabels(ytick_labels)

	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	

	y = np.array(
		[
			dataframes[0]["fidelity"] / dataframes[1]["fidelity"]
		]
	)

	yerr = np.array(
		[
			dataframes[0]["fidelity_std"] / dataframes[1]["fidelity_std"]
		]
	)
	
	#print(y)
	#print(yerr)
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y.T, yerr.T, [""], show_average_text=True, average_text_position=24)

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 0.95, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_baseline_utilizations(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "utiization_limits.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE_2)

	x = np.array(["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])
	#x = dataframes[0]["bench_name"]

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	#axis[0].set_yscale(0, 100)
	axis[0].set_ylim(0, 100)

	#ytick_locations = [1e0, 1e1, 1e2, 1e3, 1e4, 1e5]
	#ytick_labels = ['0', '1', '2', '4', '8', '16', '32']
	#axis[0].set_yticklabels(ytick_labels)

	arr = [29.6, 29.6, 29.6, 29.6, 29.6, 14.8, 22.2, 22.2, 29.6,]

	y = np.array(
		[
			arr
		]
	)

	yerr = np.array(
		[
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		]
	)

	axis[0].axhline(np.mean(arr), color="red", linestyle="-", linewidth=1)
	print(np.mean(arr))
	
	#print(y)
	#print(yerr)
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y.T, yerr.T, [""], show_average_text=True, average_text_position=40)

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 0.93, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_small_circuit_relative_properties(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "relative_properties.pdf"):

	fig = plt.figure(figsize=WIDE_FIGSIZE)

	#x = np.array([12, 24])
	x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 1
	ncols = 2
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])

	axis[1].set_ylabel(ylabel[1])
	axis[1].set_xlabel(xlabel[1])

	axis[0].set_ylim(0, 1.5)
	axis[1].set_ylim(0, 1.5)

	axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	

	y0 = np.array(
		[
			df["depth"] for df in dataframes
		]
	)

	
	yerr0 = np.array(
		[
			df["fidelity"] for df in dataframes
		]
	)

	y1 = np.array(
		[
			df["num_nonlocal_gates"] for df in dataframes
		]
	)

	yerr1 = np.array(
		[
			df["fidelity"] for df in dataframes
		]
	)
	
	axis[0].set_xticklabels(x)
	axis[1].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y0, yerr0, ["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, average_text_position=1.3)
	grouped_bar_plot(axis[1], y1, yerr1, ["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, average_text_position=1.3)

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")

	handles, labels = axis[0].get_legend_handles_labels()

	fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.2),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def cycle_until_sizematch(ref:pd.DataFrame, array:pd.DataFrame):
	while len(ref) > len(array):
		array = pd.concat([array, array], ignore_index=True)

	return array[:len(ref)]


def custom_custom_plot_small_circuit_relative_properties(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "relative_properties.pdf"):

	xlabel = ['12 qubits', '24 qubits']
	ylabel = ['Depth', 'Number of CNOT gates']
	titles = ['Depth - 12 qubits', 'Number of CNOT gates - 12 qubits', 'Depth - 24 qubits', 'Number of CNOT gates - 24 qubits']

	df_join = pd.DataFrame()

	for df in dataframes:
		df_wo_reference = df[df['method'] != 'qiskit'].reset_index(drop=True)
		reference = df[df['method'] == 'qiskit'].reset_index(drop=True)
	
		for col in df.columns[2:5]:  # Skip the first column (bench_name)
			base_values = reference[col]
			df_wo_reference[col] = df_wo_reference[col] / cycle_until_sizematch(df_wo_reference[col], base_values)

		df_join = pd.concat([df_join, df_wo_reference], ignore_index=True)

	df = df_join
	bench_names = np.unique(df["bench_name"].to_list())
	print(bench_names)

	fig = plt.figure(figsize=(13, 5.6))

	#x = np.array([12, 24])
	x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 2
	ncols = 2
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	colors = sns.color_palette("pastel")
	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	#pdb.set_trace()
	#axis[0].set_ylim(0, 1.5)
	#axis[1].set_ylim(0, 1.5)
	#axis[2].set_ylim(0, 1.5)
	#axis[3].set_ylim(0, 1.5)

	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	#pdb.set_trace()
	#axis[2].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[3].axhline(1, color="red", linestyle="-", linewidth=2)

	y00 = df[df.num_qubits == 12].set_index("method")
	y01 = df[df.num_qubits == 12].set_index("method")
	y10 = df[df.num_qubits == 24].set_index("method")
	y11 = df[df.num_qubits == 24].set_index("method")
	
	#axis[0].set_xticklabels(x)
	#axis[1].set_xticklabels(x)
	#axis[2].set_xticklabels(x)
	#axis[3].set_xticklabels(x)

	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)
	axis[2].grid(axis="y", linestyle="-", zorder=-1)
	axis[3].grid(axis="y", linestyle="-", zorder=-1)
	#grouped_bar_plot(ax=axis[0], y=y00, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#seaborn grouped bar plot, grouped by method for y00, y01, y10, y11

	sns.barplot(data=y00, x="method", y="depth", ax=axis[0], hue="bench_name", legend=False, palette="pastel", edgecolor="black", linewidth=1.5)

	sns.barplot(data=y01, x="method", y="num_nonlocal_gates", ax=axis[1], hue="bench_name", palette="pastel", legend=False, edgecolor="black", linewidth=1.5)

	sns.barplot(data=y10, x="method", y="depth", ax=axis[2], palette="pastel", hue="bench_name", edgecolor="black", linewidth=1.5)

	sns.barplot(data=y11, x="method", y="num_nonlocal_gates", ax=axis[3], hue="bench_name" , palette="pastel", legend=False, edgecolor="black", linewidth=1.5)
	
	y00_depth_means = y00.groupby('method')['depth'].mean()
	y01_cnot_means = y01.groupby('method')['num_nonlocal_gates'].mean()
	y10_depth_means = y10.groupby('method')['depth'].mean()
	y11_cnot_means = y11.groupby('method')['num_nonlocal_gates'].mean()

	print(y00_depth_means)

	#draw horizontal lines for the mean values, 3 mean values per plot
	#axis[0].axhline(y=(y00_depth_means['FrozenQubits']), color=colors[0], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[1].axhline(y=y01_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[2].axhline(y=y10_depth_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[3].axhline(y=y11_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['QOS'], color=colors[2], linestyle='--')

	#hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:len(df['bench_name'].unique())]))

	hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:3]))

	print(hatch_order)
	
	#for i, patch in enumerate(axis[0].patches):
	#	patch.set_hatch(hatch_order[i])
	
	# Plot average values on the graph

	#y00.plot(kind='bar', ax=axis[0], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")
	#grouped_bar_plot(ax=axis[1], y=y01, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y01.plot(kind='bar', ax=axis[1], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	#grouped_bar_plot(ax=axis[2], y=y10, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y10.plot(kind='bar', ax=axis[2], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")

	#grouped_bar_plot(ax=axis[3], y=y11, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y11.plot(kind='bar', ax=axis[3], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	axis[3].set_title(titles[3], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)
	axis[1].set_xlabel(None)
	axis[2].set_xlabel(None)
	axis[3].set_xlabel(None)

	axis[0].set_ylabel(None)
	axis[1].set_ylabel(None)
	axis[2].set_ylabel(None)
	axis[3].set_ylabel(None)

	axis[0].axhline(y=1, color='red', linestyle='--')
	axis[1].axhline(y=1, color='red', linestyle='--')
	axis[2].axhline(y=1, color='red', linestyle='--')
	axis[3].axhline(y=1, color='red', linestyle='--')

	plt.subplots_adjust(hspace=0.35)

	#Add shared ylabel to figure
	fig.text(0.06, 0.5, "Relative values to Qiskit", va='center', rotation='vertical', fontweight="bold", fontsize=FONTSIZE)

	#Add shared xlabel to figure
	#fig.text(0.5, 0.04, , ha='center', fontweight="bold", fontsize=FONTSIZE)

	handles, labels = axis[2].get_legend_handles_labels()

	axis[2].legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(1,-0.4),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_budget_comparison(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "budget_comparison.pdf"):

	xlabel = ['3', '4', '5']

	ylabel = ['Depth', 'Number of CNOT gates']
	titles = ['(a) Depth - 12 qubits', '(b) Number of CNOT gates - 12 qubits']

	df_join = pd.DataFrame()

	for df in dataframes:
		df_wo_reference = df[df['method'] != 'qiskit'].reset_index(drop=True)
		reference = df[df['method'] == 'qiskit'].reset_index(drop=True)
	
		for col in df.columns[2:5]:  # Skip the first column (bench_name)
			base_values = reference[col]
			df_wo_reference[col] = df_wo_reference[col] / cycle_until_sizematch(df_wo_reference[col], base_values)

		df_join = pd.concat([df_join, df_wo_reference], ignore_index=True)

	df = df_join
	bench_names = np.unique(df["bench_name"].to_list())
	print(bench_names)

	fig = plt.figure(figsize=(13, 5.6))

	#x = np.array([12, 24])
	x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 1
	ncols = 2
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	#pdb.set_trace()
	#axis[0].set_ylim(0, 1.5)
	#axis[1].set_ylim(0, 1.5)
	#axis[2].set_ylim(0, 1.5)
	#axis[3].set_ylim(0, 1.5)

	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	#pdb.set_trace()
	#axis[2].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[3].axhline(1, color="red", linestyle="-", linewidth=2)

	y0 = df[df.num_qubits == 12].set_index("budget")
	y1 = df[df.num_qubits == 12].set_index("budget")
	
	#axis[0].set_xticklabels(x)
	#axis[1].set_xticklabels(x)
	#axis[2].set_xticklabels(x)
	#axis[3].set_xticklabels(x)

	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	#axis[3].set_ylim(0,1.25)	
	
	grouped_bar_plot(ax=axis[0], y=np.array(y0['depth']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], group_labels=['b=3', 'b=4', 'b=5'], show_average_text=True, average_text_position=0.8)

	grouped_bar_plot(ax=axis[1], y=np.array(y1['num_nonlocal_gates']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['b=3', 'b=4', 'b=5'], average_text_position=0.5)
	'''
	#seaborn grouped bar plot, grouped by method for y00, y01, y10, y11
	#sns.barplot(data=y00, x="method", y="depth", ax=axis[0], hue="bench_name", legend=False, palette="pastel", edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y01, x="method", y="num_nonlocal_gates", ax=axis[1], hue="bench_name", palette="pastel", legend=False, edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y10, x="method", y="depth", ax=axis[2], palette="pastel", hue="bench_name", edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y11, x="method", y="num_nonlocal_gates", ax=axis[3], hue="bench_name" , palette="pastel", legend=False, edgecolor="black", linewidth=1.5)
	#
	y00_depth_means = y00.groupby('method')['depth'].mean()
	y01_cnot_means = y01.groupby('method')['num_nonlocal_gates'].mean()
	y10_depth_means = y10.groupby('method')['depth'].mean()
	y11_cnot_means = y11.groupby('method')['num_nonlocal_gates'].mean()

	print(y00_depth_means)

	#draw horizontal lines for the mean values, 3 mean values per plot
	#axis[0].axhline(y=(y00_depth_means['FrozenQubits']), color=colors[0], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[1].axhline(y=y01_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[2].axhline(y=y10_depth_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[3].axhline(y=y11_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['QOS'], color=colors[2], linestyle='--')

	#hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:len(df['bench_name'].unique())]))

	hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:3]))

	print(hatch_order)
	
	#for i, patch in enumerate(axis[0].patches):
	#	patch.set_hatch(hatch_order[i])
	
	# Plot average values on the graph

	#y00.plot(kind='bar', ax=axis[0], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")
	#grouped_bar_plot(ax=axis[1], y=y01, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y01.plot(kind='bar', ax=axis[1], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	#grouped_bar_plot(ax=axis[2], y=y10, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y10.plot(kind='bar', ax=axis[2], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")

	#grouped_bar_plot(ax=axis[3], y=y11, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y11.plot(kind='bar', ax=axis[3], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	'''
	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)
	axis[1].set_xlabel(None)

	axis[0].set_ylabel(None)
	axis[1].set_ylabel(None)

	axis[0].axhline(y=1, color='red', linestyle='--')
	axis[1].axhline(y=1, color='red', linestyle='--')

	plt.subplots_adjust(hspace=0.35)

	#Add shared ylabel to figure
	fig.text(0.06, 0.5, "Relative values to Qiskit", va='center', rotation='vertical', fontsize=FONTSIZE)

	#Add shared xlabel to figure
	#fig.text(0.5, 0.04, , ha='center', fontweight="bold", fontsize=FONTSIZE)

	handles, labels = axis[1].get_legend_handles_labels()

	axis[1].legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(-0.15,-0.15),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_budget_comparison_fidelity(dataframes: list[pd.DataFrame], titles: list[str]=[]):

	xlabel = ['12 qubits', '24 qubits']

	ylabel = ['Relative difference']
	output_file = "budget_comparison_overhead_fidelity__.pdf"

	df = dataframes[0]

	#for df in dataframes:
	#	df_new = df[df['method'] != 'qiskit'].reset_index(drop=True)
	#	df_join = pd.concat([df_join, df_new], ignore_index=True)

	#df = df_join
	#bench_names = np.unique(df["bench_name"].to_list())
	#print(bench_names)

	fig = plt.figure(figsize=(6.5, 4.3))

	#x = np.array([12, 24])
	#x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	#pdb.set_trace()
	#axis[0].set_ylim(0, 1.5)
	#axis[1].set_ylim(0, 1.5)
	#axis[2].set_ylim(0, 1.5)
	#axis[3].set_ylim(0, 1.5)

	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	#pdb.set_trace()
	#axis[2].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[3].axhline(1, color="red", linestyle="-", linewidth=2)

	y0 = df.set_index("size")
	#y1 = df[df.num_qubits == 12].set_index("budget")
	
	#axis[0].set_xticklabels(x)
	#axis[1].set_xticklabels(x)
	#axis[2].set_xticklabels(x)
	#axis[3].set_xticklabels(x)

	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	#axis[3].set_ylim(0,1.25)	
	
	grouped_bar_plot(ax=axis[0], y=np.array(y0), bar_labels=["Classical Overhead", "Quantum Overhead", "Fidelity Improvement"], group_labels=['12 qubits', '24 qubits'], show_average_text=False)

	#grouped_bar_plot(ax=axis[1], y=np.array(y1['num_nonlocal_gates']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['b=3', 'b=4', 'b=5'], average_text_position=0.5)

	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	#axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)
	#axis[1].set_xlabel(None)

	axis[0].set_ylabel(None)
	#axis[1].set_ylabel(None)

	axis[0].axhline(y=1, color='red', linestyle='--')
	#axis[1].axhline(y=1, color='red', linestyle='--')

	#plt.subplots_adjust(hspace=0.35)

	#Add shared ylabel to figure
	fig.text(0.01, 0.5, "Relative Factor to Qiskit", va='center', rotation='vertical', fontsize=FONTSIZE)

	#Add shared xlabel to figure
	#fig.text(0.5, 0.04, , ha='center', fontweight="bold", fontsize=FONTSIZE)

	handles, labels = axis[0].get_legend_handles_labels()

	axis[0].set_yscale('log')

	axis[0].legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(0.25,0.86),
        ncol=1,
        frameon=True,
    )
	
	fig.text(0.5, 0.9, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def plot_budget_comparison_fidelity(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "budget_comparison_fid.pdf"):

	xlabel = ['Qiskit', 'Budget b=3', 'Budget b=4', 'Budget b=5']

	ylabel = ['ESP']
	titles = ['(a) ESP']

	df_join = pd.DataFrame()

	reference = dataframes[0][dataframes[0]['method'] == 'qiskit'].reset_index(drop=True)

	df_join = pd.concat([df_join, reference], ignore_index=True)

	reference = dataframes[1][dataframes[1]['method'] == 'qiskit'].reset_index(drop=True)

	df_join = pd.concat([df_join, reference], ignore_index=True)

	for df in dataframes:
		df_wo_reference = df[df['method'] != 'qiskit'].reset_index(drop=True)
	
		#col = df.columns[2]
		#base_values = reference[col]
		#df_wo_reference[col] = df_wo_reference[col] / cycle_until_sizematch(df_wo_reference[col], base_values)
  
		df_join = pd.concat([df_join, df_wo_reference], ignore_index=True)
	
	df = df_join
	bench_names = np.unique(df["bench_name"].to_list())
	print(bench_names)

	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	#x = np.array([12, 24])
	x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	#pdb.set_trace()
	axis[0].set_ylim(0, 1)

	#axis[1].set_ylim(0, 1.2)
	#axis[2].set_ylim(0, 1.5)
	#axis[3].set_ylim(0, 1.5)

	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	#pdb.set_trace()
	#axis[2].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[3].axhline(1, color="red", linestyle="-", linewidth=2)

	#y0 = df[df.method == 'qiskit'].set_index("budget")
	#y1 = df[df.method == 'QOS'].set_index("budget")
	
	#axis[0].set_xticklabels(x)
	#axis[1].set_xticklabels(x)
	#axis[2].set_xticklabels(x)
	#axis[3].set_xticklabels(x)
 
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	#axis[3].set_ylim(0,1.25)
 
	avgs = df.groupby(['method', 'budget', 'num_qubits'])['fidelity'].mean().reset_index()
	
	#bar_plot(ax=axis[0], y=np.array(avgs)[:,2].reshape(4,1), show_average_text=False, bar_labels=["Qiskit", "Budget b=3", "Budget b=4", "Budget b=5"])
 
	avgs = avgs.iloc[[6,0,2,4,7,1,3,5]]

	grouped_bar_plot(ax=axis[0], y=np.array(avgs['fidelity']).reshape(2,4), bar_labels=["Qiskit", "Budget b=3", 'Budget b=4', 'Budget b=5'], show_average_text=False, group_labels=['12 qubits', '24 qubits'], bar_width=0.15)

	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)

	axis[0].set_ylabel(None)

	#axis[0].axhline(y=0.74, color='red', linestyle='--')
	#axis[1].axhline(y=1, color='red', linestyle='--')

	#plt.subplots_adjust(hspace=0.35)

	#Add shared ylabel to figure
	fig.text(0.01, 0.5, "ESP", va='center', rotation='vertical', fontsize=FONTSIZE)

	#Add shared xlabel to figure
	#fig.text(0.5, 0.04, , ha='center', fontweight="bold", fontsize=FONTSIZE)

	handles, labels = axis[0].get_legend_handles_labels()

	axis[0].legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(0.5,-0.17),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_custom_plot_small_circuit_relative_properties_barplot(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "relative_properties.pdf"):

	xlabel = ['12 qubits', '24 qubits']
	ylabel = ['Depth', 'Number of CNOT gates']
	titles = ['(a) Depth - 12 qubits', '(b) Number of CNOT gates - 12 qubits', '(c) Depth - 24 qubits', '(d) Number of CNOT gates - 24 qubits']

	df_join = pd.DataFrame()

	for df in dataframes:
		df_wo_reference = df[df['method'] != 'qiskit'].reset_index(drop=True)
		reference = df[df['method'] == 'qiskit'].reset_index(drop=True)
	
		for col in df.columns[2:5]:  # Skip the first column (bench_name)
			base_values = reference[col]
			df_wo_reference[col] = df_wo_reference[col] / cycle_until_sizematch(df_wo_reference[col], base_values)

		df_join = pd.concat([df_join, df_wo_reference], ignore_index=True)
		
	df = df_join
	bench_names = np.unique(df["bench_name"].to_list())
	print(bench_names)

	fig = plt.figure(figsize=(26, 2.8))
	#fig = plt.figure(figsize=(13, 5.6))

	#x = np.array([12, 24])
	x = dataframes[0]["bench_name"]

	#On the first row we plot 12 qubit circuits, on the second row 24 qubit circuits
	#On each row we plot the depth and the number of cnot gates

	nrows = 1
	ncols = 4
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]
 	
	#df = df[~((df['method'] == 'FrozenQubits') & (df['bench_name'] != 'qaoa_r3') & (df['bench_name'] != 'qaoa_pl1'))]

	y00 = df[df.num_qubits == 12].set_index("method")
	y01 = df[df.num_qubits == 12].set_index("method")
	y10 = df[df.num_qubits == 24].set_index("method")
	y11 = df[df.num_qubits == 24].set_index("method")
	
	axis[0].set_xticklabels(x)
	axis[1].set_xticklabels(x)
	axis[2].set_xticklabels(x)
	axis[3].set_xticklabels(x)

	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)
	axis[2].grid(axis="y", linestyle="-", zorder=-1)
	axis[3].grid(axis="y", linestyle="-", zorder=-1)

	axis[3].set_ylim(0,1.35)

	groupings = [0,2,11,20]

	#y00 = np.array(y00)
	#y00 = [y00[groupings[j-1]:groupings[j]] for j in range(1,len(groupings))]
#
	#y01 = np.array(y01)
	#y01 = [y01[groupings[j-1]:groupings[j]] for j in range(1,len(groupings))]
#
	#y10 = np.array(y10)
	#y10 = [y10[groupings[j-1]:groupings[j]] for j in range(1,len(groupings))]
#
	#y11 = np.array(y11)
	#y11 = [y11[groupings[j-1]:groupings[j]] for j in range(1,len(groupings))]

	#remove rows with FrozenQubits as method and benchmark different from qaoa-r3 and qaoa-p1  
	#uneven_grouped_bar_plot(ax=axis[0], y=y00, bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], group_labels=['FrozenQubits', 'CutQC', 'QOS'], show_average_text=True)

	#uneven_grouped_bar_plot(ax=axis[1], y=y01, bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'])
#
	#uneven_grouped_bar_plot(ax=axis[2], y=y10, bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'], average_text_position=1.1)
#
	#uneven_grouped_bar_plot(ax=axis[3], y=y11, bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'])

	#[ax.get_legend().remove() for ax in axis]
 
	#pdb.set_trace()

	df[df.loc[((df['method'] == 'FrozenQubits') & (df['bench_name'] != 'qaoa_r3') & (df['bench_name'] != 'qaoa_pl1'))]]['depth'] = 0

	grouped_bar_plot(ax=axis[0], y=np.array(y00['depth']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], group_labels=['FrozenQubits', 'CutQC', 'QOS'], show_average_text=True)

	grouped_bar_plot(ax=axis[1], y=np.array(y01['num_nonlocal_gates']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'])

	grouped_bar_plot(ax=axis[2], y=np.array(y10['depth']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'], average_text_position=1.1)

	grouped_bar_plot(ax=axis[3], y=np.array(y11['num_nonlocal_gates']).reshape(3,9), bar_labels=["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, group_labels=['FrozenQubits', 'CutQC', 'QOS'])

	'''

	#seaborn grouped bar plot, grouped by method for y00, y01, y10, y11
	#sns.barplot(data=y00, x="method", y="depth", ax=axis[0], hue="bench_name", legend=False, palette="pastel", edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y01, x="method", y="num_nonlocal_gates", ax=axis[1], hue="bench_name", palette="pastel", legend=False, edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y10, x="method", y="depth", ax=axis[2], palette="pastel", hue="bench_name", edgecolor="black", linewidth=1.5)
#
	#sns.barplot(data=y11, x="method", y="num_nonlocal_gates", ax=axis[3], hue="bench_name" , palette="pastel", legend=False, edgecolor="black", linewidth=1.5)
	#
	y00_depth_means = y00.groupby('method')['depth'].mean()
	y01_cnot_means = y01.groupby('method')['num_nonlocal_gates'].mean()
	y10_depth_means = y10.groupby('method')['depth'].mean()
	y11_cnot_means = y11.groupby('method')['num_nonlocal_gates'].mean()

	print(y00_depth_means)

	#draw horizontal lines for the mean values, 3 mean values per plot
	#axis[0].axhline(y=(y00_depth_means['FrozenQubits']), color=colors[0], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[0].axhline(y=y00_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[1].axhline(y=y01_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[1].axhline(y=y01_cnot_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[2].axhline(y=y10_depth_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['CutQC'], color=colors[1], linestyle='--')
	#axis[2].axhline(y=y10_depth_means['QOS'], color=colors[2], linestyle='--')
#
	#axis[3].axhline(y=y11_cnot_means['FrozenQubits'], color=colors[0], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['CutQC'], color=colors[1], linestyle='--')
	#axis[3].axhline(y=y11_cnot_means['QOS'], color=colors[2], linestyle='--')

	#hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:len(df['bench_name'].unique())]))

	hatch_order = cycle_until_sizematch(pd.DataFrame(list(axis[0].patches)), pd.DataFrame(hatches[:3]))

	print(hatch_order)
	
	#for i, patch in enumerate(axis[0].patches):
	#	patch.set_hatch(hatch_order[i])
	
	# Plot average values on the graph

	#y00.plot(kind='bar', ax=axis[0], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")
	#grouped_bar_plot(ax=axis[1], y=y01, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y01.plot(kind='bar', ax=axis[1], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	#grouped_bar_plot(ax=axis[2], y=y10, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y10.plot(kind='bar', ax=axis[2], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="depth")

	#grouped_bar_plot(ax=axis[3], y=y11, bar_labels=["qiskit", "qf", "wr", "qos"], show_average_text=True, average_text_position=1.3)

	#y11.plot(kind='bar', ax=axis[3], color='blue', alpha=0.5, capsize=5, error_kw=dict(lw=1, capsize=5, capthick=2), y="num_nonlocal_gates")

	'''
	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	axis[3].set_title(titles[3], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)
	axis[1].set_xlabel(None)
	axis[2].set_xlabel(None)
	axis[3].set_xlabel(None)

	axis[0].set_ylabel(None)
	axis[1].set_ylabel(None)
	axis[2].set_ylabel(None)
	axis[3].set_ylabel(None)

	axis[0].axhline(y=1, color='red', linestyle='--')
	axis[1].axhline(y=1, color='red', linestyle='--')
	axis[2].axhline(y=1, color='red', linestyle='--')
	axis[3].axhline(y=1, color='red', linestyle='--')

	#plt.subplots_adjust(hspace=1)
	#plt.subplots_adjust()

	#Add shared ylabel to figure
	#fig.text(0.06, 0.5, "Relative Values to Qiskit", va='center', rotation='vertical', fontsize=FONTSIZE)
 
	fig.text(0.1, 0.5, "Relative Values to Qiskit", va='center', rotation='vertical', fontsize=FONTSIZE)

	#Add shared xlabel to figure
	#fig.text(0.5, 0.04, , ha='center', fontweight="bold", fontsize=FONTSIZE)

	handles, labels = axis[2].get_legend_handles_labels()

	axis[2].legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(-0.1,-0.2),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	#plt.tight_layout(w_pad=-30)
	plt.subplots_adjust(wspace=0.15)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_small_circuit_overheads(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "overheads.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	x = np.array([12, 24])
	#x = dataframes[0]["bench_name"]

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])

	#axis[1].set_ylabel(ylabel[1])
	#axis[1].set_xlabel(xlabel[1])

	#axis[0].set_yscale("log")
	axis[0].set_ylim(0, 1.6)

	#ytick_labels = ['0', '1', '2', '4', '8', '16', '32']
	#axis[0].set_yticklabels(ytick_labels)

	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	axis[3].set_title(titles[3], fontsize=FONTSIZE, fontweight="bold")
	
	axis[0].set_xlabel(None)
	axis[1].set_xlabel(None)
	axis[2].set_xlabel(None)
	axis[3].set_xlabel(None)
	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	#axis[1].axhline(1, color="red", linestyle="-", linewidth=2)
	
	to_plot = []
	to_plot.append([])
	#print(np.mean(dataframes[0]["num_nonlocal_gates"].to_list()))
	to_plot[0].append(np.median(dataframes[0]["num_qubits"].to_list()))
	to_plot[0].append(np.median(dataframes[0]["fidelity"].to_list()))
	to_plot[0].append(np.median(dataframes[0]["num_nonlocal_gates"].to_list()))

	print(np.median(dataframes[0]["num_nonlocal_gates"].to_list()) / np.median(dataframes[0]["num_qubits"].to_list()))

	to_plot.append([])
	to_plot[1].append(np.median(dataframes[1]["num_qubits"].to_list()))
	to_plot[1].append(np.median(dataframes[1]["fidelity"].to_list()))
	to_plot[1].append(np.median(dataframes[1]["num_nonlocal_gates"].to_list()))

	print(np.median(dataframes[1]["num_nonlocal_gates"].to_list()) / np.median(dataframes[1]["num_qubits"].to_list()))
	#print(np.mean(dataframes[1]["num_nonlocal_gates"].to_list()))
	#print(to_plot)
	y0 = np.array(
		to_plot
	)

	to_plot = []
	to_plot.append([])
	to_plot[0].append(np.mean(dataframes[0]["depth"].to_list()))
	to_plot[0].append(np.mean(dataframes[0]["fidelity_std"].to_list()))
	to_plot[0].append(np.mean(dataframes[0]["num_measurements"].to_list()))

	
	to_plot.append([])
	to_plot[1].append(np.mean(dataframes[1]["depth"].to_list()))
	to_plot[1].append(np.mean(dataframes[1]["fidelity_std"].to_list()))
	to_plot[1].append(np.mean(dataframes[1]["num_measurements"].to_list()))
	
	yerr0 = np.array(
		to_plot
	)

	#print(y0)
	#exit()
	
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)


	grouped_bar_plot(axis[0], y0, yerr0, ["Baseline", "QOS Optimizer", "QOS Compilation"])

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	#axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	#fig.legend()

	handles, labels = axis[0].get_legend_handles_labels()
	
	axis[0].xticks([])
	axis[1].xticks([])
	axis[2].xticks([])
	axis[3].xticks([])	

	groups = ["FrozenQubits", "CutQc", "QOS"]

	fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
		labels=groups,
        frameon=False,
    )
	
	fig.text(0.5, 0.95, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_small_circuit_fidelities(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "dt_fidelities.pdf"):

	#fig = plt.figure(figsize=WIDE_FIGSIZE)

	x = np.array([12, 24])
	#x = dataframes[0]["bench_name"]

	nrows = 1
	ncols = 9
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	#axis = [fig.add_subplot(gs[i, j], sharey=True, sharex=True) for i in range(nrows) for j in range(ncols)]
	fig, axis = plt.subplots(1, ncols, figsize=WIDE_FIGSIZE, sharex=True, sharey=True)

	axis[0].set_ylabel(ylabel[0])
	axis[4].set_xlabel(xlabel[0])

	averages_12 = []
	averages_24 = []

	for i in range(9):		

		axis[i].set_ylim(0, 1)

		#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)
	
		to_plot = []
		#print(np.mean([df["num_nonlocal_gates"].to_list() for df in dataframes]))
		to_plot.append([])
		to_plot[0].append(dataframes[0]["fidelity"][i])
		to_plot[0].append(dataframes[1]["fidelity"][i])

		averages_12.append(dataframes[1]["fidelity"][i] / dataframes[0]["fidelity"][i])

		to_plot.append([])
		to_plot[1].append(dataframes[2]["fidelity"][i])
		to_plot[1].append(dataframes[3]["fidelity"][i])

		averages_24.append(dataframes[3]["fidelity"][i] / dataframes[2]["fidelity"][i])

		y0 = np.array(
			to_plot
		)

		to_plot = []
		to_plot.append([])
		to_plot[0].append(dataframes[0]["fidelity_std"][i])
		to_plot[0].append(dataframes[1]["fidelity_std"][i])

		to_plot.append([])
		to_plot[1].append(dataframes[1]["fidelity_std"][i])
		to_plot[1].append(dataframes[3]["fidelity_std"][i])

		yerr0 = np.array(
			to_plot
		)

		axis[i].set_xticklabels(x)
		axis[i].grid(axis="y", linestyle="-", zorder=-1)


		grouped_bar_plot(axis[i], y0, yerr0, ["Baseline", "QOS DT"])

		axis[i].set_title(titles[i], fontsize=FONTSIZE, fontweight="bold")
	#axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	#fig.legend()
	print(np.mean(averages_12), gmean(averages_12), np.median(averages_12))
	print(np.mean(averages_24), gmean(averages_24), np.median(averages_24))

	handles, labels = axis[0].get_legend_handles_labels()

	fig.legend(
        handles,
        labels,
        loc="lower left",
        bbox_to_anchor=(0.17, -0.11),
        ncol=9,
        frameon=False,
    )
	
	fig.text(0.5, 1.05, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_multiprogrammer(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "multiprogrammer_performance.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	x = np.array([30, 60, 88])

	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[0].set_ylim(0, 1.0)

	to_plot = []


	for i in range(3):
		to_plot.append([])
		no_mp_mean = np.mean(dataframes[(i*2)+1]["fidelity"].to_list())
		baseline_mp_mean = np.mean(dataframes[i*2]["fidelity"].to_list())
		qos_mp_mean = np.mean(dataframes[i*2]["fidelity_std"].to_list())

		to_plot[i].append(no_mp_mean)
		to_plot[i].append(baseline_mp_mean)
		to_plot[i].append(qos_mp_mean)
		print(qos_mp_mean / no_mp_mean, qos_mp_mean / baseline_mp_mean)
	
	y = np.array(
		to_plot
	)

	to_plot = []

	for i in range(3):
		to_plot.append([])
		to_plot[i].append(iqr(dataframes[(i*2)+1]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2]["fidelity_std"].to_list(), rng=(35, 65), scale='normal'))
		#print(to_plot[i])
		#print("---------------------")
		#print(iqr(dataframes[(i*2)+1]["fidelity"].to_list(), scale='normal'))

	yerr = np.array(
		to_plot
	)
	
	grouped_bar_plot(axis[0], y, yerr, ["No M/P", "Baseline M/P", "QOS M/P"])
	axis[0].legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=3, frameon=False)

	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 0.93, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_multiprogrammer_relative(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "multiprogrammer_relative.pdf"):

	#fig = plt.figure(figsize=WIDE_FIGSIZE)

	nrows = 1
	ncols = 3
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	#axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]
	fig, axis = plt.subplots(1, ncols, figsize=WIDE_FIGSIZE, gridspec_kw={'width_ratios': [1.1,0.8,1.1]})
	fig.tight_layout()

	x0 = np.array([30, 60, 88])

	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xticklabels(x0)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[0].set_ylim(0, 1.0)

	to_plot = []

	for i in range(3):
		to_plot.append([])
		no_mp_mean = np.mean(dataframes[(i*2)+1]["fidelity"].to_list())
		baseline_mp_mean = np.mean(dataframes[i*2]["fidelity"].to_list())
		qos_mp_mean = np.mean(dataframes[i*2]["fidelity_std"].to_list())

		to_plot[i].append(no_mp_mean)
		to_plot[i].append(baseline_mp_mean)
		to_plot[i].append(qos_mp_mean)
		#print(qos_mp_mean / no_mp_mean, qos_mp_mean / baseline_mp_mean)
	
	y = np.array(
		to_plot
	)

	to_plot = []

	for i in range(3):
		to_plot.append([])
		to_plot[i].append(iqr(dataframes[(i*2)+1]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2]["fidelity_std"].to_list(), rng=(35, 65), scale='normal'))

	yerr = np.array(
		to_plot
	)
	
	grouped_bar_plot(axis[0], y, yerr, ["No M/P", "Baseline M/P", "QOS M/P"])
	#axis[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=3, frameon=False)
	axis[0].legend()
	#axis[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=3, frameon=False)
	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	x1 = np.array([30, 60, 88])

	axis[1].set_xlabel(xlabel[1])
	axis[1].set_ylabel(ylabel[1])
	axis[1].set_xticklabels(x1)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].set_ylim(0, 100)
	

	y = np.array(
		[
			[23.3, 44.5, 70.2],
			[25.5, 53, 81.3]
		]
	)

	yerr = np.array(
		[
			[0, 0, 0],
			[0, 0, 0]
		]
	)

	grouped_bar_plot(axis[1], y.T, yerr.T, ["Basline M/P", "QOS M/P"])
	axis[1].legend()

	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")

	""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

	x1 = np.array([30, 60, 88])

	axis[2].set_xlabel(xlabel[2])
	axis[2].set_ylabel(ylabel[2])
	axis[2].set_xticklabels(x1)
	axis[2].grid(axis="y", linestyle="-", zorder=-1)
	axis[2].set_ylim(0, 1.2)
	axis[2].axhline(1, color="red", linestyle="-", linewidth=2)

	to_plot = []


	for i in range(3):
		to_plot.append([])
		for j in range(9):
			to_plot[i].append(dataframes[i*2 + 6]["fidelity_std"][j] / dataframes[(i*2)+7]["fidelity"][j])
		#to_plot[i].append(np.mean(dataframes[(i*2)+1]["fidelity"].to_list()))
		#to_plot[i].append(np.median(dataframes[i*2]["fidelity"].to_list()))
		#to_plot[i].append(np.median(dataframes[i*2]["fidelity_std"].to_list()))

	y = np.array(
		to_plot
	)

	yerr = np.zeros((3, 9))
	
	grouped_bar_plot(axis[2], y, yerr, ["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, average_text_position=1.1)
	#axis[2].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, fontsize=10)
	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 1.05, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_matcher(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "static_scheduler.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	x = np.array(["QAOA-R3", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])

	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[0].set_ylim(0, 1)
	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)

	y = np.array(
		dataframes[0][["num_qubits", "fidelity"]].values
	)

	yerr = np.array(

		dataframes[0][["depth", "fidelity_std"]].values

	)

	grouped_bar_plot(axis[0], y, yerr, ["IBM Auckland", "QOS"], show_average_text=False)

	axis[0].legend()
	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 0.93, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_spatial_hetero(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "spatial_heterogeneity.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE)

	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]

	x = np.array(["cairo", "hanoi", "kolkata", "mumbai", "algiers", "auckland"])

	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xticklabels(x)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[0].set_ylim(0, 1)
	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)

	y = np.array(
		[
			dataframes[0]["fidelity"]
		]
	)

	yerr = np.array(
		[
			dataframes[0]["fidelity_std"]
		]

	)

	grouped_bar_plot(axis[0], y.T, yerr.T, [""], show_average_text=False)

	#axis[0].legend()
	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	fig.text(0.5, 0.93, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_scal_spatial_hetero(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "scal_spatial_hetero.pdf"):


	nrows = 1
	ncols = 2
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	fig, axis = plt.subplots(1, ncols, figsize=WIDE_FIGSIZE, sharey=True, gridspec_kw={'width_ratios': [2, 1]})
	fig.tight_layout()

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylim(0, 1.1)
	x0 = np.array([4, 8, 12, 16, 20, 24])

	y = np.array(
		[
			df["fidelity"] for df in dataframes[0:6]
		]
	)

	yerr = np.array(
		[
			df["fidelity_std"] for df in dataframes[0:6]
		]
	)

	axis[0].set_xticklabels(x0)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y, yerr, ["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"], show_average_text=True, average_text_position=1.02)

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	
	handles, labels = axis[0].get_legend_handles_labels()

	axis[0].legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.5),
        ncol=7,
        frameon=False,
		#fontsize=10,
    )


	x1 = np.array(["cairo", "hanoi", "kolkata", "mumbai", "algiers", "auckland"])

	axis[1].set_xlabel(xlabel[1])
	axis[1].set_xticklabels(x1, rotation=45)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].set_ylim(0, 1.1)
	#axis[0].axhline(1, color="red", linestyle="-", linewidth=2)

	y = np.array(
		[
			dataframes[6]["fidelity"]
		]
	)

	yerr = np.array(
		[
			dataframes[6]["fidelity_std"]
		]

	)

	grouped_bar_plot(axis[1], y.T, yerr, [""], show_average_text=True, average_text_position=1.02)

	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")

	"""
	sns.set_style("whitegrid")
	colors = sns.color_palette("pastel")

	y = np.array(

		dataframes[7]["fidelity"]

	)
	print(y)
	x2=list(range(1, len(y)))

	sns.lineplot(data=y, ax=axis[2])
	axis[2].set_xlabel(xlabel[2])
	axis[2].set_xlim(0, 120)
	#axis[2].axline(np.mean(y), color="red", linestyle="-", linewidth=2)

	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	"""

	fig.text(0.5, 1.05, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

	return

def custom_plot_temp_util_load(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "temp_util_load.pdf"):

	#fig=plt.figure(figsize=WIDE_FIGSIZE)

	fig, axis = plt.subplots(1, 3, figsize=WIDE_FIGSIZE)
	fig.tight_layout()

	axis0 = axis[0]
	axis1 = axis[1]
	axis2 = axis[2]

	sns.set_style("whitegrid")
	colors = sns.color_palette("pastel")

	y = np.array(

		dataframes[0]["fidelity"]

	)
	x0=list(range(1, len(y)))

	sns.lineplot(data=y, ax=axis0)
	axis0.set_xlabel(xlabel[0])
	axis0.set_ylabel(ylabel[0])
	axis0.set_xlim(0, 120)
	axis0.set_ylim(0, 1)
	#axis[2].axline(np.mean(y), color="red", linestyle="-", linewidth=2)

	axis0.set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis0.text(60, 1.2, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	x1 = np.array(["QAOA-R3", "BV", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])

	axis1.set_ylabel(ylabel[1])
	axis1.set_xlabel(xlabel[1])
	axis1.set_ylim(0, 100)

	arr = [29.6, 29.6, 29.6, 29.6, 29.6, 14.8, 22.2, 22.2, 29.6,]
	
	y = np.array(
		[
			arr
		]
	)

	yerr = np.array(
		[
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		]
	)

	axis1.axhline(np.mean(arr), color="red", linestyle="-", linewidth=1)
	#print(np.mean(arr))
	
	axis1.set_xticklabels(x1, rotation=30, ha="right")
	axis1.grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis1, y.T, yerr.T, [""])

	axis1.set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	axis1.text(4, 120, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)	

	x2 = ["lagos", "nairobi", "perth", "algiers", "auckland", "cairo", "hanoi", "kolkata", "mumbai", "brisbane", "cusco", "nazca", "sherbrooke"]

	axis2.set_xlabel(xlabel[2])
	axis2.set_ylabel(ylabel[2])
	axis2.set_yscale("log")
	axis2.set_ylim(1, 10000)
	axis2.set_xticklabels(x2, rotation=30, ha="right")
	axis[2].axvline(2.5, color="red", linestyle="--", linewidth=1)
	axis[2].axvline(8.5, color="red", linestyle="--", linewidth=1)

	y = np.array(
		[
			dataframes[1]["queue_size"]
		]
	)

	yerr = np.array(
		[
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0]
		]
	)

	#print(len(x2))
	#print(len(y.T))

	grouped_bar_plot(axis2, y.T, yerr.T, [""])

	axis2.set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	axis2.text(6, 63000, "Equal is better", ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)	

	plt.savefig(output_file, bbox_inches="tight")

	return

def custom_plot_dt_mp_estim(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "dt_mp_estim_results.pdf"):

	fig, axis = plt.subplots(1, 3, figsize=WIDE_FIGSIZE)
	fig.tight_layout()

	x0 = np.array([12, 24, 40])	

	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xlabel(xlabel[0])

	#axis[0].set_ylim(0, 1.5)
	axis[0].set_yscale("log")

	to_plot = []
	to_plot.append([])

	to_plot[0].append(np.median(dataframes[0]["num_qubits"].to_list()))
	to_plot[0].append(np.median(dataframes[0]["fidelity"].to_list()))
	to_plot[0].append(np.median(dataframes[0]["num_nonlocal_gates"].to_list()))

	#print(np.median(dataframes[0]["num_nonlocal_gates"].to_list()) / np.median(dataframes[0]["num_qubits"].to_list()))

	to_plot.append([])
	to_plot[1].append(np.median(dataframes[1]["num_qubits"].to_list()))
	to_plot[1].append(np.median(dataframes[1]["fidelity"].to_list()))
	to_plot[1].append(np.median(dataframes[1]["num_nonlocal_gates"].to_list()))

	to_plot.append([])
	to_plot[2].append(np.median(dataframes[2]["num_qubits"].to_list()))
	to_plot[2].append(np.median(dataframes[2]["fidelity"].to_list()))
	to_plot[2].append(np.median(dataframes[2]["num_nonlocal_gates"].to_list()))

	print(np.median(dataframes[2]["num_nonlocal_gates"].to_list()) / np.median(dataframes[2]["num_qubits"].to_list()))

	y0 = np.array(
		to_plot
	)
	#print(dataframes[2])

	to_plot = []
	to_plot.append([])
	to_plot[0].append(np.mean(dataframes[0]["depth"].to_list()))
	to_plot[0].append(np.mean(dataframes[0]["fidelity_std"].to_list()))
	to_plot[0].append(np.mean(dataframes[0]["num_measurements"].to_list()))
	
	to_plot.append([])
	to_plot[1].append(np.mean(dataframes[1]["depth"].to_list()))
	to_plot[1].append(np.mean(dataframes[1]["fidelity_std"].to_list()))
	to_plot[1].append(np.mean(dataframes[1]["num_measurements"].to_list()))

	to_plot.append([])
	to_plot[2].append(np.mean(dataframes[2]["depth"].to_list()))
	to_plot[2].append(np.mean(dataframes[2]["fidelity_std"].to_list()))
	to_plot[2].append(np.mean(dataframes[2]["num_measurements"].to_list()))
	
	yerr0 = np.array(
		to_plot
	)

	axis[0].set_xticklabels(x0)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)

	grouped_bar_plot(axis[0], y0, yerr0, ["Baseline", "QOS Optimizer", "QOS Compilation"])

	axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[0].text(1, 220, LOWERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)
	axis[0].legend(loc="upper left")

	''''''''''''''''''''''''''''''''''''''''''''''''''''''
	x1 = np.array([30, 60, 88])

	axis[1].set_xlabel(xlabel[1])
	axis[1].set_ylabel(ylabel[1])
	axis[1].set_xticklabels(x1)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)
	axis[1].set_ylim(0, 1.0)

	to_plot = []

	for i in range(3):
		to_plot.append([])
		no_mp_mean = np.mean(dataframes[(i*2)+4]["fidelity"].to_list())
		baseline_mp_mean = np.mean(dataframes[i*2 + 3]["fidelity"].to_list())
		qos_mp_mean = np.mean(dataframes[i*2 + 3]["fidelity_std"].to_list())

		to_plot[i].append(no_mp_mean)
		to_plot[i].append(baseline_mp_mean)
		to_plot[i].append(qos_mp_mean)
		#print(qos_mp_mean / no_mp_mean, qos_mp_mean / baseline_mp_mean)
	
	y = np.array(
		to_plot
	)

	to_plot = []

	for i in range(3):
		to_plot.append([])
		to_plot[i].append(iqr(dataframes[(i*2)+4]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2 + 3]["fidelity"].to_list(), rng=(35, 65), scale='normal'))
		to_plot[i].append(iqr(dataframes[i*2 + 3]["fidelity_std"].to_list(), rng=(35, 65), scale='normal'))

	yerr = np.array(
		to_plot
	)
	
	grouped_bar_plot(axis[1], y, yerr, ["No M/P", "Baseline M/P", "QOS M/P"])
	#axis[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=3, frameon=False)
	axis[1].legend()
	#axis[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=3, frameon=False)
	axis[1].set_title(titles[1], fontsize=FONTSIZE, fontweight="bold")
	axis[1].text(1.3, 1.2, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	''''''''''''''''''''''''''''''''''''''''''''''''''''''

	x2 = np.array(["QAOA-R3", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])

	axis[2].set_xlabel(xlabel[2])
	axis[2].set_ylabel(ylabel[2])
	axis[2].set_xticklabels(x2, rotation=30)
	axis[2].grid(axis="y", linestyle="-", zorder=-1)
	axis[2].set_ylim(0, 1)

	y = np.array(
		dataframes[9][["num_qubits", "fidelity"]].values
	)

	yerr = np.array(

		dataframes[9][["depth", "fidelity_std"]].values

	)

	grouped_bar_plot(axis[2], y, yerr, ["IBM Auckland", "QOS Estimator"], show_average_text=False)

	axis[2].legend()
	axis[2].set_title(titles[2], fontsize=FONTSIZE, fontweight="bold")
	axis[2].text(3.6, 1.2, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_estimator(dataframes: list[pd.DataFrame], titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "estimator_results.pdf"):

	fig = plt.figure(figsize=COLUMN_FIGSIZE)
	nrows = 1
	ncols = 1
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)
	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]
	fig.tight_layout()

	x0 = np.array(["QAOA-R3", "GHZ", "HS-1", "QAOA-P1", "QSVM", "TL-1", "VQE-1", "W-STATE"])

	axis[0].set_xlabel(xlabel[0])
	axis[0].set_ylabel(ylabel[0])
	axis[0].set_xticklabels(x0, rotation=0)
	axis[0].grid(axis="y", linestyle="-", zorder=-1)
	axis[0].set_ylim(0, 1)

	y = np.array(
		dataframes[0][["num_qubits", "fidelity"]].values
	)

	yerr = np.array(

		dataframes[0][["depth", "fidelity_std"]].values

	)

	grouped_bar_plot(axis[0], y, yerr, ["IBM Auckland", "QOS Estimator"], show_average_text=False)

	axis[0].legend()
	#axis[0].set_title(titles[0], fontsize=FONTSIZE, fontweight="bold")
	axis[0].text(3.6, 1.05, HIGHERISBETTER, ha="center", va="center", fontweight="bold", color="navy", fontsize=ISBETTER_FONTSIZE)

	plt.savefig(output_file, bbox_inches="tight")

def custom_plot_dataframes(
	dataframes: list[pd.DataFrame],
	keys: list[list[str]],
	labels: list[list[str]],
	titles: list[str],
	ylabel: list[str],
	xlabel: list[str],
	output_file: str = "noisy_scale.pdf",
	nrows: int = 2,
	logscale = False,
) -> None:
	ncols = len(dataframes)
	fig = plt.figure(figsize=[13, 3.2])
	gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)

	axis = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]
	
	axis[0].set_yscale("log")
	axis[1].set_yscale("log")
	axis[2].set_yscale("log")

	#axis[2].set_xlim([10, 30])
	axis[1].set_ylim([1, 50000])
	#axis[2].set_ylim([10, 10 ** 20])
	#axis[2].set_yscale("log")

	for i, ax in enumerate(axis):
		ax.set_ylabel(ylabel=ylabel[i])
		ax.set_xlabel(xlabel=xlabel[i])
	
	#print(keys)
	plot_lines(axis[0], keys[0], labels[0], [dataframes[0]])
	axis[0].legend()		
	axis[0].set_title(titles[0], fontsize=12, fontweight="bold")
	
	plot_lines(axis[2], keys[2], labels[2], [dataframes[2]])
	axis[2].legend()		
	axis[2].set_title(titles[2], fontsize=12, fontweight="bold")

	num_vgates = dataframes[1]['qpu_size'].tolist()
	simulation = dataframes[1]['simulation'].tolist()
	knitting = dataframes[1]['knitting'].tolist()
	data = {
		"Simulation" : simulation,
		"Knitting" : knitting,
	}

	x = np.array([15, 20, 25])
	#x = np.arange(len(num_vgates))  # the label locations
	#width = 0.25  # the width of the bars
	#multiplier = 0
	y = np.array(
		[
			[9.52130384114571, 120.0079321230296, 801.0942367650568],
			[11.77336971112527, 726.3718322570203, 208.40429024997866],
			[1.7376548638567328, 5857.7779290829785, 305.2052580610034]
		]
	)

	yerr = np.array(
		[
			[1.3718322570203, 6.270605635945685, 41.68920839508064],
			[2.7376548638567328, 33.503638901049, 8.03563788096653],
			[0.2052580610034, 155.2813523421064, 22.93891781999264]
		]
	)
	
	axis[1].set_xticklabels(x)
	axis[1].grid(axis="y", linestyle="-", zorder=-1)	
	grouped_bar_plot(axis[1], y, yerr, ["Compilation", "Simulation", "Knitting"])
	axis[1].legend()

	axis[1].set_yticks(np.logspace(1, 5, base=10, num=5, dtype='int'))
	axis[1].set_title(titles[1], fontsize=12, fontweight="bold")
	
	fig.text(0.5, 1, "Lower is better ↓", ha="center", va="center", fontweight="bold", color="navy", fontsize=14)
	os.makedirs(os.path.dirname(output_file), exist_ok=True)
	plt.tight_layout(pad=1)
	plt.savefig(output_file, bbox_inches="tight")
