import socket

"""
HEIGHT SENSING SUBSYSTEM
------------------------

The Height Sensing Subsystem (HSS) is a sytem that receives data from a laser altimeter that is
placed vertically beneath the lander spacecraft.  The purpose on this system is to extract the
height of the spacecraft and once the height has achieved a landing event it will transmit a
ENGINE_CUTOFF message to all other subsystems. The subsystem has also been designed to warn the
user if there are any faulty sensors or if there was a possible crash.  
"""


class HeightSensingSubsystem:
    """
    Main Class for the Height Sensing Subsystem.

    Attributes
    ----------
    host : string
        The host IP address.
    port : int
        HSS port
    bus_router_port : integer
        The message bus router port between subsystems and lander spacecraft.
    socket : socket
        Creating a UDP datagram socket. Where socket.bind will bind to all interfaces.
    message_type : Dictionary
        The message that will be sent through the bus router.

    Methods
    -------
    initialize()
        Initialize the class by creating a UDP socket and binding it to all interfaces.
    get_int_from_bytes()
        Converts Network bytes (big-endian) to integers.
    convert_to_cm()
        Converts telemetry data of lander spacecraft into centimeters.
    get_sensor_height()
        Obtains the height of a single sensor data.
    get_all_sensors_height()
        Obtains all three sensors height data.
    check_sensor_status()
        Checks the status of the sensors if, one, two or all sensors are down.
    get_current_space_craft_height()
        Gets the average height between all sensors.
    get_telemetry_data()
        Receives telemetry data.
    send_engine_cutoff_message()
        Sends ENGINE_CUTOFF message to all subsystems.
    send_lander_height()
        Sends the height of spacecraft after ENGINE_CUTOFF message.
    close_subsystem()
        Closes communication of the HSS.
    """

    def __init__(self, HOST="0.0.0.0", PORT=12778, BUS_ROUTER_PORT=12777):
        self.host = HOST
        self.port = PORT
        self.bus_router_port = BUS_ROUTER_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.message_type = {"ENGINE_CUTOFF": b"\xaa\x11", "HEIGHT": b"\xaa\x31"}

    def get_int_from_bytes(self, byte_data):
        return int.from_bytes(byte_data, "big")

    def convert_to_cm(self, int_data):
        return 100000 * (int_data / 65535)

    def get_sensor_height(self, sensor_data):
        sensor_height = self.convert_to_cm(self.get_int_from_bytes(sensor_data))
        return sensor_height

    def get_all_sensors_height(self, payload_data):
        """
        Gets the height of all sensors from laser altimeter.

        Parameters
        ----------
        payload_data : 0-4096 bytes

        Returns
        -------
        An int list with height of all sensors.
        """
        sensor_1_height = self.get_sensor_height(payload_data[0:2])
        sensor_2_height = self.get_sensor_height(payload_data[2:4])
        sensor_3_height = self.get_sensor_height(payload_data[4:6])
        return [sensor_1_height, sensor_2_height, sensor_3_height]

    def get_current_space_craft_height(self, laser_altimeter_data):
        """
        Gets the average height between all three sensors assuming.

        Assumptions
        -----------
        All three sensors are working.

        Parameters
        ----------
        laser_altimeter_data : int list
            A list of the height measurement of all sensors.

        Returns
        -------
        The current height of lander spacecraft.
        """
        return sum(laser_altimeter_data) / len(laser_altimeter_data)

    def check_sensor_status(self, laser_altimeter_data):
        """
        Check the status of each sensors and return a message if any sensors has malfunction.

        Parameters
        ----------
        laser_altimeter_data : int list
            A list of the height measurement of all sensors.

        Returns
        -------
        A print message if any sensors are faulty.
        """
        faulty_sensor = {}
        for i in range(len(laser_altimeter_data)):
            if laser_altimeter_data[i] == None:
                faulty_sensor[i] = i + 1
            elif laser_altimeter_data[i] < 5 or laser_altimeter_data[i] > 100000:
                faulty_sensor[i] = i + 1

        if len(faulty_sensor) > 0 and len(faulty_sensor) < 3:
            return f"There are {len(faulty_sensor)} sensor malfunctions ---> Sensor(s) not working: {faulty_sensor.values()}"

        if len(faulty_sensor) == 3:
            return "All sensors are down! Space craft either crashed or something went wrong with sensor communication."

    def get_telemetry_data(self, max_bytes):
        """
        Receive telemetry data and extract the message type, time, and the message payload.

        Parameters
        ----------
        max_bytes : int
            The maximum allowed bytes to receive from server system.

        Returns
        -------
        The message type, elapse time of spacecraft, payload of data.

        type_ : int
        time_ : int
        payload_ : byte.
        """
        data = self.socket.recv(max_bytes)
        type_ = self.get_int_from_bytes(data[:2])
        time_ = self.get_int_from_bytes(data[2:6])
        payload_ = data[6:]
        return type_, time_, payload_

    def send_engine_cutoff_message(self):
        """Transmits ENGINE_CUTOFF message to all subsytems"""
        self.socket.sendto(
            self.message_type["ENGINE_CUTOFF"], (self.host, self.bus_router_port)
        )

    def send_lander_height(self, spacecraft_current_height, time_):
        """Trasnmits Spacecraft height to all subsystems"""
        height_to_bytes = (int(spacecraft_current_height)).to_bytes(2, byteorder="big")
        time_to_bytes = (int(time_)).to_bytes(4, byteorder="big")
        lander_height_message = [
            self.message_type["HEIGHT"],
            time_to_bytes,
            height_to_bytes,
        ]
        lander_height_message_bytes = b"".join(lander_height_message)
        self.socket.sendto(
            lander_height_message_bytes, (self.host, self.bus_router_port)
        )

    def close_subsystem(self):
        self.socket.close()


if __name__ == "__main__":

    loop = True
    laser_altimeter_type = int.from_bytes(
        b"\xaa\x01", "big"
    )  # LASER_ALTIMETER  : 0xAA01

    # Initialize HSS class
    hss = HeightSensingSubsystem()

    while loop:

        type_, time_, payload_ = hss.get_telemetry_data(4102)

        if type_ == laser_altimeter_type:

            laser_altimeter_data = hss.get_all_sensors_height(payload_)
            hss.check_sensor_status(laser_altimeter_data)
            spacecraft_current_height = hss.get_current_space_craft_height(
                laser_altimeter_data
            )

            if (
                laser_altimeter_data[0] <= 40
                or laser_altimeter_data[1] <= 40
                or laser_altimeter_data[2] <= 40
            ):
                print("Initiate Engine cut-off")
                print("\nTrasnmitting Engine cut-off message to subsytems")
                hss.send_engine_cutoff_message()
                print("\nMessage Received.")
                loop = False
            else:
                print(
                    "Curent height of Spacecraft: {:.2f}(cm)".format(
                        spacecraft_current_height
                    )
                )
                hss.send_lander_height(spacecraft_current_height, time_)

    print("Closing Communication")
    hss.close_subsystem()
