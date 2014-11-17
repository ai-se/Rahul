from _model import *
import sys, pdb
import os
_HOME=os.environ["HOME"]
sys.path.insert(0,_HOME+"/git/ai-se/Rahul/DEADANT")
from deadAnt import *
class Model:
 def __init__(self,name):
  self.name = name
  if name == 'pom3':
   self.model = Pom()
  elif name == 'xomo':
   self.model = Xomo(model = 'flight')
  elif name == 'xomoflight':
   self.model = Xomo(model='flight')
  elif name == 'xomoground':
   self.model = Xomo(model='ground')
  elif name == 'xomoosp':
   self.model = Xomo(model='osp')
  elif name == 'xomoosp2':
   self.model = Xomo(model='osp2')
  elif name == 'xomoall':
   self.model = Xomo(model='all')
  else:
   sys.stderr.write("Enter valid model name pom3 or xomoflight --> xomo[flight/ground/osp/osp2/all]\n")
   sys.exit()

 def trials(self,N,verbose=False):
  #returns headers and rows
  return self.model.trials(N,verbose)

 def oo(self, verbose=False):
  return self.model.c

 def update(self,fea,cond,thresh):
  #cond is true when <=
  self.model.update(fea,cond,thresh)

 def __repr__(self):
  return self.name

def p(m,headers,rows):
 print "#"*50,m
 print ">>>>>>","headers"
 print headers
 print ">>>>>","rows"
 print rows

# Model Demo
def modeld():
 m = Model('xomoall')
 headers,rows = m.trials(5)
 p(m,headers,rows)
 m = Model('pom3')
 headers,rows = m.trials(5)
 p(m,headers,rows)

# def lookInto():
#  m = Model('xomoall')
#  c = m.oo()

def xomo(modelName='xomoall'):
 m = Model(modelName)
 c = m.oo()
 scaleFactors=c.scaleFactors
 effortMultipliers=c.effortMultipliers
 defectRemovers=c.defectRemovers
 headers = scaleFactors+effortMultipliers+defectRemovers
 bounds={h:(c.all[h].min, c.all[h].max) 
         for h in headers}
 a=c.x()['b']; b=c.all['b'].y(a)
 
 restructure = lambda x: {headers[i]: x(i) 
                           for i in xrange(len(headers))}
 
 sum   = lambda x: c.sumSfs(restructure(x),reset=True)
 prod  = lambda x: c.prodEms(restructure(x),reset=True)
 exp   = lambda x: b + 0.01 * sum(x)
 effort  = lambda x: c.effort_calc(restructure(x[1:-4]), 
                                   a, b, exp(x), sum(x), prod(x))
 months  = lambda x: c.month_calc(restructure(x[1:-4]), 
                                  effort(x), sum(x), prod(x))
 defects = lambda x: c.defect_calc(restructure(x[1:-4]))
 risks   = lambda x: c.risk_calc(restructure(x[1:-4]))
 
 return Cols(xomo,
             [N(least=bounds[h][0], most=bounds[h][1])
              for h in headers] + 
             [effort, months, defects, risks])




if __name__ == '__main__':
 getModels()
