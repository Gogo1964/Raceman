from typing import List, Tuple


class FuelConsumption:
	"""Calculate fuel consumption from an ordered consumption curve.

	Args:
		time_base: reference time in seconds that the curve's consumption values correspond to.
		consumption_curve: list of (speed_m_s, percent_per_time_base) pairs ordered by speed (ascending).
	"""

	def __init__(self, time_base: float, consumption_curve: List[Tuple[float, float]]):
		if time_base <= 0:
			raise ValueError("time_base must be positive (seconds)")
		if not consumption_curve:
			raise ValueError("consumption_curve must not be empty")

		# Ensure curve is sorted by speed
		self.time_base = float(time_base)
		self.curve = sorted([(float(s), float(c)) for s, c in consumption_curve], key=lambda x: x[0])

	def _interp_consumption_at_speed(self, speed_m_s: float) -> float:
		"""Return interpolated consumption (percent per time_base) for given speed (m/s).

		If speed is outside the provided range, the endpoint value is used (clamped).
		"""
		# clamp to endpoints if outside range
		if speed_m_s <= self.curve[0][0]:
			return self.curve[0][1]
		if speed_m_s >= self.curve[-1][0]:
			return self.curve[-1][1]

		# find interval
		for i in range(1, len(self.curve)):
			s0, c0 = self.curve[i - 1]
			s1, c1 = self.curve[i]
			if s0 <= speed_m_s <= s1:
				# linear interpolation
				if s1 == s0:
					return (c0 + c1) / 2.0
				t = (speed_m_s - s0) / (s1 - s0)
				return c0 + t * (c1 - c0)

		# fallback (should not reach)
		return self.curve[-1][1]

	def get_fuel_consumption(self, time_ms: float, distance_m: float) -> float:
		"""Calculate percentage of full tank used over given time and distance.

		Args:
			time_ms: time interval in milliseconds.
			distance_m: distance traveled during the interval in meters.

		Returns:
			Percentage of the full tank consumed (float). Can be zero or positive.
		"""
		if time_ms <= 0:
			return 0.0

		time_s = float(time_ms) / 1000.0
		# compute average speed (m/s)
		avg_speed = distance_m / time_s if time_s > 0 else 0.0

		# get interpolated consumption for the reference time_base
		percent_per_time_base = self._interp_consumption_at_speed(avg_speed)

		# scale consumption by the ratio of actual time to time_base
		consumption = (time_s / self.time_base) * percent_per_time_base

		# do not return negative values
		return max(0.0, consumption)
