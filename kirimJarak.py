#!/usr/bin/env python3

import asyncio
import json
import threading
import time

import websockets


class WebSocketRobot:

    def __init__(self):
        # =====================================================
        # KONFIGURASI ROBOT
        # =====================================================

        self.ROBOT_ID = 1

        # IP WebSocket SERVER
        self.WEBSOCKET_URI = "ws://192.168.97.106:8765"

        # =====================================================
        # JARAK ROBOT SENDIRI
        # =====================================================

        self.distance = 0.0

        # =====================================================
        # DATA ROBOT LAIN
        # =====================================================

        self.robot_data = {}

        # =====================================================
        # ASYNCIO
        # =====================================================

        self.loop = asyncio.new_event_loop()

        self.websocket_thread = threading.Thread(
            target=self.run_websocket,
            daemon=True
        )

        self.websocket_thread.start()

        print(
            f"[SYSTEM] WebSocket Robot {self.ROBOT_ID} started"
        )

    # =========================================================
    # SET JARAK ROBOT SENDIRI
    # =========================================================

    def set_distance(self, distance):

        self.distance = float(distance)

        print(
            f"[DISTANCE] Robot {self.ROBOT_ID} = "
            f"{self.distance:.2f} cm"
        )

    # =========================================================
    # WEBSOCKET THREAD
    # =========================================================

    def run_websocket(self):

        asyncio.set_event_loop(self.loop)

        try:

            self.loop.run_until_complete(
                self.websocket_main()
            )

        except Exception as e:

            print(
                f"[WEBSOCKET THREAD ERROR] {e}"
            )

    # =========================================================
    # WEBSOCKET MAIN
    # =========================================================

    async def websocket_main(self):

        while True:

            try:

                print(
                    f"[WEBSOCKET] Menghubungkan ke "
                    f"{self.WEBSOCKET_URI}"
                )

                async with websockets.connect(
                    self.WEBSOCKET_URI,
                    ping_interval=20,
                    ping_timeout=20
                ) as websocket:

                    print(
                        "[WEBSOCKET] Connected"
                    )

                    # SEND dan RECEIVE bersamaan

                    await asyncio.gather(
                        self.send_data(websocket),
                        self.receive_data(websocket)
                    )

            except Exception as e:

                print(
                    f"[WEBSOCKET] Connection error: {e}"
                )

                print(
                    "[WEBSOCKET] Reconnect dalam 2 detik..."
                )

                await asyncio.sleep(2)

    # =========================================================
    # SEND DATA
    # =========================================================

    async def send_data(self, websocket):

        while True:

            try:

                data = {
                    "type": "camera_distance",
                    "robot_id": self.ROBOT_ID,
                    "distance": self.distance,
                    "timestamp": time.time()
                }

                message = json.dumps(data)

                await websocket.send(message)

                print(
                    f"[SEND] Robot {self.ROBOT_ID} "
                    f"jarak={self.distance:.2f} cm"
                )

                # 10 Hz

                await asyncio.sleep(0.1)

            except Exception as e:

                print(
                    f"[SEND ERROR] {e}"
                )

                break

    # =========================================================
    # RECEIVE DATA
    # =========================================================

    async def receive_data(self, websocket):

        while True:

            try:

                message = await websocket.recv()

                print(
                    f"[RECEIVE] {message}"
                )

                # =================================================
                # DECODE JSON
                # =================================================

                try:

                    data = json.loads(message)

                except json.JSONDecodeError:

                    print(
                        "[WARNING] Data bukan JSON"
                    )

                    continue

                # =================================================
                # AMBIL DATA
                # =================================================

                robot_id = data.get(
                    "robot_id",
                    None
                )

                distance = data.get(
                    "distance",
                    None
                )

                message_type = data.get(
                    "type",
                    "unknown"
                )

                # =================================================
                # VALIDASI
                # =================================================

                if robot_id is None:

                    print(
                        "[WARNING] robot_id tidak ditemukan"
                    )

                    continue

                if distance is None:

                    print(
                        "[WARNING] distance tidak ditemukan"
                    )

                    continue

                # Jangan proses robot sendiri

                if robot_id == self.ROBOT_ID:

                    continue

                # =================================================
                # SIMPAN DATA ROBOT LAIN
                # =================================================

                self.robot_data[robot_id] = {

                    "distance": float(distance),

                    "type": message_type,

                    "timestamp": data.get(
                        "timestamp",
                        time.time()
                    )
                }

                print(
                    f"[ROBOT {robot_id}] "
                    f"jarak={float(distance):.2f} cm"
                )

            except websockets.exceptions.ConnectionClosed:

                print(
                    "[RECEIVE] Connection closed"
                )

                break

            except Exception as e:

                print(
                    f"[RECEIVE ERROR] {e}"
                )

                break


# =============================================================
# MAIN
# =============================================================

def main():

    robot = WebSocketRobot()

    # =========================================================
    # CONTOH JARAK
    # =========================================================

    # Ganti bagian ini dengan hasil pembacaan
    # kamera / sensor Anda.

    robot.set_distance(1)

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        print(
            "\n[SYSTEM] Program stopped"
        )


if __name__ == "__main__":

    main()