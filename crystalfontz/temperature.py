from typing import Iterable, List

from crystalfontz.device import Device


def pack_temperature_settings(enabled: Iterable[int], device: Device) -> bytes:
    bs: List[int] = [0 for _ in range(0, device.n_temperature_sensors // 8)]
    for sensor in set(enabled):
        sensor_idx = sensor - 1
        bytes_idx: int = sensor_idx // 8
        print("sensor_idx:", sensor_idx)
        print("bytes_idx:", bytes_idx)
        mask: int = 0b00000001 << (sensor_idx - (bytes_idx * 8))
        bs[bytes_idx] ^= mask

    return bytes(bs)
