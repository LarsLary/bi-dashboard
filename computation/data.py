"""
This is data.py.

data.py contains classes DataPings and DataSessions.
"""

import datetime as dt

import numpy as np
import pandas as pd


class DataPings:
    """Data frame of pings.

    Attributes
    ----------
    data : np.DataFrame
        pings
    features : np.DataFrame
        metered features
    metered_days : list of dt.Date
        list of dates, on which at least one ping metered happened
    day_sequence_of_timespan : list of dt.Date
        list of dates between first and last metered date (both inclusive)
    filename: str
        name of the file from which the pings come from

    Methods
    -------
    get_pings()
        return data frame of pings
    filter_out_unmetered_bitmask_entries()
        remove entries with unmetered bitmasks
    get_metered_days()
        return metered_days
    get_filename()
        return filename
    get_sequence_of_days()
        return day_sequence_of_timespan
    """

    def __init__(self, filename: str, data: pd.DataFrame, features: pd.DataFrame):
        """Declare/Initialize variables and filter pings.

        Parameters
        ----------
        filename: str
        data : np.DataFrame
        features : np.DataFrame
        """
        self.data = data
        self.features = features
        self.metered_days = None
        self.day_sequence_of_timespan = None
        self.filename = filename

        self.filter_out_unmetered_bitmask_entries()
        self.data = self.data.drop_duplicates()

    def get_pings(self) -> pd.DataFrame:
        """Return pings.

        Returns
        ----------
        data : np.DataFrame
            pings
        """
        return self.data

    def filter_out_unmetered_bitmask_entries(self) -> None:
        """
        Filter out unmetered bitmask entries.

        Remove entries from data with bitmasks, that don't contain a metered feature.
        """
        metered_bitmasks = self.features["bitmask"].agg(
            lambda x: np.bitwise_or.reduce(x.values)
        )
        self.data = self.data[self.data["feature_mask"] & metered_bitmasks > 0]

    def get_metered_days(self) -> list:
        """
        Return metered_days.

        If metered_days is None metered_days gets assigned.

        Returns
        ----------
        metered_days : list of dt.Date
            list of dates, on which at least one ping metered happened

        Yields
        ------
        unique_days : pd.Series
        dates : list of dt.Date
        """
        if not self.metered_days:
            unique_days = self.data["time"].str[:10].drop_duplicates()
            dates = []
            for day in unique_days:
                dates.append(dt.datetime.strptime(day, "%Y-%m-%d").date())
            dates.sort()
            self.metered_days = dates
        return self.metered_days

    def get_filename(self) -> str:
        """Returns the name of the file from which the pings come from

        Returns
        ----------
        filename : str
        """
        return self.filename

    def get_sequence_of_days(self) -> list:
        """
        Return day_sequence_of_timespan.

        If day_sequence_of_timespan is None day_sequence_of_timespan gets assigned.

        Returns
        ----------
        day_sequence_of_timespan : list of dt.Date
            list of dates between first and last metered date (both inclusive)

        Yields
        ------
        first_day : dt.Date
        last_day : dt.Date
        """
        if not self.day_sequence_of_timespan:
            if not self.metered_days:
                self.get_metered_days()
            first_day = self.metered_days[0]
            last_day = self.metered_days[-1]
            self.day_sequence_of_timespan = [
                first_day + dt.timedelta(days=x)
                for x in range((last_day - first_day).days + 1)
            ]
        return self.day_sequence_of_timespan


