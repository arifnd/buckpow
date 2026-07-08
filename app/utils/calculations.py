def calc_load_voltage(bus_voltage, shunt_voltage):
    return bus_voltage + (shunt_voltage / 1000)


def calc_energy_increment(power_watts, sampling_interval_seconds):
    return power_watts * (sampling_interval_seconds / 3600)
