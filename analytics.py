def analyze_activity(count):
    if count >= 5:
        return "High Crowd"
    elif count >= 2:
        return "Moderate Activity"
    else:
        return "Low Activity"