class DataSessions:
    """Data frames of sessions.

    Attributes
    ----------
    data_pings : DataPings
        pings
    block_length : int
        length of a block in seconds
    features : np.DataFrame
        metered features
    data : np.DataFrame
        sessions
    data_with_feature_use : pd.DataFrame
        data, appended by one column for each feature containing 0 or 1, depending on if the feature was used in
        appropriate block
    data_with_token_cost : pd.DataFrame
        data, appended by one column for each feature containing 0 or the cost of the feature, depending on if the
        feature was used in appropriate block and one column containing the total cost appropriate block
    data_cas : pd.DataFrame
        data frame containing the concurrent active sessions
    feature_package_combination: pd.DataFrame
        data frame containing how often a feature with which features in combination is used daily

    Methods
    -------
    extract_session_blocks()
        create sessions
    get_data_with_feature_use()
        return sessions with feature usage information
    get_feature_data_from_bitmasks(bitmasks)
        return feature usage information from given bitmasks
    get_data_with_token_cost()
        return sessions with feature usage cost
    get_token_consumption()
        return token consumption of given interval.
    get_cas()
        return the number of concurrent active sessions by date.
    crop_data()
        sets the data to the wanted interval
    get_total_token_amount()
        return the total token usage.
    get_package_combination_percentage()
        return daily feature package combinations
    get_cas_statistics()
        return the statistics for the concurrent active sessions
    """

    def __init__(
        self,
        data: pd.DataFrame,
        data_pings: DataPings,
        features: pd.DataFrame,
        block_length: int,
    ):
        """Declare/Initialize variable and extract sessions.

        Parameters
        ----------
        data : pd.Dataframe
        data_pings : DataPings
        features : pd.Dataframe
        block_length : int
            session period in seconds
        """
        self.data_pings = data_pings
        self.features = features
        self.block_length = block_length
        self.data = data
        self.data_with_feature_use = None
        self.data_with_token_cost = None
        self.data_cas = None
        self.feature_package_combination = None

    def extract_session_blocks(self):
        """Create session blocks.

        Yields
        ------
        data : pd.DataFrame
        time_format : String
        session_data : list of list
        cur_timestamp : dt.datetime
        cur_bitmask : int
        cur_c_id : String
        cur_a_id : String
        cur_last_ping : dt.datetime
        timestamp : dt.datetime
        bitmask : int
        c_id : String
        a_id : String
        block_end_timestamp : dt.datetime
        """
        data = self.data_pings.data.copy()
        data = data.sort_values(by=["cluster_id", "app_instance_id", "time"])
        data = data.reset_index()  # make sure that indices exist correctly

        time_format = "%Y-%m-%d %H:%M:%S"
        session_data = []

        cur_timestamp = None
        cur_bitmask = None
        cur_c_id = None
        cur_a_id = None
        cur_last_ping = None

        # iterate through data frame
        for index, row in data.iterrows():
            timestamp = dt.datetime.strptime(row["time"], "%Y-%m-%dT%H:%M:%SZ")
            bitmask = row["feature_mask"]
            c_id = row["cluster_id"]
            a_id = row["app_instance_id"]

            # no open block -> open one
            if not cur_timestamp:
                cur_timestamp = timestamp
                cur_bitmask = bitmask
                cur_c_id = c_id
                cur_a_id = a_id
                cur_last_ping = timestamp

            #    new cluster_id
            # or same cluster id and new app_instance_id
            # or timestamp is not in the block
            # ==> close open block and open new one
            elif (
                c_id != cur_c_id
                or (c_id == cur_c_id and a_id != cur_a_id)
                or timestamp >= cur_timestamp + dt.timedelta(seconds=self.block_length)
            ):
                block_end_timestamp = (
                    cur_timestamp + dt.timedelta(seconds=self.block_length)
                ).strftime(time_format)
                # TODO: Optimize? Better way than append?
                session_data.append(
                    [
                        cur_c_id,
                        cur_a_id,
                        cur_bitmask,
                        cur_timestamp.strftime(time_format),
                        block_end_timestamp,
                        cur_last_ping.strftime(time_format),
                    ]
                )
                cur_timestamp = timestamp
                cur_bitmask = bitmask
                cur_c_id = c_id
                cur_a_id = a_id
                cur_last_ping = timestamp
            # timestamp is in the block -> bitwise or on bitmask
            else:
                cur_bitmask = cur_bitmask | bitmask
                cur_last_ping = timestamp
        # close last block
        if cur_timestamp:
            block_end_timestamp = (
                cur_timestamp + dt.timedelta(seconds=self.block_length)
            ).strftime(time_format)
            # TODO: Optimize? Better way than append?
            session_data.append(
                [
                    cur_c_id,
                    cur_a_id,
                    cur_bitmask,
                    cur_timestamp.strftime(time_format),
                    block_end_timestamp,
                    cur_last_ping.strftime(time_format),
                ]
            )

        self.data = pd.DataFrame(
            session_data,
            columns=[
                "cluster_id",
                "app_instance_id",
                "feature_mask",
                "block_start",
                "block_end",
                "last_ping",
            ],
        )

    def get_data_with_feature_use(self):
        """
        Return data_with_feature_use.

        If data_with_feature_use is None, create sessions with feature usage information.

        Returns
        -------
        data_with_feature_use : pd.DataFrame
            data, appended by one column for each feature containing 0 or 1, depending on if the feature was used in
            appropriate block

        Yields
        ------
        data : pd.DataFrame
        feature_df : pd.Series
        """
        if self.data_with_feature_use is None:
            data = self.data.copy()
            feature_df = self.get_feature_data_from_bitmasks(data["feature_mask"])
            feature_df.index = feature_df.index.astype(int)
            data.index = data.index.astype(int)
            self.data_with_feature_use = pd.concat([data, feature_df], axis="columns")
        return self.data_with_feature_use

    def get_feature_data_from_bitmasks(self, bitmasks: pd.Series):
        """
        Dig feature usage information from given bitmasks.

        Parameters
        ----------
        bitmasks : pd.Series
            bitmasks to dig features from

        Returns
        -------
        pd.DataFrame
            feature usage (0 or 1) for each feature of each feature mask

        Yields
        ------
        feature_data : list of list of int
        feature_df : pd.Series
        """
        # get data if feature is used as list of list (:= feature_x of row_x)
        feature_data = [
            [int(f & b > 0) for f in self.features["bitmask"]] for b in bitmasks
        ]

        # get column names as list
        col_names = [name for name in self.features["keyword"]]

        return pd.DataFrame(feature_data, columns=col_names)

    def get_data_with_token_cost(self):
        """
        Return data_with_token_cost.

        If data_with_token_cost is None, create sessions with feature usage cost and total cost per session block.

        Returns
        -------
        data_with_token_cost : pd.DataFrame
            data, appended by one column for each feature containing 0 or the cost of the feature, depending on if the
            feature was used in appropriate block and one column containing the total cost of appropriate block

        Yields
        ------
        data : pd.DataFrame
        features_in_df : list of String
        feat_name : String
        """
        if self.data_with_token_cost is None:
            if self.data_with_feature_use is None:
                self.get_data_with_feature_use()
            data = self.data_with_feature_use.copy()
            # map feature usage to feature token cost
            features_in_df = []
            data = data.reset_index()  # make sure that indices exist correctly
            for index, row in self.features.iterrows():
                feat_name = row["keyword"]
                if feat_name in data.columns:
                    data[feat_name] = data[feat_name].apply(
                        lambda x: x * row["token_consumption"]
                    )
                    features_in_df.append(feat_name)

            # calculate total token consumption of session block and extend
            # with column for it
            data["total"] = data[features_in_df].sum(axis=1)

            self.data_with_token_cost = data

        return self.data_with_token_cost

    def get_token_consumption(self, interval: str = "D"):
        """
        Return token consumption of given interval.

        Parameters
        ----------
        interval : str
            length of interval
            for minutes use: "[num of min]min"
            for hours use: "[num of hours]H"
            for days use: "[num of days]D"
            full list: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

        Returns
        -------
        pd.DataFrame
            data frame containing cost of each feature per chosen interval, as well as total cost per chosen interval
        """
        if self.data_with_token_cost is None:
            self.get_data_with_token_cost()
        data = self.data_with_token_cost.copy()
        data = data.drop(
            [
                "cluster_id",
                "app_instance_id",
                "feature_mask",
                "block_end",
                "last_ping",
            ],
            axis="columns",
        )
        feat_names = self.features["keyword"].tolist()
        feat_names.append("total")
        data["block_start"] = pd.to_datetime(data["block_start"])
        data = data.groupby(pd.Grouper(key="block_start", freq=interval))[
            feat_names
        ].sum()
        data = data.reset_index()  # make sure that indices exist correctly

        data.rename(columns={"block_start": "time"}, inplace=True)

        return data

    def get_cas(self, interval: str = "D"):
        """
        Get number of concurrent active sessions by date.

        Parameters
        ----------
        interval : str
            length of interval
            for minutes use: "[num of min]min"
            for hours use: "[num of hours]H"
            for days use: "[num of days]D"
            full list: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

        Returns
        -------
        pd.DataFrame
            data frame containing most active sessions (within 15 min) per given interval

        Raises
        ------
        Exception
            If self.block_length is not equal to 300
        """
        if self.block_length != 300:
            raise Exception("Method only works with self.block_length == 300")

        # remove sessions, that don't include one of the 15min-timestamps
        s = self.data["block_start"].copy()
        s = s[
            (s.str[14:16].astype("int") % 15 >= 10)
            | (
                (s.str[14:16].astype("int") % 15 == 0)
                & (s.str[17:19].astype("int") == 0)
            )
        ]

        data = s.to_frame()
        data = data.reset_index(drop=True)
        data.rename(columns={"block_start": "time"}, inplace=True)
        data["time"] = pd.to_datetime(data["time"])
        data["amount"] = 1

        # amount of sessions that are active at 15min-timestamps
        data = data.groupby(pd.Grouper(key="time", label="right", freq="15min"))[
            "amount"
        ].sum()
        data = data.reset_index()

        # find max num of 15min interval-sessions in given interval
        data = data.groupby(pd.Grouper(key="time", freq=interval))["amount"].max()
        data = data.reset_index()

        return data

    def crop_data(self, first_date, last_date):
        """
        Set the data to the wanted interval.

        Parameters
        ---------
        first_date: str
            first date of the new interval
        last_date: str
            last date of the new interval
        """
        self.data = self.data[
            (self.data["block_start"] >= str(first_date))
            & (self.data["block_end"] <= str(last_date))
        ]

    def get_total_token_amount(self):
        """
        Compute the total token usage.

        Returns
        -------
        pd.Dataframe:
                total token usage for each product and total token usage
        """
        if self.data_with_token_cost is None:
            self.get_data_with_token_cost()
        cols = self.features.keyword
        cols = pd.concat([cols, pd.Series(["total"])])
        data = self.data_with_token_cost.copy()
        data = data[cols].sum()

        return data

    def get_package_combination_percentage(self):
        """
        Return the amount of possible feature in percentage.

        Returns
        ---------
        feature_package_combination: pd.DataFrame
            data containing usage of possible feature packages
        """
        if self.feature_package_combination is None:
            if self.data_with_feature_use is None:
                self.get_data_with_feature_use()
        feat_names = self.features["keyword"].tolist()
        fpc_data = []
        for i in range(1, 2 ** len(feat_names)):
            combination = []
            data = self.data_with_feature_use
            j = 0
            for fn in feat_names:
                if (2**j & i) > 0:
                    combination.append(fn)
                    data = data[self.data_with_feature_use[fn] == 1]
                else:
                    data = data[self.data_with_feature_use[fn] == 0]
                j += 1
            total_rows = len(self.data_with_feature_use.index)
            num_of_combination = len(data.index)
            fpc_data.append(
                [", ".join(combination), (num_of_combination / total_rows) * 100]
            )

        self.feature_package_combination = pd.DataFrame(
            fpc_data,
            columns=[
                "package_names",
                "usage",
            ],
        )

        return self.feature_package_combination

    def get_cas_statistics(self):
        """
        Compute the statistics for the concurrent active sessions.

        Returns
        -------
        pd.Dataframe:
             Maximum, Mean and Mean for weekdays for the concurrent active sessions
        """

        cas = self.get_cas()
        cas_max = cas["amount"].max()
        cas_mean = round(cas["amount"].mean(), 0)
        cas_weekdays_mean = round(cas[cas.time.dt.dayofweek < 5]["amount"].mean(), 0)

        cas_statistics = {
            "name": ["Max", "Mean", "Mean in weekdays"],
            "values": [cas_max, cas_mean, cas_weekdays_mean],
        }

        return pd.DataFrame(cas_statistics)
