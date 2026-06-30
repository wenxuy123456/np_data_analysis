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

##Scatter experimental data
def plot_np_dataset_scatter():
    x = df_sorted["simulation time"]
    y = df_sorted["bound particles"]
    plt.scatter(x, y, label="NP Detachment Curve", color="red", s=1)
    plt.title("NP Dataset")
    plt.xlabel("Detachment Time")
    plt.ylabel("Bound Particles Percentage (%)")

##Original decay curve equation
def decay_curve(t, kD, beta):
    return np.exp(kD * (t ** beta) / (beta - 1)) * 100

##Best fit curve
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
    y_fit = np.exp(kD * (x_fit ** beta) / (beta - 1)) * 100

    plt.plot(x_fit, y_fit, color="blue", label=f"Best Fit line (kD = {kD:.4f}, β = {beta:.4f})")
    return kD, beta

##Best fit with beta = 0.75, kD = 0.01
def plot_decay_curve_optimized(kD, beta):
    t = df_sorted["simulation time"].values
    x_fit = np.linspace(t.min(), t.max(), 500)
    y_fit = decay_curve(x_fit, kD, beta)
    plt.plot(x_fit, y_fit, color="green", label=f"Optimized Decay Curve (β = {beta})")


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

    print(beta_lower, beta_upper)
    return kD_lower, kD_upper, beta_lower, beta_upper, beta_values

def plot_bootstrap_decay_curve(t, kD, beta, color, label):
    bootstrap_x = np.linspace(t.min(), t.max(), 500)
    bootstrap_y = decay_curve(bootstrap_x, kD, beta)
    plt.plot(bootstrap_x, bootstrap_y, color=color, label=f"{label} (β = {beta}) (kD ={kD:.4f})")


def main():
    plt.figure()
    plot_np_dataset_scatter()
    plot_decay_curve()
    plot_decay_curve_optimized(0.01, 0.75)

    kD_lower, kD_upper, beta_lower, beta_upper, beta_values = bootstrap_bounds(df_sorted)

    plot_bootstrap_decay_curve(df_sorted["simulation time"], kD_lower, beta_lower, color="orange", label="Bootstrap Decay Curve")
    plot_bootstrap_decay_curve(df_sorted["simulation time"], kD_upper, beta_upper, color="purple", label="Bootstrap Decay Curve")

    plt.legend(loc="best")

    os.makedirs(os.path.join(script_dir, "outputs"), exist_ok=True)
    plt.savefig(os.path.join(script_dir, "outputs", "bootstrap_high_low.png"), dpi=150, bbox_inches="tight")

    if not os.environ.get("CI"):
        plt.show()
    else:
        plt.close()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()