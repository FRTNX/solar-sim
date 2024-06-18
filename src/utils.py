import re
import secrets
import random

from simulator_types import Percentage

def calculate_volts(watts, amps):
    """Calculate voltage from watts and amperes."""
    return watts / amps

def calculate_watts(volts, amps):
    """Calculate watts from voltage and amperes."""
    return volts * amps

def uuid(prefix: str='xxxxxxxx'):
    """Generate uuid with optional prefix."""
    if len(prefix) > 10:
        raise ValueError('uuid prefixes cannot exceed 10 characters')
    first_block_chars = 16 - len(prefix)
    first_block = 'x' * first_block_chars
    return re.sub('x', lambda m: secrets.choice('0123456789abcdef'),
                  f'{prefix}-{first_block}-xxxx-xxxx-xxxx-xxxxxxxx')

def variation(value, variance: Percentage = 0.3):
    """Create realistic variance in output values."""
    if value > 10:
        decimal = random.randrange(0, 99) * 0.01
        min_value = value - (value * variance)
        return random.randrange(int(min_value), int(value)) + decimal
    return value

class PhotoVoltaicError(Exception):
    """Indicates a PV misconfiguration."""
    pass

class InsufficientPowerError(Exception):
    """Thrown on inverter load misconfiguration."""
    pass
