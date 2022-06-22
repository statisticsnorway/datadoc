DATA sasdata;
LENGTH tekst $98;
tall=123;
tekst='Dette er en tekst';
dato=DHMS('09feb21'd, 15, 30, 16);
LABEL tall='Tall'
      tekst='Tekst'
	  dato='Dato';
FORMAT tall NUMX20.2
       dato DATETIME20.;
RUN;