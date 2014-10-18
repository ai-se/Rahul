from __future__ import division,print_function
import sys,random
sys.dont_write_bytecode =True

def settings(**d): return o(
  name="DEADANT v0.1",
  what="A stochastic multi-objective tabu active learner",
  synopsis="""
    DeadAnt's tabu memory is a trail of 'dead ants' in
    regions known to be sub-optimal. Landing too close
    to a dead ant will 'kill' any new candidate.  To
    reduce the overhead of searching through the ants,
    pairs of close dead ants are incrementally fused
    together.  To better explore good solutions, if a
    candidate is dominated by a live ant, then the
    candidate is nudged towards the better ant. This is
    an active learner since new solutions are only
    evaluated if are not 'close' to a dead ant (where
    'close' is learned dynamically).""",
  _logo="""
             "=.
             "=. \ 
                \ \ 
             _,-=\/=._        _.-,_
            /         \      /=-._ "-.
           |=-./~\___/~\    / How `-._\ 
           |   \o/   \o/   /  to      /
            \_   `~~~;/    |  Dodge   |
              `~,._,-'    /   Dead   /
                 | |      =-._Things/
             _,-=/ \=-._     /|`-._/
           //           \\   )\ 
          /|    I See   |)_.'/
         //|    Dead    |\_."   _.-\ 
        (|  \   People /    _.`=    \ 
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
    """,
  author="Tim Menzies, Rahul Krishna",
  copyleft="(c) 2014, MIT license, http://goo.gl/3UYBp",
  seed=1,
  np=10,
  k=100,
  kMore=1.1,
  tiny=0.05,
  start='print(The._logo)',
  closeEnough=2,
  de=o(np=10,
       f=0.3,
       cf=0.4,
       lives=9)
  ).update(**d)

class o:
  def __init__(i,**d): i.update(**d)
  def update(i,**d): i.__dict__.update(**d); return i

rand= random.random
seed= random.seed
any = random.choice

def say(*lst):
  sys.stdout.write(' '.join(map(str,lst)))
  sys.stdout.flush()
def sayln(*lst):
  say(*lst); print("")

def _say(): sayln(1,2,3,4)

The= settings()

def cmd(com=The.start):
  if globals()["__name__"] == "__main__":
    if len(sys.argv) == 3:
      if sys.argv[1] == '--cmd':
        com = sys.argv[2] + '()'
    if len(sys.argv) == 4:
        com = sys.argv[2] + '(' + sys.argv[3] + ')'
    eval(com)

class Close():
  def __init__(i):
    i.sum, i.n = [0]*32, [0]*32
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
      if x >= mu: return i
      if i.sum[j] < The.closeEnough: return i
    return i
  def close(i,x):
    return i.p(x) < The.tiny

def _close(n=10000,p=2,rseed=None):
  seed(rseed or The.seed)
  cl=Close()
  for _ in xrange(n):
    cl += rand()*100
  print(':p',cl.p(p),':close',cl.close(p))
  print(map(lambda x: int(x[0]/x[1]) if x[1] else 0,zip(cl.sum,cl.n)))

class Col:
  def any(i): return None
  def fuse(i,x,w1,y,w2): return None
  def nudge(i,x,y): return None
  def dist(i,x,y): return 0
  def norm(i,x) : return x
  def extrapolate(x,y,z): return None

class N(Col):
  "For nums"
  def __init__(i,col=0,least=0,most=1,name=None):
    i.col=col
    i.name=None
    i.least, i.most=least,most  
    i.lo,i.hi = 10**32, -1*10**32
  def extrapolate(i,x,y,z):
    return x + f*(y - z) if rand() < The.de.cf else x    
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
    
class S(Col):
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
  def dist(i,x,y): return 0 if x == y else 0
  def fuse(i,x,w1,y,w2):
    return x if rand() <= w1/(w1+w2) else y
  def nudge(i,x,y):
    return x if rand() < 0.33 else y
  def extrapolate(i,x,y,z):
    if rand() >= The.de.cf: 
      return x
    else:
      w = y if rand() <= f else z 
      return x if rand() <= 0.5 else w

class O(Col):
  "for objectives"
  def __init__(i,col=0,f=lambda x: 1,name=None,
    love=False # for objectives to maximize, set love to True
    ):
    i.f=f
    i.name= name or f.__name__
    i.n= N(col=col,least= -10**32, most=10**32)
  def score(i,lst):
    x = lst[i.col]
    if x == None:
        x = i.f(lst)
        i.n += x
        lst[i.col] = x
    return x
  def height(i):
    return i.n.norm(i._score)
  def better(i,x,y):
    return x > y if i.love else x < y
  def worse(i,x,y):
    return x < y if i.love else x > y
  
class Meta(Col):
  id=0
  def __init__(i,of,weight=1,dead=True):
    i.weight, i.dead,i.of = weight,dead,of
    i.id = Meta.id = Meta.id + 1
  def any(i):
    return Meta(i.of)
  def fuse(i,x,w1,y,w2): 
    tmp = i.any()
    tmp.weight = w1+w2
    return tmp
  def nudge(i): return i.any()
  def __repr__(i):
    return i.of.name + ':' \
           + 'DEAD' if i.dead else 'ALIVE' \
           + '*' + str(i.weight)

