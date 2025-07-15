#!/usr/bin/env python3
"""
Creative Tools Demo: Self-modifying code with data visualization
This script demonstrates creative use of Claude tools including:
1. Data analysis and visualization
2. Self-modifying code capabilities
3. Tool chaining
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

class SelfModifyingAnalyzer:
    def __init__(self):
        self.version = 1.0
        self.improvements = []
        self.metrics = {
            'execution_count': 0,
            'performance_scores': [],
            'modifications_made': 0
        }
    
    def analyze_data(self, data):
        """Analyze data and create visualization"""
        self.metrics['execution_count'] += 1
        
        # Generate sample data if none provided
        if data is None:
            data = np.random.randn(100)
        
        # Calculate statistics
        stats = {
            'mean': np.mean(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data)
        }
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histogram
        ax1.hist(data, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_title(f'Data Distribution (v{self.version})')
        ax1.set_xlabel('Value')
        ax1.set_ylabel('Frequency')
        
        # Box plot with stats
        box_data = ax2.boxplot(data, vert=True, patch_artist=True)
        box_data['boxes'][0].set_facecolor('lightblue')
        ax2.set_title('Statistical Summary')
        ax2.set_ylabel('Value')
        
        # Add stats text
        stats_text = f"Mean: {stats['mean']:.2f}\nStd: {stats['std']:.2f}\nMin: {stats['min']:.2f}\nMax: {stats['max']:.2f}"
        ax2.text(1.5, stats['mean'], stats_text, fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f'/mnt/host/c/CORA/analysis_v{self.version}.png')
        plt.close()
        
        return stats
    
    def improve_myself(self):
        """Self-modifying function that improves the code"""
        self.metrics['modifications_made'] += 1
        
        # Read own source code
        with open(__file__, 'r') as f:
            source_code = f.read()
        
        # Example improvement: Add performance tracking
        if 'import time' not in source_code:
            # Add time import
            source_code = source_code.replace(
                'import os', 
                'import os\nimport time'
            )
            
            # Add timing to analyze_data
            source_code = source_code.replace(
                'def analyze_data(self, data):',
                'def analyze_data(self, data):\n        start_time = time.time()'
            )
            
            source_code = source_code.replace(
                'return stats',
                'elapsed = time.time() - start_time\n        self.metrics["performance_scores"].append(elapsed)\n        return stats'
            )
            
            self.improvements.append(f"Added performance tracking (v{self.version})")
            self.version += 0.1
            
            # Write improved version
            with open(__file__, 'w') as f:
                f.write(source_code)
            
            return True
        
        return False
    
    def save_metrics(self):
        """Save metrics to JSON file"""
        metrics_file = '/mnt/host/c/CORA/analyzer_metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump({
                'version': self.version,
                'metrics': self.metrics,
                'improvements': self.improvements,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

# Demo creative tool combinations
def demonstrate_tool_chains():
    """Demonstrate creative tool combinations"""
    analyzer = SelfModifyingAnalyzer()
    
    # Generate different datasets
    datasets = {
        'normal': np.random.normal(0, 1, 100),
        'exponential': np.random.exponential(2, 100),
        'uniform': np.random.uniform(-3, 3, 100)
    }
    
    results = {}
    for name, data in datasets.items():
        print(f"Analyzing {name} distribution...")
        results[name] = analyzer.analyze_data(data)
    
    # Try to improve the analyzer
    if analyzer.improve_myself():
        print(f"Analyzer improved to version {analyzer.version}")
    
    # Save metrics
    analyzer.save_metrics()
    
    return results

if __name__ == "__main__":
    results = demonstrate_tool_chains()
    print("Analysis complete. Results saved.")
    print(json.dumps(results, indent=2))