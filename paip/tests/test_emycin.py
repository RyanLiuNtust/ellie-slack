import unittest
from paip.emycin import *

class CFTests(unittest.TestCase):
    def test_cf_or(self):
        cases = [
            (0.6,   0.4,   0.76),
            (-0.3, -0.75, -0.825),
            (0.3,  -0.4,  -1.0/7.0),
            (-0.4,  0.3,  -1.0/7.0),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, cf_or(a, b))

    def test_cf_and(self):
        cases = [
            (0.6,   0.4,  0.4), 
            (-0.3, -0.75, -0.75),
            (0.3,  -0.4,  -0.4),
            (-0.4,  0.3,  -0.4),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, cf_and(a, b))

    def test_is_cf(self):
        cases = [
            (-0.7, True),
            (0.0, True),
            (0.999, True),
            (1.001, False),
            (-3, False),
        ]
        for a, b in cases:
            self.assertEqual(b, is_cf(a))

    def test_cf_true(self):
        cases = [
            (-3,    False),
            (-0.85,  False),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, True),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, cf_true(a))

    def test_cf_false(self):
        cases = [
            (-3,    False),
            (-0.85,  True),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, False),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, cf_false(a))


class DBTests(unittest.TestCase):
    def setUp(self):
        self.db = {
            ('age', 'patient'): [(25, 0.7), (24, 0.2)],
            ('age', 'patient_wife'): [(24, CF.true)],
            ('smokes', 'patient'): [(False, CF.false)],
            ('precip', 'weather'): [('raining', -0.4),
                                    ('snowing', CF.false),
                                    ('none', 0.6)],
        }

    def test_get_vals(self):
        vals = get_vals(self.db, 'age', 'patient_wife')
        self.assertEqual([(24, CF.true)], vals)

    def test_get_vals_empty(self):
        vals = get_vals(self.db, 'smokes', 'patient_wife')
        self.assertEqual([], vals)

    def test_get_cf(self):
        cf = get_cf(self.db, 'precip', 'weather', 'none')
        self.assertEqual(0.6, cf)

    def test_get_cf_no_key(self):
        cf = get_cf(self.db, 'precip', 'tomorrow', 'snowing')
        self.assertEqual(CF.unknown, cf)

    def test_get_cf_no_val(self):
        cf = get_cf(self.db, 'precip', 'weather', 'sleeting')
        self.assertEqual(CF.unknown, cf)
                         

    def test_update_cf(self):
        update_cf(self.db, 'precip', 'weather', 'raining', 0.1)
        cf = get_cf(self.db, 'precip', 'weather', 'raining')
        self.assertAlmostEqual(-1.0/3.0, cf)

    def test_update_cf_no_key(self):
        update_cf(self.db, 'precip', 'tomorrow', 'rain', CF.true)
        cf = get_cf(self.db, 'precip', 'tomorrow', 'rain')
        self.assertAlmostEqual(CF.true, cf)

    def test_update_cf_no_val(self):
        update_cf(self.db, 'precip', 'weather', 'sleeting', CF.false)
        cf = get_cf(self.db, 'precip', 'weather', 'sleeting')
        self.assertAlmostEqual(CF.false, cf)


class ParseReplyTests(unittest.TestCase):
    def test_parse_reply_none(self):
        reply = ''
        self.assertEqual(None, parse_reply(reply))

    def test_parse_definite(self):
        reply = 'blue'
        self.assertEqual([(reply, CF.true)], parse_reply(reply))

    def test_parse_single(self):
        reply = 'blue .5'
        self.assertEqual([('blue', 0.5)], parse_reply(reply))
    
    def test_parse_multiple(self):
        reply = 'blue .5, red .4, green -.3'
        self.assertEqual([('blue', 0.5),
                          ('red', 0.4),
                          ('green', -0.3)], parse_reply(reply))

