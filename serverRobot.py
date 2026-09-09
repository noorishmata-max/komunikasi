#!/usr/bin/env python3

import asyncio
import json
import websockets


# =========================================================
# CLIENT YANG TERHUBUNG
# =========================================================

clients = set()


# =========================================================
# HANDLER CLIENT
# =========================================================

async def handler(websocket):
    clients.add(websocket)

    print(f"[SERVER] Robot connected")
    print(f"[SERVER] Total robot connected: {len(clients)}")

    try:

        async for message in websocket:

            print(f"\n[RECEIVE] {message}")

            # =================================================
            # VALIDASI JSON
            # =================================================

            try:
                data = json.loads(message)

            except json.JSONDecodeError:
                print("[SERVER] Data bukan JSON")
                continue

            robot_id = data.get("robot_id", "unknown")
            message_type = data.get("type", "unknown")

            print(
                f"[SERVER] Robot {robot_id} "
                f"mengirim data type={message_type}"
            )

            # =================================================
            # BROADCAST KE ROBOT LAIN
            # =================================================

            disconnected = set()

            for client in clients:

                # Jangan kirim kembali ke pengirim
                if client == websocket:
                    continue

                try:

                    await client.send(message)

                    print(
                        f"[SERVER] Broadcast Robot {robot_id} "
                        f"→ robot lain"
                    )

                except Exception as e:

                    print(
                        f"[SERVER] Gagal mengirim ke client: {e}"
                    )

                    disconnected.add(client)

            # =================================================
            # HAPUS CLIENT YANG PUTUS
            # =================================================

            clients.difference_update(disconnected)

    except websockets.exceptions.ConnectionClosed:
        print("[SERVER] Robot disconnected")

    except Exception as e:
        print(f"[SERVER] Error handler: {e}")

    finally:

        clients.discard(websocket)

        print(
            f"[SERVER] Client removed. "
            f"Total robot connected: {len(clients)}"
        )


# =========================================================
# MAIN SERVER
# =========================================================

async def main():

    print("==========================================")
    print("     WEBSOCKET SERVER - 3 ROBOT")
    print("==========================================")
    print("Server : 0.0.0.0")
    print("Port   : 8765")
    print("==========================================")

    async with websockets.serve(
        handler,
        "0.0.0.0",
        8765
    ):

        print("[SERVER] WebSocket server berjalan...")

        await asyncio.Future()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n[SERVER] Server dihentikan")