def analyze_activity(count):
    if count >= 15:
        return "High Crowd"
    elif count >= 5:
        return "Moderate Activity"
    else:
        return "Low Activity"
