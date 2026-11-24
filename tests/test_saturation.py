import os
import shutil
import tempfile
import unittest

from streamhdr import saturation


def parse(text):
    lines = text.strip().splitlines()
    size = int(lines[1].split()[1])
    rows = [[float(v) for v in line.split()] for line in lines[2:]]
    return size, rows


class LutTests(unittest.TestCase):
    def test_header_and_size(self):
        text = saturation.lut_text(1.0)
        self.assertIn("LUT_3D_SIZE 17", text)
        size, rows = parse(text)
        self.assertEqual(size, 17)
        self.assertEqual(len(rows), 17 ** 3)

    def test_identity_lut_matches_grid(self):
        size, rows = parse(saturation.lut_text(1.0))
        worst = 0.0
        for blue in range(size):
            for green in range(size):
                for red in range(size):
                    row = rows[(blue * size + green) * size + red]
                    for got, want in zip(row, (red / 16, green / 16, blue / 16)):
                        worst = max(worst, abs(got - want))
        self.assertLess(worst, 1e-5)

    def test_zero_saturation_is_gray(self):
        _, rows = parse(saturation.lut_text(0.0))
        for row in rows:
            self.assertAlmostEqual(row[0], row[1], places=5)
            self.assertAlmostEqual(row[1], row[2], places=5)

    def test_gray_axis_is_unchanged_at_any_saturation(self):
        size, rows = parse(saturation.lut_text(1.5))
        for index in range(size):
            row = rows[(index * size + index) * size + index]
            for value in row:
                self.assertAlmostEqual(value, index / 16, places=4)

    def test_boost_keeps_luminance_and_increases_chroma(self):
        # A mildly colored cell (9, 8, 7): boosting it does not push any channel below zero,
        # so luminance must be unchanged. Strongly colored cells clip at zero by design.
        size, base = parse(saturation.lut_text(1.0))
        _, boosted = parse(saturation.lut_text(1.5))
        position = (7 * size + 8) * size + 9
        before, after = base[position], boosted[position]
        nits_before = [saturation.decode_pq(v) for v in before]
        nits_after = [saturation.decode_pq(v) for v in after]
        luma = lambda rgb: sum(w * c for w, c in zip(saturation.BT2020_LUMA, rgb))
        self.assertAlmostEqual(luma(nits_after) / luma(nits_before), 1.0, places=3)
        self.assertGreater(max(after) - min(after), max(before) - min(before))

    def test_values_stay_in_range_at_maximum(self):
        _, rows = parse(saturation.lut_text(2.0))
        for row in rows:
            for value in row:
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)


class PercentTests(unittest.TestCase):
    def test_clamp_snaps_and_limits(self):
        self.assertEqual(saturation.clamp_percent(100), 100)
        self.assertEqual(saturation.clamp_percent(102), 100)
        self.assertEqual(saturation.clamp_percent(103), 105)
        self.assertEqual(saturation.clamp_percent(108), 110)
        self.assertEqual(saturation.clamp_percent(145), 145)
        self.assertEqual(saturation.clamp_percent(-50), 0)
        self.assertEqual(saturation.clamp_percent(999), 200)

    def test_factor(self):
        self.assertEqual(saturation.percent_to_factor(150), 1.5)

    def test_filename_has_one_file_per_value(self):
        self.assertEqual(saturation.lut_filename(150), "look_pq_sat150.cube")
        self.assertNotEqual(saturation.lut_filename(140), saturation.lut_filename(150))


class EnsureLutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_creates_and_reuses_file(self):
        path = saturation.ensure_lut(os.path.join(self.tmp, "luts"), 150)
        self.assertTrue(os.path.isfile(path))
        mtime = os.path.getmtime(path)
        self.assertEqual(saturation.ensure_lut(os.path.join(self.tmp, "luts"), 150), path)
        self.assertEqual(os.path.getmtime(path), mtime)
        self.assertFalse(os.path.exists(path + ".tmp"))


if __name__ == "__main__":
    unittest.main()
