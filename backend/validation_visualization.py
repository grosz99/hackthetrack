"""
Visualization Tools for Statistical Validation Results

Creates publication-quality charts to communicate validation findings.

Author: Statistical Validation System
Date: 2025-11-10
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
from scipy import stats

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11


class ValidationVisualizer:
    """Create visualizations for statistical validation results."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("data/validation_visualizations")
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def load_data(self, race_name: str) -> pd.DataFrame:
        """Load merged telemetry and lap time data."""
        # Load telemetry
        telemetry_path = (
            self.data_dir /
            "analysis_outputs" /
            f"{race_name}_telemetry_features.csv"
        )
        telemetry = pd.read_csv(telemetry_path)

        # Load lap times
        lap_times_path = (
            self.data_dir /
            "race_results" /
            "best_10_laps" /
            f"{race_name}_best_10_laps.csv"
        )
        lap_df = pd.read_csv(lap_times_path, sep=';')

        # Convert lap times
        lap_df['AVERAGE_SECONDS'] = lap_df['AVERAGE'].apply(
            self._convert_laptime_to_seconds
        )

        # Merge
        merged = telemetry.merge(
            lap_df[['NUMBER', 'AVERAGE_SECONDS']],
            left_on='driver_number',
            right_on='NUMBER',
            how='inner'
        )

        return merged

    def _convert_laptime_to_seconds(self, time_str: str) -> float:
        """Convert lap time string (MM:SS.mmm) to seconds."""
        try:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except:
            return np.nan

    def plot_correlation_matrix(self, race_name: str) -> None:
        """Plot correlation matrix for all metrics."""
        data = self.load_data(race_name)

        metrics = [
            'throttle_smoothness',
            'steering_smoothness',
            'braking_point_consistency',
            'corner_efficiency',
            'accel_efficiency',
            'lateral_g_utilization',
            'straight_speed_consistency',
            'AVERAGE_SECONDS'
        ]

        # Select available metrics
        available = [m for m in metrics if m in data.columns]
        corr_data = data[available].dropna()

        # Calculate correlation
        corr_matrix = corr_data.corr()

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot heatmap
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.3f',
            cmap='RdBu_r',
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )

        ax.set_title(
            f'Correlation Matrix: Telemetry Metrics vs Lap Time\n{race_name.replace("_", " ").title()}',
            fontsize=14,
            fontweight='bold'
        )

        plt.tight_layout()
        plt.savefig(
            self.output_dir / f'{race_name}_correlation_matrix.png',
            dpi=300,
            bbox_inches='tight'
        )
        print(f"Saved: {race_name}_correlation_matrix.png")
        plt.close()

    def plot_validation_summary(self) -> None:
        """Create summary chart of metric validation results."""
        # Validation results from statistical analysis
        metrics = [
            'braking_point_consistency',
            'lateral_g_utilization',
            'corner_efficiency',
            'throttle_smoothness',
            'steering_smoothness',
            'accel_efficiency',
            'straight_speed_consistency'
        ]

        correlations = [0.573, -0.803, -0.306, 0.163, 0.147, -0.027, -0.088]
        p_values = [0.020, 0.0002, 0.249, 0.546, 0.587, 0.920, 0.745]
        actionable = [True, False, True, True, True, False, True]

        # Create DataFrame
        df = pd.DataFrame({
            'Metric': metrics,
            'Correlation': correlations,
            'P-Value': p_values,
            'Actionable': actionable,
            'Significant': [p < 0.05 for p in p_values]
        })

        # Determine status
        df['Status'] = df.apply(
            lambda row: 'VALIDATED' if (row['Significant'] and row['Actionable'])
            else 'INFORMATIONAL' if (row['Significant'] and not row['Actionable'])
            else 'NOT VALIDATED',
            axis=1
        )

        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Correlation strength
        colors = [
            'green' if s == 'VALIDATED' else 'orange' if s == 'INFORMATIONAL' else 'red'
            for s in df['Status']
        ]

        bars = ax1.barh(df['Metric'], abs(df['Correlation']), color=colors, alpha=0.7)
        ax1.axvline(0.3, color='gray', linestyle='--', linewidth=1, label='Medium effect')
        ax1.set_xlabel('Absolute Correlation with Lap Time', fontweight='bold')
        ax1.set_title('Correlation Strength', fontweight='bold')
        ax1.legend()

        # Add p-value annotations
        for i, (corr, p) in enumerate(zip(abs(df['Correlation']), df['P-Value'])):
            ax1.text(
                corr + 0.02,
                i,
                f"p={p:.3f}",
                va='center',
                fontsize=9
            )

        # Plot 2: Statistical significance
        df_sorted = df.sort_values('P-Value')
        colors2 = [
            'green' if s == 'VALIDATED' else 'orange' if s == 'INFORMATIONAL' else 'red'
            for s in df_sorted['Status']
        ]

        ax2.barh(df_sorted['Metric'], -np.log10(df_sorted['P-Value']), color=colors2, alpha=0.7)
        ax2.axvline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='p=0.05')
        ax2.set_xlabel('-log10(P-Value)', fontweight='bold')
        ax2.set_title('Statistical Significance', fontweight='bold')
        ax2.legend()

        # Create legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='VALIDATED (use for coaching)'),
            Patch(facecolor='orange', alpha=0.7, label='INFORMATIONAL (car setup)'),
            Patch(facecolor='red', alpha=0.7, label='NOT VALIDATED (insufficient evidence)')
        ]
        fig.legend(
            handles=legend_elements,
            loc='upper center',
            bbox_to_anchor=(0.5, 0.05),
            ncol=3,
            frameon=True
        )

        fig.suptitle(
            'Statistical Validation Summary: Telemetry Metrics\nBarber Race 1 (n=16)',
            fontsize=16,
            fontweight='bold',
            y=0.98
        )

        plt.tight_layout(rect=[0, 0.08, 1, 0.95])
        plt.savefig(
            self.output_dir / 'validation_summary.png',
            dpi=300,
            bbox_inches='tight'
        )
        print("Saved: validation_summary.png")
        plt.close()

    def plot_braking_consistency_analysis(self, race_name: str) -> None:
        """Deep dive into validated metric: braking consistency."""
        data = self.load_data(race_name)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: Scatter plot with regression
        ax1 = axes[0, 0]
        x = data['braking_point_consistency']
        y = data['AVERAGE_SECONDS']

        ax1.scatter(x, y, alpha=0.6, s=100, edgecolors='black', linewidth=1)

        # Add regression line
        mask = ~np.isnan(x) & ~np.isnan(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], y[mask])
        line_x = np.linspace(x.min(), x.max(), 100)
        line_y = slope * line_x + intercept

        ax1.plot(line_x, line_y, 'r--', linewidth=2, label=f'r={r_value:.3f}, p={p_value:.3f}')
        ax1.set_xlabel('Braking Point Consistency (std dev)', fontweight='bold')
        ax1.set_ylabel('Lap Time (seconds)', fontweight='bold')
        ax1.set_title('Correlation Analysis', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Distribution
        ax2 = axes[0, 1]
        ax2.hist(x.dropna(), bins=10, edgecolor='black', alpha=0.7, color='skyblue')
        ax2.axvline(x.quantile(0.25), color='green', linestyle='--', linewidth=2, label='Top 25%')
        ax2.axvline(x.median(), color='orange', linestyle='--', linewidth=2, label='Median')
        ax2.axvline(x.quantile(0.75), color='red', linestyle='--', linewidth=2, label='Bottom 25%')
        ax2.set_xlabel('Braking Point Consistency', fontweight='bold')
        ax2.set_ylabel('Number of Drivers', fontweight='bold')
        ax2.set_title('Distribution', fontweight='bold')
        ax2.legend()

        # Plot 3: Percentile vs Lap Time
        ax3 = axes[1, 0]
        data_sorted = data.sort_values('braking_point_consistency')
        data_sorted['percentile'] = np.arange(len(data_sorted)) / len(data_sorted) * 100

        ax3.scatter(
            data_sorted['percentile'],
            data_sorted['AVERAGE_SECONDS'],
            alpha=0.6,
            s=100,
            edgecolors='black',
            linewidth=1
        )
        ax3.set_xlabel('Percentile (0=worst, 100=best)', fontweight='bold')
        ax3.set_ylabel('Lap Time (seconds)', fontweight='bold')
        ax3.set_title('Percentile Performance', fontweight='bold')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Box plot by quartile
        ax4 = axes[1, 1]
        data['quartile'] = pd.qcut(
            data['braking_point_consistency'],
            q=4,
            labels=['Q1 (Best)', 'Q2', 'Q3', 'Q4 (Worst)']
        )

        data.boxplot(
            column='AVERAGE_SECONDS',
            by='quartile',
            ax=ax4,
            patch_artist=True
        )
        ax4.set_xlabel('Braking Consistency Quartile', fontweight='bold')
        ax4.set_ylabel('Lap Time (seconds)', fontweight='bold')
        ax4.set_title('Lap Time by Consistency Quartile', fontweight='bold')
        plt.sca(ax4)
        plt.xticks(rotation=45)

        fig.suptitle(
            'Braking Point Consistency Analysis\nVALIDATED METRIC (r=0.573, p=0.020)',
            fontsize=16,
            fontweight='bold',
            y=0.995
        )

        plt.tight_layout()
        plt.savefig(
            self.output_dir / f'{race_name}_braking_analysis.png',
            dpi=300,
            bbox_inches='tight'
        )
        print(f"Saved: {race_name}_braking_analysis.png")
        plt.close()

    def plot_overfitting_demonstration(self) -> None:
        """Visualize overfitting problem with small sample size."""
        # Simulate the overfitting problem
        np.random.seed(42)

        # True relationship: lap_time = 98 + noise
        n_drivers = 16
        true_mean = 98.5

        # Generate data
        lap_times = np.random.normal(true_mean, 1, n_drivers)

        # Generate 7 random "metrics" (pure noise)
        metrics = np.random.randn(n_drivers, 7)

        # Fit overfit model
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score

        model = LinearRegression()

        # Training R²
        model.fit(metrics, lap_times)
        train_r2 = model.score(metrics, lap_times)

        # Cross-validation R²
        cv_scores = cross_val_score(model, metrics, lap_times, cv=5, scoring='r2')
        cv_r2 = cv_scores.mean()

        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Training vs CV performance
        ax1 = axes[0]
        models = ['Training\nPerformance', 'Cross-Validation\nPerformance']
        r2_scores = [train_r2, cv_r2]
        colors = ['green', 'red']

        bars = ax1.bar(models, r2_scores, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax1.axhline(0, color='black', linestyle='-', linewidth=1)
        ax1.set_ylabel('R² Score', fontweight='bold', fontsize=12)
        ax1.set_title('Overfitting in Small Samples\n(n=16, k=7 predictors)', fontweight='bold', fontsize=14)
        ax1.set_ylim(-1.5, 1.0)

        # Add value labels
        for bar, score in zip(bars, r2_scores):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.05 if height > 0 else height - 0.05,
                f'{score:.3f}',
                ha='center',
                va='bottom' if height > 0 else 'top',
                fontweight='bold',
                fontsize=12
            )

        # Add annotations
        ax1.text(
            0.5, 0.95,
            'SEVERE OVERFITTING',
            transform=ax1.transAxes,
            fontsize=14,
            fontweight='bold',
            color='red',
            ha='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7)
        )

        # Plot 2: Sample size requirements
        ax2 = axes[1]
        categories = ['Current\nSample', 'Required\n(Minimum)', 'Required\n(Ideal)']
        sample_sizes = [16, 70, 140]
        colors2 = ['red', 'orange', 'green']

        bars2 = ax2.bar(categories, sample_sizes, color=colors2, alpha=0.7, edgecolor='black', linewidth=2)
        ax2.set_ylabel('Number of Drivers', fontweight='bold', fontsize=12)
        ax2.set_title('Sample Size Requirements\n(7 predictors)', fontweight='bold', fontsize=14)

        # Add value labels
        for bar, size in zip(bars2, sample_sizes):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'n={size}',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=12
            )

        # Add gap annotation
        ax2.annotate(
            '',
            xy=(0, 16),
            xytext=(1, 70),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2)
        )
        ax2.text(
            0.5, 43,
            'Gap: -54 drivers',
            ha='center',
            fontweight='bold',
            color='red',
            fontsize=11
        )

        plt.tight_layout()
        plt.savefig(
            self.output_dir / 'overfitting_demonstration.png',
            dpi=300,
            bbox_inches='tight'
        )
        print("Saved: overfitting_demonstration.png")
        plt.close()

    def plot_sample_size_power_analysis(self) -> None:
        """Show statistical power vs sample size."""
        from scipy.stats import t

        # Effect sizes
        effect_sizes = [0.3, 0.5, 0.7]  # Small, medium, large correlations
        sample_sizes = np.arange(10, 150, 5)

        fig, ax = plt.subplots(figsize=(10, 6))

        for r in effect_sizes:
            powers = []
            for n in sample_sizes:
                # Calculate power for correlation test
                df = n - 2
                t_crit = t.ppf(0.975, df)  # Two-tailed, alpha=0.05

                # Non-centrality parameter
                ncp = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)

                # Power = P(reject H0 | H1 true)
                power = 1 - t.cdf(t_crit, df, ncp) + t.cdf(-t_crit, df, ncp)
                powers.append(power)

            label = f'r={r:.1f} (' + ('small' if r == 0.3 else 'medium' if r == 0.5 else 'large') + ' effect)'
            ax.plot(sample_sizes, powers, linewidth=2, label=label)

        # Add reference lines
        ax.axhline(0.8, color='green', linestyle='--', linewidth=2, label='80% power (target)')
        ax.axvline(16, color='red', linestyle='--', linewidth=2, label='Current n=16')

        ax.set_xlabel('Sample Size (number of drivers)', fontweight='bold', fontsize=12)
        ax.set_ylabel('Statistical Power', fontweight='bold', fontsize=12)
        ax.set_title('Statistical Power vs Sample Size\n(Two-tailed correlation test, α=0.05)', fontweight='bold', fontsize=14)
        ax.legend(loc='lower right', frameon=True)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)

        # Annotate current position
        ax.annotate(
            'Current\npower <30%',
            xy=(16, 0.25),
            xytext=(30, 0.15),
            fontweight='bold',
            color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=2)
        )

        plt.tight_layout()
        plt.savefig(
            self.output_dir / 'power_analysis.png',
            dpi=300,
            bbox_inches='tight'
        )
        print("Saved: power_analysis.png")
        plt.close()

    def generate_all_visualizations(self, race_name: str = "barber_r1") -> None:
        """Generate all validation visualizations."""
        print("\nGenerating Statistical Validation Visualizations...")
        print("=" * 60)

        print("\n1. Correlation Matrix...")
        self.plot_correlation_matrix(race_name)

        print("\n2. Validation Summary...")
        self.plot_validation_summary()

        print("\n3. Braking Consistency Analysis...")
        self.plot_braking_consistency_analysis(race_name)

        print("\n4. Overfitting Demonstration...")
        self.plot_overfitting_demonstration()

        print("\n5. Power Analysis...")
        self.plot_sample_size_power_analysis()

        print("\n" + "=" * 60)
        print(f"All visualizations saved to: {self.output_dir}")
        print("=" * 60)


def main():
    """Generate all validation visualizations."""
    visualizer = ValidationVisualizer(data_dir="data")
    visualizer.generate_all_visualizations("barber_r1")


if __name__ == "__main__":
    main()
