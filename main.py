import socket
import math
import time

from evdev import UInput, ecodes


# ============================================================
# SETTINGS
# ============================================================

UDP_PORT = 4210

DEAD_ZONE = 5.0

MAX_ANGLE = 45.0

MAX_SPEED = 25

UPDATE_TIME = 0.01


# ============================================================
# UDP SOCKET
# ============================================================

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind(
    ("0.0.0.0", UDP_PORT)
)

sock.setblocking(False)


# ============================================================
# VIRTUAL MOUSE
# ============================================================

capabilities = {

    ecodes.EV_REL: [
        ecodes.REL_X,
        ecodes.REL_Y
    ],

    ecodes.EV_KEY: [
        ecodes.BTN_LEFT
    ]
}


mouse = UInput(
    capabilities,
    name="MPU-6500 Tilt Mouse"
)


# ============================================================
# ANGLE TO SPEED
# ============================================================

def angle_to_speed(angle):

    absolute_angle = abs(angle)

    if absolute_angle <= DEAD_ZONE:
        return 0

    effective_angle = absolute_angle - DEAD_ZONE

    effective_max = MAX_ANGLE - DEAD_ZONE

    normalized = effective_angle / effective_max

    normalized = max(
        0.0,
        min(1.0, normalized)
    )

    speed = (
        normalized ** 1.5
    ) * MAX_SPEED

    if speed < 1:
        speed = 1

    return int(speed)


# ============================================================
# MAIN
# ============================================================

print()
print("======================================")
print("       MPU-6500 TILT MOUSE")
print("======================================")
print()
print("UDP port:", UDP_PORT)
print()
print("X axis : LEFT / RIGHT")
print("Y axis : UP / DOWN")
print()
print("Button 1 : LEFT CLICK")
print("Button 2 : RESERVED")
print()
print("Press CTRL+C to stop.")
print()


latest_data = None

# Button state remembered by Python
previous_button1 = 0


try:

    while True:

        # ====================================================
        # RECEIVE UDP
        # ====================================================

        while True:

            try:

                data, address = sock.recvfrom(1024)

                latest_data = data.decode().strip()

            except BlockingIOError:

                break


        # ====================================================
        # PROCESS DATA
        # ====================================================

        if latest_data is not None:

            try:

                values = list(
                    map(
                        int,
                        latest_data.split(",")
                    )
                )


                # Make sure packet contains
                # AX, AY, AZ, BUTTON1, BUTTON2

                if len(values) >= 5:

                    ax = values[0]
                    ay = values[1]
                    az = values[2]

                    button1 = values[3]
                    button2 = values[4]


                    # =========================================
                    # CALCULATE X ANGLE
                    # =========================================

                    x_angle = math.degrees(
                        math.atan2(
                            ax,
                            math.sqrt(
                                ay * ay +
                                az * az
                            )
                        )
                    )


                    # =========================================
                    # CALCULATE Y ANGLE
                    # =========================================

                    y_angle = math.degrees(
                        math.atan2(
                            ay,
                            math.sqrt(
                                ax * ax +
                                az * az
                            )
                        )
                    )


                    # =========================================
                    # MOUSE SPEED
                    # =========================================

                    x_speed = angle_to_speed(
                        x_angle
                    )

                    y_speed = angle_to_speed(
                        y_angle
                    )


                    mouse_x = 0
                    mouse_y = 0


                    # =========================================
                    # X AXIS
                    #
                    # IMPORTANT:
                    #
                    # We are reversing X here.
                    #
                    # Your physical LEFT
                    # was previously moving RIGHT.
                    #
                    # =========================================

                    if x_angle > DEAD_ZONE:

                        # Physical LEFT
                        mouse_x = -x_speed

                    elif x_angle < -DEAD_ZONE:

                        # Physical RIGHT
                        mouse_x = x_speed


                    # =========================================
                    # Y AXIS
                    # =========================================

                    if y_angle > DEAD_ZONE:

                        # UP
                        mouse_y = -y_speed

                    elif y_angle < -DEAD_ZONE:

                        # DOWN
                        mouse_y = y_speed


                    # =========================================
                    # MOVE MOUSE
                    # =========================================

                    if mouse_x != 0:

                        mouse.write(
                            ecodes.EV_REL,
                            ecodes.REL_X,
                            mouse_x
                        )


                    if mouse_y != 0:

                        mouse.write(
                            ecodes.EV_REL,
                            ecodes.REL_Y,
                            mouse_y
                        )


                    # =========================================
                    # BUTTON 1
                    #
                    # Physical button -> LEFT CLICK
                    # =========================================

                    if button1 != previous_button1:

                        if button1 == 1:

                            # Button pressed
                            mouse.write(
                                ecodes.EV_KEY,
                                ecodes.BTN_LEFT,
                                1
                            )

                        else:

                            # Button released
                            mouse.write(
                                ecodes.EV_KEY,
                                ecodes.BTN_LEFT,
                                0
                            )

                        mouse.syn()

                        previous_button1 = button1


                    # =========================================
                    # BUTTON 2
                    #
                    # RESERVED FOR YOUR USE CASE
                    # =========================================

                    if button2 == 1:

                        pass


                    # =========================================
                    # SEND MOUSE EVENTS
                    # =========================================

                    mouse.syn()


            except (ValueError, IndexError):

                pass


        time.sleep(UPDATE_TIME)


except KeyboardInterrupt:

    print()
    print("Stopping MPU-6500 mouse...")


finally:

    mouse.close()

    sock.close()

    print("Mouse controller stopped.")