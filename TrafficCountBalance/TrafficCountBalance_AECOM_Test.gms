$TITLE OD ESTIMATION PROBLEM
OPTIONS  ITERLIM=2000 , RESLIM = 1200 , SYSOUT = OFF, SOLPRINT = OFF, RMINLP = MINOS55,OPTCR= 0.1, LIMROW = 0, LIMCOL = 0;
$include C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\sets.inc
$include C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\index.inc
$include C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\weight.inc
$include C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\observecount.inc
$include C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\LP_Flow.inc


parameter alpha1 is the scaling factor for the variable lowest limit;
alpha1=0;
parameter alpha2 is the scaling factor for the variable lowest limit;
alpha2=1.5;

VARIABLES
Demand(I,T)   demand on OD pair (ij) departing at time d;
Demand.lo(I,T)=(alpha1*OBSFLOW(I,T));
Demand.L(I,T) = (alpha1*OBSFLOW(I,T));
*Assign an intial point to decision variable
VARIABLE
OBJ     sum of deviations between observed link volume and estimated link volume
;
EQUATIONS
OBJF    define objective function
EqualDemand(J,T) define the constrain of demand conservation
TODDemand(I) define the constrain of traffic equilibrium every Segment for all TOD period
;

OBJF.. OBJ =E=SUM((I,T)$(OBSFLOW(I,T) gt 0),sqr((Demand(I,T)- OBSFLOW(I,T))/OBSFLOW(I,T))*Weight(I,T));

EqualDemand(J,T)..sum(I, Demand(I,T)*LINKP(I,J,T))=E=0;
TODDemand(I)..(Demand(I,"1")-Demand(I,"2")-Demand(I,"3")-Demand(I,"4")-Demand(I,"5"))=E=0;

MODEL ODE /ALL/;
file fopt /minos55.opt/;
put fopt;
put "superbasics limit 10000"/;
putclose;
ODE.optfile=1;
ODE.workspace = 750;
SOLVE ODE USING RMINLP MINIMIZING OBJ;
File estdemand /C:\Projects\Florida_D5Project\TrafficCountBalance\GAMSProgram\TrafficCountBalance\BalancedTrafficCount.dat/;
put estdemand;
loop((I,T)$(Demand.L(I,T) gt 0), put I.tl:>4:1; put T.tl:>4:1; put Demand.L(I,T):>12:4; put /;);
DISPLAY OBJ.L;
DISPLAY Demand.L;
