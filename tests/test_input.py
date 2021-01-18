from preprocessy.input import ReadData
import pandas as pd
import numpy as np
import pytest


class TestReader:
    def test_file_name(self):
        with pytest.raises(ValueError):
            ReadData(file_name="datasets")

    def test_reader(self):
        reader = ReadData(file_name="datasets/encoding/test.csv")
        assert isinstance(reader.df, pd.core.frame.DataFrame) == True
        assert reader.df.shape == (3, 4)
        assert reader.stats.iloc[1, 0] == -4003

    def test_file_not_exists(self):
        with pytest.raises(FileNotFoundError):
            reader = ReadData(file_name="hello.csv")
