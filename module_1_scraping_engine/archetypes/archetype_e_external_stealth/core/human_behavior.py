"""
Archetype E Stealth Toolkit: Human Behavior Mimicry
Generates Bezier curve mouse coordinates, realistic human typing emulation delays,
and randomized micro-jitter intervals to bypass bot detection heuristics.
"""
import asyncio
import random
import time
from typing import List, Tuple


class HumanBehavior:
    @staticmethod
    async def jitter_sleep(min_sec: float = 1.0, max_sec: float = 3.5):
        """Randomized sleep with normal-distribution variance."""
        delay = random.uniform(min_sec, max_sec) + random.gauss(0.1, 0.05)
        delay = max(min_sec, delay)
        await asyncio.sleep(delay)

    @staticmethod
    def generate_bezier_curve(
        start: Tuple[int, int],
        end: Tuple[int, int],
        control_points_count: int = 2,
        steps: int = 25
    ) -> List[Tuple[int, int]]:
        """
        Generates realistic cubic Bezier curve points between start and end cursor coordinates.
        """
        # Generate random control points in between
        ctrl_x1 = random.randint(min(start[0], end[0]), max(start[0], end[0]) + 50)
        ctrl_y1 = random.randint(min(start[1], end[1]) - 40, max(start[1], end[1]) + 40)
        ctrl_x2 = random.randint(min(start[0], end[0]), max(start[0], end[0]) + 30)
        ctrl_y2 = random.randint(min(start[1], end[1]) - 30, max(start[1], end[1]) + 30)

        points = []
        for i in range(steps + 1):
            t = i / float(steps)
            # Cubic Bezier formula
            x = (
                (1 - t) ** 3 * start[0]
                + 3 * (1 - t) ** 2 * t * ctrl_x1
                + 3 * (1 - t) * t ** 2 * ctrl_x2
                + t ** 3 * end[0]
            )
            y = (
                (1 - t) ** 3 * start[1]
                + 3 * (1 - t) ** 2 * t * ctrl_y1
                + 3 * (1 - t) * t ** 2 * ctrl_y2
                + t ** 3 * end[1]
            )
            points.append((int(x), int(y)))
        return points

    @staticmethod
    async def simulate_human_typing(text: str, target_element_callback=None):
        """
        Simulates natural human keystroke cadence:
        30ms - 120ms per character with occasional 200ms thinking pauses between words.
        """
        for char in text:
            delay = random.uniform(0.04, 0.12)
            if char == " ":
                delay += random.uniform(0.08, 0.18)
            await asyncio.sleep(delay)
            if target_element_callback:
                target_element_callback(char)
