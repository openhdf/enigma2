from __future__ import absolute_import
from math import sin, cos, radians, sqrt, degrees, atan, fabs, floor, asin

f = 1.00 / 298.257 # Earth flattning factor
r_sat = 42164.57 # Distance from earth centre to satellite
r_eq = 6378.14  # Earth radius


def calcElevation(SatLon, SiteLat, SiteLon, Height_over_ocean=0):
	a0 = 0.58804392
	a1 = -0.17941557
	a2 = 0.29906946E-1
	a3 = -0.25187400E-2
	a4 = 0.82622101E-4

	sinRadSiteLat = sin(radians(SiteLat))
	cosRadSiteLat = cos(radians(SiteLat))

	Rstation = r_eq / (sqrt(1.00 - f * (2.00 - f) * sinRadSiteLat ** 2))

	Ra = (Rstation + Height_over_ocean) * cosRadSiteLat
	Rz = Rstation * (1.00 - f) * (1.00 - f) * sinRadSiteLat

	alfa_rx = r_sat * cos(radians(SatLon - SiteLon)) - Ra
	alfa_ry = r_sat * sin(radians(SatLon - SiteLon))
	alfa_rz = -Rz

	alfa_r_north = -alfa_rx * sinRadSiteLat + alfa_rz * cosRadSiteLat
	alfa_r_zenith = alfa_rx * cosRadSiteLat + alfa_rz * sinRadSiteLat

	den = alfa_r_north ** 2 + alfa_ry ** 2
	if den > 0:
		El_geometric = degrees(atan(alfa_r_zenith / sqrt(den)))
	else:
		El_geometric = 90

	x = fabs(El_geometric + 0.589)
	refraction = fabs(a0 + (a1 + (a2 + (a3 + a4 * x) * x) * x) * x)

	if El_geometric > 10.2:
		El_observed = El_geometric + 0.01617 * (cos(radians(fabs(El_geometric))) / sin(radians(fabs(El_geometric))))
	else:
		El_observed = El_geometric + refraction

	if alfa_r_zenith < -3000:
		El_observed = -99

	return El_observed


def calcAzimuth(SatLon, SiteLat, SiteLon, Height_over_ocean=0):

	def rev(number):
		return number - floor(number / 360.0) * 360

	sinRadSiteLat = sin(radians(SiteLat))
	cosRadSiteLat = cos(radians(SiteLat))

	Rstation = r_eq / (sqrt(1 - f * (2 - f) * sinRadSiteLat ** 2))
	Ra = (Rstation + Height_over_ocean) * cosRadSiteLat
	Rz = Rstation * (1 - f) ** 2 * sinRadSiteLat

	alfa_rx = r_sat * cos(radians(SatLon - SiteLon)) - Ra
	alfa_ry = r_sat * sin(radians(SatLon - SiteLon))
	alfa_rz = -Rz

	alfa_r_north = -alfa_rx * sinRadSiteLat + alfa_rz * cosRadSiteLat

	if alfa_r_north < 0:
		Azimuth = 180 + degrees(atan(alfa_ry / alfa_r_north))
	elif alfa_r_north > 0:
		Azimuth = rev(360 + degrees(atan(alfa_ry / alfa_r_north)))
	else:
		Azimuth = 0
	return Azimuth


def calcDeclination(SiteLat, Azimuth, Elevation):
	return degrees(asin(sin(radians(Elevation)) *
								  sin(radians(SiteLat)) +
								  cos(radians(Elevation)) *
								  cos(radians(SiteLat)) +
								  cos(radians(Azimuth))
	))


def calcSatHourangle(SatLon, SiteLat, SiteLon):
	Azimuth = calcAzimuth(SatLon, SiteLat, SiteLon)
	Elevation = calcElevation(SatLon, SiteLat, SiteLon)

	a = - cos(radians(Elevation)) * sin(radians(Azimuth))
	b = sin(radians(Elevation)) * cos(radians(SiteLat)) - \
		cos(radians(Elevation)) * sin(radians(SiteLat)) * \
		cos(radians(Azimuth))

	# Works for all azimuths (northern & southern hemisphere)
	returnvalue = 180 + degrees(atan(a / b))

	if Azimuth > 270:
		returnvalue += 180
		if returnvalue > 360:
			returnvalue = 720 - returnvalue

	if Azimuth < 90:
		returnvalue = 180 - returnvalue

	return returnvalue
