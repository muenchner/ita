'''Author: Mahalia Miller
Date: this file takes the bridge results and then gets them ready for a run in cube'''

import pickle, string, time, pdb, os
import networkx as nx

import util
from travel_main_simple_simplev3 import damage_highway_network, damage_transit_network

#first load the all-purpose dictionary linking info about the bridges
with open('input/20130114_master_bridge_dict.pkl','rb') as f:
	master_dict = pickle.load(f) #has 1743 keys. One per highway bridge. (NOT BART)
	'''
	dict with a bridge_key that ranges from 1 to 1889 and then the value is another dictionary with the following keys: 
	loren_row_number: the row number in Loren Turner's table that has info on all CA bridges (where the header line is row 0)
	original_id: the original id (1-1889)
	new_id: the new id that excludes filtered out bridges (1-1743). Bridges are filtered out if a.) no seismic capacity data AND non-transbay bridge or b.) not located by Jessica (no edge list). this id is the new value that is the column number for the lnsa simulations.
	jessica_id: the id number jessica used. it's also the number in arcgis.
	a_b_pairs_direct: list of (a,b) tuples that would be directly impacted by bridge damage (bridge is carrying these roads)
	a_b_pairs_indirect: ditto but roads under the indirectly impacted bridges
	edge_ids_direct: edge object IDS for edges that would be directly impacted by bridge damage
	edge_ids_indirect: ditto but roads under the indirectly impacted bridges
	mod_lnSa: median lnSa for the moderate damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
	ext_lnSa: median lnSa for the extensive damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
	com_lnSa: median lnSa for the complete damage state. the dispersion (beta) for the lognormal distribution is 0.6. (See hazus/mceer method)
	'''
with open('input/20140114_master_transit_dict.pkl','rb') as f:
	master_transit_dict = pickle.load(f) #the keys go from 17440 to 31520 One per BART structure. The new_id values go from 1744 to 3152!!

def intize_list(my_list):
	'''takes a list where elements are strings and makes them ints if it can'''
	return [int(string.strip(s)) for s in my_list]

def switch_old_ids_to_new(damaged_bridges_internal):
  	damaged_bridges_new = []
  	for b in damaged_bridges_internal:
  		if int(b) <= 1889:
	  		damaged_bridges_new.append(master_dict[b]['new_id'])
	  	else:
	  		damaged_bridges_new.append(master_transit_dict[b]['new_id'])
	return damaged_bridges_new

def post_process_bridges(bridge_list_internal, G, index):
	'''bridge list is a list of the original ids (1-1889, not the new ids 1-1743!!!!!!!) plus the transit ones (17440-315200)
	G is the graph. 
	index is the scenario id (start at 0 as in python indices)'''	
	damaged_bridges_new = switch_old_ids_to_new(bridge_list_internal)

	cube_folder_path = time.strftime("%Y%m%d")+'_filesForCube/'
	#road damage
	damage_highway_network(bridge_list_internal, G, cube_folder_path, index)
	#transit damage
	damage_transit_network(damaged_bridges_new, cube_folder_path, index) 

def retrofit(damaged_bridges_internal, holy_bridges):
	'''damaged bridges is a list of the original ids (1-1889, not the new ids 1-1743!!!!!!!) plus the transit ones (17440-315200)
	holy_bridges is new new ids (1-1743)'''
	try:
		if len(damaged_bridges_internal) > 0:
			b = damaged_bridges_internal[0].lower()
	except AttributeError:
		raise('Sorry. You must use the original ids, which are strings')
	new_list = []
	for site in damaged_bridges_internal:
	    if int(site) <= 1889: #in original ids, not new ones since that is what is in the damaged bridges list
	    	if master_dict[site]['new_id'] not in holy_bridges:
	    		new_list.append(site) #original ids
	    	else:
	    		'yo!!: this bridge is holy: ', master_dict[site]['new_id']
	    else: #probably can comment out since we are not retrofitting transit bridges
	    	if master_transit_dict[site]['new_id'] not in holy_bridges:
	    		new_list.append(site) #original ids
	    	else:
	    		'yo!!: this transit bridge is holy: ', master_transit_dict[site]['new_id']
	return new_list

