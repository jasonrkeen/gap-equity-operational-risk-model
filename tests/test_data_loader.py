from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_loader import snapshot_to_dict


class DataLoaderTests(unittest.TestCase):
    def test_snapshot_to_dict(self) -> None:
        frame = pd.DataFrame(
            [
                {"metric": "price", "value": 20.38},
                {"metric": "eps", "value": 2.35},
            ]
        )
        result = snapshot_to_dict(frame)
        self.assertEqual(result, {"price": 20.38, "eps": 2.35})


if __name__ == "__main__":
    unittest.main()

