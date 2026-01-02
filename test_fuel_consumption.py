import unittest

from fuel_consumption import FuelConsumption


class TestFuelConsumption(unittest.TestCase):
    def setUp(self):
        # time_base = 60s, curve: (speed m/s, percent per time_base)
        self.curve = [(0.0, 0.5), (5.0, 1.0), (10.0, 2.0)]
        self.fc = FuelConsumption(60, self.curve)

    def test_exact_point(self):
        # speed 5 m/s, time 60s => distance 300m -> consumption == 1.0
        self.assertAlmostEqual(self.fc.get_fuel_consumption(60000, 300), 1.0)

    def test_interpolation(self):
        # avg speed 7.5 m/s -> interpolated percent_per_time_base = 1.5
        # time 60s -> consumption == 1.5
        self.assertAlmostEqual(self.fc.get_fuel_consumption(60000, 450), 1.5)

    def test_time_scaling(self):
        # half the time_base => half consumption
        self.assertAlmostEqual(self.fc.get_fuel_consumption(30000, 150), 0.5)

    def test_zero_and_negative_time(self):
        self.assertEqual(self.fc.get_fuel_consumption(0, 100), 0.0)
        self.assertEqual(self.fc.get_fuel_consumption(-100, 100), 0.0)

    def test_clamping_out_of_range(self):
        # distance 0 -> avg speed 0 -> uses first curve point
        self.assertAlmostEqual(self.fc.get_fuel_consumption(60000, 0), 0.5)
        # very high speed -> clamps to last curve point (2.0 per base)
        self.assertAlmostEqual(self.fc.get_fuel_consumption(60000, 20 * 60), 2.0)


if __name__ == "__main__":
    unittest.main()
