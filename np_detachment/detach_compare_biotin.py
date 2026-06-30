import os
import matplotlib

if os.environ.get("CI"):
    matplotlib.use("Agg")

from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
fig5_dir = os.path.join(script_dir, "..", "web_plot_data", "np_detachment_fig5")

input_file = os.path.join(script_dir, 'np_dataset_analysis.xlsx')
fig5_file_list = [
    os.path.join(fig5_dir, "np_detachment_fig5_biotin_hh.xlsx"),
    os.path.join(fig5_dir, "np_detachment_fig5_biotin_hl.xlsx"),
    os.path.join(fig5_dir, "np_detachment_fig5_biotin_lh.xlsx"),
    os.path.join(fig5_dir, "np_detachment_fig5_biotin_ll.xlsx"),
]

output_file = os.path.join(script_dir, "np_sorted_file.xlsx")

# Marker/color styling to match reference figure (one marker shape + color per condition)
condition_style = {
    "hh": {"marker": "s", "color": "#1a1a4d", "label": "High/High"},
    "hl": {"marker": "o", "color": "#2244aa", "label": "High/Low"},
    "lh": {"marker": "D", "color": "#3a6fd8", "label": "Low/High"},
    "ll": {"marker": "^", "color": "#5ec8e8", "label": "Low/Low"},
}

# Group fig5 files by their condition suffix (hh, hl, lh, ll) so files
# that share a condition get combined into a single dataset before plotting.
def group_files_by_condition(file_list):
    grouped = {}
    for file in file_list:
        basename = os.path.basename(file).replace(".xlsx", "")
        condition = basename.split("_")[-1]
        grouped.setdefault(condition, []).append(file)
    return grouped

# Read and clean a single fig5 file
def process_fig5_file(file):
    df = pd.read_excel(file, header=None, names=["simulation time", "bound particles"])
    df.loc[df["simulation time"] < 0, "simulation time"] = 0
    df.loc[df["bound particles"] < 0, "bound particles"] = 0
    df["bound particles"] = df["bound particles"] * 100
    df = df[df["simulation time"] < 700]
    return df

# Combine all files belonging to the same condition into one sorted dataframe
def process_condition_group(files, condition):
    combined = pd.concat([process_fig5_file(f) for f in files], ignore_index=True)
    df_sorted = combined.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
    df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))

    output_file_fig5 = os.path.join(fig5_dir, f"np_detachment_fig5_biotin_{condition}_combined_sorted.xlsx")
    df_sorted.to_excel(output_file_fig5, index=False)

    return df_sorted

def fig5_sorted_df():
    grouped_files = group_files_by_condition(fig5_file_list)
    all_conformations = {}
    for condition, files in grouped_files.items():
        all_conformations[condition] = process_condition_group(files, condition)
    return all_conformations

# Bin the data into time windows and compute mean +/- std so error bars can be drawn,
# matching the binned/error-bar style of the reference figure
def bin_with_error(df, n_bins=15):
    x = df["simulation time"]
    bins = np.linspace(x.min(), x.max(), n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    means = []
    stds = []
    for i in range(n_bins):
        mask = (x >= bins[i]) & (x < bins[i + 1])
        vals = df.loc[mask, "bound particles"] / 100  # convert to fraction remaining
        if len(vals) > 0:
            means.append(vals.mean())
            stds.append(vals.std())
        else:
            means.append(np.nan)
            stds.append(np.nan)

    return bin_centers, np.array(means), np.array(stds)

def plot_condition(condition, df_sorted_fig5):
    style = condition_style.get(condition, {"marker": "x", "color": "black", "label": condition})
    x, y, yerr = bin_with_error(df_sorted_fig5)

    plt.errorbar(
        x, y, yerr=yerr,
        marker=style["marker"],
        color=style["color"],
        mfc="white",
        linestyle="-",
        capsize=3,
        markersize=6,
        label=style["label"],
    )

# ----- Original detachment dataset (np_dataset_analysis.xlsx) -----
df = pd.read_excel(input_file)

df_sorted = df.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
df_sorted = df_sorted[df_sorted["simulation time"] < 600]
df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))
df_sorted.to_excel(output_file, index=False)

B0 = len(df_sorted["renumbered"])
df_sorted["numbers detached"] = range(1, B0 + 1)
df_sorted["bound particles"] = (B0 - df_sorted["numbers detached"]) / B0 * 100

def plot_np_dataset_scatter():
    x = df_sorted["simulation time"]
    y = df_sorted["bound particles"] / 100
    plt.scatter(x, y, label="NP Detachment Data", color="#c98a3e", s=8)

def decay_curve(t, kD, beta):
    return np.exp(kD * (t ** beta) / (beta - 1)) * 100

def plot_decay_curve():
    x = df_sorted["simulation time"]
    y = df_sorted["bound particles"]

    params, __ = curve_fit(
        decay_curve,
        x,
        y,
        p0=[0.01, 0],
        bounds=([0, 0], [np.inf, 100])
    )

    kD, beta = params

    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = decay_curve(x_fit, kD, beta) / 100

    plt.plot(x_fit, y_fit, color="#c98a3e", label="Biotin/Avidin")
    return kD, beta
# --------------------------------------------------------------------

def main():
    all_fig5_data = fig5_sorted_df()

    os.makedirs(os.path.join(script_dir, "outputs"), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_np_dataset_scatter()
    plot_decay_curve()

    for condition, df_sorted_fig5 in all_fig5_data.items():
        plot_condition(condition, df_sorted_fig5)

    ax.set_xlabel(r"$\gamma$ (s$^{-1}$)", fontsize=12)
    ax.set_ylabel("Fraction Particles Remaining", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="best", frameon=True)

    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, "outputs", "biotin_all_conditions.png"), dpi=150, bbox_inches="tight")

    if not os.environ.get("CI"):
        plt.show()
    else:
        plt.close()

if __name__ == "__main__":
    main()