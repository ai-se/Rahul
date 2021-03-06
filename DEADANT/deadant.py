#!/usr/bin/env python
from __future__ import division, print_function
import sys, random, time; import os, pdb, math, numpy as np
from math import sin
_pwd=os.getcwd()
from re import search
sys.path.insert(0, '/Users/rkrsn/git/axe/axe')
sys.path.insert(1, _pwd+'/Models/')
sys.path.insert(2, _pwd+'/Models/pom3/')
import pom3
from _XOMO  import *
#import _POM3
#from pom3 import *
import sk; rdivDemo=sk.rdivDemo
sys.dont_write_bytecode = True
exp=math.e
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
  kMore=1,
  tiny=0.01,
  start='print(The._logo)',
  closeEnough=1,
  de=o(np=5,
       epsilon=1.01,
       f=0.3,
       cf=0.4,
       lives=100)
  ).update(**d)

def say(lst):
 sys.stdout.write(lst)
 
class o:
  def __init__(self, **d): self.update(**d)
  def update(self, **d): self.__dict__.update(**d); return self

rand = random.random
seed = random.seed
any = random.choice
exp = math.exp

def say(*lst):
  sys.stdout.write(' '.join(map(str, lst)))
  sys.stdout.flush()
def sayln(*lst):
  say(*lst); print("")

def _say(): sayln(1, 2, 3, 4)

The = settings()


def cmd(com=The.start):
  if globals()["__name__"] == "__main__":
    if len(sys.argv) == 3:
      if sys.argv[1] == '--cmd':
        com = sys.argv[2] + '()'
    if len(sys.argv) == 4:
        com = sys.argv[2] + '(' + sys.argv[3] + ')'
    eval(com)

class Close():
  def __init__(self):
    self.sum, self.n = [0] * 32, [0] * 32
  def p(self, x):
    for j in xrange(len(self.sum)):
      mu = self.sum[j] / self.n[j] if self.n[j] else 0
      if x > mu:
        return self.n[j] / self.n[0]
    return self.n[-1] / self.n[0]
  def __iadd__(self, x):
    for j in xrange(len(self.sum)):
      self.sum[j] += x
      self.n[j] += 1
      mu = self.sum[j] / self.n[j]
      if x >= mu: return self
      if self.sum[j] < The.closeEnough: return self
    return self
  def close(self, x):
    return self.p(x) < The.tiny

def _close(n=10000, p=2, rseed=None):
  seed(rseed or The.seed)
  cl = Close()
  for _ in xrange(n):
    cl += rand() * 100
  print(':p', cl.p(p), ':close', cl.close(p))
  print(map(lambda x: int(x[0] / x[1]) if x[1] else 0, zip(cl.sum, cl.n)))

class Col:
  def any(self): return None
  def fuse(self, x, w1, y, w2): return None
  def nudge(self, x, y, sampled): return None
  def dist(self, x, y): return 0
  def norm(self, x) : return x
  def extrapolate(self, x, y, z): return None

class N(Col):
  "For nums"
  def __init__(self, col=0, least=0, most=1, name=None):
    self.col = col
    self.name = None
    self.least, self.most = least, most  
    self.lo, self.hi = 10 ** 32, -1 * 10 ** 32
  def extrapolate(self, x, y, z):
    f = The.de.f
    return x + f * (y - z)    
  def any(self):
   return max(self.least,
               min(self.most,
                   self.least + rand() * (self.most - self.least)))
  def __iadd__(self, x):
    #print("x",x,"least",self.least,"most",self.most)
    #x = x if not x >= self.least else self.most if x >
    self.lo = min(self.lo, x)
    self.hi = max(self.hi, x)
    return self
  def norm(self, x):
    tmp = (x - self.lo) / (self.hi - self.lo + 0.00001)
    return max(0, min(1, tmp))
  def dist(self, x, y):
    return np.sqrt(self.norm(x)**2 - self.norm(y)**2)
  def fuse(self, x, w1, y, w2):
    return (x * w1 + y * w2) / (w1 + w2)
  def nudge(self, x, y, sampled):
   if sampled: 
    tmp = sorted([x + rand() * 1.5 * (y - x) 
                  for _ in xrange(100)], 
                 key = lambda F: abs(F-x))[-1]
   else:
    tmp = x + rand() * 1.5 * (y - x) 
   if tmp > self.most : tmp = self.least
   if tmp < self.least: tmp = self.most
   return tmp
    
