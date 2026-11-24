"""
Clustering Experiments for Phase 5.3
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.recommendation.clustering_features import (
    ClusteringConfig, 
    ClusteringFeatureBuilder, 
    build_clustering_features,
)
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score
import numpy as np

# Output paths
OUTPUT_DIR = Path("reports/phase5/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_clustering_experiments():
    """Run clustering experiments."""
    print("=" * 60)
    print("PHASE 5.3: CLUSTERING EXPERIMENTS")
    print("=" * 60)
    
    print("Building clustering features...")
    config = ClusteringConfig(
        tfidf_max_features=500,
        pca_components=20,
        random_seed=42,
    )
    
    builder = ClusteringFeatureBuilder(ClusteringConfig(
        tfidf_max_features=500,
        pca_components=20,
        random_seed=42,
    ))
    builder.load_data()
    print("Building features...")
    start = time.time()
    builder.build_features()
    print(f"Built features in {time.time() - start:.2f}s")
    
    features = builder.get_feature_matrix("combined_scaled")
    recipe_ids = builder.get_recipe_ids()
    print(f"Feature matrix shape: {features.shape}")
    
    # Run clustering experiments
    cluster_configs = [
        {"name": "kmeans_20", "method": "kmeans", "n_clusters": 20},
        {"name": "kmeans_50", "method": "kmeans", "n_clusters": 50},
        {"name": "kmeans_100", "method": "kmeans", "n_clusters": 100},
        {"name": "agglomerative_20", "method": "agglomerative", "n_clusters": 20},
        {"name": "agglomerative_50", "method": "agglomerative", "n_clusters": 50},
    ]
    
    features = builder.get_feature_matrix("combined_scaled")
    recipe_ids = builder.get_recipe_ids()
    results = {}
    
    for config in cluster_configs:
        print(f"\nRunning {config['name']}...")
        start = time.time()
        
        if config["method"] == "kmeans":
            model = KMeans(
                n_clusters=config["n_clusters"],
                random_state=42,
                n_init=10,
            )
        else:
            model = AgglomerativeClustering(
                n_clusters=config["n_clusters"],
                linkage="ward",
            )
        
        labels = model.fit_predict(features)
        elapsed = time.time() - start
        
        # Evaluate
        if len(set(model.labels_)) > 1:
            silhouette = silhouette_score(features, model.labels_)
            db_score = davies_bouldin_score(features, model.labels_)
        else:
            silhouette = 0.0
            db_score = float('inf')
        
        # Cluster statistics
        unique, counts = np.unique(model.labels_, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        results[config["name"]] = {
            "config": config,
            "n_clusters": len(unique),
            "silhouette": float(silhouette),
            "davies_bouldin": float(db_score),
            "cluster_sizes": cluster_sizes,
            "time_seconds": elapsed,
        }
        
        print(f"  Clusters: {len(unique)}")
        print(f"  Silhouette: {silhouette:.4f}")
        print(f"  Davies-Bouldin: {db_score:.4f}")
        print(f"  Time: {elapsed:.2f}s")
    
    # Save clustering results
    output_path = Path("reports/phase5/experiments/results/clustering_experiments.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nClustering results saved to: {output_path}")
    return results


if __name__ == "__main__":
    import json
    import time
    from pathlib import Path
    from typing import Dict, List, Optional, Any
    import numpy as np
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.recommendation.clustering_features import (
        ClusteringConfig, 
        ClusteringFeatureBuilder, 
        build_clustering_features,
    )
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    import numpy as np
    
    # Output paths
    OUTPUT_DIR = Path("reports/phase5/experiments/results")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run clustering experiments
    results = run_clustering_experiments()
    
    # Save summary
    summary_path = Path("reports/phase5/experiments/summary/clustering_summary.json")
    summary_dir = Path("reports/phase5/experiments/summary")
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "experiment": "clustering",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": {name: {
            "n_clusters": r["n_clusters"],
            "silhouette": r["silhouette"],
            "davies_bouldin": r["davies_bouldin"],
            "time_seconds": r["time_seconds"],
        } for name, r in results.items()}
    }
    
    with open("reports/phase5/experiments/summary/clustering_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("\nClustering experiments complete!")


if __name__ == "__main__":
    import json
    import time
    from pathlib import Path
    from typing import Dict, List, Optional, Any
    import numpy as np
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.recommendation.clustering_features import (
        ClusteringConfig, 
        ClusteringFeatureBuilder, 
        build_clustering_features,
    )
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    import numpy as np
    
    # Output paths
    OUTPUT_DIR = Path("reports/phase5/experiments/results")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    run_clustering_experiments()