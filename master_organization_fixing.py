#Author: Mahalia Miller
#Project: Finnland here I come!
#Date: Jan 16, 2013

'''On Jan. 14th I noted a mismatch between the network links and the bridges in the master_dict. So, this file aims to remedy that problem. The strategy is:
go through the table from ArcGIS. Try to get a match in nbiLoren_just1743wPrefix of the Bridge_Number string. Then, go back into the master_dict and fix up that entry.'''

import util, pickle, pdb, string

def clean_up(master_dict):
	'''clears many values in dict'''
	for key in master_dict.keys():
		master_dict[key]['loren_row_number'] = -1
		master_dict[key]['jessica_id'] = -1
		master_dict[key]['a_b_pairs_direct'] = []
		master_dict[key]['a_b_pairs_indirect'] = []
		master_dict[key]['edge_ids_direct'] = []
		master_dict[key]['edge_ids_indirect'] = []
	return master_dict

def update_ids(master_dict, arcgis_table, nbi_table_full, nbi_table_1743):

	#create a little bridge_number to new id dict
	bn_ni = {}
	for row in nbi_table_1743:
		bn_ni[row[1]] = int(row[0])

	#create a little new id to original (internal) id dict
	ni_oi = {}
	for key in master_dict.keys():
		ni_oi[master_dict[key]['new_id']] = key
		assert int(key) == int(master_dict[key]['original_id']), 'the key and the original (internal) id should be the same'

	#now let's loop through the arcgis table (the only thing we can be confident about)
	counter = 0
	good_counter = 0
	zero_counter = 0
	for row in arcgis_table:
		new_id_temp = -1
		Bridge_number_temp = row[4] #might have extra quotation marks
		if Bridge_number_temp.startswith('"') and Bridge_number_temp.endswith('"'):
			Bridge_number_temp = Bridge_number_temp[1:-1]
		jessica_id_temp = int(float(row[3]))
		try:
			new_id_temp = bn_ni[Bridge_number_temp]
			original_id_temp = ni_oi[new_id_temp] #this is the key for master dict!
			#ha! We now know the new id and the original id

			#fix ids
			master_dict[original_id_temp]['loren_row_number'] = jessica_id_temp + 1
			master_dict[original_id_temp]['jessica_id'] = jessica_id_temp
			# master_dict[original_id_temp]['a_b_pairs_direct'] = 
			# master_dict[original_id_temp]
			# master_dict[original_id_temp]
			# master_dict[original_id_temp]
			good_counter += 1
		except KeyError:
			if float(row[-2]) > 0.01:
				counter +=1

			else:
				zero_counter += 1
				# pdb.set_trace()

	print 'this is how many bridges we did not have in our new id table (should be 11261-1743=9518 plus zeros below): ,', counter
	print 'this is how many bridges I found: ,', good_counter
	print 'and zeros: ', zero_counter
	assert zero_counter + good_counter + counter == len(arcgis_table), 'counters should add up'
	return master_dict

def update_edge_info(master_dict, nbi_table_full):
	'''update the (a,b) pairs and edge ids
			a_b_pairs_direct: list of (a,b) tuples that would be directly impacted by bridge damage (bridge is carrying these roads)
		a_b_pairs_indirect: ditto but roads under the indirectly impacted bridges
		edge_ids_direct: edge object IDS for edges that would be directly impacted by bridge damage
		edge_ids_indirect: ditto but roads under the indirectly impacted bridges
		'''
	#add edge object IDs and (A,B) pairs for edges related to each bridge

	#load file that converts an edge id to a, b pair
	with open('input/20130123_mtc_edge_dict.pkl', 'rb') as f:
		edge_dict = pickle.load(f) #NOTE: this is directly from the first 3 entries of each row of 20120711EdgesLatLong.txt, which is the exported table from the MTC arcgis model

	edge_array = util.read_2dlist('input/20120711EdgesLatLong.txt',',', True)

	#create a little jessica id to original (internal) id dict
	ji_oi = {}
	for key in master_dict.keys():
		ji_oi[master_dict[key]['jessica_id']] = key
		assert int(key) == int(master_dict[key]['original_id']), 'the key and the original (internal) id should be the same'


	#load file that jessica made that tells edge ids affected by bridge failures
	row_index = 0
	co = 0
	real_counter = 0
	dummy_counter = 0
	missing_index_counter = 0
	# jessica_to_original = {}
	with open('/Users/mahalia/Documents/Fruehling2012/summerInterns/justBridgesFinal2.csv', 'rb') as f:
		rows = f.readlines()
		print 'number of rows in just bridges final: ', len(rows)
		for row in rows:
			row_index+=1
			direct_edges = []
			indirect_edges = []
			direct_list = []
			indirect_list = []
			tokens = row.split(',')
			if float(tokens[1])>= 0: #our code that it seems reasonable
				co+=1
				for token in tokens[2:15]:
					if len(token)>2:
						direct_edges.append(int(token))
				for token in tokens[15:]:
					if len(token)>2:
						indirect_edges.append(int(token))	
				#now we have the edge object IDs. Let us now find the a,b pairs.
				try:
					for edge in direct_edges:
						#check if FT = 6, which means a dummy link http://analytics.mtc.ca.gov/foswiki/Main/MasterNetworkLookupTables
						try:
							if int(edge_array[int(edge) -1 ][13]) != 6:
								pair = edge_dict[edge]
								direct_list.append((pair[0], pair[1]))
								real_counter += 1
							else:
								dummy_counter += 1
						except IndexError:
							print 'bad index: ', int(edge)
					for edge in indirect_edges:
					#check if FT = 6, which means a dummy link http://analytics.mtc.ca.gov/foswiki/Main/MasterNetworkLookupTables
						try:
							if int(edge_array[int(edge) -1 ][13]) != 6:
								pair = edge_dict[edge]
								indirect_list.append((pair[0], pair[1]))
								real_counter +=1
							else:
								dummy_counter +=1
						except IndexError:
							print 'bad index: ', int(edge)
				except KeyError as e:
					print 'key error: ', e 
			#now get the bridge key
			try:
				bridge_key = ji_oi[int(tokens[0])]
			except:
				#this is a bridge somehow not in our 1743 bridges in our master_dict. Explanations include duplicate and no structural demand capacity info. If truly worried, change this code.
				try:
					if float(nbi_table_full[int(tokens[0]) -1][-2]) > 0.01: #checked it out!
						# print 'missing one: ', tokens
						# print nbi_table_full[int(tokens[0]) -1]
						missing_index_counter += 1
				except:
					pass #probably a #n/a
			master_dict[bridge_key]['a_b_pairs_direct'] = direct_list
			master_dict[bridge_key]['a_b_pairs_indirect'] = indirect_list
			master_dict[bridge_key]['edge_ids_direct'] = direct_edges
			master_dict[bridge_key]['edge_ids_indirect'] = indirect_edges

	print 'real counter total: ', real_counter
	print 'dummy counter total (we did not damage these since they are fake): ', dummy_counter
	print 'missing index counter (these are rows of the table created by Jessica for which we did not add edges to the master dict, whether due to duplication (that we eliminated on purpose) or error): ', missing_index_counter
	return master_dict

