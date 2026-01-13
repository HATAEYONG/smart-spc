"""
Genetic Algorithm Engine

STEP 4: Hybrid GA + Local Search
"""
from .runner import (
    run_ga_with_local_search,
    run_ga_only,
    run_local_search_only,
    compare_methods
)
from .local_search import (
    local_search,
    simulated_annealing_search,
    variable_neighborhood_search
)
from .encoding import Chromosome, encode_jobs, decode_chromosome
from .fitness import evaluate_fitness, calculate_metrics

__all__ = [
    # Main functions
    'run_ga_with_local_search',
    'run_ga_only',
    'run_local_search_only',
    'compare_methods',

    # Local Search variants
    'local_search',
    'simulated_annealing_search',
    'variable_neighborhood_search',

    # Utilities
    'Chromosome',
    'encode_jobs',
    'decode_chromosome',
    'evaluate_fitness',
    'calculate_metrics',
]
