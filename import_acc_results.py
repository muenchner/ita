#Author: mahalia miller
#Future author: Samuel Cortes?
#Date: December 22, 2013
#Project: Accessibility paper

import util, time

# TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
# TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
#Flavor A: aggregate over TAZ
def grab_accessibility_by_income(scenario, mandatory = True):
	'''returns 4 values:  are low income total accessiblity, ...  very high total accessibility
	Inputs:
		taz: number 1-1454
		folder_names: numbers that represent the scenario numbers we are examining
		mandatory: true means to use the mandatory accessibility file. false means use nonMandatoryAccessibities
	Outputs:
		4 values:   low income total accessiblity, ...  very high total accessibility for a given scenario taking a weighted average over all tazs
		'''
	if mandatory == True:
		filename = 'bigDamagedTransitTake2accessibilityWooAcc/' + str(scenario) + '/accessibilities/mandatoryAccessibities.csv'
	else:
		filename = 'bigDamagedTransitTake2accessibilityWooAcc/' + str(scenario) + '/accessibilities/nonMandatoryAccessibities.csv'
	try:
		accs = util.read_2dlist(filename, ',', True)
		print 'accs  length: ', len(accs) #1454 taz and 3 subzones each
		print len(accs[0]) #15 columns
		###################################################
		#TODO
		#Your code here
		subtotal_low = 0 #sum of households * accessibility values
		hh_low = 0 #total number of low income households



		######################################################
		counter = 0
		la = 0
		ma = 0
		ha = 0
		vha = 0
		for row in accs:
			#get the accessibility data
			la += float(row[0]) #auto only
			ma += float(row[3])
			ha += float(row[6])
			vha += float(row[9])

			#every three rows, we are at a new TAZ. When that happens, get all the population data and take an average by TAZ by income group
			if counter%3 == 0:
				low = get_numHouseholds(counter/3 + 1, 'low')
				medium = get_numHouseholds(counter/3 + 1, 'medium')
				high = get_numHouseholds(counter/3 + 1, 'high')
				veryHigh = get_numHouseholds(counter/3 + 1, 'veryHigh')

				subtotal_low += la * low #single taz and just low income
				hh_low += low #keeping a running total of low income households

				#TODO
		###################################################
		#TODO
		#Your code here






		######################################################
		#old, wrong, code:
		# accs = util.read_2dlist(filename, ',', True)
		# print 'accs  length: ', len(accs) #1454 taz and 3 subzones each
		# print len(accs[0]) #15 columns

		# good_accs = [[float(row[0]), float(row[3]), float(row[6]), float(row[9])] for row in accs]
		# final_accs = []
		# # for subzone in range(0, len(good_accs), 3):
		# # 	final_accs.append()
		# print 'good acs len: ', len(good_accs)
		# for acc in range(len(good_accs[0])):
		# 	#TODO: take weighted average
		# 	final_accs.append(sum([subzonelist[acc] for subzonelist in good_accs])/float(len(good_accs))) #take average. TODO: do this correctly by weighting by population
		return [subtotal_low/float(hh_low), -1, -1 , -1] #TODO: change this to actual values (accessibility for this scenario weighted over all taz. one value per income group)
	except IOError as e:
		print e
		return [-1, -1, -1 , -1]


def grab_cumulative_accessibility(scenario, mandatory = True):
	'''returns one value for mandatory accessibility across incomes and taz. averages over households, not people
	Inputs:
		taz: number 1-1454
		folder_names: numbers that represent the scenario numbers we are examining
		mandatory: true means to use the mandatory accessibility file. false means use nonMandatoryAccessibities
	Outputs:
		1 value. averaged accessibility for a given scenario, taking a weighted average over all taz
		'''
	if mandatory == True:
		filename = 'bigDamagedTransitTake2accessibilityWooAcc/' + str(scenario) + '/accessibilities/mandatoryAccessibities.csv'
	else:
		filename = 'bigDamagedTransitTake2accessibilityWooAcc/' + str(scenario) + '/accessibilities/nonMandatoryAccessibities.csv'
	try:
		accs = util.read_2dlist(filename, ',', True)
		print 'accs  length: ', len(accs) #1454 taz and 3 subzones each
		print len(accs[0]) #15 columns
		final_accs = []
		counter = 0
		la = 0
		ma = 0
		ha = 0
		vha = 0
		for row in accs:
			#get the accessibility data
			la += float(row[0]) #auto only
			ma += float(row[3])
			ha += float(row[6])
			vha += float(row[9])

			#every three rows, we are at a new TAZ. When that happens, get all the population data and take a weighted average
			if counter%3 == 0:
				low = get_numHouseholds(counter/3 + 1, 'low')
				medium = get_numHouseholds(counter/3 + 1, 'medium')
				high = get_numHouseholds(counter/3 + 1, 'high')
				veryHigh = get_numHouseholds(counter/3 + 1, 'veryHigh')
				pop = la*low + ma*medium + ha* high + vha * veryHigh 
				final_accs.append(pop/ 3.0) #we take the average over subzones

				#reset the accessibility data
				la = 0
				ma = 0
				ha = 0
				vha = 0
			counter += 1

		#ok, so we now have a value per taz
		# hh = 0
		# for i in range(1454):
		# 	hh += get_totalHH(i + 1)
		hh = 2608023 # this is a hack. It is equivalent to the previous 3 lines but much faster
		return sum(final_accs)/float(hh) #TODO: change
	except IOError as e:
		print e
		return -1

