import pandas as pd

from ..exceptions import ArgumentsError


class Scaler:
    def __init__(self):
        """Class for Scaling the columns

        Private Methods
        ---------------

        __validate_input() : validates the input

        __min_max_scaler() : function to scale the supplied columns on the basis of Min-Max-Scaling technique

        __binary_scaler() : function to scale the supplied columns on the basis of binary Scaling

        __standard_scaler() : function to standardise the supplied columns

        Note: For more information on these scaling techniques read .scaling_tecniques.txt

        Public Methods
        --------------

        execute() : Main function that performs the operations on supplied dataframe and returns a new dataframe

        """

        self.train_df = None
        self.test_df = None
        self.type = "StandardScaler"
        self.columns = None
        self.is_combined = False
        self.threshold = None
        self.new_train_df = None
        self.new_test_df = None
        self.final_train_df = None
        self.final_test_df = None
        self.categorical_columns = None
        self.target_col = None

    def __repr__(self):
        return f"Scaler(type={self.type}, is_combined={self.is_combined}, threshold={self.threshold})"

    def __validate_input(self):
        if self.train_df is None:
            raise ValueError(
                "Feature train dataframe should not be of None type"
            )

        if type(self.train_df) is not pd.core.frame.DataFrame:
            raise TypeError(
                "Feature train dataframe is not a valid dataframe.\nExpected object"
                " type: pandas.core.frame.DataFrame"
            )

        if self.test_df is not None:
            if type(self.test_df) is not pd.core.frame.DataFrame:
                raise TypeError(
                    "Feature test dataframe is not a valid dataframe.\nExpected object"
                    " type: pandas.core.frame.DataFrame"
                )

        if type(self.type) is not str:
            raise TypeError('Expected string value for argument "type" ')

        if self.type not in [
            "MinMaxScaler",
            "BinaryScaler",
            "StandardScaler",
        ]:
            raise ArgumentsError(
                'Allowed argument for type is "MinMaxScaler" or'
                f' "BinaryScaler" or "StandardScaler", got {self.type}'
            )

        if self.columns is not None:
            if not isinstance(self.columns, list):
                raise TypeError(
                    f"Expected list type for argument columns, got {type(self.columns)}"
                )
            column_list = list(self.train_df.keys())
            for column in self.columns:
                if type(column) != str:
                    raise TypeError(
                        f"Expected str type column, got {type(column)}"
                    )
                if column not in column_list:
                    raise ArgumentsError(
                        f"Column {column} does not exist in dataframe"
                    )

        if self.threshold is not None:
            if type(self.threshold) is not dict:
                raise TypeError(
                    f"Expected dict type threshold, got {type(column)}"
                )
            for column in self.threshold.keys():
                if column not in list(self.train_df.keys()):
                    raise ArgumentsError(
                        f"Column {column} does not exist in dataframe"
                    )

        if self.categorical_columns is not None:
            if not isinstance(self.categorical_columns, list):
                raise TypeError(
                    f"Expected list type for argument categorical_columns, got {type(self.columns)}"
                )

        if not isinstance(self.target_col, str):
            raise TypeError(
                f"Expected str type for argument target_col, got {type(self.columns)}"
            )

        self.new_train_df = self.train_df
        self.new_test_df = self.test_df

    def isNumeric(self, column):
        # i => int (signed), u => unsigned int, f => float, c => complex
        return column.dtype.kind in "iufc"

    def __min_max_scaler_helper(self, df):
        new_df = df.copy()
        to_be_dropped_columns = list()
        if self.categorical_columns is not None:
            to_be_dropped_columns = self.categorical_columns
        to_be_dropped_columns.append(self.target_col)
        if not self.is_combined:
            for column in self.columns:
                if column in to_be_dropped_columns:
                    continue
                if not self.isNumeric(df[column]):
                    raise TypeError(
                        f"Unexpected datatype of column, {type(column)}"
                    )
                cur_col = df[column]
                max = cur_col.max()
                min = cur_col.min()
                cur_col = (cur_col - min) / (max - min)
                new_df[column] = cur_col
        else:
            temp_df = new_df.drop(columns=to_be_dropped_columns)
            max = temp_df.to_numpy().max()
            min = temp_df.to_numpy().min()
            for column in self.columns:
                if column in to_be_dropped_columns:
                    continue
                if not self.isNumeric(df[column]):
                    raise TypeError(
                        f"Unexpected datatype of column, {type(column)}"
                    )
                new_df[column] = (temp_df[column] - min) / (max - min)
        return new_df

    def __min_max_scaler(self):
        if self.train_df is not None:
            self.new_train_df = self.__min_max_scaler_helper(self.train_df)
        if self.test_df is not None:
            self.new_test_df = self.__min_max_scaler_helper(self.test_df)
        return self.new_train_df, self.new_test_df

    def __binary_scaler_helper(self, df):
        new_df = df.copy()
        to_be_dropped_columns = list()
        if self.categorical_columns is not None:
            to_be_dropped_columns = self.categorical_columns
        to_be_dropped_columns.append(self.target_col)
        for column in self.columns:
            if not self.isNumeric(df[column]):
                raise TypeError(
                    f"Unexpected datatype of column, {type(column)}"
                )
            if column in to_be_dropped_columns:
                continue
            cur_thresh = 0
            if self.threshold is not None:
                if column in self.threshold.keys():
                    cur_thresh = self.threshold[column]
            new_df[column] = df[column].apply(
                lambda val: 0 if val <= cur_thresh else 1
            )
        return new_df

    def __binary_scaler(self):
        if self.train_df is not None:
            self.new_train_df = self.__binary_scaler_helper(self.train_df)
        if self.test_df is not None:
            self.new_test_df = self.__binary_scaler_helper(self.test_df)
        return self.new_train_df, self.new_test_df

    def __standard_scaler_helper(self, df):
        new_df = df.copy()
        to_be_dropped_columns = list()
        if self.categorical_columns is not None:
            to_be_dropped_columns = self.categorical_columns
        to_be_dropped_columns.append(self.target_col)
        if not self.is_combined:
            for column in self.columns:
                if column in to_be_dropped_columns:
                    continue
                if not self.isNumeric(df[column]):
                    raise TypeError(
                        f"Unexpected datatype of column, {type(column)}"
                    )
                cur_col = df[column]
                mean = cur_col.mean()
                std = cur_col.std()
                cur_col = (cur_col - mean) / std
                new_df[column] = cur_col
        else:
            temp_df = new_df.drop(columns=to_be_dropped_columns)
            mean = temp_df.stack().mean()
            std = temp_df.stack().std()
            for column in self.columns:
                if column in to_be_dropped_columns:
                    continue
                if not self.isNumeric(df[column]):
                    raise TypeError(
                        f"Unexpected datatype of column, {type(column)}"
                    )
                new_df[column] = (temp_df[column] - mean) / std
        return new_df

    def __standard_scaler(self):
        if self.train_df is not None:
            self.new_train_df = self.__standard_scaler_helper(self.train_df)
        if self.test_df is not None:
            self.new_test_df = self.__standard_scaler_helper(self.test_df)
        return self.new_train_df, self.new_test_df

    def execute(self, params):

        if "type" in params.keys():
            self.type = params["type"]
        if "columns" in params.keys():
            self.columns = params["columns"]
        if "is_combined" in params.keys():
            self.is_combined = params["is_combined"]
        if "train_df" in params.keys():
            self.train_df = params["train_df"]
        if "test_df" in params.keys():
            self.test_df = params["test_df"]
        if "threshold" in params.keys():
            self.threshold = params["threshold"]
        if "categorical_columns" in params.keys():
            self.categorical_columns = params["categorical_columns"]
        if "target_col" in params.keys():
            self.target_col = params["target_col"]

        self.__validate_input()

        if self.type == "MinMaxScaler":
            self.final_train_df, self.final_test_df = self.__min_max_scaler()
        elif self.type == "BinaryScaler":
            self.final_train_df, self.final_test_df = self.__binary_scaler()
        elif self.type == "StandardScaler":
            self.final_train_df, self.final_test_df = self.__standard_scaler()

        params["train_df"] = self.final_train_df
        params["test_df"] = self.final_test_df
