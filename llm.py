def generate_insight(activity, count):
    if activity == "High":
        return "⚠️ High crowd detected. Monitor closely."
    elif activity == "Moderate":
        return "Moderate activity observed."
    else:
        return "Low activity. Safe environment."