def main():
	#get the buggy master dict
	with open('input/20130518_master_bridge_dict.pkl','rb') as f:
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

	#Now, recognizing that loren_row_number, jessica_id and all the edge stuff is incorrect, clear it.
	master_dict = clean_up(master_dict)

	#now that felt good! On to using some tables of known data to update the ids
	arcgis_table = util.read_2dlist('input/20140116_arcgissummer2012.txt', delimiter=',', skipheader=True) #Bridge_number is the 4th column (counting starting at 0th), BRIDGEID is 3rd
	nbi_table_full = util.read_2dlist('/Users/mahalia/Documents/Fruehling2012/summerInterns/NBIDatabaseLoren2.csv', delimiter=',', skipheader=True) #Bridge_number is the 1st column (counting starting at 0th), Loren row number is the row (where the header is the 1st. Wow, confusing!)
	nbi_table_1743 = util.read_2dlist('/Users/mahalia/Documents/fruehling2013/nbiLoren_just1743wPrefix_sorted_v1.csv', delimiter=',', skipheader=False) #no header #Bridge_number is the 1st column (counting starting at 0th), new id is the 0th column. Changed row 1674 (starting at 0), the bridge id to 23 0179F from 23 0178F
	master_dict = update_ids(master_dict, arcgis_table, nbi_table_full, nbi_table_1743)

	#now, let us update the edge info
	master_dict = update_edge_info(master_dict, nbi_table_full)

	test(master_dict, arcgis_table, nbi_table_full, nbi_table_1743)

	with open('input/20130114_master_bridge_dict.pkl', 'wb') as f:
		pickle.dump(master_dict, f)
def test(master_dict, arcgis_table, nbi_table_full, nbi_table_1743):
	matlab_table = util.read_2dlist('input/20140114_hwyBridges1743PlusBART.txt')
	for key in master_dict.keys():
		supposed_loren_id = master_dict[key]['loren_row_number']
		supposed_new_id = master_dict[key]['new_id']

		try:
			assert nbi_table_full[supposed_loren_id - 2][0] == nbi_table_1743[supposed_new_id - 1][1], 'these bridge numbers should be the same'
			assert float(nbi_table_full[supposed_loren_id - 2][-2]) == float(nbi_table_1743[supposed_new_id - 1][-2]), 'structural demand capacity should also be the same'
			assert float(nbi_table_full[supposed_loren_id - 2][-2]) == float(matlab_table[supposed_new_id - 1][6]), 'structural demand capacity should also be the same'
		except AssertionError:
			print supposed_loren_id
			print supposed_new_id
			print 'first one: ', nbi_table_full[supposed_loren_id - 2][0]
			print 'small one: ', nbi_table_1743[supposed_new_id - 1][1]
			print master_dict[key]
			print nbi_table_1743[supposed_new_id - 1][-1]
			print nbi_table_full[supposed_loren_id - 2][-1]
			print matlab_table[supposed_new_id - 1]

		#now let us check lat/lon
			assert float(nbi_table_full[supposed_loren_id - 2][7]) == float(nbi_table_1743[supposed_new_id - 1][8]), 'latitude should also be the same'
			assert float(nbi_table_full[supposed_loren_id - 2][7]) == float(matlab_table[supposed_new_id - 1][2]), 'latitude should also be the same'
if __name__ == '__main__':
	main()