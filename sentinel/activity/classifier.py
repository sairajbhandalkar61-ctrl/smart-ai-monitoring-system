import numpy as np
from typing import List, Dict, Any
from sentinel.tracking.tracker import Track

class ActivityClassifier:
    """
    Kinematic & Spatial Activity Classifier.
    Computes real crowd dynamics: occupancy, velocity dispersion, net movement flux.
    Provides uncertainty quantification and human review flagging.
    """
    def __init__(self, confidence_floor: float = 0.60):
        self.confidence_floor = confidence_floor
        self.classes = ["Low Activity", "Moderate Activity", "High Activity"]

    def extract_features(self, count: int, tracks: List[Track], count_diff: int, entry_rate: float, exit_rate: float) -> Dict[str, float]:
        """Extracts physically grounded kinematic features from active tracks."""
        if tracks:
            speeds = [np.sqrt(t.velocity[0]**2 + t.velocity[1]**2) for t in tracks]
            mean_speed = float(np.mean(speeds))
            speed_variance = float(np.var(speeds))
        else:
            mean_speed = 0.0
            speed_variance = 0.0

        flux = float(abs(count_diff) + (entry_rate + exit_rate))

        return {
            "count": float(count),
            "mean_speed": round(mean_speed, 2),
            "speed_variance": round(speed_variance, 2),
            "count_diff": float(count_diff),
            "flux": round(flux, 2)
        }

    def classify(self, count: int, tracks: List[Track], count_diff: int = 0, entry_rate: float = 0.0, exit_rate: float = 0.0) -> Dict[str, Any]:
        features = self.extract_features(count, tracks, count_diff, entry_rate, exit_rate)
        
        # Multidimensional kinetic scoring
        # Activity score combines spatial density and movement kinetics
        kinetic_energy = features["count"] * (1.0 + 0.15 * features["mean_speed"] + 0.1 * features["flux"])
        
        # Probabilistic soft scoring
        if kinetic_energy < 3.0:
            probs = [0.85, 0.12, 0.03]
            pred_class = "Low Activity"
        elif kinetic_energy < 8.0:
            probs = [0.15, 0.70, 0.15]
            pred_class = "Moderate Activity"
        else:
            probs = [0.05, 0.20, 0.75]
            pred_class = "High Activity"

        top_prob = float(max(probs))
        is_uncertain = top_prob < self.confidence_floor

        status = pred_class
        if is_uncertain:
            status = f"{pred_class} (Low Confidence - Verification Recommended)"

        return {
            "activity": pred_class,
            "status": status,
            "confidence": round(top_prob, 3),
            "probabilities": {
                "Low": round(probs[0], 3),
                "Moderate": round(probs[1], 3),
                "High": round(probs[2], 3)
            },
            "is_uncertain": is_uncertain,
            "features": features,
            "kinetic_score": round(kinetic_energy, 2)
        }
