from __future__ import printFunction, diviide
import sys,random
sys.dontWriteByteCode=True

rand= random.random
seed= random.seed

class o:
  def __init__(i,**d): i.update(**d)
  def update(i,**d): i.__dict__.update(**d); return i
    
def settings(**d): return o(
    seed=1,
    np=10
    k=100,
    kMore=1.1,
    tiny=0.05
    _logo="""
             "=.
             "=. \ 
                \ \ 
             _,-=\/=._        _.-,_
            /         \      /=-._ "-.
           |=-./~\___/~\    /     `-._\ 
           |   \o/   \o/   /         /
            \_   `~~~;/    |         |
              `~,._,-'    /          /
                 | |      =-._      /
             _,-=/ \=-._     /|`-._/
           //           \\   )\ 
          /|             |)_.'/
         //|             |\_."   _.-\ 
        (|  \           /    _.`=    \ 
        ||   ":_    _.;"_.-;"   _.-=.:
     _-."/    / `-."\_."        =-_.;\ 
    `-_./   /             _.-=.    / \\ 
           |              =-_.;\ ."   \\ 
           \                   \\/     \\ 
           /\_                .'\\      \\ 
          //  `=_         _.-"   \\      \\ 
         //      `~-.=`"`'       ||      ||
   LGB   ||    _.-_/|            ||      |\_.-_
     _.-_/|   /_.-._/            |\_.-_  \_.-._\ 
    /_.-._/                      \_.-._\ 
  """).update(**d)
  
The= settings()
  
class Close():
  def __init__(i):
    i.sum, i.n = [0.0]*32, [0.0]*32
  def p(i,x):
    for j in xrange(len(i.sum)):
      mu = i.sum[j] / i.n[j]
      if x > mu:
        return i.n[j]/i.n[0]
    return i.n[-1]/i.n[0]
  def keep(i,x):
    for j in xrange(len(i.sum)):
      i.sum[j] += x
      i.n[j]   += 1
      mu        = i.sum[j] / i.n[j]
      if x > mu: return x
    return x
  def close(i,x):
    return i.p(x) < The.tiny
 
class N:
  "For nums"
  def __init__(i,col=0,least=0,most=1,name=None):
    i.col=col
    i.name=None
    i.least, i.most=least,most  
    i.lo,i.hi = 10**32, -1*10**32
  def any(i):
    return i.least + rand()*(i.most - i.least)
  def __iadd__(i,x):
    assert x >= i.least and x <= i.most
    i.lo = min(i.lo,x)
    i.hi = max(i.hi,x)
    return i
  def norm(i,x):
    return (x - i.lo)/ (i.hi - i.lo + 0.00001)
  def dist(i,x,y):
    return i.norm(x) - i.norm(y)
  def fuse(i,x,w1,y,w2):
    return (x*w1 + y*w2)/(w1+w2)
  def nudge(i,x,y):
    tmp = x + rand()*1.5*(y-x)
    if tmp > i.most : tmp = i.least
    if tmp < i.least: tmp = i.most
    return tmp
    
class S:
  "For syms"
  def __init__(i,col=0,items=[],name=None):
    i.index = frozenset(items)
    i.items = items
    i.col=col
    i.name=name 
  def any(i):
    return random.choice(i.items)
  def __iadd__(i,x): 
    assert x in i.index
  def norm(i,x):  return x
  def dist(i,x,y): return 0 if x == y else 0
  def fuse(i,x,w1,y,w2):
    return x if rand() <= w1/(w1+w2) else y
  def nudge(i,x,y):
    return x if rand() < 0.33 else y


class O:
  "for objectives"
  def __init__(i,col=0,f=lambda x: 1,name=None),
    love=False # for objectives to maximize, set love to True
    ):
    i.f=f
    i.name= name or f.__name__
    i.n= N(col,least,most)
  def score(i,lst):
    x = lst[i.col]
    if x == None
        i.n += x = i.f(row)
        lst[i.col] = x
    return x
  def height(i):
    return i.n.norm(i._score)
  def better(i,x,y):
    return x > y if i.love else x < y
  def worse(i,x,y):
      return x < y if i.love else x > y
    for sym in i.syms: sym += lst[sym.col]
  def evalute(i,row):
    "defined by sub-class"
    pass
  
def Schaffer():
  def f1(row): return row[0]**2
  def f2(row): return (row[0]-2)**2
  return Columns([N(least=-4, most=4)
                 ,O(f=f1),
                 ,O(f=f2)
                 ])

