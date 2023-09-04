$TITLE OD ESTIMATION PROBLEM
OPTIONS  ITERLIM=10000 , RESLIM = 1200 , SYSOUT = OFF, SOLPRINT = OFF, RMINLP = MINOS55,OPTCR= 0.1, LIMROW = 0, LIMCOL = 0;
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\sets.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\index.inc
*$include D:\TrafficBalanceTools_D4\TrafficCountBalance\weight.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\observetraveltime.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\linkseg.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\Weave.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\BPR.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\VC.inc
$include D:\TrafficBalanceTools_D4\TrafficCountBalance\FF.inc


parameter alpha1 is the scaling factor for the variable lowest limit;
alpha1=0;
parameter alpha2 is the scaling factor for the variable lowest limit;
alpha2=1.0;
Parameter OBSSEGTT(J,T) is the observed travel time by NPMRDS segment;
OBSSEGTT(J,T)=sum(I$Linkseg(I,J),OBSTT(I,T)*Linkseg(I,J));

VARIABLES
BPRPARA(J,M,N) is the BPR parameter d;
BPRPARA.lo(J,M,N)=alpha1*BPR(J,M,N);
BPRPARA.L(J,M,N) = BPR(J,M,N);
*VARIABLES
*CAPFACPARA(J,T) is the Capacity factor parameter d;
*CAPFACPARA.lo(J,T)=0.7;
*CAPFACPARA.L(J,T) = 1.0;

*Assign an intial point to decision variable
VARIABLE
OBJ     sum of deviations between observed link volume and estimated link volume
;
EQUATIONS
OBJF    define objective function
*EqualDemand(J,T) define the constrain of demand conservation
*TODDemand(I) define the constrain of traffic equilibrium every Segment for all TOD period
;

*OBJF.. OBJ =E=SUM((I,T)$(OBSFLOW(I,T) gt 0),sqr((Demand(I,T)- OBSFLOW(I,T))/OBSFLOW(I,T))*Weight(I,T));

*EqualDemand(J,T)..sum(I, Demand(I,T)*LINKP(I,J,T))=E=0;
*TODDemand(I)..(Demand(I,"1")-Demand(I,"2")-Demand(I,"3")-Demand(I,"4")-Demand(I,"5")-Demand(I,"6"))*TODFactor(I)=E=0;
OBJF.. OBJ =E=SUM((J,T)$(OBSSEGTT(J,T) gt 0),sqr(sum(I$linkseg(I,J),(FF(I)*(1+VC(I,T)*(BPRPARA(J,"1","1")$(WEAVE(I)=0)+BPRPARA(J,"2","1")$(WEAVE(I)>0))+(BPRPARA(J,"1","2")$(WEAVE(I)=0)+BPRPARA(J,"2","2")$(WEAVE(I)>0))*(VC(I,T))**(BPRPARA(J,"1","3")$(WEAVE(I)=0)+BPRPARA(J,"2","3")$(WEAVE(I)>0)))- OBSTT(I,T)))/OBSSEGTT(J,T)))+
0.001*sum((J,M,N)$(ord(N) = card(N)),sqr((BPRPARA(J,M,N)-BPR(J,M,N))/BPR(J,M,N)))+0.001*sum((J,M,N)$(ord(N) <> card(N)),sqr((BPRPARA(J,M,N)-BPR(J,M,N))/BPR(J,M,N)));
MODEL ODE /ALL/;
file fopt /minos55.opt/;
put fopt;
put "superbasics limit 10000"/;
putclose;
ODE.optfile=1;
ODE.workspace = 750;
SOLVE ODE USING RMINLP MINIMIZING OBJ;
File estdemand /D:\TrafficBalanceTools_D4\TrafficCountBalance\BalancedTrafficCount.dat/;
put estdemand;
loop((J,M,N), put J.tl:>4:1; put M.tl:>4:1; put N.tl:>4:1;put BPRPARA.L(J,M,N):>12:5; put /;);

*File estdemand1 /D:\TrafficBalanceTools_D4\TrafficCountBalance\capacityAdj.dat/;
*put estdemand1;
*loop((J,T), put J.tl:>4:1; put T.tl:>4:1; put CAPFACPARA.L(J,T):>12:5; put /;);

DISPLAY OBJ.L;
DISPLAY BPRPARA.L;
*DISPLAY CAPFACPARA.L;
