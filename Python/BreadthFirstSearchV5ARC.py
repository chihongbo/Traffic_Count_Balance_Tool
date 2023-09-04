import networkx as nx
import csv
from collections import defaultdict
from collections import deque
def generic_bfs_edges(G, visited, company, source, neighbors=None, depth_limit=None):
    visited.add(source)
    if depth_limit is None:
        depth_limit = len(G)
    queue = deque([(source, depth_limit, neighbors(source))])
    CCheck=0                                                 ## for connector check
    normal=0                                                 ## for counted links not in the boundary of a search region
    while queue:
        parent, depth_now, children = queue[0]
        try:
            child = next(children)
            if(G[parent][child]['FacType'] in range(51,60)):#[51,52,53,54]):  ##Visit a connector
                CCheck=-1
                yield parent, child, depth_now, 1,normal, CCheck
            if child not in visited and G[parent][child]['COUNT_DAIL']==0:
                visited.add(child)
                company[child]=source
                if depth_now > 1:
                    queue.append((child, depth_now - 1, neighbors(child)))
            if (child not in visited or (child in visited and company[child]!=source)) and (G[parent][child]['COUNT_DAIL']>0 and G[child][parent]['COUNT_DAIL']>0):
                normal=0
                if G[parent][child]['LinkRev']>0 or G[child][parent]['LinkRev']>0:
                    if G[parent][child]['LinkRev']==0:
                        yield parent, child, depth_now, 1,normal, CCheck
                    if G[child][parent]['LinkRev']==0:
                        yield child, parent, depth_now, 2,normal, CCheck                       
                else:
                    yield parent, child, depth_now, 1, normal, CCheck
                    yield child, parent, depth_now, 2, normal, CCheck
            if (child in visited and company[child]==source and G[parent][child]['COUNT_DAIL']>0 and G[child][parent]['COUNT_DAIL']>0): ## inside the search region, so we need to cancel the link count
                normal=-1
                if G[parent][child]['LinkRev']>0 or G[child][parent]['LinkRev']>0:
                    if G[parent][child]['LinkRev']==0:
                        yield parent, child, depth_now, 1, normal, CCheck
                    if G[child][parent]['LinkRev']==0:
                        yield child, parent, depth_now, 2, normal, CCheck                       
                else:
                    yield parent, child, depth_now, 1, normal, CCheck
                    yield child, parent, depth_now, 2, normal, CCheck
        except StopIteration:
            queue.popleft()
def bfs_edges(G, visited, company, source, reverse=False, depth_limit=None):
    if reverse and G.is_directed():
        successors = G.predecessors
    else:
        successors = G.neighbors
    for e in generic_bfs_edges(G, visited, company, source, successors, depth_limit):
        yield e
G = nx.read_edgelist('CFRPMLinks.csv', create_using=nx.DiGraph(), delimiter=',',nodetype=int, data=(('FacType',int),('LinkRev',int),('COUNT_DAIL',int),))

CountNode = []
ReadNode = csv.reader(open('CFRPMCountNodes.csv', 'r'))
for row in ReadNode:
   Node = int(row[0])
   CountNode.append(Node)
#CountNode = [61159]
visited=set()
company={}
#CompanyCount={}             ## how many validate basic segment
CompanyNode=defaultdict(set)  ## for each segment store the unqiue link node

NodeCheck=set()
LinkCheck=set()
LinkList=[]
SegNode=set()


f=open('BreadthFirstTest.csv','w+')

for Node in CountNode:
    if Node not in visited:
        company[Node]=Node
        edges = bfs_edges(G, visited, company,Node,depth_limit=None)
        for u, v, depth, direction, normal, CCheck  in edges:
            if(CCheck==-1):
               NodeCheck.add(Node) 
            if(normal==-1):
                LinkCheck.add((Node,u,v))
            if(CCheck==0 and normal==0):
                CompanyNode[Node].add(u)
                CompanyNode[Node].add(v)
            LinkList.append((Node, u, v, depth,direction,normal,CCheck))
            f.write('%d %d %d %d %d %d %d\n' % (Node, u, v, depth,direction,normal,CCheck))
f.close()

#visited=set()
#company={}


f=open('BreadthFirstSel.csv','w+')
f1=open('BreadthFirstSelForm.csv','w+')

SegNo=0
MAINFTYPE=[11,91,92,16,17]
RAMPFTYPE=[71,72,73,74,75,76,77,78,79,93,94,95,96,97,98,99]
for edge in LinkList:
    Node, u, v, depth,direction,normal,CCheck=edge
    if(Node not in NodeCheck and (Node, u, v) not in LinkCheck and len(CompanyNode[Node])>2):
        f.write('%d %d %d %d %d %d %d\n' % (Node, u, v, depth,direction,normal,CCheck))  
        if(Node not in SegNode):
            SegNo=SegNo+1
            SegNode.add(Node)
        if(direction==1):
            bound='OUT'
        if(direction==2):
            bound='IN'
        FTYPE=G[u][v]['FacType']
        if FTYPE in MAINFTYPE:
            FTYPEStr='M'
        elif FTYPE in RAMPFTYPE:
            FTYPEStr='R'
        else:
            FTYPEStr='N'
        CNTDay=G[u][v]['COUNT_DAIL']
        CNTAM= G[u][v]['COUNT_AM']
        CNTMD= G[u][v]['COUNT_MD']
        CNTPM= G[u][v]['COUNT_PM']
        CNTNT= G[u][v]['COUNT_NT']
        CNTTOT=CNTAM+CNTMD+CNTPM+CNTNT
        if(FTYPEStr=='M' and CNTTOT==0):
            FTYPEStr='M_0'
        if(FTYPEStr=='R' and CNTTOT==0):
            FTYPEStr='R_0'
        if(FTYPEStr=='N' and CNTTOT==0):
            FTYPEStr='N_0'
        f1.write('%d %d %s %d %d %d %d %d %d %d %s\n' % (Node, SegNo, bound,u, v,CNTDay,CNTAM,CNTMD,CNTPM,CNTNT,FTYPEStr))

"""
for Node in CountNode:
    if Node not in visited:
        company[Node]=Node
        edges = bfs_edges(G, visited, company,Node,depth_limit=None)
        for u, v, depth, direction, normal, CCheck  in edges:
            if(Node not in NodeCheck):
                if((Node, u, v) not in LinkCheck):
                    f.write('%d %d %d %d %d %d %d\n' % (Node, u, v, depth,direction,normal,CCheck))
"""
f1.close()
f.close()