class S(Col):
  "For syms"
  def __init__(self, col=0, items=[], name=None):
    self.index = frozenset(items)
    self.items = items
    self.col = col
    self.name = name 
  def any(self):
    return random.choice(self.items)
  def __iadd__(self, x): 
    assert x in self.index
  def dist(self, x, y): return 0 if x == y else 0
  def fuse(self, x, w1, y, w2):
    return x if rand() <= w1 / (w1 + w2) else y
  def nudge(self, x, y, sampled=True):
    return x if rand() < 0.33 else y
  def extrapolate(self, x, y, z):
    if rand() >= The.de.cf: 
      return x
    else:
      w = y if rand() <= f else z 
      return x if rand() <= 0.5 else w

class O(Col):
  "for objectives"
  def __init__(self, col=0, f=lambda x: 1, name=None,
    love=False  # for objectives to maximize, set love to True
    ):
    self.f = f
    self.love = love
    self.name = name or f.__name__
    self.n = N(col=col, least=-10 ** 32, most=10 ** 32)
  def score(self, lst):
    x = lst[self.col]
    if x == None:
        x = self.f(lst)
        self.n += x
        lst[self.col] = x
    return x
  def better(self, x, y):
    e = The.de.epsilon
    return x > y * e if self.love else x < y / e
  def worse(self, x, y):
    return x < y if self.love else x > y
  
class Meta(Col):
  id = 0
  def __init__(self, of, weight=1, dead=True):
    self.weight, self.dead, self.of = weight, dead, of
    self.id = Meta.id = Meta.id + 1
  def any(self):
    return Meta(self.of)
  def fuse(self, x, w1, y, w2): 
    tmp = self.any()
    tmp.weight = w1 + w2
    return tmp
  def nudge(self, x, y, sampled=True): return self.any()
  def extrapolate(self, x, y, z):
   return Meta(self.of)
  def __repr__(self):
    return self.of.name + ':' \
           + ('DEAD' if self.dead else 'ALIVE') \
           + '*' + str(self.weight)
  
#===============================================================================
#  STANDARD MODELS
#===============================================================================

# Schaffer

def Schaffer():
 "Schaffer"
 def f1(row): return row[1] ** 2
 def f2(row): return (row[1] - 2) ** 2
 return Cols(Schaffer,
                [N(least=-10, most=10)
                , O(f=f1) 
                , O(f=f2)
                ])

# Fonseca

def fonseca():
 "Fonseca" 
 n=3;
 def f1(x): return 1-math.exp(-np.sum([(x[1+z]-1/(n**0.5))**2 
                                     for z in xrange(n)]))
 def f2(x): return 1-math.exp(-np.sum([(x[1+z]+1/(n**0.5))**2 
                                     for z in xrange(n)]))
 return Cols(fonseca,
                n*[ N(least=-4, most=4)]
                + [ O(f=f1)
                ,   O(f=f2)
                ])

# Kursawe

def kursawe():
 "Kursawe" 
 n=3;
 a=0.8; b=3
 def f1(x): return np.sum([-10*math.exp(-0.2*math.sqrt(x[1+z]**2+x[z+2]**2)) 
                             for z in xrange(n-1)])
 
 def f2(x): return np.sum([np.abs(x[z+1])**a+5*math.sin(x[z+1]**b) 
                             for z in xrange(n)])
 
 return Cols(kursawe,
                n*[ N(least=-4, most=4)]
                + [ O(f=f1)
                ,   O(f=f2)
                ])
 
# ZDT1

