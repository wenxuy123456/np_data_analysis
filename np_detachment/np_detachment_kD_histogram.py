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
print(df.head())

output_file = os.path.join(script_dir, "np_sorted_file.xlsx")
df_sorted = df.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
df_sorted = df_sorted[df_sorted["simulation time"] < 600]
df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))
df_sorted.to_excel(output_file, index=False)

B0 = len(df_sorted["renumbered"])
df_sorted["numbers detached"] = range(1, B0 + 1)
df_sorted["bound particles"] = (B0 - df_sorted["numbers detached"]) / B0 * 100

##Original decay curve equation
def decay_curve(t, kD, beta):
    return np.exp(kD * (t ** beta) / (beta - 1)) * 100


##Bootstrap curve
def bootstrap_bound_particles(time):
    B0 = len(time)
    unique_times, counts = np.unique(np.array(time), return_counts=True)

    bootstrap_numbers_detached = np.cumsum(counts)
    bootstrap_bound_particles = (B0 - bootstrap_numbers_detached) / B0 * 100
    return unique_times, bootstrap_bound_particles

def bootstrap_beta(x, y):
    params, __ = curve_fit(
        decay_curve,
        x,
        y,
        p0=[0.01, 0.75],
        bounds=([0, 0], [np.inf, 0.999])
    )

    kD, beta = params
    return kD, beta

##Bootstrap resampling
def bootstrap_bounds(df_sorted, random_state=None):
    n_resamples = 1000
    rng = np.random.default_rng(random_state)

    kD_values = []
    beta_values = []

    for i in range(n_resamples):
        n = rng.integers(0, len(df_sorted), size=(len(df_sorted)))
        bootstrap_result = df_sorted.iloc[n]

        x_bootstrap, y_bootstrap = bootstrap_bound_particles(bootstrap_result["simulation time"])

        kD, beta = bootstrap_beta(x_bootstrap, y_bootstrap)
        kD_values.append(kD)
        beta_values.append(beta)

    kD_lower = np.percentile(kD_values, 2.5)
    kD_upper = np.percentile(kD_values, 97.5)

    beta_lower = np.percentile(beta_values, 2.5)
    beta_upper = np.percentile(beta_values, 97.5)

    print(beta_lower, beta_upper, kD_lower, kD_upper)
    return beta_values, kD_values

##Bootstrap kD histogram
def plot_bootstrap_kD_histogram(kD_values):
    plt.hist(kD_values, bins=30, color="lightblue", edgecolor="black")
    plt.title("Bootstrap kD Histogram")
    plt.xlabel("kD Values")
    plt.ylabel("Number of kD Values")
    plt.axvline(np.mean(kD_values), color='red', linestyle='dashed', linewidth=1, label=f"Mean kD = {np.mean(kD_values):.4f}")
    plt.legend()

def main():
    beta_values, kD_values = bootstrap_bounds(df_sorted)

    plt.figure()
    plot_bootstrap_kD_histogram(kD_values)

    plt.legend(loc="best")

    os.makedirs(os.path.join(script_dir, "outputs"), exist_ok=True)
    plt.savefig(os.path.join(script_dir, "outputs", "bootstrap_kD_histogram.png"), dpi=150, bbox_inches="tight")

    if not os.environ.get("CI"):
        plt.show()
    else:
        plt.close()

if __name__ == "__main__":
    main()