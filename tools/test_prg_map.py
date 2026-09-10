import unittest
from extract_prg_overlays import segment_map, recipe_for


class SegmentMapTests(unittest.TestCase):
    def document(self):
        return {'sha1': 'not-matching', 'segments': [{'type': 'code', 'start': 0,
            'vram': 0x80068800, 'subsegments': [[0, '.rodata'], [16, 'c'], [32, 'asm'],
                                             {'start': 48, 'type': 'data'}]}, [64]]}

    def test_data_is_excluded_and_adjacent_code_merged(self):
        base, spans, entries = segment_map(self.document(), 64)
        self.assertEqual(spans, [(base+16, base+48)])
        self.assertEqual(entries, [base+16, base+32])

    def test_wrong_disc_rejected_before_address_use(self):
        with self.assertRaisesRegex(ValueError, 'SHA1'):
            recipe_for('sample', bytes(64), self.document())

    def test_bad_address_rejected(self):
        doc = self.document()
        doc['segments'][0]['vram'] = 0x801FFFF0
        with self.assertRaisesRegex(ValueError, 'RAM'):
            segment_map(doc, 64)

    def test_unaligned_code_rejected(self):
        doc = self.document()
        doc['segments'][0]['subsegments'][1][0] = 17
        with self.assertRaisesRegex(ValueError, 'Unaligned'):
            segment_map(doc, 64)


if __name__ == '__main__':
    unittest.main()
