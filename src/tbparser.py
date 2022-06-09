import csv
import pathlib
from typing import Optional, Dict, List, Iterable, Union
import tensorboard.backend.event_processing.event_accumulator as tbea

Path = Union[str, pathlib.Path]


class TBParser:
    """Parse tensorboard logs to required format.

    For now handles only ScalarEvents.
    Hyperparams are second requested.
    """
    def __init__(self, path: Path, size_guidance: int = 0):
        self._acc = self._prepare_accumulator(path, size_guidance)

    def to_dict(
            self,
            prefix_keys: Optional[Iterable] = None,
            only_values: bool = False
    ) -> Dict[str, List[Union[tbea.SCALARS, float]]]:
        """Extract dictionary of ScalarEvents for required keys."""

        def _get_values(key):
            scalars = self._acc.Scalars(key)
            if only_values:
                scalars = list(map(lambda sc: sc.value, scalars))
            return scalars

        def _predicate(key):
            if prefix_keys:
                return any(map(key.endswith, self.keys))
            else:
                return True

        return {key: _get_values(key) for key in self._acc.scalars.Keys() if _predicate(key)}

    def to_csv(
            self,
            path: Path,
            prefix_keys: Optional[Iterable] = None
    ) -> None:
        dict_log = self.to_dict(prefix_keys=prefix_keys, only_values=True)
        row_numbers = set(map(len, dict_log.values()))
        assert len(row_numbers) == 1, "Number of rows differ per column."

        with open(path, 'w') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=dict_log.keys())
            writer.writeheader()

            keys = dict_log.keys()
            rows = map(lambda values: {k: v for k, v in zip(keys, values)}, zip(*dict_log.values()))
            writer.writerows(rows)

    def to_npz(self, path) -> None:
        """To reduce memory usage."""

    def to_json(self, path) -> None:
        """Since DVC support JSON."""

    @staticmethod
    def _prepare_accumulator(path: Path, size_guidance: int) -> tbea.EventAccumulator:
        acc = tbea.EventAccumulator(path, size_guidance={tbea.SCALARS: size_guidance})
        return acc.Reload()

    @classmethod
    def detect_logs(cls, root: Path):
        return tuple(filter(
            tbea.io_wrapper.IsSummaryEventsFile,
            tbea.io_wrapper.ListRecursivelyViaWalking(root)
        ))




