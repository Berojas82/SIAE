"""
Carga y división estratificada del dataset (70% Train / 15% Val / 15% Test).
"""
import os
import pandas as pd
from pathlib import Path
from typing import Tuple, cast
from sklearn.model_selection import train_test_split

from ..utils.constants import PROCESSED_DATA_PATH, SPLITS_DIR, TARGET_COL
from ..utils.logger import get_logger

logger = get_logger("DataLoader")

class DataLoader:
    def __init__(self, data_path: str | Path = PROCESSED_DATA_PATH, seed: int = 42):
        self.data_path = Path(data_path)
        self.seed = seed

    def load_raw_processed(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de datos en: {self.data_path}")
        logger.info(f"Cargando dataset desde {self.data_path}")
        return pd.read_csv(self.data_path, encoding="utf-8")

    def split_data(
        self,
        save_splits: bool = True,
        splits_dir: str | Path = SPLITS_DIR
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = self.load_raw_processed()

        # 1. Separar 15% para Test
        res1 = train_test_split(
            df,
            test_size=0.15,
            random_state=self.seed,
            stratify=df[TARGET_COL]
        )
        train_val_df, test_df = cast(Tuple[pd.DataFrame, pd.DataFrame], res1)

        # 2. Del 85% restante, separar 15/85 (= 17.647%) para Validación -> 15% del total
        val_relative_size = 0.15 / 0.85
        res2 = train_test_split(
            train_val_df,
            test_size=val_relative_size,
            random_state=self.seed,
            stratify=train_val_df[TARGET_COL]
        )
        train_df, val_df = cast(Tuple[pd.DataFrame, pd.DataFrame], res2)

        logger.info(f"Split completado: Train={len(train_df)} ({len(train_df)/len(df):.1%}), "
                    f"Val={len(val_df)} ({len(val_df)/len(df):.1%}), "
                    f"Test={len(test_df)} ({len(test_df)/len(df):.1%})")

        if save_splits:
            splits_path = Path(splits_dir)
            splits_path.mkdir(parents=True, exist_ok=True)
            train_df.to_csv(splits_path / "train.csv", index=False, encoding="utf-8")
            val_df.to_csv(splits_path / "val.csv", index=False, encoding="utf-8")
            test_df.to_csv(splits_path / "test.csv", index=False, encoding="utf-8")
            logger.info(f"Splits guardados en: {splits_path}")

        return train_df, val_df, test_df
