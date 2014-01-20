'''
Author: Mahalia Miller
Date: Dec. 11, 2013
Project: graduating

This file provides some utilities for figuring out which transit parts to damage given that bridges are damaged. '''

import string
import shutil

'''list out all the bridge IDs of structures that impact the respective transit authorities. These are the new ids (1-1743)!!!! Not Jessica IDS or the old ones'''
VTA = [230, 270, 481, 261, 206, 48, 176, 237, 243, 325, 277, 85, 170, 178, 168, 87, 167, 163, 155, 145, 118, 117, 103, 119, 159, 262, 135, 200, 113]
MUNI = [964, 903, 864, 837, 939, 867, 873]
BART = range(1744, 3153)
CALTRAIN = [902, 842, 853, 1760, 652, 724, 669, 501, 689, 572, 692, 574, 564, 565, 57, 291, 101, 391, 311, 66, 168, 37, 216, 61]
PATH_TO_TRANSIT_FOLDER_COPY = '/Users/mahaliamiller/Desktop/trncopy/transit_lines/' #without modfications
PATH_TO_TRANSIT_FOLDER = 'test' #what I'll be changing

def damage_transit_file(filename, old_string, row_index_from_0):
	'''comments out whatever line is listed in old string. The row index is the index (from 0) in the file of this line. This redundancy makes sure we comment out the correct line.'''
	new_lines = []
	with open(PATH_TO_TRANSIT_FOLDER + filename, 'rb') as f:
		counter = 0
		for line in f:
			if line.strip() == old_string.strip() and counter == row_index_from_0:
				new_lines.append('; ' + line)
			else:
				new_lines.append(line)
			counter += 1

	with open(PATH_TO_TRANSIT_FOLDER + filename, 'wb') as f:
		f.writelines(new_lines)

def clear_transit_file(filename):
	'''copies over a file'''
	print 'from: ', PATH_TO_TRANSIT_FOLDER_COPY + filename
	print 'to: ', PATH_TO_TRANSIT_FOLDER + filename
	shutil.copy(PATH_TO_TRANSIT_FOLDER_COPY + filename, PATH_TO_TRANSIT_FOLDER + filename)
	

def damage_vta(damaged_bridge_list):
	'''this file damages the input files to the Cube model according to if any bridges that impact VTA Light Rail are damaged (all or nothing)'''
	problem_cases = set(damaged_bridge_list) & set(VTA) 
	print problem_cases
	if len(problem_cases) > 0:
		print 'vta lrt out'
		#vta is not functioning
		damage_transit_file('Transit_Lines.block', '    read  file = trn\SCVTA_LRT.tpl', 34)
	else:
		pass

