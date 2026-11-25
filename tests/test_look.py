import os
import shutil
import tempfile
import unittest

from streamhdr import look
from streamhdr.look import Look

NEUTRAL = Look(100, 100, 100, 200)


def parse(text):
    lines = text.strip().splitlines()
    size = int(lines[1].split()[1])
    rows = [[float(v) for v in line.split()] for line in lines[2:]]
    return size, rows


def cell(rows, size, red, green, blue):
    return rows[(blue * size + green) * size + red]


class LutTests(unittest.TestCase):
    def test_header_and_size(self):
        text = look.lut_text(1.0)
        self.assertIn("LUT_3D_SIZE 17", text)
        size, rows = parse(text)
        self.assertEqual(size, 17)
        self.assertEqual(len(rows), 17 ** 3)

    def test_identity_lut_matches_grid(self):
        size, rows = parse(look.lut_text(1.0))
        worst = 0.0
        for blue in range(size):
            for green in range(size):
                for red in range(size):
                    got = cell(rows, size, red, green, blue)
                    for value, want in zip(got, (red / 16, green / 16, blue / 16)):
                        worst = max(worst, abs(value - want))
        self.assertLess(worst, 1e-5)

    def test_zero_saturation_is_gray(self):
        _, rows = parse(look.lut_text(0.0))
        for row in rows:
            self.assertAlmostEqual(row[0], row[1], places=5)
            self.assertAlmostEqual(row[1], row[2], places=5)

    def test_gray_axis_is_unchanged_at_any_saturation(self):
        size, rows = parse(look.lut_text(1.5))
        for index in range(size):
            for value in cell(rows, size, index, index, index):
                self.assertAlmostEqual(value, index / 16, places=4)

    def test_boost_keeps_luminance_and_increases_chroma(self):
        # A mildly colored cell (9, 8, 7): boosting it does not push any channel below zero,
        # so luminance must be unchanged. Strongly colored cells clip at zero by design.
        size, base = parse(look.lut_text(1.0))
        _, boosted = parse(look.lut_text(1.5))
        before, after = cell(base, size, 9, 8, 7), cell(boosted, size, 9, 8, 7)
        luma = lambda rgb: look.luminance([look.decode_pq(v) for v in rgb])
        self.assertAlmostEqual(luma(after) / luma(before), 1.0, places=3)
        self.assertGreater(max(after) - min(after), max(before) - min(before))

    def test_values_stay_in_range_at_extremes(self):
        for kwargs in (
            dict(saturation=2.0, contrast=2.0, gamma=0.5),
            dict(saturation=2.0, contrast=0.0, gamma=2.0),
            dict(saturation=0.0, contrast=2.0, gamma=2.0),
        ):
            _, rows = parse(look.lut_text(**kwargs))
            for row in rows:
                for value in row:
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 1.0)


