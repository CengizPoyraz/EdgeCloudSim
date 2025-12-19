#!/usr/bin/env python3
"""
Energy-Aware Task Offloading Results Analysis
Analyzes simulation results and generates comparison graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from pathlib import Path

# Configuration
POLICIES = ['BASELINE', 'GREEDY', 'ENERGY_AWARE']
POLICY_LABELS = {
    'BASELINE': 'Baseline (Random)',
    'GREEDY': 'Greedy (Always Offload)',
    'ENERGY_AWARE': 'Energy-Aware (Proposed)'
}
COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1']

class ResultsAnalyzer:
    
    def __init__(self, results_dir='sim_results'):
        self.results_dir = results_dir
        self.data = {}
        
    def find_latest_results(self):
        """Find the most recent results directory"""
        pattern = os.path.join(self.results_dir, 'ite*')
        dirs = glob.glob(pattern)
        
        if not dirs:
            print(f"No results found in {self.results_dir}")
            return None
            
        # Get the latest directory
        latest = max(dirs, key=os.path.getmtime)
        print(f"Using results from: {latest}")
        return latest
        
    def load_results(self):
        """Load CSV results for all policies"""
        print("\n" + "="*70)
        print("Loading simulation results...")
        print("="*70)
        
        results_dir = self.find_latest_results()
        if not results_dir:
            print("ERROR: No results directory found!")
            return False
            
        for policy in POLICIES:
            print(f"\nLoading {policy}...")
            policy_data = self._load_policy_results(results_dir, policy)
            self.data[policy] = policy_data
            
            # Print summary
            if policy_data['completed_tasks']:
                print(f"  ✓ Loaded {len(policy_data['completed_tasks'])} completed tasks")
            else:
                print(f"  ⚠ No data found for {policy}")
        
        print("\n" + "="*70)
        print("Results loaded successfully!")
        print("="*70 + "\n")
        return True
        
    def _load_policy_results(self, results_dir, policy):
        """Load results for a specific policy"""
        results = {
            'completed_tasks': 0,
            'failed_tasks': 0,
            'service_times': [],
            'vm_types': []
        }
        
        # Find all log files for this policy
        pattern = os.path.join(results_dir, f"{policy}_*", "GENERIC_LOG.csv")
        files = glob.glob(pattern)
        
        if not files:
            print(f"    Warning: No log files found at {pattern}")
            return results
            
        for file_path in files:
            try:
                # Read CSV file
                df = pd.read_csv(file_path, delimiter=';')
                
                # Count tasks
                if 'status' in df.columns:
                    completed = (df['status'] == 'COMPLETE').sum()
                    failed = (df['status'] == 'FAILED').sum()
                    results['completed_tasks'] += completed
                    results['failed_tasks'] += failed
                
                # Get service times
                if 'service_time' in df.columns:
                    times = df[df['status'] == 'COMPLETE']['service_time'].dropna()
                    results['service_times'].extend(times.tolist())
                
                # Get VM types
                if 'vm_type' in df.columns:
                    vm_types = df['vm_type'].dropna()
                    results['vm_types'].extend(vm_types.tolist())
                    
            except Exception as e:
                print(f"    Error loading {file_path}: {e}")
                
        return results
    
    def calculate_metrics(self):
        """Calculate performance metrics for each policy"""
        print("\n" + "="*70)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*70)
        
        for policy in POLICIES:
            data = self.data[policy]
            
            print(f"\n{POLICY_LABELS[policy]}")
            print("-" * 70)
            
            # Tasks
            total_tasks = data['completed_tasks'] + data['failed_tasks']
            if total_tasks > 0:
                failure_rate = (data['failed_tasks'] / total_tasks) * 100
                print(f"  Total Tasks: {total_tasks}")
                print(f"  Completed: {data['completed_tasks']}")
                print(f"  Failed: {data['failed_tasks']}")
                print(f"  Failure Rate: {failure_rate:.2f}%")
            else:
                print(f"  No tasks recorded")
            
            # Service times
            if data['service_times']:
                avg_time = np.mean(data['service_times'])
                std_time = np.std(data['service_times'])
                print(f"  Avg Service Time: {avg_time:.3f} ± {std_time:.3f} seconds")
                print(f"  Min Service Time: {np.min(data['service_times']):.3f} seconds")
                print(f"  Max Service Time: {np.max(data['service_times']):.3f} seconds")
            
            # Offloading decisions
            if data['vm_types']:
                edge_count = data['vm_types'].count('EDGE_VM')
                mobile_count = data['vm_types'].count('MOBILE_VM')
                total = edge_count + mobile_count
                if total > 0:
                    print(f"  Edge Offload Rate: {(edge_count/total)*100:.1f}%")
                    print(f"  Local Execution Rate: {(mobile_count/total)*100:.1f}%")
        
        print("\n" + "="*70 + "\n")
    
    def plot_failure_rate(self):
        """Plot failure rate comparison"""
        plt.figure(figsize=(10, 6))
        
        failure_rates = []
        for policy in POLICIES:
            data = self.data[policy]
            total = data['completed_tasks'] + data['failed_tasks']
            if total > 0:
                rate = (data['failed_tasks'] / total) * 100
            else:
                rate = 0
            failure_rates.append(rate)
        
        x = np.arange(len(POLICIES))
        bars = plt.bar(x, failure_rates, color=COLORS, alpha=0.7, width=0.6)
        
        plt.xlabel('Offloading Strategy', fontsize=12, fontweight='bold')
        plt.ylabel('Task Failure Rate (%)', fontsize=12, fontweight='bold')
        plt.title('Task Failure Rate Comparison', fontsize=14, fontweight='bold')
        plt.xticks(x, [POLICY_LABELS[p] for p in POLICIES], fontsize=10)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar, rate in zip(bars, failure_rates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height,
                    f'{rate:.1f}%', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('failure_rate_comparison.png', dpi=300, bbox_inches='tight')
        print("✓ Generated: failure_rate_comparison.png")
        plt.close()
        
    def plot_service_time(self):
        """Plot service time comparison"""
        plt.figure(figsize=(10, 6))
        
        avg_times = []
        std_times = []
        
        for policy in POLICIES:
            times = self.data[policy]['service_times']
            if times:
                avg_times.append(np.mean(times))
                std_times.append(np.std(times))
            else:
                avg_times.append(0)
                std_times.append(0)
        
        x = np.arange(len(POLICIES))
        bars = plt.bar(x, avg_times, color=COLORS, alpha=0.7, 
                      yerr=std_times, capsize=5, width=0.6)
        
        plt.xlabel('Offloading Strategy', fontsize=12, fontweight='bold')
        plt.ylabel('Average Service Time (seconds)', fontsize=12, fontweight='bold')
        plt.title('Service Time Comparison', fontsize=14, fontweight='bold')
        plt.xticks(x, [POLICY_LABELS[p] for p in POLICIES], fontsize=10)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar, avg in zip(bars, avg_times):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height,
                    f'{avg:.2f}s', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('service_time_comparison.png', dpi=300, bbox_inches='tight')
        print("✓ Generated: service_time_comparison.png")
        plt.close()
        
    def plot_offloading_distribution(self):
        """Plot offloading decision distribution"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        edge_rates = []
        mobile_rates = []
        
        for policy in POLICIES:
            vm_types = self.data[policy]['vm_types']
            if vm_types:
                edge = vm_types.count('EDGE_VM')
                mobile = vm_types.count('MOBILE_VM')
                total = edge + mobile
                if total > 0:
                    edge_rates.append((edge / total) * 100)
                    mobile_rates.append((mobile / total) * 100)
                else:
                    edge_rates.append(0)
                    mobile_rates.append(0)
            else:
                edge_rates.append(0)
                mobile_rates.append(0)
        
        x = np.arange(len(POLICIES))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, edge_rates, width, label='Edge Execution',
                      color='#4ECDC4', alpha=0.8)
        bars2 = ax.bar(x + width/2, mobile_rates, width, label='Local Execution',
                      color='#FF6B6B', alpha=0.8)
        
        ax.set_xlabel('Offloading Strategy', fontsize=12, fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Offloading Decision Distribution', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([POLICY_LABELS[p] for p in POLICIES], fontsize=10)
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f'{height:.1f}%', ha='center', va='bottom',
                       fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('offloading_distribution.png', dpi=300, bbox_inches='tight')
        print("✓ Generated: offloading_distribution.png")
        plt.close()
        
    def plot_service_time_distribution(self):
        """Plot service time distribution"""
        plt.figure(figsize=(12, 6))
        
        for i, policy in enumerate(POLICIES):
            times = self.data[policy]['service_times']
            if times:
                plt.hist(times, bins=30, alpha=0.6, 
                        label=POLICY_LABELS[policy], color=COLORS[i])
        
        plt.xlabel('Service Time (seconds)', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title('Service Time Distribution', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig('service_time_distribution.png', dpi=300, bbox_inches='tight')
        print("✓ Generated: service_time_distribution.png")
        plt.close()
    
    def generate_summary_report(self):
        """Generate text summary report"""
        with open('results_summary.txt', 'w') as f:
            f.write("="*70 + "\n")
            f.write("ENERGY-AWARE TASK OFFLOADING - RESULTS SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            for policy in POLICIES:
                data = self.data[policy]
                
                f.write(f"\n{POLICY_LABELS[policy]}\n")
                f.write("-"*70 + "\n")
                
                # Tasks
                total = data['completed_tasks'] + data['failed_tasks']
                if total > 0:
                    failure_rate = (data['failed_tasks'] / total) * 100
                    f.write(f"  Total Tasks: {total}\n")
                    f.write(f"  Completed: {data['completed_tasks']}\n")
                    f.write(f"  Failed: {data['failed_tasks']}\n")
                    f.write(f"  Failure Rate: {failure_rate:.2f}%\n")
                
                # Service times
                if data['service_times']:
                    avg = np.mean(data['service_times'])
                    std = np.std(data['service_times'])
                    f.write(f"  Average Service Time: {avg:.3f} ± {std:.3f} seconds\n")
                
                # Offloading
                if data['vm_types']:
                    edge = data['vm_types'].count('EDGE_VM')
                    mobile = data['vm_types'].count('MOBILE_VM')
                    total_vm = edge + mobile
                    if total_vm > 0:
                        f.write(f"  Edge Offload Rate: {(edge/total_vm)*100:.1f}%\n")
                        f.write(f"  Local Execution: {(mobile/total_vm)*100:.1f}%\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print("✓ Generated: results_summary.txt")
    
    def generate_all_plots(self):
        """Generate all analysis plots"""
        print("\nGenerating analysis plots...")
        print("-" * 50)
        
        self.plot_failure_rate()
        self.plot_service_time()
        self.plot_offloading_distribution()
        self.plot_service_time_distribution()
        
        print("-" * 50)
        print("\nAll plots generated successfully!")

def main():
    print("\n" + "="*70)
    print("Energy-Aware Task Offloading - Results Analysis")
    print("="*70)
    
    analyzer = ResultsAnalyzer()
    
    if not analyzer.load_results():
        print("\nERROR: Could not load results!")
        print("Make sure simulations have completed and results are in sim_results/")
        return
    
    analyzer.calculate_metrics()
    analyzer.generate_all_plots()
    analyzer.generate_summary_report()
    
    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - failure_rate_comparison.png")
    print("  - service_time_comparison.png")
    print("  - offloading_distribution.png")
    print("  - service_time_distribution.png")
    print("  - results_summary.txt")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()