import unittest
import warnings

from HSS import HeightSensingSubsystem

"""
Basic Unit test of most functions within the HSS class.  A CustomAssertion class was 
developed in order to avoid installing external libraries (ie. pytest).
"""


class CustomAssertions:
    def assert_approx_equals(self, pred_val_array, target_val, min_difference):
        for i in range(len(pred_val_array)):
            if (
                pred_val_array[i] > target_val + min_difference
                or pred_val_array[i] < target_val - min_difference
            ):
                raise AssertionError("Height Test Failed")

    def assert_sensor_status(self, pred_str, expected_str):
        if pred_str != expected_str:
            raise AssertionError("Check Sensor Status Test Failed")


class HSSTest(unittest.TestCase, CustomAssertions):
    def test_0_sensor_height(self):
        warnings.filterwarnings("ignore")
        height_ = (655).to_bytes(
            2, byteorder="big"
        )  # 655 is aprox 10 meters if you convert to int from bytes
        payload_data = [height_, height_, height_]
        simulated_data = b"".join(payload_data)
        hss = HeightSensingSubsystem()
        height_of_sensors = hss.get_all_sensors_height(simulated_data)
        self.assert_approx_equals(height_of_sensors, 1000, 15)

    def test_1_network_byte_to_cm(self):
        max_int = 2**16 - 1
        max_network_byte = (max_int).to_bytes(2, byteorder="big")
        hss = HeightSensingSubsystem()
        height_in_cm = hss.get_sensor_height(max_network_byte)
        assert 100000 == height_in_cm

    def test_2_bytes_to_int(self):
        max_int = 2**16 - 1
        max_network_byte = (max_int).to_bytes(2, byteorder="big")
        hss = HeightSensingSubsystem()
        integer = hss.get_int_from_bytes(max_network_byte)
        assert 65535 == integer

    def test_3_sensor_status(self):
        edge_cases = [
            [2, 0, 50],
            [1, 100, 1000000],
            [20, 1, 45],
            [50, None, None],
            [1, 1, 1],
        ]
        expected_str = [
            "There are 2 sensor malfunctions ---> Sensor(s) not working: dict_values([1, 2])",
            "There are 2 sensor malfunctions ---> Sensor(s) not working: dict_values([1, 3])",
            "There are 1 sensor malfunctions ---> Sensor(s) not working: dict_values([2])",
            "There are 2 sensor malfunctions ---> Sensor(s) not working: dict_values([2, 3])",
            "All sensors are down! Space craft either crashed or something went wrong with sensor communication.",
        ]
        hss = HeightSensingSubsystem()
        for i in range(len(edge_cases)):
            self.assert_sensor_status(
                expected_str[i], hss.check_sensor_status(edge_cases[i])
            )

    def test_4_space_craft_height(self):
        sensor_height = [15, 16, 17]
        hss = HeightSensingSubsystem()
        spacecraft_height = hss.get_current_space_craft_height(sensor_height)
        assert 16 == spacecraft_height


if __name__ == "__main__":
    unittest.main()
