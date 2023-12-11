import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from std_msgs.msg import UInt8
from sensor_msgs.msg import Joy

print('\033[1m\033[31m'+'赤色'+'\033[0m')

class MinimalSubscriber(Node):
    state = 1

    distance = 0
    angle = 999

    motor1_speed = 0
    motor2_speed = 0

    button_start = 0
    button_back = 0
    button_forward = 0
    button_manual_control = 0
    button_auto_pilot = 0

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.publisher_Drive_Controller_Node = self.create_publisher(Int16MultiArray, 'Drive_Controller_Node', 10)
        self.publisher_state = self.create_publisher(UInt8, 'state', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.listener_callback_joy,
            10)
        self.subscription = self.create_subscription(
            Int16MultiArray,
            'state_sensor',
            self.listener_callback_state_sensor,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.001  # seconds 0.01
        # 0.001でも試す！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def listener_callback_joy(self, joy):
        # buttons[10] ホームボタン スタートボタン
        # 8 戻るボタン
        # 9 進むボタン
        # 4 L 手動操縦
        # 5 R 自動操縦

        msg = Int16MultiArray()
        msg.data = [int(joy.axes[1]*256),int(joy.axes[3]*256)]

        msg.data = [int(joy.axes[1]*256),int(joy.axes[3]*256),int(joy.axes[0]*256),int(joy.axes[2]*256)]
        self.publisher_Drive_Controller_Node.publish(msg)

    KP = 1;  # Pゲイン
    KD = 0;   # Dゲイン
    KI = 0;   # Iゲイン
    T  = 0.001;# 制御周期[秒]
    e_pre = 0; # 微分の近似計算のための初期値
    ie = 0;    # 積分の近似計算のための初期値

    def listener_callback_state_sensor(self, msg):
        pub_msg = UInt8()
        self.state = msg.data[0]
        self.distance = msg.data[1]
        self.angle = msg.data[2]
        if self.state == 1:
            # 開始待ちホームボタンを監視
            # 距離の初期位置は-90°
            button押されたら = True
        elif self.state == 2:
            # 消防署からエリア1に前進中
            # 距離監視しながら前進
            self.motor1_speed = 255
            self.motor2_speed = 255
        elif self.state == 3:
            # エリア1で右旋回中
            # 0°になるまで右旋回
            if self.angle == 0:
                pub_msg.data = self.state+1
                self.publisher_state.publish(msg)
            else:
                y = self.angle            # 出力を取得。例:センサー情報を読み取る処理
                r = 0                     # 目標値を取得。目標値が一定ならその値を代入する
                e  = r - y                # 誤差を計算
                de = (e - e_pre)/self.T        # 誤差の微分を近似計算
                ie = ie + (e + e_pre)*self.T/2 # 誤差の積分を近似計算
                u  = self.KP*e + self.KI*ie + self.KD*de # PID制御の式にそれぞれを代入
                e_pre = e

                self.motor1_speed = u*255
                self.motor2_speed = u*255 * -1




def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()