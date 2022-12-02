import pandas as pd

class Stats:
    def stats(stats, activitiies_df):
        stats.max_dist = max(activitiies_df['distance'])
        stats.fast_pace = min(activitiies_df['avg_pace'])
        stats.total_distance = sum(activitiies_df['distance'])