def make_directories(scenario_indices):
	#make directories for these scenarios
	#input (transit). In one transit (trn) folder, I'll have a bunch of folders for different scenarios and then I can just copy over the three relevant files before each simulation (transit_lines.block, bart.tpl, muni.tpl)
	if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/'):
		os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/')	

	if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/trn_staging/'):
		os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/trn_staging/')	

	if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/'):
		os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/modCapacities/')

	#output
	if not os.path.isdir(time.strftime("%Y%m%d")+'_filesForCube/aa_new/'):
		os.mkdir(time.strftime("%Y%m%d")+'_filesForCube/aa_new/')

	for scenario in scenario_indices:
		#still input
		if not os.path.isdir(time.strftime("%Y%m%d") + '_filesForCube/trn_staging/' + str(scenario) + '/'):
		    os.mkdir(time.strftime("%Y%m%d") + '_filesForCube/trn_staging/' + str(scenario) + '/')

		#output
		if not os.path.isdir(time.strftime("%Y%m%d") + '_filesForCube/aa_new/' + str(scenario) + '/'):
		    os.mkdir(time.strftime("%Y%m%d") + '_filesForCube/aa_new/' + str(scenario) + '/')

def main():
	# holy_bridges = [1036, 991, 986, 483, 596,  692, 1095, 1193, 1520, 1322, 832, 1039, 1103, 1228,   663,  423,  914,  1015, 1378, 1102] #bridges for which we assume no damage. indices start at 1
	# holy_bridges = util.read_list('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/20140113_top435.txt')
	# holy_bridges = [int(b) for b in holy_bridges]
	holy_bridges = []
	print 'We are considering that this many bridges will not fail: ', len(holy_bridges) #in 1-1743 indices
	G = nx.read_gpickle("input/graphMTC_CentroidsLength6.gpickle")

	# with open('20131212_1eps_damagedBridges2.pkl', 'rb') as f:
	with open('2014_TODO.pkl', 'rb') as f:
		bridge_array_internal = pickle.load(f) #lists of damaged bridges by scenario. indices start at 1 (matlab indices). These are the original ids!! 1-1886 for hwy and 17440-31520 for transit

	# with open('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/20131212_25_scenario_indices_python_indices.txt', 'rb') as f:
	with open('/Users/mahalia/Documents/matlab/research/Herbst2011/output_data/2014_TODO.txt', 'rb') as f:
		scenario_indices = f.readlines()
	scenario_indices = intize_list(scenario_indices)

	make_directories(scenario_indices)

	new_bridge_array_internal = [bridge_array_internal[i] for i in scenario_indices]
	index = 0
	for damaged_bridge_list_internal in new_bridge_array_internal:
		retrofitted_damaged_bridge_list_internal = retrofit(damaged_bridge_list_internal, holy_bridges) #These are the original ids!! 1-1886 for hwy and 17440-31520 for transit
		post_process_bridges(retrofitted_damaged_bridge_list_internal, G, scenario_indices[index])
		index +=1



	# pdb.set_trace()

def test():
	holy_bridges = [1,2,3]
	print retrofit(['1','1','5','6'], holy_bridges)
	with open('20140116_0eps_damagedBridgesInternal.pkl', 'rb') as f:
		bridge_array_internal = pickle.load(f) #lists of damaged bridges by scenario. indices start at 1 (matlab indices). These are the original ids!! 1-1886 for hwy and 17440-31520 for transit
	with open('20140116_0eps_damagedBridgesNewID.pkl', 'rb') as f:
		bridge_array_new = pickle.load(f) #lists of damaged bridges by scenario. indices start at 1 (matlab indices). These are the original ids!! 1-1886 for hwy and 17440-31520 for transit

	assert switch_old_ids_to_new(bridge_array_internal[0]) == bridge_array_new[0], 'these should be equivalent'

if __name__ == '__main__':
	test()