class ToneTests(unittest.TestCase):
    PIVOT = 200.0

    def test_neutral_values_change_nothing(self):
        for nits in (0.5, 50.0, 200.0, 1000.0):
            self.assertAlmostEqual(look.tone(nits, 1.0, 1.0, self.PIVOT), nits)

    def test_pivot_is_fixed_for_contrast_and_gamma(self):
        self.assertAlmostEqual(look.tone(self.PIVOT, 1.5, 1.0, self.PIVOT), self.PIVOT, places=3)
        self.assertAlmostEqual(look.tone(self.PIVOT, 1.0, 2.0, self.PIVOT), self.PIVOT, places=6)

    def test_contrast_darkens_below_and_brightens_above_the_pivot(self):
        self.assertLess(look.tone(50.0, 1.5, 1.0, self.PIVOT), 50.0)
        self.assertGreater(look.tone(800.0, 1.5, 1.0, self.PIVOT), 800.0)
        self.assertGreater(look.tone(50.0, 0.5, 1.0, self.PIVOT), 50.0)

    def test_zero_contrast_collapses_to_the_pivot(self):
        self.assertAlmostEqual(look.tone(30.0, 0.0, 1.0, self.PIVOT), self.PIVOT, places=2)

    def test_gamma_above_one_darkens_and_below_one_brightens_shadows(self):
        self.assertLess(look.tone(40.0, 1.0, 1.5, self.PIVOT), 40.0)
        self.assertGreater(look.tone(40.0, 1.0, 0.7, self.PIVOT), 40.0)

    def test_gamma_leaves_far_highlights_alone(self):
        self.assertAlmostEqual(look.tone(2000.0, 1.0, 2.0, self.PIVOT), 2000.0, places=3)

    def test_gamma_keeps_black_and_order(self):
        self.assertEqual(look.tone(0.0, 1.0, 2.0, self.PIVOT), 0.0)
        for gamma in (0.5, 1.5, 2.0):
            values = [look.tone(n, 1.0, gamma, self.PIVOT) for n in (1, 10, 50, 150, 200, 300, 600, 1000, 3000)]
            self.assertEqual(values, sorted(values))

    def test_lut_keeps_hue_for_tone_changes(self):
        # A tone change scales all channels by the same factor, so channel ratios stay the same.
        size, base = parse(look.lut_text(1.0))
        _, dark = parse(look.lut_text(1.0, gamma=1.5))
        before = [look.decode_pq(v) for v in cell(base, size, 12, 9, 6)]
        after = [look.decode_pq(v) for v in cell(dark, size, 12, 9, 6)]
        self.assertAlmostEqual(after[0] / after[1], before[0] / before[1], places=2)
        self.assertAlmostEqual(after[2] / after[1], before[2] / before[1], places=2)


class ValueTests(unittest.TestCase):
    def test_snap_and_limits(self):
        self.assertEqual(look.clamp_saturation(148), 150)
        self.assertEqual(look.clamp_saturation(999), 200)
        self.assertEqual(look.clamp_contrast(-5), 0)
        self.assertEqual(look.clamp_contrast(102), 100)
        self.assertEqual(look.clamp_gamma(104), 100)
        self.assertEqual(look.clamp_gamma(30), 50)
        self.assertEqual(look.clamp_gamma(999), 200)

    def test_neutral(self):
        self.assertTrue(NEUTRAL.is_neutral)
        self.assertTrue(Look(100, 100, 100, 300).is_neutral)  # the pivot does not matter then
        self.assertFalse(Look(110, 100, 100, 200).is_neutral)
        self.assertFalse(Look(100, 95, 100, 200).is_neutral)
        self.assertFalse(Look(100, 100, 90, 200).is_neutral)

    def test_filename_has_one_file_per_setting(self):
        self.assertEqual(look.lut_filename(Look(150, 100, 100, 200)), "look_pq_s150_c100_g100_p200.cube")
        self.assertNotEqual(look.lut_filename(Look(140, 100, 100, 200)), look.lut_filename(Look(150, 100, 100, 200)))
        self.assertNotEqual(look.lut_filename(Look(100, 100, 90, 200)), look.lut_filename(NEUTRAL))


class EnsureLutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_creates_and_reuses_file(self):
        luts = os.path.join(self.tmp, "luts")
        setting = Look(150, 120, 90, 200)
        path = look.ensure_lut(luts, setting)
        self.assertTrue(os.path.isfile(path))
        mtime = os.path.getmtime(path)
        self.assertEqual(look.ensure_lut(luts, setting), path)
        self.assertEqual(os.path.getmtime(path), mtime)
        self.assertFalse(os.path.exists(path + ".tmp"))

    def test_prune_keeps_only_the_given_file(self):
        luts = os.path.join(self.tmp, "luts")
        first = look.ensure_lut(luts, Look(150, 100, 100, 200))
        second = look.ensure_lut(luts, Look(160, 100, 100, 200))
        look.prune(luts, second)
        self.assertFalse(os.path.exists(first))
        self.assertTrue(os.path.exists(second))


if __name__ == "__main__":
    unittest.main()