def ZDT1():
 "ZDT1" 
 n=30;
 def g(x):  return (1+9*(np.sum(x[2:-2]))/(n-1))
 def f1(x): return x[1]
 def f2(x): return g(x)*(1-math.sqrt(abs(f1(x)/g(x)))); 
 
 return Cols(ZDT1,
                n*[ N(least=0, most=1)] 
                + [O(f=f1)
                ,  O(f=f2)])
# ZDT3

def ZDT3():
 "ZDT3" 
 n=30;
 def g(x):  return (1+9*(np.sum(x[2:-2]))/(n-1))
 def f1(x): return x[1]
 def f2(x): return g(x)*(1-math.sqrt(abs(f1(x)/g(x)))
                         -abs(f1(x)/g(x))*math.sin(10*math.pi*f1(x))); 
 
 return Cols(ZDT3,
                n*[ N(least=0, most=1)] 
                + [O(f=f1)
                ,  O(f=f2)])

# DTLZ7
def DTLZ7():
 "DTLZ7"
 n=20;
 def g(x):
    return 1+9/(n)*np.sum(x)
 def h(x):
    return n-np.sum([x[z]*(1+math.sin(3*math.pi*x[z]))/(1+g(x)) 
                                  for z in xrange(n-2)])
 def f1(n):
  return lambda x: x[n+1]
 def f2(x):
    return (1+g(x[1:-n]))*h(x[1:-n])
 
 return Cols(DTLZ7,
                n*[ N(least=0, most=1)] 
                + [O(f=f1(n)) for n in xrange(0,n-1)]
                + [O(f=f2)])
 
  
#===============================================================================
# SOFTWARE ENGINEERING MODELS
#===============================================================================

# XOMO

def xomo(modelName='xomoall'):
 "XOMO"
 m = Model(modelName)
 c = m.oo()
 scaleFactors=c.scaleFactors
 effortMultipliers=c.effortMultipliers
 defectRemovers=c.defectRemovers
 headers = scaleFactors+effortMultipliers+defectRemovers+['kloc']
 bounds={h:(c.all[h].min, c.all[h].max) 
         for h in headers}
 a=c.x()['b']; b=c.all['b'].y(a)
 
 def restructure(x):
  return {headers[i]: x[i] for i in xrange(len(headers))}
 
 def sumSfs(x,out=0,reset=False):
  for i in scaleFactors:
   out += x[i]
  return out

 def prodEms(x,out=1,reset=False):
  for i in effortMultipliers:
     out *= x[i] #changed_nave
  return out
 
 def Sum(x): 
  return sumSfs(restructure(x[1:-4]), reset=True)
 def prod(x): 
  return c.prodEms(restructure(x[1:-4]), reset=True)
 def exp(x): 
  return b + 0.01 * Sum(x)
 
 effort  = lambda x: c.effort_calc(restructure(x[1:-4]), 
                                   a=a, b=b, exp=exp(x), 
                                   sum=Sum(x), prod=prod(x))
 months  = lambda x: c.month_calc(restructure(x[1:-4]), 
                                  effort(x), sum=Sum(x), 
                                  prod=prod(x))
 defects = lambda x: c.defect_calc(restructure(x[1:-4]))
 risks   = lambda x: c.risk_calc(restructure(x[1:-4]))
 
 return Cols(xomo,
             [N(least=bounds[h][0], most=bounds[h][1])
              for h in headers] + 
             [O(f=effort), O(f=months), O(f=defects), O(f=risks)])
 
# POM3

