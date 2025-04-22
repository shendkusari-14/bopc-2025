# plot_handler.py

import pandas as pd
import matplotlib.pyplot as plt


class BenchmarkPlotHandler:
    def __init__(self, filepath: str, label: str):
        self.filepath = filepath
        self.label = label
        self.df = pd.read_csv(filepath, sep=";", header=None, names=["Problem Size", "Patch", "Cores", "Runtime (s)"])

    def process_data(self):
        df_grouped = self.df.groupby(["Problem Size", "Cores"]).mean()

        # Get reference runtimes (Cores == 1)
        ref_runtimes = df_grouped.loc[df_grouped.index.get_level_values("Cores") == 1, "Runtime (s)"].to_dict()
        ref_runtimes = {key[0]: value for key, value in ref_runtimes.items()}

        # Calculate speed-up and efficiency
        df_grouped["Speed-up"] = df_grouped.index.get_level_values("Problem Size").map(ref_runtimes) / df_grouped["Runtime (s)"]
        df_grouped["Efficiency"] = df_grouped["Speed-up"] / df_grouped.index.get_level_values("Cores")
        return df_grouped

    def plot_results(self):
        df_grouped = self.process_data()
        problem_sizes = df_grouped.index.get_level_values("Problem Size").unique()
        cores = df_grouped.index.get_level_values("Cores").unique()

        metrics = ["Runtime (s)", "Speed-up", "Efficiency"]
        titles = ["Runtime", "Speed-up", "Parallel Efficiency"]

        fig, axs = plt.subplots(1, 3, figsize=(14, 4))
        fig.suptitle(f"Benchmark Analysis: {self.label}")

        for idx, metric in enumerate(metrics):
            ax = axs[idx]
            for size in problem_sizes:
                ax.plot(
                    cores,
                    df_grouped.loc[size][metric],
                    label=f"Size {size}",
                    marker="o"
                )
            ax.set_title(titles[idx])
            ax.set_xlabel("Cores")
            ax.set_ylabel(metric)
            ax.grid(True)

        fig.legend(loc="upper right", fontsize="small", title="Legend", title_fontsize="medium")

        #fig.legend(loc="upper center", ncol=len(problem_sizes))
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()


if __name__ == "__main__":
    benchmark_cb_handler = BenchmarkPlotHandler("benchmark_cb.csv", "C = cb")
    benchmark_cb_handler.plot_results()

    benchmark_cs_handler = BenchmarkPlotHandler("benchmark_cs.csv", "C = cs")
    benchmark_cs_handler.plot_results()