class Columns:
  def __init__(i,cols=[]):
    i.cols=[]
    i.nums=[]
    i.syms=[]
    i.objs=[]
    for pos,header in enumerate(cols):
      header.col = pos
      if isinstance(header,N): i.nums += [header]
      if isinstance(header,S): i.syms += [header]
      if isinstance(header,O): i.objs += [header]
    i.indep = i.nums + i.syms
    i.cache = {}
    i.cl    = Close()
  def any(i):
    return [col.any() for col in i.indep] + ([None]*len(i.objs))
  def __iadd__(i,lst)
    for col in i.syms: col += lst[sym.col]
    for col in i.nums: col += lst[sym.col]
  def score(i,lst):
    return [col.score(lst) for col in i.objs]
  def nudge(i,lst1,lst2):
    #XXX what to do with old scores?
    lst3 = i.any()
    for x,y,indep in vals(lst1,lst2,i.indep):
      lst3[indep.col] = indep.nudge(x,y)
    return lst3
  def fuse(i,lst1,w1,lst2,w2):
    #XXX what to do with old scores?
    lst3 = i.any()
    for x,y,indep in vals(lst1,lst2,i.indep):
      lst3[indep.col] = indep.fuse(x,w1,y,w2)
    return lst3
  def fromHell(i):
    x,c = 0,0
    for col in i.obj():
      tmp = col.height()
      tmp = tmp if col.love else 1 - tmp
      x += tmp**2
      c += 1
    return x**0.5/c**0.5
  def dominates(i,lst1,lst2):
    i.score(lst1)
    i.score(lst2)
    better=False
    for x,y,obj in vals(lst1,lst2,i.objs):
      if obj.worse(x,y) : return False
      if obj.better(x,y): better = True
    return better
  def dist(i,lst1,lst2):
    id1=id(lst1)
    id2=id(lst2)
    if id1 > id2: id1,id2 = id2,id1
    if (id1,id2) in i.cache:
      return i.cache[(id1,id2)]
    d = i.cache[(id1,id2)] = m.dist0(lst1,lst2)
    i.cl += d
    return d
  def dist0(i,lst1,lst1):
    c=d=0
    for x,y,indep in vals(lst1,lst2,i.indep):
      d += indep.dist(x,y)**2
      c += 1
   return d**0.5/c**0.5

def vals(lst1,lst2,cols):
    for c in cols:
      yield lst1[c.cols],lst2[c.cols],c

def swapped(doomed,new,pop):
  for n,old in enumerate(pop):
    if id(old) == id(doomed):
      pop[n] = new
      return True
  error('oh hdear')

def deadAnt(model):
  m     = model()
  cache = {} # suck!
  alive = {} # suck!
  w     = {} # suck!
  np    = The.np*len(m.indep)
  pop   = [m.any() for _ in range(np)]
  def dead(lst):
    return not id(lst) in alive
  def itsAlive(lst):
    alive[id(lst)] = lst
  def itsDead(lst):
    if id(lst) in alive:
      del alive[id(lst)]
  def neighbors(lst1):
    return sorted([(m.dist(lst1,lst2),lst2) 
                   for lst2 in pop 
                   if not id(lst1) == id(lst2)])
  def cosine(a,b,old1,old2):
    c = m.dist(old1,old2)
    x = (a**2 + c**2 - b**2)/ (2*c)
    return (a**2 - max(0,x)**2)**0.5
  def fuse(lst1,lst2):
    w[id(lst1)] = w1 = w.get(id(lst1),1)
    w[id(lst2)] = w2 = w.get(id(lst2),1)
    lst3 = m.fuse(lst1,w1,lst2,w2)
    del w[id(lst1)]; itsDead(lst1)
    del w[id(lst2)]; itsDead(lst2)
    w[id(lst3)] = w1 + w2
    return lst3
  k   = The.k
  new = m.any()
  while k > 0:
    k -= 1
    (a,old1),(b,old2) = neighbors(new)[:1]
    close1 = m.cl.close(a)
    close2 = m.cl.close(b)
    if not close1:
      y = cosine(a,b,old1,old2)
      if not m.cl close(y):
        pop += [new]
        itsAlive(new)
        new = m.any()
        continue
    if dead(old1):
          swapped(old1,fuse(new,old1))
          new = m.any()
    else:
          if m.dominates(new,old1):
            itsDead(old1)
            # do i fuse? no!
            new = m.nudge(old1,new)
            k *= The.kMore
          elif m.dominates(old1,new):
            # do i fuse? no!
            new = m.nudge(new,old1)
            k *= The.kMore
          else:
            pop += [new]
            new = m.any()
        
                 
    

