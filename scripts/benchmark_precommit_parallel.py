#!/usr/bin/env python3
"""
Pre-commit Parallel Performance Benchmark Script

This script measures the performance improvement of parallel pre-commit execution
optimized for the ARES project infrastructure.
"""

import subprocess
import time
import os
import statistics
import sys
from pathlib import Path


class PreCommitBenchmark:
    """Benchmark pre-commit performance with different parallel configurations."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}

    def run_benchmark(self, name: str, env_vars: dict, runs: int = 3) -> dict:
        """Run pre-commit benchmark with specific configuration."""
        print(f"🔄 Benchmarking {name} ({runs} runs)...")

        times = []
        env = os.environ.copy()
        env.update(env_vars)

        for run in range(runs):
            print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)

            start_time = time.time()
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True,
            )
            elapsed = time.time() - start_time
            times.append(elapsed)

            if result.returncode == 0:
                print(f"✅ {elapsed:.3f}s")
            else:
                print(f"❌ {elapsed:.3f}s (failed)")
                # Print error details for debugging
                if "failed" in name.lower():
                    print(f"    Error: {result.stderr.split(chr(10))[0][:100]}...")

        return {
            "name": name,
            "times": times,
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "successful_runs": len([t for t in times if t > 0]),
        }

    def run_all_benchmarks(self):
        """Run comprehensive benchmark suite."""
        print("🚀 Starting Pre-commit Parallel Performance Benchmark")
        print("=" * 60)

        # Test configurations
        configs = [
            ("Serial (Default)", {}),
            ("Parallel 2-Core", {"PRE_COMMIT_PARALLEL": "2"}),
            ("Parallel 4-Core", {"PRE_COMMIT_PARALLEL": "4"}),
            ("Parallel 8-Core", {"PRE_COMMIT_PARALLEL": "8"}),
            ("Max Parallel", {"PRE_COMMIT_PARALLEL": str(os.cpu_count())}),
        ]

        # Environment with optimizations
        parallel_optimized = {
            "PRE_COMMIT_PARALLEL": "4",
            "PYTHONPATH": str(self.project_root / "src"),
            "PRE_COMMIT_COLOR": "never",  # Reduce output overhead
        }

        configs.append(("Optimized Parallel", parallel_optimized))

        # Run benchmarks
        for name, env_vars in configs:
            try:
                result = self.run_benchmark(name, env_vars, runs=3)
                self.results[name] = result
            except Exception as e:
                print(f"❌ Failed to benchmark {name}: {e}")

        self.print_results()
        return self.results

    def print_results(self):
        """Print benchmark results in a formatted table."""
        print("\n📊 Benchmark Results")
        print("=" * 80)
        print(
            f"{'Configuration':<20} {'Mean (s)':<10} {'Median (s)':<12} {'Min (s)':<10} {'StdDev':<10}"
        )
        print("-" * 80)

        # Sort by mean time
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]["mean"])

        baseline_mean = None
        for name, result in sorted_results:
            if baseline_mean is None:
                baseline_mean = result["mean"]

            improvement = ((baseline_mean - result["mean"]) / baseline_mean) * 100
            improvement_str = f"({improvement:+.1f}%)" if improvement != 0 else ""

            print(
                f"{name:<20} {result['mean']:<10.3f} {result['median']:<12.3f} "
                f"{result['min']:<10.3f} {result['stdev']:<10.3f} {improvement_str}"
            )

        # Find best performing configuration
        if sorted_results:
            best_config = sorted_results[0]
            print(f"\n🏆 Best Configuration: {best_config[0]}")
            print(f"   Mean Time: {best_config[1]['mean']:.3f}s")

            if len(sorted_results) > 1:
                worst_config = sorted_results[-1]
                improvement = (
                    (worst_config[1]["mean"] - best_config[1]["mean"])
                    / worst_config[1]["mean"]
                ) * 100
                print(f"   Improvement: {improvement:.1f}% faster than slowest")

    def export_results(self, filename: str = "precommit_benchmark_results.json"):
        """Export results to JSON for further analysis."""
        import json

        output_path = self.project_root / filename
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results exported to: {output_path}")
        return output_path


def main():
    """Main benchmark execution."""
    print("Pre-commit Parallel Performance Benchmark")
    print("For ARES Agent Reliability Enforcement System")
    print()

    # Check if we're in the right directory
    if not Path(".pre-commit-config.yaml").exists():
        print("❌ Error: .pre-commit-config.yaml not found in current directory")
        print("   Please run this script from the ARES project root directory")
        sys.exit(1)

    # Check if pre-commit is available
    try:
        subprocess.run(["pre-commit", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: pre-commit not found")
        print("   Please install pre-commit: pip install pre-commit")
        sys.exit(1)

    # Run benchmarks
    benchmark = PreCommitBenchmark()
    results = benchmark.run_all_benchmarks()

    # Export results
    benchmark.export_results()

    # Performance recommendations
    print("\n💡 Performance Recommendations:")
    if results:
        best_config = min(results.items(), key=lambda x: x[1]["mean"])
        print(f"   1. Use configuration: {best_config[0]}")
        print("   2. Set environment variable for best performance")
        print("   3. Consider using parallel execution in CI/CD")
        print("   4. Monitor performance regression with this script")

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