def Schaffer():
  def f1(row): return row[1]**2
  def f2(row): return (row[1]-2)**2
  return Cols(Schaffer,
                 [N(least=-4, most=4)
                 ,O(f=f1)
                 ,O(f=f2)
                 ])

def _schaffer():
  m=Schaffer()
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)
  
class Cols:
  def __init__(i,factory,cols=[]):
    i.cols = [Meta(i)] + cols
    i.factory, i.name  = factory, factory.__name__
    i.nums = [];  i.syms = []; i.objs = []
    for pos,header in enumerate(i.cols):
      header.col = pos 
      if isinstance(header,N): i.nums += [header]
      if isinstance(header,S): i.syms += [header]
      if isinstance(header,O): i.objs += [header]
    i.indep = i.nums + i.syms
    i.cl    = Close()
  def any(i): return [z.any() for z in i.cols]
  def tell(i,lst): 
    for z in i.indep: z += lst[z.col]
  def score(i,l): return [z.score(l) for z in i.objs]
  def nudge(i,lst1,lst2):
    return [one.nudge(x,w1,y,w2) 
            for x,y,one in vals(lst1,lst2,i.cols)]
  def extrapolate(i,lst1,lst2,lst3):
    tmp= [one.extrapolate(x,y,z) for x,y,z,one in 
            vals3(lst1,lst2,lst3,i.cols)]
    one = any(i.objs)
    tmp[one.col] = lst1[one.col]
    return tmp
  def fuse(i,lst1,lst2):
    w1= lst1[0].weight
    w2= lst2[0].weight
    return [one.fuse(x,w1,y,w2) 
            for x,y,one in vals(lst1,lst2,i.cols)]
  def fromHell(i):
    x,c = 0, len(i.objs)
    for col in i.objs:
      tmp = col.height()
      tmp = tmp if col.love else 1 - tmp
      x += tmp**2
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
    total,c = 0,len(i.indep)
    for x,y,indep in vals(lst1,lst2,i.indep):
      total += indep.dist(x,y)**2 
    d= total**0.5/c**0.5
    if not peeking: cl += d          
    return d

def vals(lst1,lst2,cols):
  for c in cols:
    yield lst1[c.cols],lst2[c.cols],c

def vals3(lst1,lst2,lst3,cols):
  for c in cols:
    yield lst1[c.cols],lst2[c.cols],lst3[c.cols],c

def fromLine(a,b,c):
    x = (a**2 + c**2 - b**2)/ (2*c)
    return max(0,(a**2 - x**2))**0.5

def neighbors(m,lst1,pop):
  return sorted([(m.dist(lst1,lst2),lst2) 
                 for lst2 in pop 
                 if not lst1[0].id == lst2[0].id])

def deadAnt(model):
  m   = model()
  pop = {}
  def remember(new): m += new; pop[ new[0].id ]= new
  def itsAlive(lst): lst[0].dead = False; return lst
  def itsDead(lst) : lst[0].dead = True;  return lst
  def itsGone(lst) : del pop[lst[0].id]
  def makeSomeAnts(n) :
    for _ in range(n):
      remember( itsAlive( m.any() ))
  makeSomeAnts( The.np*len(m.indep) )
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
        remember( itsAlive(new) )
        new = m.any()
        continue
      #else close enough to reflect on old
    if old[0].dead:
      new = fuse(new,old)
      itsGone(old)
      remember( itsDead(new) )
      new = m.any()
    elif  m.dominates(new,old):
      k *= The.kMore
      itsDead(old)
      remember( itsAlive(new) )
      new = m.nudge(old,new)
    elif m.dominates(old,new):
      remember( itsDead(new) )
      new = m.nudge(new,old)
    else:
      remember( itsAlive(new) )
      new = m.any()

def one234(one, pop, f=lambda x:x): 
  def oneOther():
    x = any(pop)

    while f(x) in seen: 
      x = any(pop)
    seen.append( f(x) )
    return x
  print(one)
  seen  = [ f(one) ]
  return oneOther(), oneOther(), oneOther()

def _one234():
  seed(The.seed)
  for _ in range(10):
    print(one234(1,range(1000)))



def de(model):
  m   = model()
  frontier = []
  def remember(new): 
    m.tell(new); frontier.append(new)
  def pop0(n) :
    for i in range(n): 
      remember( m.any())
  pop0( The.np * len(m.indep) )
  lives = The.de.lives
  while lives > 0:
    say(lives)
    lives -= 1
    better = False
    for pos,l1 in enumerate(frontier):
      print(l1[0].id)
      l2, l3, l4 = one234(l1,frontier,lambda x:x[0].id)
      candidate = m.extrapolate(l2,l3,l4)
      if m.dominates(candidate,l1):
          better = True
          frontier[pos] = candidate
    if better:
       lives += 1

cmd('_close()')

