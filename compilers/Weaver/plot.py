#from qiskit.transpiler.passes import SabreLayout
from qiskit import QuantumCircuit
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

#from qiskit import transpile
import pdb
#from time import perf_counter
import numpy as np
import pandas as pd
#from qiskit.providers.fake_provider import FakeWashington
from utils.plot.util import grouped_bar_plot, plot_line, stacked_grouped_bar_plot
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

#if not isinstance(n_variables, list):
#   n_variables = [n_variables]

n_variables = [20, 50, 75, 100, 150, 250]

def plot_compilation_time():

    data_atomique = pd.read_csv('results/atomique_results.csv')
    data_geyser = pd.read_csv('results/geyser_results.csv')
    data_superconducting = pd.read_csv('results/superconducting_results.csv')
    data_weaver = pd.read_csv('results/weaver_results.csv')
    data_dpqa = pd.read_csv('results/dpqa_results.csv')

    data = []
    fig, ax = plt.subplots(1,2, figsize=(20, 4.5))

    benchmarks = ['uf20-01', 'uf20-02', 'uf20-03', 'uf20-04', 'uf20-05', 'uf20-06', 'uf20-07', 'uf20-08', 'uf20-09', 'uf20-10', 'Mean']

    # (a) Compilation time for fixed number of variables (20 variables)    
    var = 20

    atomique_compilation_time = data_atomique[data_atomique['n_variables']==var]['compilation_time'].to_list()
    atomique_compilation_time_mean = data_atomique[data_atomique['n_variables']==var]['compilation_time'].mean()

    geyser_compilation_time = data_geyser[data_geyser['n_variables']==var]['runtime'].to_list()
    geyser_compilation_time_mean = data_geyser[data_geyser['n_variables']==var]['runtime'].mean()
        
    superconducting_compilation_time = data_superconducting[data_superconducting['n_variables']==var]['runtime'].to_list()
    superconducting_compilation_time_mean = data_superconducting[data_superconducting['n_variables']==var]['runtime'].mean()

    weaver_compilation_time = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['compilation_time (seconds)'].to_list()
    weaver_compilation_time_mean = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['compilation_time (seconds)'].mean()
        
    dpqa_compilation_time = data_dpqa[data_dpqa['n_variables']==var]['compile_time'].to_list()
    dpqa_compilation_time_mean = data_dpqa[data_dpqa['n_variables']==var]['compile_time'].mean()

    data = [[superconducting_compilation_time[i], atomique_compilation_time[i], weaver_compilation_time[i], dpqa_compilation_time[i], geyser_compilation_time[i]] for i in range(len(atomique_compilation_time))]
    data.append([superconducting_compilation_time_mean, atomique_compilation_time_mean, weaver_compilation_time_mean, dpqa_compilation_time_mean, geyser_compilation_time_mean])        
    data = np.array(data)

    grouped_bar_plot(ax[0], data, bar_labels=['Superconducting', 'Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in benchmarks])

    ax[0].axvline(9.85, color='grey', linestyle='dashed', linewidth=2)

    ax[0].text(
        8.5,
        60000,
        "Lower is better ↓",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color="midnightblue",
    )

    ax[0].set_yscale('log')
    ax[0].set_ylabel('Compilation time [seconds]')
    ax[0].set_title('(a) Compilation time - Fixed size circuit', fontweight='bold', loc='left')

    spacing = 0.95

    num_groups, num_bars = data.shape

    bar_width = None

    if bar_width == None:
        bar_width = spacing / (num_bars + 1)

    bar_width = bar_width * 1.1

    nan_n = 3
    for j in range(num_groups):
        if np.isnan(data[j][nan_n]):
            ax[0].text((nan_n+j*num_groups-1)//num_groups+nan_n*bar_width, 10**-1.43, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

    data = []

    for var in n_variables:
        atomique_compilation_time = data_atomique[data_atomique['n_variables']==var]['compilation_time'].mean()
        geyser_compilation_time = data_geyser[data_geyser['n_variables']==var]['runtime'].mean()
        superconducting_compilation_time = np.array(data_superconducting[data_superconducting['n_variables']==var]['runtime']).mean()
        weaver_compilation_time = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['compilation_time (seconds)'].mean()
        dpqa_compilation_time = data_dpqa[data_dpqa['n_variables']==var]['compile_time'].mean()
        data.append([superconducting_compilation_time, atomique_compilation_time, weaver_compilation_time, dpqa_compilation_time, geyser_compilation_time])
        
    data = np.array(data)

    grouped_bar_plot(ax[1], data, bar_labels=['Superconducting', 'Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in n_variables])

    ax[1].set_yscale('log')
    ax[1].set_title('(b) Compilation time - Variable size circuit', fontweight='bold', loc='left')

    num_groups, num_bars = data.shape
    spacing = 0.95
    bar_width = None

    if bar_width == None:
        bar_width = spacing / (num_bars + 1)

    bar_width = bar_width * 1.1

    ax[1].set_xlim(-0.3, 5.85)

    for nan_n in range(5):
        for j in range(num_groups):
            if np.isnan(data[j][nan_n]):
                ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width, 10**-1.29, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax[1].text(
        4.5,
        10**4.5,
        "Lower is better ↓",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color="midnightblue",
    )

    ax[1].set_xlabel('Number of variables')
    ax[0].set_xlabel('MAX-3SAT Benchmark Suite')
    ax[0].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)
    ax[1].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)

    plt.subplots_adjust(bottom=0.22)
    plt.tight_layout()

    output_file = 'plots/figure9.pdf'
    plt.savefig(output_file)
    

def plot_execution_time():
        # Execution time fixed 20 variables

        data_atomique = pd.read_csv('results/atomique_results.csv')
        data_geyser = pd.read_csv('results/geyser_results.csv')
        data_superconducting = pd.read_csv('results/superconducting_results.csv')
        data_weaver = pd.read_csv('results/weaver_results.csv')
        data_dpqa = pd.read_csv('results/dpqa_results.csv')

        data = []
        fig, ax = plt.subplots(1,2, figsize=(20, 4.5))

        spacing = 0.95

        var = 20
        atomique_execution_time = data_atomique[data_atomique['n_variables']==var]['execution_time'].tolist()
        atomique_execution_time_mean = data_atomique[data_atomique['n_variables']==var]['execution_time'].mean()
        
        geyser_execution_time = (data_geyser[data_geyser['n_variables']==var]['execution_time'] / 1e6).to_list()
        geyser_execution_time_mean = data_geyser[data_geyser['n_variables']==var]['execution_time'].mean() / 1e6
        
        superconducting_execution_time = np.array(data_superconducting[data_superconducting['n_variables']==var]['execution_time']).tolist()
        superconducting_execution_time_mean = np.array(data_superconducting[data_superconducting['n_variables']==var]['execution_time']).mean()
        
        weaver_execution_time = (data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['execution_time (microseconds)'] / 1e6).tolist()
        weaver_execution_time_mean = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['execution_time (microseconds)'].mean() / 1e6
        
        dpqa_execution_time = data_dpqa[data_dpqa['n_variables']==var]['eps'].to_list()
        dpqa_execution_time_mean = data_dpqa[data_dpqa['n_variables']==var]['eps'].mean()

        data = [[superconducting_execution_time[i], atomique_execution_time[i], weaver_execution_time[i], dpqa_execution_time[i], geyser_execution_time[i]] for i in range(len(atomique_execution_time))]
        data.append([superconducting_execution_time_mean, atomique_execution_time_mean, weaver_execution_time_mean, dpqa_execution_time_mean, geyser_execution_time_mean])

        benchmarks = ['uf20-01', 'uf20-02', 'uf20-03', 'uf20-04', 'uf20-05', 'uf20-06', 'uf20-07', 'uf20-08', 'uf20-09', 'uf20-10', 'Mean']

        data = np.array(data)

        grouped_bar_plot(ax[0], data, bar_labels=['Superconducting', 'Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in benchmarks])

        num_groups, num_bars = data.shape

        bar_width = spacing / (num_bars + 1)

        bar_width = bar_width * 1.1

        nan_n = 3
        for j in range(num_groups):
            if np.isnan(data[j][nan_n]):
                ax[0].text((nan_n+j*num_groups-1)//num_groups+nan_n*bar_width, 10**-3.64, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

        #ax.set_title('Circuit execution time', fontweight='bold')

        ax[0].set_ylabel('Execution time [seconds]')

        ax[0].set_title('(a) Execution time - Fixed size', fontweight='bold', loc='left')

        ax[0].axvline(9.85, color='grey', linestyle='dashed', linewidth=2)

        ax[0].text(
            8.5,
            0.225,
            "Lower is better ↓",
            ha="center",
            fontsize=14,
            fontweight="bold",
            color="midnightblue",
        )

        ax[0].set_yscale('log')

        # Execution time variable

        data = []
        for var in n_variables:
            atomique_execution_time = data_atomique[data_atomique['n_variables']==var]['execution_time'].mean()# * 1e6
            geyser_execution_time = data_geyser[data_geyser['n_variables']==var]['execution_time'].mean() / 1e6
            superconducting_execution_time = np.array(data_superconducting[data_superconducting['n_variables']==var]['execution_time']).mean()# * 1e6
            weaver_execution_time = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['execution_time (microseconds)'].mean() / 1e6
            dpqa_execution_time = data_dpqa[data_dpqa['n_variables']==var]['eps'].mean()

            data.append([superconducting_execution_time, atomique_execution_time, weaver_execution_time, dpqa_execution_time, geyser_execution_time])

        data = np.array(data)

        num_groups, num_bars = data.shape

        grouped_bar_plot(ax[1], data, bar_labels=['Superconducting', 'Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in n_variables])

        ax[1].text(
            4.5,
            4,
            "Lower is better ↓",
            ha="center",
            fontsize=14,
            fontweight="bold",
            color="midnightblue",
        )

        ax[1].set_title('(b) Execution time - Variable size', fontweight='bold', loc='left')

        ax[1].set_yscale('log')

        ax[1].set_xlabel('Number of variables')

        ax[0].set_xlabel('MAX-3SAT Benchmark Suite')

        ax[1].set_xlim(-0.3, 5.85)

        for nan_n in range(5):
            for j in range(num_groups):
                if np.isnan(data[j][nan_n]):
                    ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width, 10**-3.65, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax[0].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)

        ax[1].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)

        plt.subplots_adjust(bottom=0.22)

        plt.tight_layout()

        output_file = 'plots/figure11.pdf'
        plt.savefig(output_file)


def plot_fidelity():

        data = []
        fig, ax = plt.subplots(1,2, figsize=(20, 4.5))
        spacing = 0.95

        data_atomique = pd.read_csv('results/atomique_results.csv')
        data_geyser = pd.read_csv('results/geyser_results.csv')
        data_superconducting = pd.read_csv('results/superconducting_results.csv')
        data_weaver = pd.read_csv('results/weaver_results.csv')
        data_dpqa = pd.read_csv('results/dpqa_results.csv')

        benchmarks = ['uf20-01', 'uf20-02', 'uf20-03', 'uf20-04', 'uf20-05', 'uf20-06', 'uf20-07', 'uf20-08', 'uf20-09', 'uf20-10', 'Mean']
        var = 20

        atomique_fidelity = data_atomique[data_atomique['n_variables']==var]['total_fidelity'].to_list()
        atomique_fidelity_mean = data_atomique[data_atomique['n_variables']==var]['total_fidelity'].mean()

        superconducting_fidelity = np.array(data_superconducting[data_superconducting['n_variables']==var]['eps']).tolist()
        superconducting_fidelity_mean = np.array(data_superconducting[data_superconducting['n_variables']==var]['eps']).mean()
        
        dpqa_fidelity = data_dpqa[data_dpqa['n_variables']==var]['eps'].tolist()
        dpqa_fidelity_mean = data_dpqa[data_dpqa['n_variables']==var]['eps'].mean()

        weaver_fidelity = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['eps (fidelity)'].to_list()
        weaver_fidelity_mean = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['eps (fidelity)'].mean()

        geyser_fidelity = [np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN]
        geyser_fidelity_mean = np.NAN

        data = [[atomique_fidelity[i], weaver_fidelity[i], dpqa_fidelity[i], geyser_fidelity[i]] for i in range(len(atomique_fidelity))]
        
        data.append([atomique_fidelity_mean, weaver_fidelity_mean, dpqa_fidelity_mean, geyser_fidelity_mean])
        
        data = np.array(data)

        grouped_bar_plot(ax[0], data, bar_labels=['Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in benchmarks], colors= sns.color_palette("pastel")[1:])

        ax[0].set_title('(a) EPS - Fixed size circuit (20 variables)', fontweight='bold', loc='left')

        ax[0].set_yscale('log')

        ax[0].set_ylim(10**-2.29, 10**-1)

        ax[0].axvline(9.8, color='grey', linestyle='dashed', linewidth=2)

        ax[0].text(
            9.5,
            0.105,
            "Higher is better ↑",
            ha="center",
            fontsize=14,
            fontweight="bold",
            color="midnightblue",
        )

        num_groups, num_bars = data.shape

        bar_width = spacing / (num_bars + 1)

        bar_width = bar_width * 1.1

        for nan_n in range(4):
            for j in range(num_groups):
                if np.isnan(data[j][nan_n]):
                    ax[0].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width, 10**-2.29, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

        avg_improv = 1
        data = []

        for var in n_variables:
            atomique_fidelity = data_atomique[data_atomique['n_variables']==var]['total_fidelity'].mean()
            superconducting_fidelity = np.array(data_superconducting[data_superconducting['n_variables']==var]['eps']).mean()
            dpqa_fidelity = data_dpqa[data_dpqa['n_variables']==var]['eps'].mean()
            weaver_fidelity = data_weaver[data_weaver['ccz_fidelity']==0.98][data_weaver['num_variables']==var]['eps (fidelity)'].mean()
            avg_improv *= atomique_fidelity/weaver_fidelity
            #superconducting_fidelity = [np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN]
            superconducting_fidelity = np.NAN
            print(var, data_atomique[data_atomique['n_variables']==var]['total_fidelity'].mean())
            geyser_fidelity = np.NAN

            if var == 250:
                atomique_fidelity = np.NAN

            data.append([superconducting_fidelity, atomique_fidelity, weaver_fidelity, dpqa_fidelity, geyser_fidelity])
           
        data = np.array(data)

        num_groups, num_bars = data.shape

        print(avg_improv**(1/len(n_variables)))

        grouped_bar_plot(ax[1], data, bar_labels=['Superconducting', 'Atomique', 'Weaver', 'DPQA', 'Geyser'], group_labels=[str(i) for i in n_variables])

        for nan_n in range(5):
            if nan_n == 0:
                continue
            for j in range(num_groups):
                if np.isnan(data[j][nan_n]):
                    if nan_n == 4 and j == 0 or nan_n == 4 and j == 1 or nan_n == 4 and j == 2:
                        ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width-0.12, 10**-41.3, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')    
                        continue
                    if nan_n == 3:
                        ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width-0.1, 10**-41.3, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')
                        continue
                    if nan_n == 1 and j == 5:
                        continue
                        
                    ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width-0.12, 10**-41.3, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax[1].text((1+5*num_groups)//num_groups+1*bar_width-0.08, 10**-3, "10⁻⁵¹", ha='center', va='bottom', fontsize=11, fontweight='bold', color=sns.color_palette("pastel")[1])
        ax[1].vlines((1+5*num_groups)//num_groups+1*bar_width-0.08, 10**-41, 10**-4, color=sns.color_palette("pastel")[1], linewidth=2, linestyle='dashed')

        ax[1].text(0-0.04, 10**-3, "10⁻⁸", ha='center', va='bottom', fontsize=11, fontweight='bold', color=sns.color_palette("pastel")[0])
        ax[1].vlines(-0.08, 10**-41, 10**-4, color=sns.color_palette("pastel")[0], linewidth=2, linestyle='dashed')
        
        ax[1].text(1-0.06, 10**-3, "10⁻⁵⁶", ha='center', va='bottom', fontsize=11, fontweight='bold', color=sns.color_palette("pastel")[0])
        ax[1].vlines(0.86, 10**-41, 10**-4, color=sns.color_palette("pastel")[0], linewidth=2, linestyle='dashed')
        
        ax[1].text((2*num_groups)//num_groups-0.07, 10**-3, "10⁻¹¹¹", ha='center', va='bottom', fontsize=11, fontweight='bold', color=sns.color_palette("pastel")[0])
        ax[1].vlines(1.83, 10**-41, 10**-4, color=sns.color_palette("pastel")[0], linewidth=2, linestyle='dashed')

        ax[1].text((3*num_groups)//num_groups-0.07, 10**-3, "10⁻¹⁷⁸", ha='center', va='bottom', fontsize=11, fontweight='bold', color=sns.color_palette("pastel")[0])
        ax[1].vlines(2.86, 10**-41, 10**-4, color=sns.color_palette("pastel")[0], linewidth=2, linestyle='dashed')

        ax[1].text((4*num_groups)//num_groups, 10**-41.3, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax[1].text((5*num_groups)//num_groups-0.05, 10**-41.3, "X", ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax[1].set_ylim(10**-41.3, 5)

        ax[0].set_ylabel('Estimated probability of success')

        ax[1].text(
            5,
            10**2,
            "Higher is better ↑",
            ha="center",
            fontsize=14,
            fontweight="bold",
            color="midnightblue",
        )

        ax[1].set_title('(b) EPS - Variable size circuit', fontweight='bold', loc='left')

        ax[1].set_xlabel('Number of variables')

        ax[0].set_xlabel('MAX-3SAT Benchmark Suite')

        ax[1].set_yscale('log')

        plt.xlim(-0.3, 5.9)
        
        ax[0].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)
        ax[1].legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.285), fontsize=13)

        plt.tight_layout()

        plt.subplots_adjust(bottom=0.21)

        output_file = 'plots/figure12.pdf'
        plt.savefig(output_file)


def plot_analysis():


        data = []
        fig, ax = plt.subplots(1, 3, figsize=(14, 4))
        spacing = 0.95

        data_atomique = pd.read_csv('results/atomique_results.csv')
        data_geyser = pd.read_csv('results/geyser_results.csv')
        data_superconducting = pd.read_csv('results/superconducting_results.csv')
        data_weaver = pd.read_csv('results/weaver_results.csv')
        data_dpqa = pd.read_csv('results/dpqa_results.csv')

        var = 20

        n_qubits = range(20,200)

        superconducting_complexity = [n_qubits[i]**3 for i in range(len(n_qubits))]

        weaver_complexity = [n_qubits[i]**2 for i in range(len(n_qubits))]

        atomique_complexity = [n_qubits[i]**2.8 for i in range(len(n_qubits))]

        geyser_complexity = [5789.6487*n_qubits[i]**2 - 87825.2997*n_qubits[i] - 103601.8515 for i in range(len(n_qubits))]

        dpqa_complexity = [2**n_qubits[i] for i in range(len(n_qubits))]
        
        df = pd.DataFrame({'n_qubits': list(n_qubits),
                           'Superconducting': superconducting_complexity,
                           'Weaver': weaver_complexity,
                           'Geyser': geyser_complexity,
                           'Atomique': atomique_complexity,
                           'DPQA': dpqa_complexity})
        
        df_melted = df.melt('n_qubits', var_name='complexity_type', value_name='complexity')

        sns.set_theme()
        sns.set_style("whitegrid")
        ax[0].set_yscale('log')

        sns.lineplot(ax=ax[0], x='n_qubits', y='complexity', hue='complexity_type', data=df_melted, linewidth=2)

        ax[0].set_ylim(1e2, 1e20)

        ax[0].legend().set_title('')
        ax[0].legend().set_bbox_to_anchor((0.45, 0.45))

        ax[0].text(105, 10**20.1, "Lower is better ↓", ha='center', va='bottom', fontsize=14, fontweight='bold', color='midnightblue')

        ax[0].text(190, 10**18.5, "10⁶⁰", ha='center', va='bottom', fontsize=14, fontweight='bold', color=sns.color_palette()[4])

        ax[0].text(150, 10**18.5, "10⁴⁵", ha='center', va='bottom', fontsize=14, fontweight='bold', color=sns.color_palette()[4])

        ax[0].set_title('(a) Complexity Comparison', fontweight='bold', pad=20)

        ax[0].set_xlabel('Number of variables')
        ax[0].set_ylabel('Complexity [Number of steps]')

        FONTSIZE = 12

        #--------------------------------------------------------------------

        data = []

        for var in n_variables:
            weaver_gates1q = data_weaver[data_weaver['num_variables']==var][data_weaver['ccz_fidelity']==0.98]['#u3'].mean()
            weaver_gates2q = data_weaver[data_weaver['num_variables']==var][data_weaver['ccz_fidelity']==0.98]['#cz'].mean()
            weaver_gates3q = data_weaver[data_weaver['num_variables']==var][data_weaver['ccz_fidelity']==0.98]['#ccz'].mean()

            dpqa_gates1q = data_dpqa[data_dpqa['n_variables']==var]['1q_gates'].mean()
            dpqa_gates2q = data_dpqa[data_dpqa['n_variables']==var]['2q_gates'].mean() 

            atomique_gates1q = data_atomique[data_atomique['n_variables']==var]['n_1q_gate'].mean()
            atomique_gates2q = data_atomique[data_atomique['n_variables']==var]['n_2q_gate'].mean()
    
            geyser_pulses = data_geyser[data_geyser['n_variables']==var]['n_pulses'].mean()

            weaver_pulses = weaver_gates1q + weaver_gates2q*3 + weaver_gates3q*5

            atomique_pulses = atomique_gates1q + atomique_gates2q*3

            print(atomique_pulses, weaver_pulses, atomique_pulses/weaver_pulses)

            dpqa_pulses = dpqa_gates1q + dpqa_gates2q*3

            data.append([atomique_pulses, weaver_pulses, geyser_pulses, dpqa_pulses])

        data = np.array(data)

        grouped_bar_plot(ax[1], data, bar_labels=['Atomique', 'Weaver', 'Geyser', 'DPQA'], group_labels=[str(i) for i in n_variables])

        spacing = 0.95

        num_groups, num_bars = data.shape

        bar_width = None

        if bar_width == None:
            bar_width = spacing / (num_bars + 1)

        bar_width = bar_width * 1.1

        ax[1].set_yscale('log')

        for nan_n in range(4):
            for j in range(num_groups):
                if np.isnan(data[j][nan_n]):
                    ax[1].text((nan_n+j*num_groups)//num_groups+nan_n*bar_width, 10**2.81, "X", ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax[1].set_title('(b) Number of pulses', fontweight='bold', pad=20)

        ax[1].set_xlim(-0.3, 5.85)

        ax[1].set_ylabel('Number of pulses')

        ax[1].set_xlabel('Number of variables')

        ax[1].legend(loc="upper left", ncol=1)

        #--------------------------------------------------------------------
    
        data = []

        fids = [0.9775, 0.98, 0.9825, 0.985, 0.9875, 0.99, 0.9925, 0.995, 0.9975]

        for var in fids:
            weaver_fidelity = data_weaver[data_weaver['ccz_fidelity']==var][data_weaver['num_variables']==n_variables[0]]['eps (fidelity)'].mean()
            data.append(weaver_fidelity)

        atomique_fidelity = data_atomique[data_atomique['n_variables']==n_variables[0]]['total_fidelity'].mean()
        superconducting_fidelity = np.array(data_superconducting[data_superconducting['n_variables']==n_variables[0]]['eps']).mean()
        dpqa_fidelity = data_dpqa[data_dpqa['n_variables']==n_variables[0]]['eps'].mean()

        data = [[data[i],fids[i]] for i in range(len(fids))]
        
        data = pd.DataFrame(data, columns=['ccz_fidelity', 'eps'])

        sns.set_theme()
        sns.set_style("whitegrid")

        sns.lineplot(ax=ax[2], data=data, x='eps', y='ccz_fidelity', label='Weaver', markers='o', linewidth=2, legend=False)

        ax[2].set_ylabel('Estimated probability of success (eps)')

        ax[2].set_title('(c) CCZ fidelty threshold', fontweight='bold', pad=20)

        ax[2].set_xlabel('CCZ Gate fidelity')

        #higher is better
        ax[2].text(0.988, 0.127, "Higher is better ↑", ha='center', va='bottom', fontsize=14, fontweight='bold', color='midnightblue')

        ax[2].text(0.9916, dpqa_fidelity-0.006, "X", ha='center', va='bottom', fontsize=18, fontweight='bold', color='r')
        ax[2].hlines(atomique_fidelity, label='Atomique', colors='r', linestyles='dashed', xmin=0.9775, xmax=0.9975, linewidth=2)
        ax[2].hlines(superconducting_fidelity, label='Superconducting', colors='g', linestyles='dashdot', xmin=0.9775, xmax=0.9975, linewidth=2)
        ax[2].hlines(dpqa_fidelity, label='DPQA', colors='b', linestyles='dotted', xmin=0.9775, xmax=0.9975, linewidth=2)

        ax[2].text(0.985, dpqa_fidelity+0.001, "CCZ Fidelity = 0.9916", ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax[2].legend(loc="upper left", ncol=1)

        plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))

        plt.tight_layout()

        output_file = 'plots/figure10.pdf'
        plt.savefig(output_file)


def get_circuit_n_operations():

    circuit_list = [
        'a1_n20.qasm',
        'a1_n50.qasm',
        'a1_n75.qasm',
        'a1_n100.qasm',
        'a1_n150.qasm',
        'a1_n250.qasm',
    ]

    n_operations = []

    for name in circuit_list:
        qc = QuantumCircuit.from_qasm_file('./evaluation/benchmarks/QASMBench/' + name)
        operations = qc.count_ops()
        n_operations.append(0)

        for i in list(operations.items()):
            name, nops = i
            if name != 'barrier' and name != 'measure':
                n_operations[-1] += nops

    return n_operations