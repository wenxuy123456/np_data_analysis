from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd

input_file ='np_dataset_analysis.xlsx'
df = pd.read_excel(input_file)
print(df.head())

output_file= "np_sorted_file.xlsx"
df_sorted = df.sort_values(by="simulation time", ascending=True).reset_index(drop=True)
df_sorted = df_sorted[df_sorted["simulation time"] < 600]
df_sorted.insert(0, "renumbered", range(1, len(df_sorted) +1))
df_sorted.to_excel(output_file, index=False)

B0 = len(df_sorted["renumbered"])
df_sorted["numbers detached"] = range(1, B0+1)
df_sorted["bound particles"] = (B0 - df_sorted["numbers detached"]) / B0 * 100

##% distance of best fit from scatter data
def calculate_percent_distance(kD, beta):
    t = df_sorted["simulation time"].values
    y_scatter = df_sorted["bound particles"].values
    y_fit = np.exp(kD * (t ** beta) / (beta - 1)) * 100

    percent_distance = np.abs(y_scatter - y_fit) / y_scatter * 100
    return percent_distance

## plot percent distance of best fit from scatter data
def plot_percent_distance(kD, beta):
    percent_distance = calculate_percent_distance(kD, beta)
    plt.scatter(df_sorted["simulation time"], percent_distance, color="purple", s=1)
    plt.plot(df_sorted["simulation time"], percent_distance, color="purple", label=f"Percent Distance")
    plt.title("Percent Distance of Best Fit from Scatter Data")
    plt.xlabel("Detachment Time")
    plt.ylabel("Percent Distance (%)")

##Scatter experimental data
def plot_np_dataset_scatter():
    x = df_sorted["simulation time"]
    y = df_sorted["bound particles"]
    plt.scatter(x,y,label="NP Detachment Scatter", color="red",s=1)

##Original decay curve equation
def decay_curve(t, kD, beta):
    return np.exp(kD * (t ** beta) / (beta - 1)) * 100

##Best fit curve
def plot_decay_curve(kD=None, beta=None):

    x = df_sorted["simulation time"]
    y = df_sorted["bound particles"]

    params, __ = curve_fit(
        decay_curve,
        x,
        y,
        p0 = [0.01, 0],
        bounds = ([0, 0], [np.inf, 100])
    )

    kD, beta = params

    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = np.exp(kD * (x_fit ** beta) / (beta - 1)) * 100 
    
    ##plt.plot(x_fit, y_fit, color="blue", label=f"Best Fit line (kD = {kD:.4f}, β = {beta:.4f})")
    return kD, beta


def main():
    ##plot_np_dataset_scatter()
    ##plot_decay_curve()

    kD, beta = plot_decay_curve()
    plot_percent_distance(kD, beta)

    plt.legend(loc = "best")
    plt.show()
    
if __name__ =="__main__":
    main()