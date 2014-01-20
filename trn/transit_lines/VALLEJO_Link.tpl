;;<<Trnbuild>>;;

link nodes=7611,8888,   speed=25, dist=9,  oneway=no, modes=91  ; Transbay Terminal Ramp
link nodes=8888,8887,   speed=25, dist=21, oneway=y,  modes=91  ; Outbound Bay Bridge Transbay Terminal Ramp
link nodes=8887,7014,   speed=25, dist=19, oneway=y,  modes=91  ; Outbound Bay Bridge Transbay Terminal Ramp
link nodes=7013,8888,   speed=25, dist=21, oneway=y,  modes=91  ; Inbound  Bay Bridge Transbay Terminal Ramp
link nodes=9865,9867,   speed=45, dist=48, oneway=y,  modes=91  ; Toll plaza bypass (not present in off-peak highway)
link nodes=9867,9869,   speed=45, dist=10, oneway=y,  modes=91  ; Toll plaza bypass (not present in off-peak highway)
link nodes=3147,12835,  speed=25, dist=2,  oneway=no, modes=91  ; Highway to park and ride pad
link nodes=2283,12843,  speed=25, dist=3,  oneway=no, modes=91  ; Highway to park and ride pad
link nodes=11042,12868, speed=25, dist=16, oneway=no, modes=91  ; Highway to park and ride pad
link nodes=8888,7598,   speed=25, dist=9,  oneway=no, modes=90  ; Transbay Terminal Ramp

LINE NAME="91_80SB", RUNTIME=27, FREQ[1]=90,
     FREQ[2]=15, FREQ[3]=30, FREQ[4]=15, FREQ[5]=30, ONEWAY=T,
     MODE=91, OWNER="20", COLOR=1, N=11792, -11656,
     11709, -11656, 11899, 11654, 11926, -11653, -11646, -11686,
     -11684, -11643, -9506, -9285, -9225, -20010, -9223,
     -9221, -9218, -9220, -8997, -8931, -8933, -9217, -8937, -8939,
     -8941, -20009, -8943, -20011, -8947, -20012, -8949, -20013,
     -8953, -20014, -8957, -8959, -8961, -2325, -2406, 2407
LINE NAME="91_85SB", RUNTIME=45, FREQ[1]=0, FREQ[2]=30, FREQ[3]=60,
     FREQ[4]=60, FREQ[5]=60, ONEWAY=T, MODE=91, OWNER="20", COLOR=1,
     N=11042, -11882, -11880, -11881,
     -11866, -20007, -9294, -20004, -9293, -20002, -9291, -9289,
     -11829, 11821, 11889, 11900, 11803, -11813, -9972, -9975,
     -9976, -11064, -11066, -11808, -8672, -11768, -11764, -11767,
     11083, 11772, 11773, 11019, 11735, 11018, 11733, 11721, 11715,
     11713, 11718, 11002, 11792, -11656, 11709
LINE NAME="91_85NB", RUNTIME=45, FREQ[1]=99.99,
     FREQ[2]=30, FREQ[3]=60, FREQ[4]=60, FREQ[5]=60, ONEWAY=T,
     MODE=91, OWNER="20", COLOR=1, N=11709, -11656,
     11792, 11002, 11718, 11713, 11715, 11721, 11733, 11018, 11735,
     11019, 11773, 11772, 11083, -11767, -11765, -11769, -8671,
     -11807, -11065, -11063, -9979, -9980, -9974, -11815, -11817,
     11803, 11900, 11889, 11821, -11822, -11830, -9288, -9286,
     -9290, -20003, -9292, -20005, -9295, -11879, -11880, -11882,
     11042
LINE NAME="91_80NB", RUNTIME=28, FREQ[1]=0,
     FREQ[2]=240, FREQ[3]=30, FREQ[4]=15, FREQ[5]=30, ONEWAY=T,
     MODE=91, OWNER="20", COLOR=1, N=2407, -2406, -8962,
     -8960, -8958, -8956, -8954, -8952, -8950, -8948, -8946, -20023,
     -8944, -8942, -8940, -8938, -8936, 8934, -8932, -2220, -2224,
     -2210, -2115, -2116, -2174, -2175, -2178, -2180, -2206, -11637,
     -11642, -11636, -11685, -11645, -11704, -11927, 11926, -11927,
     11654, 11899, -11656, 11709, -11656, 11792
LINE NAME="91_200SB", ONEWAY=T, OWNER="20", COLOR=1, 
     MODE=91, RUNTIME=60, FREQ[1]=90, FREQ[2]=80, FREQ[3]=0,
     FREQ[4]=80, FREQ[5]=75, N=11792, -11656, -11649, -11091,
     -11650, -11651, -11644, -11643, -9506, -9285, -9225,
     -20010, -9223, -9221, -9218, -9220, -8997, -8931, -8933, -9217,
     -8937, -8939, -8941, -20009, -8943, -20011, -8947, -20012,
     -8949, -20013, -8953, -20014, -8957, -8959, -8961, -20015,
     -8965, -20016, -8969, -20017, -8973, -20018, -8977, -8979,
     -20019, -8983, -20020, -8987, -20021, -8991, -8993, -9863,
     -9861, -9865, -9867, -9869, -2803, -2783, -6972, -6968, -6970,
     -7016, -7013, -6976, -7611, -7612, -7609, -7608, -7614, -7616,
     -7623, 7624
