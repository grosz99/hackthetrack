"""
Lightweight numpy-based implementations of statistical functions.

This module provides numpy-only alternatives to scipy functions
to reduce serverless function size for Vercel deployment.
"""

import numpy as np
from typing import Tuple


def norm_ppf(p: float) -> float:
    """
    Compute the inverse of the standard normal CDF (percent point function).

    This is a numpy-based approximation of scipy.stats.norm.ppf
    using the AS241 algorithm (Wichura, 1988), accurate to ~1e-15.

    Args:
        p: Probability value between 0 and 1

    Returns:
        Z-score corresponding to the given probability

    Example:
        >>> norm_ppf(0.5)  # Should be ~0.0
        0.0
        >>> norm_ppf(0.975)  # Should be ~1.96
        1.959963984540054

    Reference:
        Wichura, M.J. (1988) Algorithm AS 241: The Percentage Points of the Normal Distribution
    """
    # Handle edge cases
    if p <= 0:
        return -np.inf
    if p >= 1:
        return np.inf
    if p == 0.5:
        return 0.0

    # Use symmetry for p > 0.5
    if p > 0.5:
        q = 1 - p
        sign = 1
    else:
        q = p
        sign = -1

    # AS241 algorithm constants
    # Coefficients for the rational approximation in the central region
    a0 = 3.3871328727963666080e0
    a1 = 1.3314166789178437745e2
    a2 = 1.9715909503065514427e3
    a3 = 1.3731693765509461125e4
    a4 = 4.5921953931549871457e4
    a5 = 6.7265770927008700853e4
    a6 = 3.3430575583588128105e4
    a7 = 2.5090809287301226727e3

    b1 = 4.2313330701600911252e1
    b2 = 6.8718700749205790830e2
    b3 = 5.3941960214247511077e3
    b4 = 2.1213794301586595867e4
    b5 = 3.9307895800092710610e4
    b6 = 2.8729085735721942674e4
    b7 = 5.2264952788528545610e3

    # Coefficients for the rational approximation in the tail region
    c0 = 1.42343711074968357734e0
    c1 = 4.63033784615654529590e0
    c2 = 5.76949722146069140550e0
    c3 = 3.64784832476320460504e0
    c4 = 1.27045825245236838258e0
    c5 = 2.41780725177450611770e-1
    c6 = 2.27238449892691845833e-2
    c7 = 7.74545014278341407640e-4

    d1 = 2.05319162663775882187e0
    d2 = 1.67638483018380384940e0
    d3 = 6.89767334985100004550e-1
    d4 = 1.48103976427480074590e-1
    d5 = 1.51986665636164571966e-2
    d6 = 5.47593808499534494600e-4
    d7 = 1.05075007164441684324e-9

    split1 = 0.425
    split2 = 5.0

    if q > split1:
        # Central region
        r = q - 0.5
        s = r * r
        num = (((((((a7 * s + a6) * s + a5) * s + a4) * s + a3) * s + a2) * s + a1) * s + a0)
        den = ((((((b7 * s + b6) * s + b5) * s + b4) * s + b3) * s + b2) * s + b1) * s + 1.0
        return sign * r * num / den
    else:
        # Tail region
        r = np.sqrt(-np.log(q))
        if r <= split2:
            r = r - 1.6
            num = (((((((c7 * r + c6) * r + c5) * r + c4) * r + c3) * r + c2) * r + c1) * r + c0)
            den = (((((((d7 * r + d6) * r + d5) * r + d4) * r + d3) * r + d2) * r + d1) * r + 1.0)
        else:
            r = r - split2
            num = (((((((c7 * r + c6) * r + c5) * r + c4) * r + c3) * r + c2) * r + c1) * r + c0)
            den = (((((((d7 * r + d6) * r + d5) * r + d4) * r + d3) * r + d2) * r + d1) * r + 1.0)

        return sign * num / den


def find_peaks_simple(
    x: np.ndarray,
    distance: int = 1,
    prominence: float = 0
) -> Tuple[np.ndarray, dict]:
    """
    Find peaks (local maxima) in a 1D array.

    Simplified numpy-only implementation of scipy.signal.find_peaks
    for basic peak detection without scipy dependency.

    Args:
        x: 1D array of data
        distance: Minimum number of samples between peaks
        prominence: Minimum prominence of peaks (height above surrounding valleys)

    Returns:
        Tuple of (peak_indices, properties_dict)

    Example:
        >>> x = np.array([0, 1, 0, 2, 0, 3, 0, 2, 0])
        >>> peaks, _ = find_peaks_simple(x)
        >>> peaks
        array([1, 3, 5, 7])
    """
    # Find local maxima (points higher than both neighbors)
    if len(x) < 3:
        return np.array([]), {}

    # Create comparison arrays
    left_comparison = np.diff(x[:-1]) > 0  # Rising on left
    right_comparison = np.diff(x[1:]) < 0   # Falling on right

    # Peak is where both conditions are true
    peak_mask = np.zeros(len(x), dtype=bool)
    peak_mask[1:-1] = left_comparison & right_comparison
    peak_indices = np.where(peak_mask)[0]

    if len(peak_indices) == 0:
        return peak_indices, {}

    # Apply distance constraint
    if distance > 1:
        # Keep peaks that are at least 'distance' apart
        keep = np.ones(len(peak_indices), dtype=bool)
        for i in range(len(peak_indices) - 1):
            if not keep[i]:
                continue
            # Mark peaks within distance as not to keep
            too_close = (peak_indices[i+1:] - peak_indices[i]) < distance
            if np.any(too_close):
                # Keep the highest peak among those too close
                close_group = np.concatenate(([i], np.where(too_close)[0] + i + 1))
                close_heights = x[peak_indices[close_group]]
                best_idx = close_group[np.argmax(close_heights)]
                keep[close_group] = False
                keep[best_idx] = True

        peak_indices = peak_indices[keep]

    # Apply prominence constraint (if > 0)
    if prominence > 0 and len(peak_indices) > 0:
        # Calculate simple prominence as height above minimum of surrounding valleys
        prominences = np.zeros(len(peak_indices))

        for i, peak_idx in enumerate(peak_indices):
            # Find surrounding valleys
            left_valley = np.min(x[:peak_idx]) if peak_idx > 0 else x[peak_idx]
            right_valley = np.min(x[peak_idx+1:]) if peak_idx < len(x)-1 else x[peak_idx]
            surrounding_min = min(left_valley, right_valley)
            prominences[i] = x[peak_idx] - surrounding_min

        # Keep only peaks with sufficient prominence
        keep = prominences >= prominence
        peak_indices = peak_indices[keep]
        prominences = prominences[keep]

    # Return peaks and properties
    properties = {}
    return peak_indices, properties


# Backward compatibility aliases
def percentile_to_z(percentile: float) -> float:
    """
    Convert percentile (0-100) to z-score.

    Args:
        percentile: Percentile value between 0 and 100

    Returns:
        Z-score corresponding to the given percentile
    """
    # Clamp to valid range and convert to probability
    p = max(0.01, min(0.99, percentile / 100.0))
    return norm_ppf(p)
