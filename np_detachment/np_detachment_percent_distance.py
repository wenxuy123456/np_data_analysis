import os
import matplotlib

if os.environ.get("CI"):
    matplotlib.use("Agg")

from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, 'np_dataset_analysis.xlsx')
df = pd.read_excel(input_file)

output_file = os.path.join(script_dir, "np_sorted_file.xlsx")
df_sorted = df.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
df_sorted = df_sorted[df_sorted["simulation time"] < 600]
df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))
df_sorted.to_excel(output_file, index=False)

B0 = len(df_sorted["renumbered"])
df_sorted["numbers detached"] = range(1, B0 + 1)
df_sorted["bound particles"] = (B0 - df_sorted["numbers detached"]) / B0 * 100

# % distance of best fit from scatter data
def calculate_percent_distance(kD, beta):
    t = df_sorted["simulation time"].values
    y_scatter = df_sorted["bound particles"].values
    y_fit = np.exp(kD * (t ** beta) / (beta - 1)) * 100

    percent_distance = (y_scatter - y_fit) / y_scatter * 100
    return percent_distance

# plot percent distance of best fit from scatter data (scatter only, no connecting line)
def plot_percent_distance(kD, beta):
    percent_distance = calculate_percent_distance(kD, beta)
    plt.scatter(df_sorted["simulation time"], percent_distance, color="purple", s=10)
    plt.xlabel("Detachment Time")
    plt.ylabel("Percent Distance (%)")

# Original decay curve equation
def decay_curve(t, kD, beta):
    return np.exp(kD * (t ** beta) / (beta - 1)) * 100

# Best fit (fit params only, no plotting)
def fit_decay_curve():
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
    return kD, beta


def main():
    kD, beta = fit_decay_curve()

    fig, ax = plt.subplots(figsize=(6, 5))
    plot_percent_distance(kD, beta)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    os.makedirs(os.path.join(script_dir, "outputs"), exist_ok=True)
    plt.savefig(os.path.join(script_dir, "outputs", "np_detachment_percent_distance.png"), dpi=150, bbox_inches="tight")

    if not os.environ.get("CI"):
        plt.show()
    else:
        plt.close()

if __name__ == "__main__":
    main()