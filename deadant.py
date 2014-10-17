from __future__ import division,print_function
import sys,random
sys.dontWriteByteCode=True

rand= random.random
seed= random.seed

class o:
  def __init__(i,**d): i.update(**d)
  def update(i,**d): i.__dict__.update(**d); return i
    
def settings(**d): return o(
    seed=1,
    np=10,
    k=100,
    kMore=1.1,
    tiny=0.05,
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
  def __iadd__(i,x):
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
    tmp = (x - i.lo)/ (i.hi - i.lo + 0.00001)
    return max(0,min(1,tmp))
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
  def __init__(i,col=0,f=lambda x: 1,name=None,
    love=False # for objectives to maximize, set love to True
    ):
    i.f=f
    i.name= name or f.__name__
    i.n= N(col,least,most)
  def any(i): return None
  def fuse(i): return None
  def nudge(i): return None
  def score(i,lst):
    x = lst[i.col]
    if x == None:
        x = i.f(row)
        i.n += x
        lst[i.col] = x
    return x
  def height(i):
    return i.n.norm(i._score)
  def better(i,x,y):
    return x > y if i.love else x < y
  def worse(i,x,y):
    return x < y if i.love else x > y
  
class Meta:
  id=0
  def __init__(i,of,weight=1,dead=True):
    i.weight, i.dead,i.of = weight,dead,of
    i.id = Meta.id = Meta.id + 1
  def any(i):
    return Meta(i.of)
  def fuse(i): return i.any()
  def nudge(i): return i.any()
  def __repr__(i):
    return of.name + ':' \
           + 'DEAD' if i.dead else 'ALIVE' \
           + '*' + i.weight

def Schaffer():
  def f1(row): return row[0]**2
  def f2(row): return (row[0]-2)**2
  return Columns(Schaffer,
                 [N(least=-4, most=4)
                 ,O(f=f1)
                 ,O(f=f2)
                 ])

class Columns:
  def __init__(i,factory,cols=[]):
    i.factory = factory
    i.name = factory.__name__
    i.cols=[Meta(i)]
    i.nums=[]
    i.syms=[]
    i.objs=[]
    for pos,header in enumerate(cols):
      header.col = pos + 1
      if isinstance(header,N): i.nums += [header]
      if isinstance(header,S): i.syms += [header]
      if isinstance(header,O): i.objs += [header]
    i.indep = i.nums + i.syms
    i.cl    = Close()
  def any(i):
    return [col.any() for col in i.cols]
  def __iadd__(i,lst):
    for one in i.indep: one += lst[one.col]
  def score(i,lst):
    return [col.score(lst) for col in i.objs]
  def nudge(i,lst1,lst2):
    return [one.nudge(x,w1,y,w2) 
            for x,y,one in vals(lst1,lst2,i.cols)]
  def fuse(i,lst1,w1,lst2,w2):
    return [one.fuse(x,w1,y,w2) 
            for x,y,one in vals(lst1,lst2,i.cols)]
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
  def dist(i,lst1,lst2,peeking=False):
    total,c = 0,0
    for x,y,indep in vals(lst1,lst2,i.indep):
      total += indep.dist(x,y)**2 
      c     += 1
    d= total**0.5/c**0.5
    if not peeking: cl += d          
    return d

def vals(lst1,lst2,cols):
    for c in cols:
      yield lst1[c.cols],lst2[c.cols],c

def fromLine(a,b,c):
    x = (a**2 + c**2 - b**2)/ (2*c)
    return max(0,(a**2 - x**2))**0.5

def neighbors(m,lst1,pop):
  return sorted([(m.dist(lst1,lst2),lst2) 
                 for lst2 in pop 
                 if not lst1[0].id == lst2[0].id])

def deadAnt(model):
  m     = model()
  np    = The.np*len(m.indep)
  pop   = {}
  for _ in range(np): 
    new= m.any()
    itsAlive(new)
    keep(new)
  def keep(new):
    m += new
    pop[ new[0].id ] = new
  def itsAlive(lst) : lst[0].dead = False
  def itsDead(lst)  : lst[0].dead = True
  def itsGone(lst)  : del pop[lst[0].id]
  def fuse(lst1,lst2):
    w1 = lst1[0].weight
    w2 = lst2[0].weight
    lst3 = m.fuse(lst1,w1,lst2,w2)
    lst3[0].weight = w1+w2
    return lst3
  k   = The.k
  new = m.any()
  while k > 0:
    k -= 1
    (a,old),(b,other) = neighbors(m,new,
                                  pop.values())[:1]
    if not m.cl.close(a):
      c = m.dist(old,other,peeking=True)
      y = fromLine(a,b,c)
      if not m.cl.close(y):
        itsAlive(new)
        keep(new)
        new = m.any()
        continue
    if old[0].dead:
      new = fuse(new,old)
      itsGone(old)
      itsDead(new)
      keep(new)
      new = m.any()
    else:
      if m.dominates(new,old):
        k *= The.kMore
        itsDead(old)
        itsAlive(new)
        keep(new)
        new = m.nudge(old,new)
      elif m.dominates(old,new):
        itsDead(new)
        keep(new)
        new = m.nudge(new,old)
      else:
        itsAlive(new)
        keep(new)
        new = m.any()
        
                 
    