def damage_muni(damaged_bridge_list, muni_dict):
	'''this file damages the input files to the Cube model according to which bridges crossing/supporting Muni lines are damaged. This is on a line by line basis.'''
	problem_cases = set(damaged_bridge_list) & set(MUNI) 

	for bridge in problem_cases:
		affected_line_list = muni_dict[str(bridge)]
		if affected_line_list['K'] == 1: #K line out
			print 'k line out'
			damage_transit_file('Munimetro.tpl', 'LINE NAME="110_K_Ingle", ONEWAY=F, MODE=110, OWNER="4",', 286)
			damage_transit_file('Munimetro.tpl', 'COLOR=11, ', 287)
			damage_transit_file('Munimetro.tpl', 'FREQ[1]=60,', 288)
			damage_transit_file('Munimetro.tpl', 'FREQ[2]=10,  ', 289)
			damage_transit_file('Munimetro.tpl', 'FREQ[3]=10,', 290)
			damage_transit_file('Munimetro.tpl', 'FREQ[4]=9,', 291)
			damage_transit_file('Munimetro.tpl', 'FREQ[5]=15,', 292)
			damage_transit_file('Munimetro.tpl', 'RUNTIME=42, ', 293)
			damage_transit_file('Munimetro.tpl', 'N=6847, -6846, -6823, -6862, 6883, -6884, 7225, 7230, 6888,', 294)
			damage_transit_file('Munimetro.tpl', '6898, -13611, 7244, 7243, 7242,   ', 295)
			damage_transit_file('Munimetro.tpl', '12408, 12407, 12406, 12405, 12404, 12403, 12402, 12401 ', 296)

		if affected_line_list['J'] == 1: #J line out
			print 'j line out'
			damage_transit_file('Munimetro.tpl', 'LINE NAME="110_J_Church", ONEWAY=F, MODE=110, OWNER="4",  ', 274)
			damage_transit_file('Munimetro.tpl', 'COLOR=11, ', 275)
			damage_transit_file('Munimetro.tpl', 'FREQ[1]=60,', 276)
			damage_transit_file('Munimetro.tpl', 'FREQ[2]=9,  ', 277)
			damage_transit_file('Munimetro.tpl', 'FREQ[3]=10,', 278)
			damage_transit_file('Munimetro.tpl', 'FREQ[4]=7,', 279)
			damage_transit_file('Munimetro.tpl', 'FREQ[5]=15,', 280)
			damage_transit_file('Munimetro.tpl', 'RUNTIME=56, ', 281)
			damage_transit_file('Munimetro.tpl', 'N=6847, 6846, 6872, -6866, 7158, -7157, 7304, 7159, 13582, 7308,', 282)
			damage_transit_file('Munimetro.tpl', '-7151, 7150, 7152, 13564, 13563, 13562, 13561, 12460,  ', 283)
			damage_transit_file('Munimetro.tpl', '12405, 12404, 12403, 12402, 12401', 284)

		if affected_line_list['N'] == 1: #N line out
			print 'n line out'
			damage_transit_file('Munimetro.tpl', 'LINE NAME="110_N_Judah", ONEWAY=F, MODE=110, OWNER="4", COLOR=11,   ', 326)
			damage_transit_file('Munimetro.tpl', 'FREQ[1]=30,', 327)
			damage_transit_file('Munimetro.tpl', 'FREQ[2]=7,  ', 328)
			damage_transit_file('Munimetro.tpl', 'FREQ[3]=10,', 329)
			damage_transit_file('Munimetro.tpl', 'FREQ[4]=7,', 330)
			damage_transit_file('Munimetro.tpl', 'FREQ[5]=12,', 331)
			damage_transit_file('Munimetro.tpl', 'RUNTIME=52, ', 332)
			damage_transit_file('Munimetro.tpl', 'N=13522, 13521, 13524, 13520, 13536, 13519, 7257, 7232, 7233,', 333)
			damage_transit_file('Munimetro.tpl', '12469, 12466, 12463, 12462, 12461, 12460, 12405, 12404, 12403,  ', 334)
			damage_transit_file('Munimetro.tpl', '12402, 12401, 6982, -6977, -7434, 7446, -7447, 7409, -7057, 6989', 335)

		if affected_line_list['T'] == 1: #T line out
			print 't out'
			damage_transit_file('Munimetro.tpl', 'LINE NAME="110_T", ONEWAY=F, MODE=110, OWNER="4", ', 346)
			damage_transit_file('Munimetro.tpl', 'COLOR=11, ', 347)
			damage_transit_file('Munimetro.tpl', 'FREQ[1]=30,', 348)
			damage_transit_file('Munimetro.tpl', 'FREQ[2]=10,  ', 349)
			damage_transit_file('Munimetro.tpl', 'FREQ[3]=10,', 350)
			damage_transit_file('Munimetro.tpl', 'FREQ[4]=9,', 351)
			damage_transit_file('Munimetro.tpl', 'FREQ[5]=12,', 352)
			damage_transit_file('Munimetro.tpl', 'RUNTIME=42, ', 353)
			damage_transit_file('Munimetro.tpl', 'N=7243, 7242,  ', 354)
			damage_transit_file('Munimetro.tpl', '12408, 12407, 12406, 12405, 12404, 12403, 12402,12401, ', 355)
			damage_transit_file('Munimetro.tpl', '6982, -6977, -7434, 7446, -7447, 7409, -7057,', 356)
			damage_transit_file('Munimetro.tpl', '6989, -6963, 7066, -7503, 6952, 6953, 6936, 6941, 6937, 6753, -6754,  ', 357)
			damage_transit_file('Munimetro.tpl', '6755, 13510, 6758, 6795, 13632, 6785, 6782, -6779, 6789, ', 358)		
			damage_transit_file('Munimetro.tpl', '6735, 6738, -6739, 6740 ', 359)
		

	pass




