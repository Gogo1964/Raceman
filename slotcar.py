class SlotCar(object):
    def __init__(self, tag_id, name, max_speed_voltage: float, slow_speed_voltage: float, FuelConsumption):
        self.tag_id = tag_id
        self.name = name
        self.max_speed_voltage = max_speed_voltage
        self.slow_speed_voltage = slow_speed_voltage
        self.fuel_consumption = FuelConsumption
        
    def accelerate(self, increment):
        """Increase the speed of the slot car by the given increment."""
        self.speed += increment
        print(f"{self.name} accelerated to {self.speed} units/sec.")

    def brake(self, decrement):
        """Decrease the speed of the slot car by the given decrement."""
        self.speed = max(0, self.speed - decrement)
        print(f"{self.name} slowed down to {self.speed} units/sec.")

    def get_speed(self):
        """Return the current speed of the slot car."""
        return self.speed

    def __str__(self):
        return f"SlotCar(name={self.name}, speed={self.speed})"