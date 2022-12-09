"""
This is Features.py.

Features.py contains class Features.
"""
import pandas as pd


# # feature bitmasks
#
# API = 0x1,
# Ui = 0x2,
# Touch = 0x4,
# Aux = 0x8,
# AuxAdvanced = 0x10,
# Query = 0x20,
# Measurement = 0x40,
# MeasurementAdvanced = 0x80,
# WebVR = 0x100,
# SharedSession = 0x200,
# LocalVisibility = 0x400,
# RemoteVisibility = 0x800,
# RemoteRendering = 0x1000,
# PaintMode = 0x2000,
# ColorComparison = 0x4000,
# StoreRestore = 0x8000,
# PointRendering = 0x10000,
# PbrMaterial = 0x20000,
# SessionStorage = 0x40000,
#
# # pkg
# Viewing = 0x80000,
# DMU = 0x100000,
# Collaboration = 0x200000,
# XR = 0x400000,
# ModelTracking = 0x800000

class Features:
    """Data frame of features.

    Attributes
    ----------
    features : np.DataFrame
        metered features

    Methods
    -------
    get_data_features()
        return features
    """

    def __init__(self):
        """Declare/Initialize features."""
        self.features = pd.DataFrame(
            {
                "keyword": ["Viewing", "DMU", "Collaboration", "XR",
                            "ModelTracking"],
                "fullname": ["", "", "", "", ""],
                "bitmask": [0x80000, 0x100000, 0x200000, 0x400000, 0x800000],
                "package": [True, True, True, True, True],
                "token_consumption": [10, 15, 20, 25, 35]
            })

    def get_data_features(self):
        """Return features.

        Returns
        ----------
        features : np.DataFrame
            metered features
        """
        return self.features
