;
;  Amtrak as of 11/8/10
;
LINK NODES= 14641,14643, TIME =19.0, DIST=660, ONEWAY=NO, MODES=131-132 ; San Jose - Great America
LINK NODES= 14643,14644, TIME =21.0, DIST=1080, ONEWAY=NO, MODES=131-132 ; Great America - Fremont
LINK NODES= 14644,14646, TIME =16.0, DIST=910, ONEWAY=NO, MODES=131-132 ; Fremont - Hayward
LINK NODES= 14646,14647, TIME =16.0, DIST=810, ONEWAY=NO, MODES=131-132 ; Hayward - Coliseum
LINK NODES= 14647,14648, TIME =10.0, DIST=510, ONEWAY=NO, MODES=131-132 ; Coliseum - Jack London Square
LINK NODES= 14648,14649, TIME =10.0, DIST=320, ONEWAY=NO, MODES=131-132 ; Jack London Square - Emeryville
LINK NODES= 14649,14650, TIME = 4.0, DIST=200, ONEWAY=NO, MODES=131-132 ; Emeryville - Berkeley
LINK NODES= 14650,14651, TIME = 8.0, DIST=560, ONEWAY=NO, MODES=131-132 ; Berkeley - Richmond
LINK NODES= 14651,14654, TIME =30.0, DIST=1310, ONEWAY=NO, MODES=131-132 ; Richmond - Martinez
LINK NODES= 14654,14655, TIME =19.0, DIST=1640, ONEWAY=NO, MODES=131-132 ; Martinez - Suisun/Fairfield
LINK NODES= 14654,14658, TIME =19.0, DIST=1740, ONEWAY=NO, MODES=131-132 ; Martinez - Antioch


; Amtrak Capitol from San Jose to Suisun/Fairfield
;
LINE NAME="131_CAP1NB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=120,
     FREQ[3]=240,
     FREQ[4]=80,
     FREQ[5]=240,
     runtime=146, 
     N=14641, 14643, 14644, 14646, 14647, 14648, 14649, 14650, 14651, 14654, 14655

; Amtrak Capitol from Suisun/Fairfield to San Jose
;
LINE NAME="131_CAP1SB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=80,
     FREQ[3]=120,
     FREQ[4]=120,
     FREQ[5]=240,
     runtime=151, 
	 N=14655, 14654, 14651, 14650, 14649, 14648, 14647, 14646, 14644, 14643, 14641

; Amtrak Capitol from Suisun/Fairfield to Jack London Square
;
LINE NAME="131_CAP2SB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=0,
     FREQ[3]=240,
     FREQ[4]=120,
     FREQ[5]=0,
     runtime=81, 
	 N=14655, 14654, 14651, 14650, 14649, 14648
	 
; Amtrak Capitol from Suisun/Fairfield to Coliseum
;
LINE NAME="131_CAP3SB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=80,
     FREQ[3]=240,
     FREQ[4]=0,
     FREQ[5]=0,
     runtime=88, 
	 N=14655, 14654, 14651, 14650, 14649, 14648, 14647	 
	 
; Amtrak Capitol from Coliseum to Suisun/Fairfield
;
LINE NAME="131_CAP2NB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=240,
     FREQ[3]=0,
     FREQ[4]=0,
     FREQ[5]=0,
     runtime=78, 
     N=14647, 14648, 14649, 14650, 14651, 14654, 14655 	 
     
; Amtrak Capitol from Jack London Square to Suisun/Fairfield
;
LINE NAME="131_CAP3NB", ONEWAY=T, MODE=131, OWNER="6", COLOR=10, 
     FREQ[1]=90,
     FREQ[2]=240,
     FREQ[3]=240,
     FREQ[4]=120,
     FREQ[5]=240,
     runtime=68, 
     N=14648, 14649, 14650, 14651, 14654, 14655      
 
; Amtrak San Joaquin from Jack London Square to Antioch
;
LINE NAME="132_SJQNB", ONEWAY=T, MODE=132, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=240,
     FREQ[3]=240,
     FREQ[4]=0,
     FREQ[5]=0,
     runtime=72, timefac=1.0,
     N=14648, 14649, 14650, 14651, 14654, 14658
 
; Amtrak San Joaquin from Antioch to Jack London Square
;
LINE NAME="132_SJQSB", ONEWAY=T, MODE=132, OWNER="6", COLOR=10, 
     FREQ[1]=0,
     FREQ[2]=0,
     FREQ[3]=240,
     FREQ[4]=240,
     FREQ[5]=0,
     runtime=87, 
	 N=14658, 14654, 14651, 14650, 14649, 14648