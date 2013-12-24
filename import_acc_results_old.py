#Author: mahalia miller

import util
import numpy as np
import time

# TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data
TARGETS = [12, 35, 55, 71, 75, 82, 86, 87, 88, 106, 108, 115, 121, 231, 241, 247, 256, 258, 260, 261, 676, 730, 733, 1231, 1548] #indices between 0 and 2110. the scenarios for which you want to save the damaged bridge data

def grab_accessibility_by_income(scenario):
	'''returns list of lists. Inner lists are low income total mandatory accessiblity, ... very high total mandatory accessibility as well as TODO: low income total non-mandatory accessiblity, ... very high total non-mandatory accessibility'''
	# filename = '/Volumes/bakergroup$/results/big/' + str(scenario) + '/accessibilities/mandatoryAccessibilities.csv'
	filename = '/Volumes/bakergroup$/results/bigtop20/' + str(scenario) + '/done_400_saturday/accessibilities/mandatoryAccessibities.csv'
	try:
		accs = util.read_2dlist(filename, ',', True)
		print 'accs  length: ', len(accs)
		print len(accs[0])

		good_accs = [[float(row[0]), float(row[3]), float(row[6]), float(row[9])] for row in accs]
		final_accs = []
		# for subzone in range(0, len(good_accs), 3):
		# 	final_accs.append()
		print 'good acs len: ', len(good_accs)
		for acc in range(len(good_accs[0])):
			final_accs.append(sum([subzonelist[acc] for subzonelist in good_accs])/float(len(good_accs))) #take average
		return final_accs
	except IOError as e:
		print e
		return [-1, -1]

def grab_general_accessibility(scenario):
	''' 'autoPeakTotal', 'autoOffPeakTotal' '''
	filename = '/Volumes/bakergroup$/results/bigtop20/' + str(scenario) + '/done_400_saturday/skims/accessibility.csv'

	try:
		accs = util.read_2dlist(filename, ',', True)
		print 'accs gen length: ', len(accs)
		print len(accs[0])

		return [sum([float(zonelist[2]) for zonelist in accs])/float(len(accs)), sum([float(zonelist[4]) for zonelist in accs])/float(len(accs))]
	except IOError as e:
		print e
		return [-1, -1]

def grab_VMT(scenario):
	return -1

def grab_VHT(scenario):
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
	acc_tot = grab_general_accessibility(scenario) # 2 lists
	vmt = grab_VMT(scenario) #1 number
	vht = grab_VHT(scenario) # 1 number

	finals = [] #output results
	#package up other data
	for ac in other:
		finals.append(ac)
	#package up accessiblity
	for ac in accs:
		finals.append(np.mean(ac))
	#package up accessiblity
	for ac in acc_tot:
		finals.append(np.mean(ac))	

	return finals


def main():
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


if __name__ == '__main__':
	main()
