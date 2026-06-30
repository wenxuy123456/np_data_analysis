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

script_dir = os.path.dirname(os.path.abspath(__file__))
fig3_dir = os.path.join(script_dir, "..", "web_plot_data", "np_attachment_fig3")
fig3_file_list = [
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_hh.xlsx"),
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_hm.xlsx"),
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_hl.xlsx"),
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_mh.xlsx"),
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_mm.xlsx"),
    os.path.join(fig3_dir, "np_attachment_fig3_4M2.4_scfv_lh.xlsx"),
]

##Organize fig3 data into a sorted dataframe
def process_fig3_file(file):
    df = pd.read_excel(file, header=None, names=["simulation time", "bound particles"])
    print(df.head())
    df_sorted = df.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
    df_sorted.insert(0, "renumbered", range(1, len(df_sorted) + 1))
    output_file_fig3 = file.replace(".xlsx", "_sorted.xlsx")
    df_sorted.to_excel(output_file_fig3, index=False)
    return df_sorted

def fig3_sorted_df():
    all_attachment_data = {}
    for file in fig3_file_list:
        all_attachment_data[file] = process_fig3_file(file)
    return all_attachment_data

##Find curve for each fig3 dataset
def plot_fig3_attachment_curve(df_sorted_fig3, label):
    x = df_sorted_fig3["simulation time"]
    y = df_sorted_fig3["bound particles"]

    params, __ = curve_fit(
        attach_curve,
        x,
        y,
        p0=[0.1, 30, y.max()],
        bounds=([0, 0, 0], [np.inf, np.inf, np.inf]),
        maxfev=10000
    )

    k_a, box_height, N_max = params

    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = attach_curve(x_fit, k_a, box_height, N_max)

    plt.plot(x_fit, y_fit, label=f"{label} (k_a = {k_a:.4f}, box_height = {box_height:.2f})")
    return k_a, box_height, N_max

def main():
    all_fig3_data = fig3_sorted_df()
    for file, df_sorted_fig3 in all_fig3_data.items():
        label = os.path.basename(file).replace(".xlsx", "").split("_")[-1]

        plt.figure()
        plot_fig3_attachment_curve(df_sorted_fig3, label)

        plt.title("Attachment Curves 4M2.4 scFv")
        plt.xlabel("Time")
        plt.ylabel("Bound Particles")
        plt.legend(loc="best")

        plot_np_dataset_scatter()
        plot_attach_curve()

        plt.xlim(0, df_sorted["formed_time"].max())

        plt.legend(loc="best", fontsize="small")

        os.makedirs("outputs", exist_ok=True)
        plt.savefig(f"outputs/4M24_scfv_{label}.png", dpi=150, bbox_inches="tight")

        if not os.environ.get("CI"):
            plt.show()
        else:
            plt.close()

if __name__ == "__main__":
    main()
