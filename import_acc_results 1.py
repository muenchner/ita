#Author: mahalia miller
#Future author: Samuel Cortes?
#Date: December 22, 2013
#Project: Accessibility paper

import util, time

# TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data

def grab_accessibility_by_income(scenario):
	'''returns list of lists. Inner lists are low income total mandatory accessiblity, ... very high total mandatory accessibility as well as TODO: low income total non-mandatory accessiblity, ... very high total non-mandatory accessibility'''
	# filename = '/Volumes/bakergroup$/results/big/' + str(scenario) + '/accessibilities/mandatoryAccessibilities.csv'
	# filename = '/Volumes/bakergroup$/results/bigtop20/' + str(scenario) + '/done_400_saturday/accessibilities/mandatoryAccessibities.csv'
	filename = 'bigDamagedTransitTake2accessibilityWoo/' + str(scenario) + '/accessibilities/mandatoryAccessibities.csv'
	try:
		#TODO

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
		return None
	except IOError as e:
		print e
		return [-1, -1, -1 , -1]

# def grab_general_accessibility(scenario):
# 	''' 'autoPeakTotal', 'autoOffPeakTotal' '''
# 	filename = '/Volumes/bakergroup$/results/bigtop20/' + str(scenario) + '/done_400_saturday/skims/accessibility.csv'
# 	try:
# 		accs = util.read_2dlist(filename, ',', True)
# 		print 'accs gen length: ', len(accs)
# 		print len(accs[0])

# 		return [sum([float(zonelist[2]) for zonelist in accs])/float(len(accs)), sum([float(zonelist[4]) for zonelist in accs])/float(len(accs))]
# 	except IOError as e:
# 		print e
# 		return [-1, -1]

def grab_cumulative_accessibility(scenario, mandatory = True):
	'''returns one value for mandatory accessibility across incomes and taz. averages over households, not people'''
	if mandatory == True:
		filename = 'bigDamagedTransitTake2accessibilityWoo/' + str(scenario) + '/accessibilities/mandatoryAccessibities.csv'
	else:
		filename = 'bigDamagedTransitTake2accessibilityWoo/' + str(scenario) + '/accessibilities/nonMandatoryAccessibities.csv'
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
		return sum(final_accs)/float(hh) #TODO: chang
	except IOError as e:
		print e
		return -1

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

def get_pop(taz, income_group):
	'''should return the population in a taz for a given income group'''

	#TODO

	#hack
	return get_numHouselholds(taz, income_group)

def get_totalHH(taz):
	'''taz is 1-1454, Returns the value of the number of households (not people!!!!!!) for this taz '''
	accs = util.read_2dlist('tazData2010.csv', ',', True)
	return float(accs[taz-1][4])

def grab_VMT(scenario):
	#TODO
	return -1

def grab_VHT(scenario):
	#TODO
	return -1


def grab_ita_bridges_vmt_vht(scenario):
	'''returns scenario id, percentage of bridges out, vmt and vht computed by iterative traffic assignment'''
	filename = '/Users/mahalia/ita/20130702_bridges_flow_paths_5eps_extensive.txt'
	try:
		other_table = util.read_2dlist(filename, ',', False) #no header
		print 'other table length: ', len(other_table)
		try:
			return [float(other_table[scenario][0]), float(other_table[scenario][7]), float(other_table[scenario][5]), float(other_table[scenario][6])]
		except TypeError as e:
			print e
			return [-1, 0, 527970705.812, 8065312.753712]
			# other_table[0] #no damage
	except IOError as e:
		print e
		return [-1, 0, 527970705.812, 8065312.753712]

def aggregate_results(scenario):

	other = grab_ita_bridges_vmt_vht(scenario) #4 numbers
	print 'other: ', other
	accs = grab_accessibility_by_income(scenario) # 4 lists
	acc_tot = grab_cumulative_accessibility(scenario, True) #
	acc_totn = grab_cumulative_accessibility(scenario, False) #

	vmt = grab_VMT(scenario) #1 number
	vht = grab_VHT(scenario) # 1 number

	finals = [] #output results
	# #package up other data
	# for ac in other:
	# 	finals.append(ac)
	# #package up accessiblity
	# for ac in accs:
	# 	finals.append(sum(ac)/float(len(ac)))
	# #package up accessiblity
	# for ac in acc_tot:
	# 	finals.append(sum(ac)/float(len(ac)))
	#TODO

	return finals

def aggregate_accessibility(folder_names):
	'''uses the accessibility results instead of the by-income ones to compute. tricky thing is that goes by different modes and by peak and off-peak. So, maybe it'd be better to get the one by income and then aggregate those?'''
	scenario_results = []
	for folder_name in folder_names:
		print 'starting folder: ', folder_name
		scenario_results.append(grab_cumulative_accessibility(folder_name))
	return scenario_results

def old_main():
	# cd /Volumes/bakergroup$/

	########################################
	#get results for the base case
	folder_name = 'base_no_road_damage_but_reduced_transit'
	folder_name = 'no_damage'
	base = aggregate_results(folder_name)
	print base
	base_results = [base]
	# print base_results
	# print ['scenario', 'bridge_per', 'vmt', 'vht', 'low_auto', 'med_auto', 'high_auto', 'veryhighauto', 'autoPeakTotal', 'autoOffPeakTotal'].append(base_results)
  	util.write_2dlist(time.strftime("%Y%m%d")+'_scen_bridge_tt_vmt_6acc_vmt_vhtbtop20.txt', base_results)

	########################################
	print 'now the next'
	#get results for all the other runs
	scenario_results = []
	folder_names = TARGETS #[261] #TARGETS
	for folder_name in folder_names:
		scenario_results.append(aggregate_results(folder_name))
	print 'base: ', base_results
	print 'scenaro: ', scenario_results
  	util.write_2dlist(time.strftime("%Y%m%d")+'_scen_bridge_tt_vmt_6acc_vmt_vhttop20261.txt', scenario_results)


def test():
	print get_numHouseholds(15, 'low')
	print get_totalHH(1)
	print grab_cumulative_accessibility(20)

def main():
	TARGETS = [20, 33, 36, 137, 142, 143, 144, 151, 152, 159, 166, 167, 171, 173, 183, 184, 192, 193, 194, 196, 205, 1676, 1692, 2851, 2914]# data within: 12-Dec-2013_12_3909_50_0.55556_25.mat #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
	# TARGETS = [20]
	y = aggregate_accessibility(TARGETS)
	util.write_list(time.strftime("%Y%m%d")+'_accessTot_fromMain.txt', y)

if __name__ == '__main__':
	main()
