from Core import polyline as pl, flip
import solver 
import GeneralCase.center_core as cc
import time
from GeneralCase import diminish_turning_crossing as dtc
from GeneralCase import center_core as cc

def sort_ccw_path(points, center, path):
    sorted_points = cc.sort_ccw(points, center)
    dict_sorted_points = {p: i for i, p in enumerate(sorted_points)}
    new_path = [dict_sorted_points[points[i]] for i in path]
    
    return sorted_points, new_path

def benchmark(points, center, path, algorithm, name):
    t0 = time.time()
    solution, explored = algorithm(points, center, path)
    t1 = time.time()

    return {
        "algorithm": name,
        "solution_length": len(solution) if solution else None,
        "explored": explored,
        "time": t1 - t0,
        "n": len(points)
    }

def run_experiment(algos, points_and_paths):
    
    results = []
    i = 0
    for points, path in points_and_paths:
        print(i)
        center = cc.barycenter(points)
        points, path = sort_ccw_path(points, center, path)
        for name, algo in algos.items():
            results.append(benchmark(points, center, path, algo, name))

        i+=1

    return results

from collections import defaultdict

def group_by_size(results):
    grouped = defaultdict(list)
    for r in results:
        grouped[r["n"]].append(r)
    return grouped

import statistics as stats

def summarize_group(group):
    """
    group = list of result dicts for a fixed n
    returns a dict of aggregated statistics
    """
    summary = defaultdict(dict)
    algorithms = set(r["algorithm"] for r in group)

    for algo in algorithms:
        subset = [r for r in group if r["algorithm"] == algo]

        summary[algo] = {
            "avg_length": stats.mean(r["solution_length"] for r in subset),
            "std_length": stats.stdev(r["solution_length"] for r in subset) if len(subset) > 1 else 0,
            "avg_explored": stats.mean(r["explored"] for r in subset),
            "avg_time": stats.mean(r["time"] for r in subset),
        }

    return summary

def summarize_all(results):
    grouped = group_by_size(results)
    summaries = {}

    for n, group in grouped.items():
        summaries[n] = summarize_group(group)

    return summaries

def print_summary(summaries):
    for n in sorted(summaries):
        print(f"\n=== n = {n} ===")
        for algo, stats in summaries[n].items():
            print(f"  {algo}:")
            print(f"    avg length   = {stats['avg_length']:.2f} (± {stats['std_length']:.2f})")
            print(f"    avg explored = {stats['avg_explored']:.1f}")
            print(f"    avg time     = {stats['avg_time']:.4f}s")


def BFS(points, center, path):
    # The points are sorted beforehand
    return solver.bfs_solver_info(points, path, list(range(len(points))))

def GBFS_ray(points, center, path):
    return dtc.diminish_turning_crossing_to_star(points, center, path, heuristic=cc.ray_edge_crossings, end_condition=0)

def GBFS_ray_fixed(points, center, path):
    return dtc.diminish_turning_crossing_to_star_fixed_start_point(points, center, path, heuristic=cc.ray_edge_crossings, end_condition=0)

def GBFS_turn_ray(points, center, path):
    return dtc.diminish_turning_crossing_to_star(points, center, path)

def GBFS_turn_ray_fixed(points, center, path):
    return dtc.diminish_turning_crossing_to_star_fixed_start_point(points, center, path)

algos = {
    #"BFS": BFS,
    "GBFS-ray": GBFS_ray,
    "GBFS-turns+ray": GBFS_turn_ray,
    #"GBFS-ray-fixed": GBFS_ray_fixed,
    "GBFS-turns+ray-fixed": GBFS_turn_ray_fixed
}

def latex_big_table(summaries):
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Benchmark results for all tested sizes}")
    print("\\begin{tabular}{lcccc}")
    print("\\hline")
    print("n & Algorithm & Avg. length & Avg. explored & Avg. time (s)\\\\")
    print("\\hline")

    for n in sorted(summaries):
        for algo, stats in summaries[n].items():
            print(f"{n} & {algo} & "
                  f"{stats['avg_length']:.2f} & "
                  f"{stats['avg_explored']:.1f} & "
                  f"{stats['avg_time']:.4f}\\\\")
    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")


if __name__ == "__main__":

    for n in (70,100):
        paths = [(pl.generate_random_path(n),list(range(n))) for _ in range(50)]

        results = run_experiment(algos, paths)
        summaries = summarize_all(results)
        print_summary(summaries)
    #print(summaries)