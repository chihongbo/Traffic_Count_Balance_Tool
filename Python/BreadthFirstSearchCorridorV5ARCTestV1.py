import networkx as nx
import csv
#from collections import defaultdict
from collections import deque
def generic_bfs_edges(G, corridor, neighbors=None):
    visited=set()
    queue=deque()
    Order=0
    
    Node0=corridor[0]
    source=corridor[1]
    NodeE=corridor[2]
    FTMainRg=corridor[3]
    FTRampRg=corridor[4]
    
    visited.add(Node0)
    visited.add(source)

    PCNT=G[Node0][source]['COUNT_DAIL']
    PFAC=G[Node0][source]['FacType']
    PREV=G[Node0][source]['LinkRev']
    
    
    NodeM=[]
    NodeR=[]
    FT1=0
    FT2=0
    FT3=0
    FTY=0
    
    if(PFAC in FTMainRg):
        FTY=1            ## parent link is Mainline 
    if(PFAC in FTRampRg):     
        if(PREV==1):     ## parent link is OnRamp
            FTY=2
        if(PREV==0):     ## parent link is Offramp
            FTY=3
    
    Order=Order+1
    print(Node0, source, Order, FTY )
    yield Node0, source, Order, FTY        ## output the first links 
    
    for node in neighbors(source):
        PFAC=G[source][node]['FacType']
        PREV=G[source][node]['LinkRev']
        
        if(node not in visited):
            if(PFAC in FTMainRg): ## for mainline
                NodeM.append(node)
                FT1= FT1+1
            elif(PFAC in FTRampRg): ## for Ramp
                NodeR.append(node)
                FT2= FT2+1
            else:
                FT3= FT3+1    # if any link is non-freeway related, then we do not add it to the queue
    #print (FT1, FT2, FT3, source, NodeM, NodeR)           
    if(FT1>0 and FT3==0 and node!=NodeE):
        queue.append((source, NodeM))
    if(FT2>0 and FT3==0 and node!=NodeE):
        queue.appendleft((source, NodeR))
    
       
    while queue:
        print(queue)
        parent, children = queue.popleft()
        
        for child in children:
            
            PCNT=G[parent][child]['COUNT_DAIL']
            PFAC=G[parent][child]['FacType']
            PREV=G[parent][child]['LinkRev']
            
            #if ((child not in visited and child!=NodeE) and ((PFAC in range(71,80) and (PCNT==0)) or (PFAC==11))):
            if ((child not in visited) and (PFAC in FTRampRg or PFAC in FTMainRg)):
                if (child==NodeE or PCNT>0):      ## corridor end node or with count link, yeild the link
                    if(PFAC in FTMainRg):
                        Order=Order+1
                        FTY=1
                        yield parent, child, Order, FTY  ## Main line
                        if(child==NodeE):
                            continue
                    elif(PFAC in FTRampRg):
                        if PREV==1:                      ## On ramp
                            Order=Order+1
                            FTY=2
                            yield child, parent, Order, FTY
                        if PREV==0:
                            Order=Order+1
                            FTY=3                        ## off ramp
                            yield parent, child, Order, FTY 
                        continue
  
                
                visited.add(child)
                NodeM=[]
                NodeR=[]
                NodeR1=[]
                FT1=0
                FT2=0
                FT3=0
                FT4=0
                
                for node in neighbors(child):
                    CFAC=G[child][node]['FacType']
                    CREV=G[child][node]['LinkRev']
                    if(node==parent):                           ## the neigbor is the parent link then stop here
                        continue
                    if(CFAC not in FTMainRg and CFAC not in FTRampRg): ## the child link is not highway related link
                        FT3=FT3+1
                    if(PFAC in FTRampRg and PREV!=CREV):   ## if child link direction is different parent (Ramp) direction, then stop
                        FT3=FT3+1
                    
                    if(node in visited):
                        if(PFAC in FTMainRg):                 # the parent link is mainline
                            if(CFAC in FTMainRg):
                                NodeM.append(node)    # if the child link is mainline, then add the node to queue at any time.
                                FT1=FT1+1
                            if(CFAC in FTRampRg): # if the child link is ramp, then add the node to a temp list
                                NodeR1.append((node,CREV))
                                FT4=FT4+1
                        if(PFAC in FTRampRg):     # if the parent link is ramp
                            if(CFAC in FTRampRg): # if the child link is also a ramp, then add the node to a temp list
                                NodeR1.append((node,CREV)) 
                                FT4=FT4+1
                        
                        
                    if(node not in visited):
                        if(PFAC in FTMainRg):                   ## if the parent link mainline, then the next searh can be ramp or mainline
                            if(CFAC in FTMainRg):               ## child link is also mainline
                                NodeM.append(node)
                                FT1=FT1+1
                            elif(CFAC in FTRampRg): ## child link is ramp
                                NodeR.append(node)
                                FT2=FT2+1
                            else:                      ## if mainline does not connect mainline or ramp, then stop
                                FT3=FT3+1
                        if(PFAC in FTRampRg):       ## Parent link is ramp type then the next search can only be in ramp, otherwise exit
                            if(CFAC in FTRampRg):   ## if the subramp is Ramp, then add the node to the queue
                                NodeR.append(node)
                                FT2=FT2+1
                            else:                      ## if ramp does not connect ramps then stop
                                FT3=FT3+1

                if(FT1>0 and FT3==0):
                    queue.append((child, NodeM))
                if(FT2>0 and FT3==0):
                    queue.appendleft((child, NodeR)) 
                if(FT3>0):                           ## the parent link must be ramp type and add nothing and yeild the parent link information
                    Order=Order+1
                    if(PREV==0):                       ## the parent ramp is offramp
                        if(PFAC in FTMainRg):
                            FTY=1           
                        else:
                            FTY=3
                        yield parent,child, Order, FTY
                    if(PREV==1):                      ## the parent ramp is onramp
                        FTY=2
                        yield child, parent, Order, FTY
                if(FT4>0 and FT3==0):
                     for item in NodeR1:
                         node, LREV=item
                         if(LREV==0):   ## off ramp
                             FTY=3
                             Order=Order+1
                             yield child, node, Order, FTY
                         if(LREV==1):   ## on ramp
                             FTY=2
                             Order=Order+1
                             yield node, child, Order, FTY

