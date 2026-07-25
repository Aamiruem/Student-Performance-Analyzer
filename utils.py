import numpy as np
import math

def calculate_statistics(data):
    return {
        "mean": round(np.mean(data), 2),
        "std_dev": round(np.std(data), 2),
        "variance": round(np.var(data), 2),
        "sqrt_total": round(math.sqrt(sum(data)), 2)
    }