def POM3(Class='a'):
 "POM3"
 p3 = pom3.pom3()
 
 headers = ['Culture', 'criticality', 'criticality_modifier'
          , 'initial_known', 'interdependency', 'dynamism'
          , 'size', 'plan', 'team_size']

 def bounds(Class):
  if Class=='a':
   return {'Culture': [0.1, 0.9], 
           'criticality': [0.82, 1.26], 
           'criticality_modifier': [0.02, 0.1], 
           'initial_known': [0.4, 0.7], 
           'interdependency': [0.0, 1.0], 
           'dynamism': [1.0, 50.0], 
           'size': [0, 4], 
           'plan': [0, 4], 
           'team_size': [1.0, 44.0], 
           }
  elif Class=='b':
   return {'Culture': [0.1, 0.9], 
           'criticality': [0.82, 1.26], 
           'criticality_modifier': [0.8, 0.95], 
           'initial_known': [0.4, 0.70], 
           'interdependency': [0.0, 1.0], 
           'dynamism': [1.0, 50], 
           'size': [0, 2], 
           'plan': [0, 4], 
           'team_size': [1.0, 44.0], 
           }
  elif Class=='c':
   return {'Culture': [0.5, 0.9], 
           'criticality': [0.82, 1.26], 
           'criticality_modifier': [0.02, 0.08], 
           'initial_known': [0.2, 0.5], 
           'interdependency': [0.0, 50.0], 
           'dynamism': [40.0, 50.0], 
           'size': [3,4], 
           'plan': [0, 4], 
           'team_size': [20.0, 44.0], 
           }
  
 cost = lambda x: p3.simulate([round(float(k),2) for k in x[1:-3]])[0]
 completion = lambda x: p3.simulate([round(float(k),2) for k in x[1:-3]])[1]
 idle = lambda x: p3.simulate([round(float(k),2) for k in x[1:-3]])[2]
 
 return Cols(POM3,
            [N(least=bounds(Class)[h][0], most=bounds(Class)[h][1])
             for h in headers] + 
            [O(f=cost), O(f=idle), O(f=completion, love=True)])
 

 
def _schaffer():
  m = Schaffer()
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)
  
def _fonseca():
  m = fonseca()
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)

def _ZDT1():
  m = ZDT1()
  print(m.__dict__)
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)
  
def _xomo():
  m = xomo()
  print(m.__dict__)
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)

def _pom3():
  m = POM3()
  for _ in range(10):
    one = m.any()
    m.score(one)
    print(one)

def depenLen(m):
 if m.__doc__=='XOMO': return 4
 
 elif m.__doc__=='DTLZ7': return 20
 
 elif m.__doc__=='POM3': return 3
 
 else: return 2
  
def trials(M,reps=10):
 m=M()
 def sum(lst):
  return (np.sum([round(float(l),4) for l in lst]))
 Obj=[]
 for _ in xrange(reps):
  one = m.any()
  m.score(one) 
  Obj+=[(sum(one[-depenLen(M):]))]
 Obj=sorted(Obj)
 return Obj[0], Obj[-1]

def trials1(M,reps=500):
 m=M()
 def sum(lst):
  return (np.sum([round(float(l),4) for l in lst]))
 Obj=[]
 for _ in xrange(reps):
  one = m.any()
  m.score(one) 
  Obj+=[(one[-depenLen(M):])]
 OO=[np.mean([O1[k] for O1 in Obj]) for k in xrange(depenLen(M))]
 return OO
  
class Cols:
  def __init__(self, factory, cols=[]):
    self.cols = [Meta(self)] + cols
    self.factory, self.name = factory, factory.__name__
    self.nums = [];  self.syms = []; self.objs = []
    for pos, header in enumerate(self.cols):
      header.col = pos 
      if isinstance(header, N): self.nums += [header]
      if isinstance(header, S): self.syms += [header]
      if isinstance(header, O): self.objs += [header]
    self.indep = self.nums + self.syms
    self.cl = Close()
  def any(self): return [z.any() for z in self.cols]
  def tell(self, lst): 
    for z in self.indep: z += lst[z.col]
  def score(self, l): return [z.score(l) for z in self.objs]
  def nudge(self, lst1, lst2, sampled):
    return [one.nudge(x, y, sampled) 
            for x, y, one in vals(lst1, lst2, self.cols)]
  def extrapolate(self, lst1, lst2, lst3):
    tmp = [one.extrapolate(x, y, z) for x, y, z, one in 
            vals3(lst1, lst2, lst3, self.cols)]
    one = any(self.objs)
    tmp[one.col] = lst1[one.col]
    return tmp
  def fuse(self, lst1, lst2):
    w1 = lst1[0].weight
    w2 = lst2[0].weight
    return [one.fuse(x, w1, y, w2) 
            for x, y, one in vals(lst1, lst2, self.cols)]
  def fromHell(self, lst):
    x, c = 0, len(self.objs)
    for header in self.objs:
      val = header.col
      tmp = header.norm(val)
      tmp = tmp if header.love else 1 - tmp
      x += tmp ** 2
    return x ** 0.5 / c ** 0.5
  def dominates(self, lst1, lst2):
    self.score(lst1)
    self.score(lst2)
    better = False
    for x, y, obj in vals(lst1, lst2, self.objs):
      if obj.worse(x, y) : return False
      if obj.better(x, y): better = True
    return better
  def dist(self, lst1, lst2, peeking=False):
    total, c = 0, len(self.indep)
    for x, y, indep in vals(lst1, lst2, self.indep):
      total += indep.dist(x, y) ** 2 
    d = total ** 0.5 / c ** 0.5
    if not peeking: self.cl += d    # Peeking? What's peeking?      
    return d

