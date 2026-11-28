"""Tests for the local mapping parser; no Minecraft downloads are needed."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'audit_vanilla_boat.py'
spec = importlib.util.spec_from_file_location('vanilla_boat_audit', MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MappingTests(unittest.TestCase):
    def test_obfuscated_methods_and_overloads(self):
        sample = '''net.minecraft.world.entity.vehicle.AbstractBoat -> cqv:
    boolean inputLeft -> az
    1:2:void controlBoat() -> Q
    3:4:void clampRotation(net.minecraft.world.entity.Entity) -> c
    5:6:void tick() -> l
    7:8:void tick(int) -> m
net.minecraft.client.player.LocalPlayer -> geb:
    1:2:void rideTick() -> r
net.minecraft.world.entity.Entity -> bum:
    1:2:void addPassenger(net.minecraft.world.entity.Entity) -> h
not.used.Class -> q:
    1:2:void tick() -> z
'''
        classes, methods = audit.parse_mappings(sample)
        self.assertEqual(classes['net.minecraft.world.entity.vehicle.AbstractBoat'], 'cqv')
        self.assertEqual(methods['net.minecraft.world.entity.vehicle.AbstractBoat']['tick'], {'l', 'm'})
        self.assertEqual(methods['net.minecraft.world.entity.vehicle.AbstractBoat']['controlBoat'], {'Q'})
        self.assertEqual(methods['net.minecraft.client.player.LocalPlayer']['rideTick'], {'r'})
        self.assertEqual(methods['net.minecraft.world.entity.Entity']['addPassenger'], {'h'})

    def test_empty_mapping_reports_no_classes(self):
        self.assertEqual(audit.parse_mappings('other.Class -> a:\n'), ({}, {}))


if __name__ == '__main__':
    unittest.main()
