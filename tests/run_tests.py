"""Run all tests under `tests/` with the stdlib runner."""
import sys
import unittest
from pathlib import Path

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=Path(__file__).parent,
                            pattern="test_*.py",
                            top_level_dir=Path(__file__).parent.parent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
