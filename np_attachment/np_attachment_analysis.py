import os

import matplotlib
matplotlib.use("Agg")

if os.environ.get("CI"):
    matplotlib.use("Agg")

from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd

input_file = 'np_dataset_attachment.csv'
df = pd.read_csv(input_file)
print(df.head())

output_file = "np_attachment_sorted_file.csv"
df_sorted = df.sort_values(by="formed_time", ascending=True).reset_index(drop=True)
df_sorted = df_sorted[df_sorted["formed_time"] < 600]
df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))
df_sorted.to_csv(output_file, index=False)

particles_attached = len(df_sorted["renumbered"])
df_sorted["numbers attached"] = range(1, len(df_sorted["renumbered"]) + 1)
df_sorted["bound particles"] = df_sorted["numbers attached"] / particles_attached * 100

##Scatter experimental data
def plot_np_dataset_scatter():
    x = df_sorted["formed_time"]
    y = df_sorted["bound particles"]
    plt.scatter(x, y, color="red", s=1)
    plt.title("NP Dataset")
    plt.xlabel("Attachment Time")
    plt.ylabel("Bound Particles Percentage (%)")

##Original attach curve equation
def attach_curve(t, k_a, box_height, N_max):
    return N_max * (1 - np.exp((-k_a * t) / box_height))

##Best fit curve
def plot_attach_curve():
    x = df_sorted["formed_time"]
    y = df_sorted["bound particles"]

    params, __ = curve_fit(
        attach_curve,
        x,
        y,
        p0=[0.01, 30, y.max()],
        bounds=([0, 0, 0], [np.inf, np.inf, np.inf])
    )

    k_a, box_height, N_max = params

    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = attach_curve(x_fit, k_a, box_height, N_max)

    plt.plot(x_fit, y_fit, color="blue", label=f"Best Fit line (k_a = {k_a:.4f}, box_height = {box_height:.2f}, N_max = {N_max:.2f})")
    return k_a, box_height, N_max

##Best fit with ?? (dk best fit parameters yet)
def plot_attach_curve_optimized(k_a, box_height, N_max):
    t = df_sorted["formed_time"].values
    x_fit = np.linspace(t.min(), t.max(), 500)
    y_fit = attach_curve(x_fit, k_a, box_height, N_max)
    plt.plot(x_fit, y_fit, color="green", label=f"Optimized Attachment Curve (k_a = {k_a:.4f}, box_height = {box_height:.2f}, N_max = {N_max:.2f})")

def main():
    plot_np_dataset_scatter()
    plot_attach_curve()
    plot_attach_curve_optimized(1, 30, 100)

    plt.legend(loc="best")

    os.makedirs("outputs", exist_ok=True)
    plt.savefig(f"outputs/np_attachment_analysis.png", dpi=150, bbox_inches="tight")

    if not os.environ.get("CI"):
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    main()