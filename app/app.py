# pangadfs-pydfsoptimizer/app/app.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the Apache 2.0 License

import json
import logging

from pangadfs.ga import GeneticAlgorithm
from pathlib import Path

import numpy as np
from stevedore.driver import DriverManager
from stevedore.named import NamedExtensionManager


DATADIR = Path(__file__).parent


def run():
	"""Example application using pangadfs"""
	logging.basicConfig(level=logging.INFO)

	ctx = {
		'ga_settings': {
			'crossover_method': 'uniform',
			'elite_divisor': 1,
			'elite_method': 'fittest',
			'mutation_rate': .05,
			'n_generations': 5,
			'points_column': 'fppg',
			'position_column': 'positions',
			'salary_column': 'salary',
			'select_method': 'roulette',
			'stop_criteria': 10,
			'verbose': True
		},

		'site_settings': {
			'flex_positions': ('RB', 'WR', 'TE'),
			'lineup_size': 9,
			'salary_cap': 50000
		}
	}

	# set up driver managers
	dmgrs = {}
	emgrs = {}
	for ns in GeneticAlgorithm.PLUGIN_NAMESPACES:
		pns = f'pangadfs.{ns}'
		if ns == 'validate':
			emgrs['validate'] = NamedExtensionManager(
				namespace=pns, 
				names=['validate_salary', 'validate_duplicates'], 
				invoke_on_load=True, 
				name_order=True)
		elif ns in ('pool', 'populate'):
			dmgrs[ns] = DriverManager(
				namespace=pns, 
				name=f'{ns}_pydfs', 
				invoke_on_load=True)
		else:
			dmgrs[ns] = DriverManager(
				namespace=pns, 
				name=f'{ns}_default', 
				invoke_on_load=True)
	
	# set up GeneticAlgorithm object
	ga = GeneticAlgorithm(driver_managers=dmgrs, extension_managers=emgrs)
	
	# no need to create pool and pospool
    # instead just load pydfs lineups and create pool
	data = json.loads((DATADIR / 'lineups.json').read_text()) 
	pool = ga.pool(lineups=data)
	initial_population = ga.populate(pool=pool)

	# create salary and points arrays
	# these match indices of pool
	cmap = {'points': ctx['ga_settings']['points_column'],
			'salary': ctx['ga_settings']['salary_column']}
	points = pool[cmap['points']].values
	salaries = pool[cmap['salary']].values
	
	# need fitness to determine best lineup
	# and also for selection when loop starts
	population_fitness = ga.fitness(
		population=initial_population, 
		points=points
	)

	# set overall_max based on initial population
	omidx = population_fitness.argmax()
	best_fitness = population_fitness[omidx]
	best_lineup = initial_population[omidx]

	# create new generations
	n_unimproved = 0
	population = initial_population.copy()

	for i in range(1, ctx['ga_settings']['n_generations'] + 1):

		# end program after n generations if not improving
		if n_unimproved == ctx['ga_settings']['stop_criteria']:
			break

		# display progress information with verbose parameter
		if ctx['ga_settings'].get('verbose'):
			logging.info(f'Starting generation {i}')
			logging.info(f'Best lineup score {best_fitness}')

		# select the population
		# here, we are holding back the fittest 20% to ensure
		# that crossover and mutation do not overwrite good individuals
		elite = ga.select(
			population=population, 
			population_fitness=population_fitness, 
			n=len(population) // ctx['ga_settings'].get('elite_divisor', 5),
			method=ctx['ga_settings'].get('elite_method', 'fittest')
		)

		selected = ga.select(
			population=population, 
			population_fitness=population_fitness, 
			n=len(population),
			method=ctx['ga_settings'].get('select_method', 'roulette')
		)

		# cross over the population
		# here, we use uniform crossover, which splits the population
		# and randomly exchanges 0 - all chromosomes
		crossed_over = ga.crossover(population=selected, method=ctx['ga_settings'].get('crossover_method', 'uniform'))

		# mutate the crossed over population (leave elite alone)
		# can use fixed rate or variable to reduce mutation over generations
		# here we use a variable rate that increases if no improvement is found
		mutation_rate = ctx['ga_settings'].get('mutation_rate', max(.05, n_unimproved / 50))
		mutated = ga.mutate(population=crossed_over, mutation_rate=mutation_rate)

		# validate the population (elite + mutated)
		population = ga.validate(
			population=np.vstack((elite, mutated)), 
			salaries=salaries, 
			salary_cap=ctx['site_settings']['salary_cap']
		)
		
		# assess fitness and get the best score
		population_fitness = ga.fitness(population=population, points=points)
		omidx = population_fitness.argmax()
		generation_max = population_fitness[omidx]
	
		# if new best score, then set n_unimproved to 0
		# and save the new best score and lineup
		# otherwise increment n_unimproved
		if generation_max > best_fitness:
			logging.info(f'Lineup improved to {generation_max}')
			best_fitness = generation_max
			best_lineup = population[omidx]
			n_unimproved = 0
		else:
			n_unimproved += 1
			logging.info(f'Lineup unimproved {n_unimproved} times')

	# FINALIZE RESULTS
	# show best score and lineup at conclusion
	# will break after n_generations or when stop_criteria reached
	print(pool.loc[best_lineup, :])
	print(f'Lineup score: {best_fitness}')
	

if __name__ == '__main__':
	run()
