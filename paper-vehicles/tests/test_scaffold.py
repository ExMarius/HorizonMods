"""Offline checks; they do not replace a Paper build or in-game tests."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper-vehicles'

class PaperScaffold(unittest.TestCase):
    def test_catalog_points_to_existing_horizon_models(self):
        source = (PAPER / 'src/main/java/ro/exmarius/horizonvehicles/VehicleCatalog.java').read_text()
        entries = re.findall(r'new Entry\("([a-z_]+)", "[^"]+", "([a-z_]+)"\)', source)
        self.assertEqual(len(entries), 14)
        self.assertEqual(len({key for key, _ in entries}), len(entries))
        self.assertNotIn('dacia_logan_police', {key for key, _ in entries})
        for _, model in entries:
            self.assertTrue((ROOT / f'content/assets/gokart/models/block/{model}.json').is_file(), model)

    def test_city_bus_staged_with_its_own_mit_license(self):
        staged = PAPER / 'asset-src/city_bus'
        original = ROOT / 'third_party/city_vehicles'
        for name in ('bus.obj', 'bus_wheel.obj', 'yellow_bus.png', 'bus_wheel.png', 'LICENSE'):
            self.assertEqual((staged / name).read_bytes(), (original / name).read_bytes())
        self.assertIn('Permission is hereby granted', (staged / 'LICENSE').read_text())

    def test_reference_is_not_a_build_source_or_resource_pack(self):
        reference = ROOT / 'third_party/paper_vehicle_reference'
        self.assertTrue((reference / 'LICENSE').is_file())
        self.assertTrue((reference / 'java/com/mrcrayfish/vehicle/paper/render/LandVehicleRig.java').is_file())
        gradle = (PAPER / 'build.gradle.kts').read_text()
        self.assertNotIn('paper_vehicle_reference', gradle)
        self.assertFalse(list(reference.rglob('*.png')))
        self.assertFalse(list(reference.rglob('*.ogg')))
        plugin = (PAPER / 'src/main/resources/plugin.yml').read_text()
        self.assertIn('hvehicle:', plugin)
        self.assertNotIn('  vehicle:', plugin)
        self.assertIn('aliases: [vehicle, vehicel]', plugin)

class ModelAudit(unittest.TestCase):
    def test_source_mesh_inventory_and_original_bus_layout(self):
        import importlib.util
        import json
        spec = importlib.util.spec_from_file_location('audit_bus_mesh', PAPER / 'tools/audit_bus_mesh.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = PAPER / 'asset-src/city_bus'
        report = module.analyze(source / 'bus.obj')
        self.assertEqual(report['faces'], 379)
        self.assertEqual(report['rectangular_quads'], 337)
        self.assertEqual(report['other_quads'], 10)
        self.assertEqual(report['degenerate_quads'], 32)
        frame = json.loads((source / 'yellow_bus_frame.json').read_text())['display']
        self.assertEqual(len(frame['wheels']), 6)
        self.assertEqual(len(frame['passenger_seats']), 13)
        self.assertEqual(frame['driver_seat'], [12, 12, 58])

    def test_catalog_audit_reports_real_conversion_blockers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('audit_models', PAPER / 'tools/audit_models.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        results = {row['vehicle']: row for row in module.audit()}
        self.assertEqual(len(results), 14)
        self.assertEqual(results['city_bus']['loader'], 'neoforge:obj')
        self.assertTrue(results['go_kart']['unsupported_angles'])
        self.assertTrue(all(not row['missing_textures'] for row in results.values()))

if __name__ == '__main__':
    unittest.main()