LINE NAME="91_200NB", ONEWAY=T, OWNER="20", COLOR=1, MODE=91,
     RUNTIME=60, FREQ[1]=0, FREQ[2]=60, FREQ[3]=240, FREQ[4]=60,
     FREQ[5]=75, N=7624, -7623, -7616, -7614, -7608,
     -7609, -7612, -7599, -7598, -6979, -6980, -7014, -7017, -6971,
     -6969, -6973, -2784, -2802, -2787, -2766, -8995, -8994, -8992,
     -8990, -8988, -8986, -8984, -8982, -8980, -8978, -8976, -8975,
     -8974, -20022, -8972, -8970, -8968, -8966, -8964, -8962, -8960,
     -8958, -8956, -8954, -8952, -8950, -8948, -8946, -20023, -8944,
     -8942, -8940, -8938, -8936, -8934, -8932, -2220, -2224, -2210,
     -2115, -2116, -2174, -2175, -2178, -2180, -2206, -11637,
     -11642, -11644, -11651, -11650, -11091, -11649, -11656, 11792
LINE NAME="91_78NB", RUNTIME=38, ONEWAY=T, MODE=91, 
     OWNER="18", COLOR=8, FREQ[1]=0, FREQ[2]=30,
     FREQ[3]=60, FREQ[4]=30, FREQ[5]=120, N=1956, -8148, -8146,
     -1954, -1974, -1973, -2082, -2075, -2077, -2036, -9739, -9740,
     -9236, -9239, -9241, -10036, -20000, -9243, -9244, -10603,
     -10602, -10007, -2142, -11596, -11624, -11599, -10274, -10273,
     11595, -11618, 11105, 11367, 11635, 11611, -11612, -11613,
     -11614, -11659, -11657, -11668, -11704, -11927, 11926, -11927,
     -11654, -11899, -11656, 11709, -11656, 11792
LINE NAME="91_78SB", RUNTIME=53, ONEWAY=T, MODE=91, 
     OWNER="18", COLOR=8, FREQ[1]=99.99, FREQ[2]=30,
     FREQ[3]=60, FREQ[4]=30, FREQ[5]=240, N=11792, -11656, 11709,
     -11656, -11899, -11654, 11926, -11653, -11647, -11658, -11661,
     -11641, -11640, -11639, 11611, 11635, 11367, 11105, -11618,
     11595, -10273, -11598, -11623, -11597, -11683, -2131, -10009,
     -9247, -9248, -20001, -9242, -10038, -9240, -10668, -9238,
     -10667, -10666, -9234, -10665, -2171, -2073, -1934, -1932,
     -2415, 2087, -8156, -8143, -8145, -1957, -8149, 1956
LINE NAME="91_80ASB", RUNTIME=40, FREQ[1]=45,
     FREQ[2]=0, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0, ONEWAY=T, MODE=91,
     OWNER="20", COLOR=1, N=11735, 11018, 11733, 11721,
     11715, 11713, 11718, 11002, 11792, -11656, 11709, -11656,
     11899, 11654, 11926, -11653, -11646, -11686, -11684, -11643,
     -9506, -9285, -9225, -20010, -9223, -9221, -9218, -9220,
     -8997, -8931, -8933, -9217, -8937, -8939, -8941, -20009, -8943,
     -20011, -8947, -20012, -8949, -20013, -8953, -20014, -8957,
     -8959, -8961, -2325, -2406, 2407
LINE NAME="91_80ANB", RUNTIME=28, FREQ[1]=60,
     FREQ[2]=15, FREQ[3]=0, FREQ[4]=0, FREQ[5]=0, ONEWAY=T, MODE=91,
     OWNER="20", COLOR=1, N=2407, -2406, -8962, -8960,
     -8958, -8956, -8954, -8952, -8950, -8948, -8946, -20023, -8944,
     -8942, -8940, -8938, -8936, 8934, -8932, -2220, -2224, -2210,
     -2115, -2116, -2174, -2175, -2178, -2180, -2206, -11637,
     -11642, -11636, -11685, -11645, -11704, -11927, 11654, 11899,
     -11656, 11709, -11656, 11792
LINE NAME="91_78ANB", RUNTIME=18, ONEWAY=T, MODE=91, 
     OWNER="18", COLOR=8, FREQ[1]=90, FREQ[2]=240,
     FREQ[3]=0, FREQ[4]=0, FREQ[5]=0, N=11105, 11367, 11635, 11611,
     -11612, -11613, -11614, -11659, -11657, -11668, -11704, -11927,
     11926, -11927, -11654, -11899, -11656, 11709, -11656, 11792