"""Dataset manager for caching RI microsimulation data."""

import logging
from policyengine_us import Microsimulation

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages the RI dataset in memory for fast access."""

    def __init__(self):
        self.baseline_sim = None
        self._is_loaded = False

    async def load(self):
        """Load RI dataset into memory - called once at startup."""
        if self._is_loaded:
            logger.info("Dataset already loaded, skipping")
            return

        logger.info("Loading RI microsimulation dataset...")
        try:
            # Load RI-specific dataset from HuggingFace
            self.baseline_sim = Microsimulation(
                dataset="hf://policyengine/test/RI-1.h5"
            )
            self._is_loaded = True
            logger.info("✓ RI dataset loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load RI dataset: {e}")
            raise

    def get_baseline(self):
        """Return the cached baseline simulation."""
        if not self._is_loaded:
            raise RuntimeError("Dataset not loaded. Call load() first.")
        return self.baseline_sim

    def is_loaded(self) -> bool:
        """Check if dataset is loaded."""
        return self._is_loaded

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up dataset manager...")
        self.baseline_sim = None
        self._is_loaded = False


# Global instance
_dataset_manager: DatasetManager = None


def get_dataset_manager() -> DatasetManager:
    """Dependency injection for dataset manager."""
    global _dataset_manager
    if _dataset_manager is None:
        raise RuntimeError("DatasetManager not initialized")
    return _dataset_manager


def init_dataset_manager() -> DatasetManager:
    """Initialize the global dataset manager."""
    global _dataset_manager
    if _dataset_manager is None:
        _dataset_manager = DatasetManager()
    return _dataset_manager
