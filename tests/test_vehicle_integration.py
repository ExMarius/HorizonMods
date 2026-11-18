"""Regression guards for native source packaging, not in-game tests."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NativeIntegration(unittest.TestCase):
    def test_glue_is_not_placeholder(self):
        glue = (ROOT / 'mixins/gokart_native/glue.rs').read_text()
        self.assertGreater(len(glue), 100_000)
        for name in ('fn spawn_kart(', 'fn entity_tick_pre(', 'fn position_rider('):
            self.assertIn(name, glue)
        self.assertNotIn('SEE_FILE_glue_final', glue)

    def test_step_height_applied_to_private_type_on_spawn_and_recovery(self):
        glue = (ROOT / 'mixins/gokart_native/glue.rs').read_text()
        self.assertIn('Tag::Double(base.to_bits())', glue)
        self.assertIn('Arc::make_mut(&mut m.kind).step_height = kind.layout().step_height', glue)
        self.assertIn('Arc::make_mut(&mut m.kind).step_height = step', glue)
        self.assertIn('lookup_kart_uuid(game, st, dimension, entity)', glue)


if __name__ == '__main__':
    unittest.main()