#Flavor B: aggregate over scenarios
def grab_accessibility_by_taz_by_income(taz, folder_names, weights, mandatory = True):
	'''returns 4 values:   low income total accessiblity, ...  very high total accessibility for a given taz, taking a weighted average over all scenarios
	Inputs:
		taz: number 1-1454
		folder_names: numbers that represent the scenario numbers we are examining
		weights: list of weights for each scenario. probably 25 scenarios so 25 weights
		mandatory: true means to use the mandatory accessibility file. false means use nonMandatoryAccessibities
	Outputs:
		4 values:   low income total accessiblity, ...  very high total accessibility for a given taz, taking a weighted average over all scenarios
		'''


		###################################################
		#TODO
		#Your code here






		######################################################
	return [-1, -1, -1, -1]

def grab_accessibility_by_taz(taz, folder_names, weights, mandatory = True):
	'''returns one value for mandatory accessibility across incomes and scenarios. averages over households, not people
		Inputs:
		taz: number 1-1454
		folder_names: numbers that represent the scenario numbers we are examining
		weights: list of weights for each scenario. probably 25 scenarios so 25 weights
		mandatory: true means to use the mandatory accessibility file. false means use nonMandatoryAccessibities
	Outputs:
		1 value. averaged accessibility for a given taz, taking a weighted average over all scenarios
		'''

		###################################################
		#TODO
		#Your code here






		######################################################
	return -1
def get_scenario_weights(filename):
	'''these come from Matlab from the ttw_subset object in the results from the optimization run used for the target scenarios that we ran in Cube. It should only be 25 long'''
	with open('12-Dec-2013_12_3909_50_0.55556_25_weights.csv', 'rb') as f:
		raw  = f.readlines()
	weights = [float(r) for r in raw]
	return weights

def get_numHouseholds(taz, income_group):
	'''taz is 1-1454, income_group is low, medium, high or very high. Returns the value of the number of households (not people!!!!!!) for this taz and income'''
	accs = util.read_2dlist('tazData2010.csv', ',', True)
	if income_group == 'low':
		return float(accs[taz-1][10])
	elif income_group == 'medium':
		return float(accs[taz-1][11])
	elif income_group == 'high':
		return float(accs[taz-1][12])
	elif income_group == 'veryHigh':
		return float(accs[taz-1][13])
	else:
		raise  RuntimeError('income group does not exist here')

def get_totalHH(taz):
	'''taz is 1-1454, Returns the value of the number of households (not people!!!!!!) for this taz '''
	accs = util.read_2dlist('tazData2010.csv', ',', True)
	return float(accs[taz-1][4])


##Flavor A: look at accessibility by scenario
def aggregate_accessibility(folder_names, mandatory = True):
	'''gets one accessibility number per scenario.'''
	scenario_results = []
	for folder_name in folder_names:
		print 'starting folder: ', folder_name
		scenario_results.append(grab_cumulative_accessibility(folder_name, mandatory))
	return scenario_results

def aggregate_accessibility_by_income(folder_names, mandatory = True):
	'''gets 4 accessibility numbers per scenario (4 income groups)'''
	scenario_results = []
	for folder_name in folder_names:
		print 'starting folder: ', folder_name
		scenario_results.append(grab_accessibility_by_income(folder_name, mandatory))
	return scenario_results

##Flavor B: look at accessibility by TAZ
def aggregate_accessibility_by_taz(folder_names, weights, mandatory = True):
	'''gets one accessibility value per taz (weighted average across scenarios)'''
	taz_results = []
	for taz in range(1, 1455):
		print 'starting taz ', taz
		scenario_results.append(grab_accessibility_by_taz(taz, folder_names,  weights, mandatory))
	return scenario_results

def aggregate_accessibility_by_taz_by_income(folder_names, weights, mandatory = True):
	'''gets 4 accessibility values per taz (weighted average across scenarios) (4 income groups)'''
	taz_results = []
	for taz in range(1, 1455):
		print 'starting taz ', taz
		scenario_results.append(grab_accessibility_by_taz_by_income(taz, folder_names, weights, mandatory))
	return scenario_results

#Write some tests
def test():
	assert 230 == int(get_numHouseholds(15, 'low'))
	assert 43 == int(get_totalHH(1))
	assert grab_cumulative_accessibility(20) > 18.2
	assert grab_cumulative_accessibility(20) < 18.3 #around 18 seems reasonable

	#############
	#TODO: add one manual check of the accessibility value for one taz and one income group

	'''describe calcs here'''
	# assert grab_accessibility_by_income(20) < #add val
	# assert grab_accessibility_by_income(20) > #add val

	###########################
#Run it!
def main():
	TARGETS = [20, 33, 36, 137, 142, 143, 144, 151, 152, 159, 166, 167, 171, 173, 183, 184, 192, 193, 194, 196, 205, 1676, 1692, 2851, 2914]# data within: 12-Dec-2013_12_3909_50_0.55556_25.mat #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
	TARGETS = ['173_high'] #we have retrofitted the top 25% ranked by accessibility impact
	weights = get_scenario_weights('12-Dec-2013_12_3909_50_0.55556_25_weights.csv')#the annual likelihood of occurance of each of the scenarios ("targets")

	y = aggregate_accessibility(TARGETS, True)
	util.write_list(time.strftime("%Y%m%d")+'_accessTotACC_fromMain.txt', y)

	#TODO: implement the 3 functions below so they actually do something
	y_array = aggregate_accessibility_by_income(TARGETS, True)
	util.write_2dlist(time.strftime("%Y%m%d")+'_accessByIncome_fromMain.txt', y_array)

	y = aggregate_accessibility_by_taz(TARGETS, weights, True)
	util.write_list(time.strftime("%Y%m%d")+'_accessbyTAZ_fromMain.txt', y)

	y_array = aggregate_accessibility_by_taz_by_income(TARGETS, weights, True)
	util.write_2dlist(time.strftime("%Y%m%d")+'_accessByTAZByIncome_fromMain.txt', y_array)

if __name__ == '__main__':
	main()