def damage_bart(damaged_bridge_list, bart_dict):
	'''this file damages the input files to the Cube model according to which BART structures are damaged. This is on a line by line basis.'''
	problem_cases = set(damaged_bridge_list) & set(BART) 
	print 'problem cases: ', problem_cases
	for bridge in list(problem_cases):
		affected_line_list = bart_dict[str(bridge)]
		print [k for k in affected_line_list.keys() if affected_line_list[k] ==1]
		if affected_line_list['milbraeRichmond'] == 1:
			print 'milbraeRichmond out'
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART1,ONEWAY=N,MODE=120,OWNER=2,COLOR=7,', 77)
			damage_transit_file('BART.TPL', 'FREQ[1]=15, FREQ[2]=15, FREQ[3]=15, FREQ[4]=15, FREQ[5]=0,', 78)
			damage_transit_file('BART.TPL', 'N= 15543 15541 15540 15539,', 79)
			damage_transit_file('BART.TPL', '15519 15518 15517 15516 15515 15514 15513 15512 15511 15510,', 80)	
			damage_transit_file('BART.TPL', '15509 15508 15507 15525 15523 15524 15522 15521 15520', 81)	

		if affected_line_list['richmondFreemont'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART2,ONEWAY=N,MODE=120,OWNER=2,COLOR=7,', 84)
			damage_transit_file('BART.TPL', 'FREQ[1]=15, FREQ[2]=15, FREQ[3]=15, FREQ[4]=15, FREQ[5]=20,', 85)
			damage_transit_file('BART.TPL', 'N=15526 15527 15528 15529 15530 15531,', 86)
			damage_transit_file('BART.TPL', '15532 15533 15534 15509 15508 15507 15525 15523 15524 15522 15521,', 87)	
			damage_transit_file('BART.TPL', '15520', 88)	

		if affected_line_list['sfoBayPoint'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART3,ONEWAY=N,MODE=120,OWNER=2,COLOR=7,', 91)
			damage_transit_file('BART.TPL', 'FREQ[1]=15, FREQ[2]=15, FREQ[3]=15, FREQ[4]=15, FREQ[5]=20,', 92)
			damage_transit_file('BART.TPL', 'N= 15542 15541 15540 15539,', 93)
			damage_transit_file('BART.TPL', '15519 15518 15517 15516 15515 15514 15513 15512 15511 15510,', 94)	
			damage_transit_file('BART.TPL', '15509 15508 15507 15506 15505 15504 15503 15502 15501 15535 15536', 95)	

		if affected_line_list['baypointMontgomery'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART4,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 98)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=99.99, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 99)
			damage_transit_file('BART.TPL', 'N= 15536 15535 15501 15502 15503 15504 15505 15506 15507, ', 100)
			damage_transit_file('BART.TPL', '15508 15509 15510 15511 15512    ', 101)	

		if affected_line_list['baypointDalyCity'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART4B,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 104)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=99.99, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 105)
			damage_transit_file('BART.TPL', 'N= 15536 15535 15501 15502 15503 15504 15505 15506 15507, ', 106)
			damage_transit_file('BART.TPL', '15508 15509 15510 15511 15512,', 107)	
			damage_transit_file('BART.TPL', '15513 15514 15515 15516 15517 15518 15519', 108)

		if affected_line_list['concordDalycity'] == 1:
			'''combining north concord and regular concord'''
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART5,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 111)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=99.99, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 112)
			damage_transit_file('BART.TPL', 'N= 15535 15501 15502 15503 15504 15505 15506 15507 15508 15509 15510,', 113)
			damage_transit_file('BART.TPL', '15511 15512 15513 15514 15515 15516 15517 15518 15519', 114)	
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART5A,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 117)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=60, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 118)
			damage_transit_file('BART.TPL', 'N= 15501 15502 15503 15504 15505 15506 15507 15508 15509 15510,', 119)
			damage_transit_file('BART.TPL', '15511 15512 15513 15514 15515 15516 15517 15518 15519', 120)	

		if affected_line_list['concord24st'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART5B,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 123)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=0, FREQ[3]=0, FREQ[4]=120, FREQ[5]=0,', 124)
			damage_transit_file('BART.TPL', 'N= 15501 15502 15503 15504 15505 15506 15507 15508 15509 15510,', 125)
			damage_transit_file('BART.TPL', '15511 15512 15513 15514 15515 15516	', 126)	
	
		if affected_line_list['pleasanthillDalycity'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART6,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 130)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=80, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 131)
			damage_transit_file('BART.TPL', 'N= 15502 15503 15504 15505 15506 15507 15508 15509 15510 15511 15512,', 132)
			damage_transit_file('BART.TPL', '15513 15514 15515 15516 15517 15518 15519', 133)	

		if affected_line_list['pleasanthillMontgomery'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART6A,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 136)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=80, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 137)
			damage_transit_file('BART.TPL', 'N= 15502 15503 15504 15505 15506 15507 15508 15509 15510 15511 15512', 138)
			
		if affected_line_list['montgomeryConcord'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART10,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 141)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=60, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0,', 142)
			damage_transit_file('BART.TPL', 'N= 15512 15511 15510 15509 15508 15507 15506 15505 15504 15503 15502 15501	', 143)
		
		if affected_line_list['24stBaypoint'] == 1:
			print '24b out'
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART3A,ONEWAY=Y,MODE=120,OWNER=2,COLOR=7,', 146)
			damage_transit_file('BART.TPL', 'FREQ[1]=0, FREQ[2]=0, FREQ[3]=0, FREQ[4]=120, FREQ[5]=0,', 147)
			damage_transit_file('BART.TPL', 'N= 15516 15515 15514 15513 15512 15511 15510,', 148)
			damage_transit_file('BART.TPL', '15509 15508 15507 15506 15505 15504 15503 15502 15501 15535 15536', 149)	

		if affected_line_list['dalycityDublin'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART7,ONEWAY=N,MODE=120,OWNER=2,COLOR=7,', 152)
			damage_transit_file('BART.TPL', 'FREQ[1]=15, FREQ[2]=15, FREQ[3]=15, FREQ[4]=15, FREQ[5]=20,', 153)
			damage_transit_file('BART.TPL', 'N= 15543 15542 15541 15540 15539,', 154)
			damage_transit_file('BART.TPL', '15519 15518 15517 15516 15515 15514 15513 15512 15511 15510 15534,', 155)	
			damage_transit_file('BART.TPL', '15533 15532 15531 15530 15537 -15545 15538', 156)

		if affected_line_list['dalycityFremont'] == 1:
			damage_transit_file('BART.TPL', 'LINE NAME=120_BART8,ONEWAY=N,MODE=120,OWNER=2,COLOR=7,', 159)
			damage_transit_file('BART.TPL', 'FREQ[1]=90, FREQ[2]=15, FREQ[3]=15, FREQ[4]=15, FREQ[5]=0,', 160)
			damage_transit_file('BART.TPL', 'N= 15519 15518 15517 15516 15515 15514 15513 15512 15511 15510 15534,', 161)
			damage_transit_file('BART.TPL', '15533 15532 15531 15530 15529 15528 15527 15526', 162)	
				

	pass

def damage_caltrain(damaged_bridge_list):
	'''this file damages the input files to the Cube model according to if any bridges that impact Caltrain are damaged (all or nothing)'''
	problem_cases = set(damaged_bridge_list) & set(CALTRAIN) 
	if len(problem_cases) > 0:
		#caltrain is not functioning
		print 'caltrain out'
		damage_transit_file('Transit_Lines.block', '    read  file = trn\CALTRAIN.tpl', 11)
	else:
		pass


def make_bart_dict():
	bart_dict = {}
	counter = 0
	with open('bart_bridge_to_line.csv', 'rb') as f: #1744 to 3152

		for line in f:
			if counter > 1:
				pieces = string.split(line, ',')
				if pieces[2] == '':
					'''this is probably not a structure that holds up or crosses a bart line. it could be something like an office building'''
					bart_dict[str(pieces[0])] = {'milbraeRichmond': 0, 'richmondFreemont': 0, 'sfoBayPoint': 0, 'baypointMontgomery': 0, 'baypointDalyCity': 0, 'concordDalycity': 0, 'concord24st': 0, 'pleasanthillDalycity': 0, 'pleasanthillMontgomery': 0, 'montgomeryConcord': 0, '24stBaypoint': 0, 'dalycityDublin': 0, 'dalycityFremont': 0}
				else:	
					bart_dict[str(pieces[0])] = {'milbraeRichmond': int(pieces[4]), 'richmondFreemont': int(pieces[5]), 'sfoBayPoint': int(pieces[6]), 'baypointMontgomery': int(pieces[7]), 'baypointDalyCity': int(pieces[8]), 'concordDalycity': int(pieces[9]), 'concord24st': int(pieces[10]), 'pleasanthillDalycity': int(pieces[11]), 'pleasanthillMontgomery': int(pieces[12]), 'montgomeryConcord': int(pieces[13]), '24stBaypoint': int(pieces[14]), 'dalycityDublin': int(pieces[15]), 'dalycityFremont': int(pieces[16])}
			counter += 1
	return bart_dict

def set_main_path(path_to_unmodified, path_to_what_I_will_modify):
	global PATH_TO_TRANSIT_FOLDER 
	PATH_TO_TRANSIT_FOLDER = path_to_what_I_will_modify
	global PATH_TO_TRANSIT_FOLDER_COPY
	PATH_TO_TRANSIT_FOLDER_COPY = path_to_unmodified

def make_muni_dict():
	muni_dict = {}
	muni_dict['964'] = {'N': 1, 'T': 1, 'K': 0, 'J': 0}
	muni_dict['903'] = {'N': 0, 'T': 1, 'K': 0, 'J': 0}
	muni_dict['864'] = {'N': 0, 'T': 0, 'K': 1, 'J': 0}
	muni_dict['837'] = {'N': 0, 'T': 0, 'K': 0, 'J': 1}
	muni_dict['939'] = {'N': 0, 'T': 0, 'K': 0, 'J': 1}
	muni_dict['867'] = {'N': 0, 'T': 0, 'K': 0, 'J': 1}
	muni_dict['873'] = {'N': 0, 'T': 0, 'K': 0, 'J': 1}
	return muni_dict

def main():

	set_main_path('/Users/mahaliamiller/Desktop/trn/transit_lines/', None)
	# bart_dict = make_bart_dict()
	# muni_dict = make_muni_dict()
	# clear_transit_file('Transit_Lines.block') #copies over a clean file
	# clear_transit_file('BART.TPL') #copies over a clean file
	# clear_transit_file('Munimetro.tpl') #copies over a clean file
	# damage_bart([800, 3145, 2130], bart_dict)
	# damage_caltrain([902])
	# damage_muni(MUNI, muni_dict) 
	# # damage_muni([864]) #k only
	# damage_vta([230])

def test():
	print PATH_TO_TRANSIT_FOLDER
	set_main_path('/Users/mahaliamiller/Desktop/trn/transit_lines/', None)
	print PATH_TO_TRANSIT_FOLDER

		#test if each go out
	damage_caltrain([902])
	damage_muni([873]) #should knock out J only
	# damage_muni([864]) #k only
	damage_vta([230])
	# #test if given bad input, don't comment out
	# damage_caltrain([1])
	# damage_muni([1])




if __name__ == '__main__':
	main()