def generic_bfs_edges2(G, corridor, neighbors=None):
    visited=set()
    queue=deque()
    Order=0
    
    Node0=corridor[0]
    source=corridor[1]
    NodeE=corridor[2]
    FTMainRg=corridor[3]
    FTRampRg=corridor[4]
    
    visited.add(Node0)
    visited.add(source)

    PCNT=G[Node0][source]['COUNT_DAIL']
    PFAC=G[Node0][source]['FacType']
    PREV=G[Node0][source]['LinkRev']
    
    
    NodeM=[]
    NodeR=[]
    FT1=0
    FT2=0
    FT3=0
    FTY=0
    
    if(PFAC in FTMainRg):
        FTY=1            ## parent link is Mainline 
    if(PFAC in FTRampRg):     
        if(PREV==1):     ## parent link is OnRamp
            FTY=2
        if(PREV==0):     ## parent link is Offramp
            FTY=3
    
    Order=Order+1
    print(Node0, source, Order, FTY )
    yield Node0, source, Order, FTY        ## output the first links 
    
    for node in neighbors(source):
        PFAC=G[source][node]['FacType']
        PREV=G[source][node]['LinkRev']
        
        if(node not in visited):
            if(PFAC in FTMainRg): ## for mainline
                NodeM.append(node)
                FT1= FT1+1
            elif(PFAC in FTRampRg): ## for Ramp
                NodeR.append(node)
                FT2= FT2+1
            else:
                FT3= FT3+1    # if any link is non-freeway related, then we do not add it to the queue
    #print (FT1, FT2, FT3, source, NodeM, NodeR)           
    if(FT1>0 and FT3==0 and node!=NodeE):
        queue.append((source, NodeM))
    if(FT2>0 and FT3==0 and node!=NodeE):
        queue.appendleft((source, NodeR))
    
       
    while queue:
        print(queue)
        parent, children = queue.popleft()
        
        for child in children:
            
            PCNT=G[parent][child]['COUNT_DAIL']
            PFAC=G[parent][child]['FacType']
            PREV=G[parent][child]['LinkRev']
            
            #if ((child not in visited and child!=NodeE) and ((PFAC in range(71,80) and (PCNT==0)) or (PFAC==11))):
            if ((child not in visited) and (PFAC in FTRampRg or PFAC in FTMainRg)):
                if (child==NodeE or PCNT>0):      ## corridor end node or with count link, yeild the link
                    if(PFAC in FTMainRg):
                        #Order=Order+1  ## for mainline, we do not need to update it order anymore if we only want the mainline volume
                        FTY=1
                        yield parent, child, Order, FTY  ## Main line
                        if(child==NodeE):
                            continue
                    elif(PFAC in FTRampRg):
                        if PREV==1:                      ## On ramp
                            Order=Order+1
                            FTY=2
                            yield child, parent, Order, FTY
                        if PREV==0:
                            Order=Order+1
                            FTY=3                        ## off ramp
                            yield parent, child, Order, FTY 
                        continue
                elif(PFAC in FTMainRg):     ##  yeild the mainline link  
                    FTY=1
                    yield parent, child, Order, FTY  ## Main line link without count
                
                
                visited.add(child)
                NodeM=[]
                NodeR=[]
                NodeR1=[]
                FT1=0
                FT2=0
                FT3=0
                FT4=0
                
                for node in neighbors(child):
                    CFAC=G[child][node]['FacType']
                    CREV=G[child][node]['LinkRev']
                    if(node==parent):                           ## the neigbor is the parent link then stop here
                        continue
                    if(CFAC not in FTMainRg and CFAC not in FTRampRg): ## the child link is not highway related link
                        FT3=FT3+1
                    if(PFAC in FTRampRg and PREV!=CREV):   ## if child link direction is different parent (Ramp) direction, then stop
                        FT3=FT3+1
                    
                    if(node in visited):
                        if(PFAC in FTMainRg):                 # the parent link is mainline
                            if(CFAC in FTMainRg):
                                NodeM.append(node)    # if the child link is mainline, then add the node to queue at any time.
                                FT1=FT1+1
                            if(CFAC in FTRampRg): # if the child link is ramp, then add the node to a temp list
                                NodeR1.append((node,CREV))
                                FT4=FT4+1
                        if(PFAC in FTRampRg):     # if the parent link is ramp
                            if(CFAC in FTRampRg): # if the child link is also a ramp, then add the node to a temp list
                                NodeR1.append((node,CREV)) 
                                FT4=FT4+1
                        
                        
                    if(node not in visited):
                        if(PFAC in FTMainRg):                   ## if the parent link mainline, then the next searh can be ramp or mainline
                            if(CFAC in FTMainRg):               ## child link is also mainline
                                NodeM.append(node)
                                FT1=FT1+1
                            elif(CFAC in FTRampRg): ## child link is ramp
                                NodeR.append(node)
                                FT2=FT2+1
                            else:                      ## if mainline does not connect mainline or ramp, then stop
                                FT3=FT3+1
                        if(PFAC in FTRampRg):       ## Parent link is ramp type then the next search can only be in ramp, otherwise exit
                            if(CFAC in FTRampRg):   ## if the subramp is Ramp, then add the node to the queue
                                NodeR.append(node)
                                FT2=FT2+1
                            else:                      ## if ramp does not connect ramps then stop
                                FT3=FT3+1

                if(FT1>0 and FT3==0):
                    queue.append((child, NodeM))
                if(FT2>0 and FT3==0):
                    queue.appendleft((child, NodeR)) 
                if(FT3>0):                           ## the parent link must be ramp type and add nothing and yeild the parent link information
                    Order=Order+1
                    if(PREV==0):                       ## the parent ramp is offramp
                        if(PFAC in FTMainRg):
                            FTY=1           
                        else:
                            FTY=3
                        yield parent,child, Order, FTY
                    if(PREV==1):                      ## the parent ramp is onramp
                        FTY=2
                        yield child, parent, Order, FTY
                if(FT4>0 and FT3==0):
                     for item in NodeR1:
                         node, LREV=item
                         if(LREV==0):   ## off ramp
                             FTY=3
                             Order=Order+1
                             yield child, node, Order, FTY
                         if(LREV==1):   ## on ramp
                             FTY=2
                             Order=Order+1
                             yield node, child, Order, FTY                             
        #except StopIteration:
        #    queue.popleft()