def vals(lst1, lst2, cols):
  for c in cols:
    yield lst1[c.col], lst2[c.col], c

def vals3(lst1, lst2, lst3, cols):
  for c in cols:
    yield lst1[c.col], lst2[c.col], lst3[c.col], c

def fromLine(a, b, c):
    x = (a ** 2 + c ** 2 - b ** 2) / (2 * c)
    return max(0, (a ** 2 - x ** 2)) ** 0.5

def neighbors(m, lst1, pop):
  return sorted([(m.dist(lst1, lst2), lst2) 
                 for lst2 in pop 
                 if not lst1[0].id == lst2[0].id])

class deadAnt(object):
  def __init__(self, model=None, sampled=True):
    self.m=model()
    self.pop = {}
    self.frontier=[]
    self.evals=0
    self.sampled=sampled
  
  def remember(self, new): 
   self.frontier.append(new); 
   self.pop[ new[ 0 ].id ] = new; 
   self.evals+=1;
   self.m.score(new)
   
  def itsAlive(self, lst): lst[0].dead = False; return lst
  def hes_Dead_Jim(self, lst) : lst[0].dead = True;  return lst
  def itsGone(self, lst) : del self.pop[lst[0].id]
  def makeSomeAnts(self, n) :
    for _ in range(n):
      self.remember(self.itsAlive(self.m.any()))
  def DA(self):
    self.makeSomeAnts(The.np * len(self.m.indep))  # initialize some ants
    k = 100#The.k  # k=100, see line 54
    new = self.m.any()
    while k > 0:
      k -= 1
      #pdb.set_trace()
      (a, old), (b, other) = neighbors(self.m, new, self.pop.values())[:2]
      #pdb.set_trace()
      
      if not self.m.cl.close(a):
        c = self.m.dist(old, other, peeking=True)
#         print('*')
        y = fromLine(a, b, c)
        if not self.m.cl.close(y):
          #print('Extrapolation')
          self.remember(self.itsAlive(new))
          new = self.m.any()
          continue
        # else close enough to reflect on old
      if old[0].dead:
#       say('x')
        #new = self.m.fuse(new, old) # <--- get rid of this
        self.itsGone(old)
        #self.remember(self.hes_Dead_Jim(new))
        new = self.m.any()
      elif  self.m.dominates(new, old):
#         say('!')
        k += 2*The.kMore
        self.hes_Dead_Jim(old)
        self.remember(self.itsAlive(new))
        new = self.m.nudge(old, new, sampled=self.sampled)
      elif self.m.dominates(old, new):
#         say('_')
        self.remember(self.hes_Dead_Jim(new))
        new = self.m.nudge(new, old, sampled=self.sampled)
      else:
        self.remember(self.itsAlive(new))
#         say('.')
        new = self.m.any()
      
      #if math.floor(k)%50==0: say('\n')
#     for k in self.frontier:
#      k.append(k[3]+k[2])
    return self.frontier
     

