# -*- coding: utf-8 -*-
"""Testes da detecção automática de zona UTM SIRGAS 2000."""
import unittest

from pbzpa_qgis.core.utm_utils import utm_zone_from_lonlat


class TestUTMZone(unittest.TestCase):
    def test_sao_paulo(self):
        # SBGR (Aeroporto de Guarulhos): -46.469, -23.435 → zona 23S → EPSG 31983
        z = utm_zone_from_lonlat(-46.469, -23.435)
        self.assertEqual(z.zone_number, 23)
        self.assertEqual(z.hemisphere, "S")
        self.assertEqual(z.epsg, 31983)

    def test_rio_de_janeiro(self):
        # SBGL: -43.243, -22.808 → zona 23S
        z = utm_zone_from_lonlat(-43.243, -22.808)
        self.assertEqual(z.zone_number, 23)
        self.assertEqual(z.hemisphere, "S")
        self.assertEqual(z.epsg, 31983)

    def test_manaus(self):
        # SBEG: -60.05, -3.04 → zona 20S
        z = utm_zone_from_lonlat(-60.05, -3.04)
        self.assertEqual(z.zone_number, 20)
        self.assertEqual(z.hemisphere, "S")
        self.assertEqual(z.epsg, 31980)

    def test_boa_vista_norte(self):
        # SBBV (Boa Vista, RR): -60.69, +2.84 → zona 20N
        z = utm_zone_from_lonlat(-60.69, 2.84)
        self.assertEqual(z.zone_number, 20)
        self.assertEqual(z.hemisphere, "N")
        self.assertEqual(z.epsg, 31974)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            utm_zone_from_lonlat(200.0, 0.0)


if __name__ == "__main__":
    unittest.main()