def bfs_edges(G, source, reverse=False):
    if reverse and G.is_directed():
        successors = G.predecessors
    else:
        successors = G.neighbors
    for e in generic_bfs_edges(G, source, successors):
        yield e
def bfs_edges2(G, source, reverse=False):
    if reverse and G.is_directed():
        successors = G.predecessors
    else:
        successors = G.neighbors
    for e in generic_bfs_edges2(G, source, successors):
        yield e
G = nx.read_edgelist('ARC15Links.csv', create_using=nx.DiGraph(), delimiter=',',nodetype=int, data=(('FacType',int),('LinkRev',int),('COUNT_DAIL',int),))

corridorList=[]
"""
ReadNode = csv.reader(open('CorridorList.csv', 'r'))
for row in ReadNode:
   Node = int(row[0])
   CountNode.append(Node)
"""

FTMain=[1]#range(11,12)
FTRamp=[4,7,8,9]#range(11,12)


#corridorList=[['I285EB',35545,281008,80053,FTMain,FTRamp],['I285W',80056,257926,35544,FTMain,FTRamp]]
#corridorList=[['I4SB',118118,110757,9020]]
corridorList=[['I85NB1',89186,208943,102704,FTMain,FTRamp],['I85NB2',102704,297706,116127,FTMain,FTRamp],['I85NB3',116127,10252,123456,FTMain,FTRamp],['I85SB1',124035,123961,116126,FTMain,FTRamp],['I85SB2',116126,257432,237103,FTMain,FTRamp],['I85SB3',237103,237099,89206,FTMain,FTRamp]]
#corridorList=[['I85SB1',124035,123961,116126,FTMain,FTRamp],['I85SB2',116126,257432,237103,FTMain,FTRamp],['I85SB3',237103,237099,89206,FTMain,FTRamp]]

f=open('BreadthFirstCorridor_I85.csv','w+')

for Item in corridorList:
    company=Item[0]
    corridor=Item[1:]
    edges = bfs_edges(G, corridor)
    for u, v, Order, FTY  in edges:
       f.write('%d %d %d %d %s\n' % (Order, u, v, FTY, company))
f.close()

f=open('BreadthFirstCorridorMainline_I85.csv','w+')

for Item in corridorList:
    company=Item[0]
    corridor=Item[1:]
    edges = bfs_edges2(G, corridor)
    for u, v, Order, FTY  in edges:
       f.write('%d %d %d %d %s\n' % (Order, u, v, FTY, company))
f.close()




