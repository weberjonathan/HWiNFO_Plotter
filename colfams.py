import pandas as pd
import numpy as np

class ColFamInfo:
    colfam_by_col = {}
    cols_by_colfam = {}

    @classmethod
    def init(cls, df: pd.DataFrame) -> None:
        # match columns to column families and store them in class members
        for name, values in df.iloc[:, 0:].iteritems():
            colfam = df[name].iloc[-1]
            if (not type(colfam) is str) and np.isnan(colfam):
                continue
            cls.colfam_by_col[name] = colfam
            if not colfam in cls.cols_by_colfam:
                cls.cols_by_colfam[colfam] = []
            cls.cols_by_colfam[colfam].append(name)

    @classmethod
    def get_family(cls, column_name: str) -> str:
        return cls.colfam_by_col[column_name]

    @classmethod
    def get_colnames(cls, column_family: str) -> list[str]:
        return cls.cols_by_colfam[column_family]

    @classmethod
    def get_families(cls) -> list[str]:
        return list(cls.cols_by_colfam.keys())