import pandas as pd
import matplotlib.pyplot as plt
import argparse

class BenchmarkPlotHandler:
    def __init__(self, filepath: str, label: str):
        self.filepath = filepath
        self.label = label
        self.df = pd.read_csv(filepath, sep=";", header=None, names=["Problem Size", "Patch", "Cores", "Runtime (s)"])

    def process_data(self):
        df_grouped = self.df.groupby(["Problem Size", "Cores"]).mean()

        ref_runtimes = df_grouped.loc[df_grouped.index.get_level_values("Cores") == 1, "Runtime (s)"].to_dict()
        ref_runtimes = {key[0]: value for key, value in ref_runtimes.items()}

        # Calculate speed-up and efficiency
        df_grouped["Speed-up"] = df_grouped.index.get_level_values("Problem Size").map(ref_runtimes) / df_grouped["Runtime (s)"]
        df_grouped["Efficiency"] = df_grouped["Speed-up"] / df_grouped.index.get_level_values("Cores")
        
        return df_grouped

    def plot_runtime(self):
        df_grouped = self.process_data()
        problem_sizes = df_grouped.index.get_level_values("Problem Size").unique()
        cores = df_grouped.index.get_level_values("Cores").unique()

        fig, ax = plt.subplots(figsize=(8, 5))
        for size in problem_sizes:
            ax.plot(
                cores,
                df_grouped.loc[size]["Runtime (s)"],
                label=f"Size {size}",
                marker="o"
            )
        ax.set_title("Runtime")
        ax.set_xlabel("Cores")
        ax.set_ylabel("Runtime (s)")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_speedup(self):
        df_grouped = self.process_data()
        problem_sizes = df_grouped.index.get_level_values("Problem Size").unique()
        cores = df_grouped.index.get_level_values("Cores").unique()
        #print(cores)
        fig, ax = plt.subplots(figsize=(8, 5))
        for size in problem_sizes:
            ax.plot(
                cores,
                df_grouped.loc[size]["Speed-up"],
                label=f"Size {size}",
                marker="o"
            )
        ax.set_title("Speed-up")
        ax.set_xlabel("Cores")
        ax.set_ylabel("Speed-up")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_efficiency(self):
        df_grouped = self.process_data()
        problem_sizes = df_grouped.index.get_level_values("Problem Size").unique()
        cores = df_grouped.index.get_level_values("Cores").unique()

        fig, ax = plt.subplots(figsize=(8, 5))
        for size in problem_sizes:
            ax.plot(
                cores,
                df_grouped.loc[size]["Efficiency"],
                label=f"Size {size}",
                marker="o"
            )
        ax.set_title("Parallel Efficiency")
        ax.set_xlabel("Cores")
        ax.set_ylabel("Efficiency")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_speedup_bar(self):
        df_grouped = self.process_data()
        problem_sizes = df_grouped.index.get_level_values("Problem Size").unique()
        cores = df_grouped.index.get_level_values("Cores").unique()

        # Bar plot for Speed-up
        fig, ax = plt.subplots(figsize=(8, 5))
        width = 0.15  # Width of the bars

        for idx, size in enumerate(problem_sizes):
            ax.bar(
                cores + idx * width, 
                df_grouped.loc[size]["Speed-up"], 
                width=width, 
                label=f"Size {size}"
            )
        ax.set_title("Speed-up Comparison (Bar Plot)")
        ax.set_xlabel("Cores")
        ax.set_ylabel("Speed-up")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_patch_runtime(self):
        df_filtered_1 = self.df[(self.df["Problem Size"] == 850) & (self.df["Cores"] == 24)]
        df_filtered = self.df[(self.df["Problem Size"] == 1000) & (self.df["Cores"] == 32)]

        # Plot for 850
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            df_filtered_1["Patch"],
            df_filtered_1["Runtime (s)"],
            marker="o",
            linestyle="-"
        )
        ax.set_title("Runtime vs. Patch Size\n(Size=850, Cores=24)")
        ax.set_xlabel("Patch Size")
        ax.set_ylabel("Mean Runtime (s)")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot for 1000
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            df_filtered["Patch"],
            df_filtered["Runtime (s)"],
            marker="o",
            linestyle="-"
            )
        ax.set_title("Runtime vs. Patch Size\n(Size=1000, Cores=32)")
        ax.set_xlabel("Patch Size")
        ax.set_ylabel("Mean Runtime (s)")
        ax.grid(True)
        plt.tight_layout()
        plt.show()




    def print_table(self):
        df_grouped = self.process_data().reset_index()
        df_grouped = df_grouped.rename(columns={
            "Problem Size": "Size",
            "Cores": "Processes",
            "Runtime (s)": "mean runtime(s)",
            "Speed-up": "speed-up",
            "Efficiency": "parallel efficiency"
        })

        df_grouped["mean runtime(s)"] = df_grouped["mean runtime(s)"].round(10)
        df_grouped["speed-up"] = df_grouped["speed-up"].round(10)
        df_grouped["parallel efficiency"] = df_grouped["parallel efficiency"].round(10)

        df_grouped = df_grouped.sort_values(by=["Size", "Processes"])

        try:
            from tabulate import tabulate
            print(tabulate(df_grouped, headers="keys", tablefmt="grid", showindex=False))
        except ImportError:
            print(df_grouped.to_string(index=False))

    def print_patch_table(self, fixed_size=1000, fixed_cores=32):
        
        # Filter for the fixed size and core count
            df_patch = self.df[
                (self.df["Problem Size"] == fixed_size) &
                (self.df["Cores"] == fixed_cores)
         ]

            df_patch = (
                df_patch
                .groupby("Patch")["Runtime (s)"]
                .mean()
                .reset_index()
                .rename(columns={"Runtime (s)": "mean runtime (s)"})
            )

            df_patch["mean runtime (s)"] = df_patch["mean runtime (s)"].round(6)

        # Prepare for printing
            try:
                from tabulate import tabulate
                print(
                    tabulate(
                        df_patch,
                        headers=["Patch Size", "Mean runtime (s)"],
                        tablefmt="grid",
                        showindex=False
                    )
                )
            except ImportError:
                print(df_patch.to_string(index=False))


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--patchmode",
        action="store_true",
        help="Only plot patch-size vs runtime from patch_cs.csv"
        )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="CSV file to load (defaults to benchmark_cs.csv or patch_cs.csv with --patchmode)"
        )
    args = parser.parse_args()
    
    
    if args.patchmode:
        handler = BenchmarkPlotHandler('patch_cs.csv', label='C = cs (patch mode)')
        handler.plot_patch_runtime()
        handler.print_patch_table()
    else:
    
    
    
    
        benchmark_cb_handler = BenchmarkPlotHandler("benchmark_cb.csv", "C = cb")
    
    # Plot and display each plot individually
        benchmark_cb_handler.plot_runtime()  
        benchmark_cb_handler.plot_speedup()  
        benchmark_cb_handler.plot_efficiency()  
        benchmark_cb_handler.plot_speedup_bar()  
    
        benchmark_cb_handler.print_table()

        benchmark_cs_handler = BenchmarkPlotHandler("benchmark_cs.csv", "C = cs")
    
    # Plot and display each plot individually
        benchmark_cs_handler.plot_runtime()  
        benchmark_cs_handler.plot_speedup()  
        benchmark_cs_handler.plot_efficiency()  
        benchmark_cs_handler.plot_speedup_bar()  
        benchmark_cs_handler.print_table()