class diffEvol(object):
  "DE"
  
  def __init__(self, model=Schaffer):
    self.m=model()
    self.pop = {}
    self.frontier=[]
    self.evals=0
  
  def itsAlive(self, lst): 
   lst[0].dead = False; self.m.score(lst); 
   return lst
  
  def remember(self, new): 
   self.frontier.append(self.itsAlive(new)); self.evals+=1;
  
  def initFront(self, n) :
    for _ in range(n):
      self.remember(self.m.any())
  def DE(self):
    self.initFront(The.np * len(self.m.indep))
    lives = The.de.lives
    while lives > 0:
      better = False
      for pos, l1 in enumerate(self.frontier):
       lives -= 1
       l2, l3, l4 = one234(l1, self.frontier)
       new = self.m.extrapolate(l2, l3, l4)
       if  self.m.dominates(new, l1):
        self.frontier.pop(pos)
        self.remember(new)
        better = True
       elif self.m.dominates(l1, new):
        better = False
       else:
        self.remember(new)
        better = True
      if better:
       lives += 1
    return self.frontier
     

def one234(one, pop, f=lambda x:id(x)): 
  def oneOther():
    x = any(pop)
    while f(x) in seen: 
      x = any(pop)
    seen.append( f(x) )
    return x
  seen  = [ f(one) ]
  return oneOther(), oneOther(), oneOther()

def _one234():
  seed(The.seed)
  for _ in range(10):
    print(one234(1, range(1000)))

def spread(frontier, depen):
 lst=[k[-depen:] for k in frontier]
 def pairs(lst):
  for j in lst[0:]:
   last = j
   for i in lst[0:]:
    yield last, i

 def dist(lst1, lst2):
  return np.sqrt(np.sum([(el1-el2)**2 for el1, el2 in zip(lst1, lst2)]))

 d=sorted([dist(one, two) for one, two in pairs(lst)])
 df, dl = d[0], d[1]
 dm = np.mean(d)
 N = len(d)

 return (df+dl+np.sum([abs(d[i]-dm) 
         for i in xrange(N-2)]))/(df+dl+(N-2)*dm)



def _de(m):
 "DE"
 DE=diffEvol(model=m);
 res = sorted([k for k in DE.DE()], 
              key=lambda F: np.sum(F[-depenLen(m):]))
 return res[0][-depenLen(m):], DE.evals, spread(res, depenLen(m))

def _da(m):
 "DA"
 da=deadAnt(model=m)
 res = sorted([k for k in da.DA() if not k[0].dead], 
               key=lambda F: np.sum(F[-depenLen(m):]))
 return res[0][-depenLen(m):], da.evals, spread(res, depenLen(m))

def _da1(m):
 "DA1"
 da=deadAnt(model=m, sampled=False)
 res = sorted([k for k in da.DA() if not k[0].dead], 
               key=lambda F: np.sum(F[-depenLen(m):]))
 return res[0][-depenLen(m):], da.evals, spread(res, depenLen(m))

def getBaselines(M):
 def redict(lst):
  s = lst.strip().split(',')
  return (float(s[0]), float(s[1]))

 def textOut(m,Baselines):
   l=[]
   for kk in Baselines: l+=[str(Baselines[kk][0]), str(Baselines[kk][1])]
   l.insert(0,m.__doc__)
   strln=len(l)-1
   return '%s=%s,%s\n' % (l[0], l[1], l[2])

 
 try:
  f = open('Baselines.txt', 'r')
  newDict={}  
  for line in f:
    listedline = line.strip().split('=') # split around the = sign
    if len(listedline) > 1: # we have the = sign in there
        newDict.update({listedline[0]:redict(listedline[1])})
  f.close()
  try: newDict[M.__doc__]; return newDict
  except KeyError:
   print('Generating Baselines for',M.__doc__)
   f = open('Baselines.txt', 'a')
   reps=int(1e2);
   Baselines={}
   emax=-10e32; emin=10e32;
   for m in [M]:
    for _ in xrange(reps):
     min, max = trials(m, reps=10)
     emax = emax if emax>max else max
     emin = emin if emin<min else min
    Baselines.update({M.__doc__:[emin, emax]})
    f.write(textOut(m, Baselines))  
    f.close()
   return getBaselines(M)
   

 except IOError:
  print('File not found')
  f = open('Baselines.txt', 'w')
  reps=int(1e2);
  Baselines={}
  emax=-10e32; emin=10e32;
  for m in [M]:
   for s in  [_da, _de, _da1]:
    for _ in xrange(reps):
     min, max = trials(m, reps=1)
     emax = emax if emax>max else max
     emin = emin if emin<min else min
    Baselines.update({s.__doc__:[emin, emax]})
   f.write(textOut(m, Baselines))  
   f.close()
  return getBaselines(M)

