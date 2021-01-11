# pangadfs-pydfsoptimizer/tests/test_pool.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the Apache 2.0 License

import json

import numpy as np
import pandas as pd
import pytest

from plugin import PyDfsPool, PyDfsPopulate


def test_pool_pydfs(test_directory, tprint):
    lineups = json.loads((test_directory / 'lineups.json').read_text())
    pool = PyDfsPool().pool(lineups=lineups)    
    assert isinstance(pool, pd.core.api.DataFrame)
    assert not pool.empty


def test_populate_pydfs(test_directory, tprint):
    lineups = json.loads((test_directory / 'lineups.json').read_text())
    pool = PyDfsPool().pool(lineups=lineups)       
    population = PyDfsPopulate().populate(pool=pool)
    assert isinstance(population, np.ndarray)
