def calculate_volts(watts, amps):
    """Calculate voltage from watts and amperes."""
    return watts / amps


def calculate_watts(volts, amps):
    """Calculate watts from voltage and amperes."""
    return volts * amps