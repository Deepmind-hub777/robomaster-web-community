"""EP Core field probe using DJI's public RoboMaster Python SDK.

This records SDK-decoded video-frame arrival and chassis velocity telemetry.
It does not implement WSS/WebRTC, raw-H.264 passthrough, or browser glass-to-glass
timing. Motion mode is a single, attended lease-expiry trial; it is not a safety
certification or a substitute for manual fault injection and physical timing.
"""
import argparse
import csv
import json
import os
import threading
import time
from datetime import datetime

from robomaster import robot


MAX_SPEED = 0.15


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sn", help="Optional robot serial number; select a specific robot on a multi-robot network")
    parser.add_argument("--observe-seconds", type=float, default=30.0)
    parser.add_argument("--arm-motion", action="store_true", help="Enable one attended low-speed trial")
    parser.add_argument("--lease-ms", type=int, default=400)
    parser.add_argument("--speed", type=float, default=0.10)
    args = parser.parse_args()

    if args.observe_seconds <= 0:
        parser.error("--observe-seconds must be positive")
    if not 100 <= args.lease_ms <= 1000:
        parser.error("--lease-ms must be between 100 and 1000 ms")
    if not 0 < args.speed <= MAX_SPEED:
        parser.error("--speed must be >0 and <=0.15 m/s")
    if args.arm_motion:
        print("运动试验要求：低速档、代表性载荷、清空区域、观察员在位、人工急停可用。")
        print("本脚本只测试 SDK 进程存活时的命令超时；不要用它测试断网/崩溃/睡眠。")
        if input("输入 ARM-ONE-TRIAL 确认只进行一次低速租约试验：").strip() != "ARM-ONE-TRIAL":
            print("未确认，退出。")
            return 2

    os.makedirs("results", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    jsonl_path = os.path.join("results", "probe-" + stamp + ".jsonl")
    csv_path = os.path.join("results", "probe-" + stamp + ".csv")
    lock = threading.Lock()
    rows = []

    def log(event, **fields):
        row = {"host_monotonic_ns": time.perf_counter_ns(), "event": event, **fields}
        with lock:
            rows.append(row)
            with open(jsonl_path, "a", encoding="utf-8") as out:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False))

    ep = robot.Robot()
    try:
        log("connect_start", conn_type="sta", sn=args.sn)
        ep.initialize(conn_type="sta", sn=args.sn)
        log("connected", sn=args.sn)

        def velocity_callback(msg):
            try:
                x, y, z = msg
                log("velocity", x=float(x), y=float(y), z=float(z))
            except Exception as exc:
                log("velocity_parse_error", error=str(exc))

        ep.chassis.sub_velocity(freq=50, callback=velocity_callback)
        ep.camera.start_video_stream(display=False)
        log("video_stream_started", path="sdk-decoded-only")

        deadline = time.perf_counter() + args.observe_seconds
        frame_count = 0
        while time.perf_counter() < deadline:
            frame = ep.camera.read_cv2_image(timeout=0.25, strategy="newest")
            if frame is not None:
                frame_count += 1
                log("video_frame", frame_index=frame_count, shape=list(frame.shape))

        log("observe_complete", seconds=args.observe_seconds, decoded_frames=frame_count,
            note="frame arrival only; not glass-to-glass latency")

        if args.arm_motion:
            # A finite SDK command timeout is only a same-process watchdog.
            # The single vector command then expires without further renewal.
            issued = time.perf_counter_ns()
            log("motion_command", x=args.speed, y=0, z=0, lease_ms=args.lease_ms,
                caveat="SDK timeout depends on this Python process remaining alive")
            ep.chassis.drive_speed(x=args.speed, y=0, z=0,
                                   timeout=args.lease_ms / 1000.0)
            log("motion_call_return", command_issued_ns=issued)
            time.sleep(args.lease_ms / 1000.0 + 1.0)
            ep.chassis.drive_speed(x=0, y=0, z=0, timeout=0.5)
            log("zero_command_sent", note="physical stop must be measured externally")
            time.sleep(1.0)

    except KeyboardInterrupt:
        log("operator_interrupt")
    except Exception as exc:
        log("error", error=repr(exc))
        raise
    finally:
        try:
            ep.chassis.drive_speed(x=0, y=0, z=0, timeout=0.5)
        except Exception:
            pass
        try:
            ep.camera.stop_video_stream()
        except Exception:
            pass
        try:
            ep.close()
        except Exception:
            pass
        with lock:
            if rows:
                keys = sorted({key for row in rows for key in row})
                with open(csv_path, "w", newline="", encoding="utf-8-sig") as out:
                    writer = csv.DictWriter(out, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(rows)
        print("JSONL:", os.path.abspath(jsonl_path))
        print("CSV:", os.path.abspath(csv_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
