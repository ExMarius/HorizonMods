import unittest
from recovery_log_check import find_failures


class RecoveryLogCheckTest(unittest.TestCase):
    def test_plugin_stack_trace_detected(self):
        self.assertTrue(find_failures('[12:00:00 ERROR]: Event failed\njava.lang.IllegalStateException: test\n\tat com.mrcrayfish.vehicle.paper.Test.run(Test.java:1)\n'))

    def test_plugin_error_and_probe_marker_detected(self):
        self.assertTrue(find_failures('[12:00:00 ERROR]: [MrCrayfishVehiclePlugin] Save failed'))
        self.assertTrue(find_failures('[12:00:00 INFO]: RECOVERY_PROBE_FAIL'))

    def test_unrelated_exception_not_misattributed_to_next_record(self):
        self.assertFalse(find_failures('[12:00:00 ERROR]: java.io.IOException: unrelated\n\tat other.Foo.run(Foo.java:1)\n[12:00:01 INFO]: [RecoveryProbe] Enabled'))


if __name__ == '__main__':
    unittest.main()
