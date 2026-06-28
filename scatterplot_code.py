from matplotlib import pyplot as plt
import numpy as np

def plot_random_normal_distribution():
    x = np.linspace(0,100,100)
    y = np.array([np.random.normal(loc=0.0, scale=1.0) for i in range(100)])
    plt.plot(x,y, label="Random Normal Distribution (plot)", color="blue")
    plt.scatter(x,y,label="Random Normal Distribution (scatter)", color="red",s=1)
    plt.title("Random Normal Distribution")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()
def main():
    plot_random_normal_distribution()
if __name__ =="__main__":
    main()