def newBaseLn(m):
  Baselines={}
  emax=-10e32; emin=10e32;
  for _ in xrange(500):
   min, max = trials(m, reps=1)
   emax = emax if emax>max else max
   emin = emin if emin<min else min
  return emin, emax

def crunch(searcher, model, emax, emin):
 (e, evals, spr) = searcher(model)
 return [abs(np.sum(e)-emin)/(emax-emin), evals, spr]

def iBaseln(model):
  Baselines=[]
  emax, emin = depenLen(model)*[-10**32], depenLen(model)*[10**32]
  for _ in xrange(100):
    val=trials1(model,reps=1)
    for k in xrange(len(val)):
      (min, max)=val[k]
      emax[k] = emax[k] if emax[k]>max else max
      emin[k] = emin[k] if emin[k]<min else min
  Baselines=[(emin[k], emax[k]) for k in len(val)]

def loss(searcher, model):
 print(model.__doc__)
 (e, evals, spr) = searcher(model)
 val=trials1(model,reps=500)
 N = depenLen(model)
 _loss = np.sum([exp((e[i]-val[i])/N) for i in xrange(0,N-1)])/N 
 return _loss
 
def testLearners(m=None):
 if not m: Models=[Schaffer, kursawe, fonseca, 
              ZDT1, ZDT3, DTLZ7,
              xomo]
 else: Models=m
 random.seed(1)
 reps=10;
 searchers = [_da, _de]# _da1]
 for m in Models:
  print('\n', m.__doc__); print(25*'=')
  RES=[];
  Loss=[];
  evals=[];
  Spread=[];
  timer={};
  for s in searchers:
   (emin, emax)=newBaseLn(m);
   t=time.time()
   tmp = [[crunch(s, m, emax, emin)[0],crunch(s, m, emax, emin)[1]
           , crunch(s, m, emax, emin)[2]]  for _ in xrange(reps)]
   t=time.time()-t
   spr=[k[2] for k in tmp]
   eval=[k[1] for k in tmp]
   tmp=[k[0] for k in tmp]
   timer.update({s.__doc__:t/reps})
   tmp.insert(0, s.__doc__)
   eval.insert(0, s.__doc__)
   spr.insert(0, s.__doc__)
   RES.append(tmp)
   Spread.append(spr)
   evals.append(eval)
  # for s in searchers:
  #  tmp = [loss(s, m)  for _ in xrange(reps)]
  #  tmp.insert(0, s.__doc__)
  #  Loss.append(tmp)
  print('\n'); print('Evaluation Time:')
  for tt in timer:
   print(tt,':', '%0.2f'%timer[tt], 's')
  print("\n"); print("Objective scores: "); print(25*"=")
  rdivDemo(RES)
  # print("\n"); print("Quality Score: "); print(25*"=")
  # rdivDemo(Loss)
  print("\n"); print("Spread"); print(25*"=")
  rdivDemo(Spread)
  print("\n"); print("No. of evaluations"); print(25*"=")
  rdivDemo(evals)


   
# for k in res:
#  print(k)
# testLearners()
# _ZDT1()
# _fonseca()
# _de(Schaffer)
# _da(Schaffer)

if __name__ == '__main__':
 testLearners([Schaffer, kursawe, fonseca])
  #print (_da(P))
  #getBaselines(POM3)
#   for m in [Schaffer, kursawe, fonseca, xomo, POM3, ZDT1]:
#    print(trials(m, reps=100))

#cmd('_deadAnt()')
