import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

# Define the TemperatureLogger node
class TemperatureLogger(Node):
    def __init__(self, filename: str):
        super().__init__("temperature_listener")
        self.sub = self.create_subscription(String, "/temperature", self.callback, 10)
        self.fout = open(filename, "w") # change to "a" if needed
        return

    def callback(self, temperature: Float32):
        self.get_logger().info(f"Temperature: {temperature}")
        self.fout.write(f"Temperature: {temperature}")
        return

def main(args=None):
    rclpy.init(args=args)

    logger = TemperatureLogger("log.txt")

    rclpy.spin(logger)

    logger.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
