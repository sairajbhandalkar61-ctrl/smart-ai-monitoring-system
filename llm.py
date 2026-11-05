def generate_insight(activity: str, count: int, movement: str = "Medium"):
    if activity == "High":
        if movement == "High":
            return "[ALERT] High crowd density and rapid movement detected. Surveillance recommendation: monitor corridor exits."
        return "[ALERT] High crowd density detected. Normal traffic flow maintained, monitoring active."
    elif activity == "Moderate":
        if count >= 10:
            return "[FLOW] Peak transition period. Moderate flow observed with balanced dispersal."
        return "[NORMAL] Steady pedestrian activity observed. Normal monitoring parameters."
    else:
        return "[SECURE] Low crowd density. Zone secured with optimal throughput."
