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
  
 
class N:
  "For nums"
  def __init__(i,col=0,least=0,most=1):
    i.col=col
    i.least, i.most=least,most  
    i.lo,i.hi = 10**32, -1*10**32
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
  def __init__(i,col=0):
      i.col=col
  def __iadd__(i,x): pass
  def norm(i,x):  return x
  def dist(i,x,y): return 0 if x == y else 0
  def fuse(i,x,w1,y,w2):
    return x if rand() <= w1/(w1+w2) else y
  def nudge(i,x,y):
    return x if rand() < 0.33 else y

class O:
  "for objectives"
  def __init__(i,col=0,least=0,most=1,
    love=False # for objectives to maximize, set love to True
    ):
    i._score=None
    i.n= N(col,least,most)
  def score(i,row):
    if i._score == None:
        i.n += i._score = i.evaluate(row)
    return i._score
  def height(i):
    return i.n.norm(i._score)
  def better(i,x,y):
    return x > y if i.love else x < y
  def worse(i,x,y):
      return x < y if i.love else x > y
    for sym in i.syms: sym += cells[sym.col]
  def evalute(i,row):
    "defined by sub-class"
    pass
  
class Row:
  def __init__(i,nums,syms,objs=[]):
    i.nums = [N(j) for j in nums] # numeric indepdents
    i.syms = [S(j) for j in objs] # symbolic independents
    i.objs = [obj(n) for n,obj in enumerate(objs)] # score fields
    i.cells=[]
  def __iadd__(i,cells)
    i.cells = cells
    for col in i.syms: col += cells[sym.col]
    for col in i.nums: col += cells[sym.col]
  def score(i):
    for col in i.objs: col.score(i.cells)
  def fromHell(i):
    x,c = 0,0
    for col in i.obj():
      tmp = col.height()
      tmp = tmp if col.love else 1 - tmp
      x += tmp**2
      c += 1
    return x**0.5/c**0.5
  def dominates(i,j):
    better=False
    for x,y,col in zip(i.cells,j,cells,i.cols)
      if col.worse(x,y):
          return False
      if col.better(x,y):
          better = True
    return better
  def dist(i,j):
    c=d=0
    for col in nums
    
     
