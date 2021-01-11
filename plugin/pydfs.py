# pangadfs-pydfsoptimizer/plugin/pydfs.py
# plugins for interoperating with pydfs-lineup-optimizer

from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from pydfs_lineup_optimizer import Lineup, Player

from pangadfs.base import PoolBase, PopulateBase


class PyDfsPool(PoolBase):

    def pool(self,
             *,
             lineups: Union[List[Lineup], List[List[dict]]],
             **kwargs):
        """Creates pool from pydfs-lineup-optimizer lineups

        Args:
            lineups (Union[List[Lineup], List[List[dict]]): pydfs lineups                  

        Returns:
            pd.DataFrame: dataframe of pydfs-lineup-optimizer lineups

        """
        # convert lineup objects to dataframe
        # can also take a list of list of dicts
        wanted = ['id', 'team', 'salary', 'fppg']
        selected_players = []
        if isinstance(lineups[0], Lineup):
            for l in lineups:
                for p in l.lineup:
                    pl = {'used_fppg': p.used_fppg}
                    pl = dict(**pl, **{k:v for k, v in p._player.__dict__.items() if k in wanted})
                    pl['position'] = p.positions[0]
                    pl['proj'] = p._player.fppg
                    selected_players.append(pl)
        else:
            for l in lineups:
                for p in l:
                    pl = {k: v[0] if isinstance(v, list) else v 
                          for k, v in p.items() if k in wanted}
                    selected_players.append(pl)
                
        # get player ids and add to dataframe
        df = pd.DataFrame(selected_players)
        xref = {a: b for a, b in zip(df.id.unique(), np.arange(len(df.id.unique())))}
        return df.assign(uid=df.id.map(xref))


class PyDfsPopulate(PopulateBase):

    def populate(self,
                 *, 
                 pool: pd.DataFrame,
                 position_order: Tuple[int] = (8, 0, 6, 1, 2, 3, 4, 5, 7),
                 **kwargs):
        """Creates population from pydfs-lineup-optimizer pool
        
        Args:
            pool (pd.DataFrame): the player pool (already lineups so may have dups)
            position_order (Tuple[int]): the order of positions in a lineup
            
        Returns:
            np.ndarray: array of size (population_size, lineup_size)

        """
        # account for sort order
        # pydfs-lineup-optimizer uses QB, RB, RB, WR, WR, WR, TE, FLEX, DST
        # pangadfs uses DST, QB, TE, RB, RB, WR, WR, WR, FLEX        
        lineup_size = len(position_order)
        n_lineups = len(pool) // lineup_size
        lineup_array = pool.uid.values.reshape(n_lineups, lineup_size)
        population = lineup_array[:, position_order]
        return np.random.permutation(population)

