from __future__ import division
"""
Handles sentence parsing procedures.
"""

PARSE='/Lab/Tools/bin/parse'
import os,pytxt

def getSents(ifn):
	f=open(ifn)
	t=str(f.read())
	f.close()
	sents=t.split('<sentence ')
	return sents[1:]

def getNumWords(sentence):
	return len(sentence.split('<word>'))-1
	
def parsetxt(txt):
	import pytxt
	fn=pytxt.write_tmp(txt,suffix='.txt')
	return parse(fn)
	
def parse(fn):
	import subprocess
	re=subprocess.call([PARSE,fn])


def parse2grid(ifn,ldlim=None,shuffle=False):
	ofn=os.path.basename(ifn)
	f=open(ifn)
	t=str(f.read())
	f.close()
	sents=t.split('<sentence ')
	
	if shuffle:
		import random
		random.shuffle(sents)
	
	sentnum=0
	
	ld=[]
	for sentence in sents[1:]:
		sentnum+=1
		
		if ldlim and sentnum>ldlim: break
		parse=sentence.split('<parse>')[1].split('</parse>')[0]
		pdat=parse.split()
		wordi=0
		
		pstack=[]
		words=[]
		for pnum in range(len(pdat)):
			p=pdat[pnum]
			
			if p.startswith('('):		# is tag
				pstack.append((p,0))
			else:						# is word
				## get word stats
				wordi+=1
				word=p.replace(')','')
				words+=[word]
				stresslevel=0
				
				## go through tags in stack according to the number of tags which closed
				num_closing_paren=p.count(')')
				for i in range(num_closing_paren):
					pt=pstack.pop()
					if pt[1]>0:		# if more than one word since this tag began:
						stresslevel+=1
				
				## add 1 to all remaining tags
				for i in range(len(pstack)):
					pstack[i]=(pstack[i][0],pstack[i][1]+1)
				
				## add this word to LD
				d={}
				d['wordnum']=wordi
				d['word']=word
				d['stresslevel']=stresslevel
				d['sentnum']=str(sentnum).zfill(3)
				ld.append(d)
		
		print " ".join(words)	
		
	return ld

def parse2tree(ifn,ldlim=None,shuffle=False):
	ofn=os.path.basename(ifn)
	f=open(ifn)
	t=str(f.read())
	f.close()
	sents=t.split('<sentence ')

	if shuffle:
		import random
		random.shuffle(sents)

	sentnum=0
	import networkx as nx
	noderoot=None
	
	
	ld=[]
	for sentence in sents[1:]:
		sentnum+=1
		G=nx.DiGraph()
		if ldlim and sentnum>ldlim: break
		parse=sentence.split('<parse>')[1].split('</parse>')[0]
		
		print parse
		
		pdat=parse.split()
		wordi=0
		pnumi=-1

		pstack=[]
		words=[]
		wordnodes=[]
		for pnum in range(len(pdat)):
			p=pdat[pnum]
			pnumi+=1
			
			pnop=p.replace('(','').replace(')','')
			if not pytxt.noPunc(pnop): continue
			pnode=(pnumi,pnop)
			
			## lay first stone
			if not len(pstack):
				pstack.append(pnode)
				noderoot=pnode
				continue
			
			
			## make sure maximally binary
			if len(G.edge):
				edges_already=sorted(G.edge[pstack[-1]].keys())
				
				if len(edges_already)>1:
					print edges_already
					
					#newnode=(pnumi+0.1,'NODE')
					newnode=(str(pnumi)+"b",'NODE')
					G.add_edge(pstack[-1],newnode,type='real',prom=None,weight=0)
					for e in edges_already[1:]:
						G.remove_edge(pstack[-1],e)
						G.add_edge(newnode,e,type='real',prom=None,weight=0)
					pstack.pop()
					pstack.append(newnode)
			
			G.add_edge(pstack[-1],pnode,weight=0,type='real',prom=None)
			
			if p.startswith('('):		# is tag	
				#G.edge[pstack[-1]][pnode]['isFinal']=False
				pstack.append(pnode)
			else:						# is word
				#G.edge[pstack[-1]][pnode]['isFinal']=True
			
				## get word stats
				word=p.replace(')','')
				
				words+=[word]
				wordnodes+=[pnode]
				stresslevel=0

				## go through tags in stack according to the number of tags which closed
				num_closing_paren=p.count(')')
				for i in range(num_closing_paren):
					pt=pstack.pop()
		
		for node in G.nodes():
			if node in wordnodes:
				G.node[node]['type']='word'
				G.node[node]['color']='green'
			else:
				G.node[node]['type']='nonword'
		
		G=treeStress(G)
		
		
		
		G=tree2grid(G)
		print G
		

	return None

def short_parse2tree(ifn,ldlim=None,shuffle=False):
	ofn=os.path.basename(ifn)
	f=open(ifn)
	parse=str(f.read())
	f.close()

	import networkx as nx
	noderoot=None
	sentnum = 0
		
	G=nx.DiGraph()
	
	pdat=parse.split()
	wordi=0
	pnumi=-1

	pstack=[]
	words=[]
	wordnodes=[]
	for pnum in range(len(pdat)):
		p=pdat[pnum]
		pnumi+=1
		
		pnop=p.replace('(','').replace(')','')
		if not pytxt.noPunc(pnop): continue
		pnode=(pnumi,pnop)
		
		## lay first stone
		if not len(pstack):
			pstack.append(pnode)
			noderoot=pnode
			continue
		
		
		## make sure maximally binary
		if len(G.edge):
			edges_already=sorted(G.edge[pstack[-1]].keys())
			
			if len(edges_already)>1:
				print edges_already
				
				#newnode=(pnumi+0.1,'NODE')
				newnode=(str(pnumi)+"b",'NODE')
				G.add_edge(pstack[-1],newnode,type='real',prom=None,weight=0)
				for e in edges_already[1:]:
					G.remove_edge(pstack[-1],e)
					G.add_edge(newnode,e,type='real',prom=None,weight=0)
				pstack.pop()
				pstack.append(newnode)
		
		G.add_edge(pstack[-1],pnode,weight=0,type='real',prom=None)
		
		if p.startswith('('):		# is tag	
			#G.edge[pstack[-1]][pnode]['isFinal']=False
			pstack.append(pnode)
		else:						# is word
			#G.edge[pstack[-1]][pnode]['isFinal']=True
		
			## get word stats
			word=p.replace(')','')
			
			words+=[word]
			wordnodes+=[pnode]
			stresslevel=0

			## go through tags in stack according to the number of tags which closed
			num_closing_paren=p.count(')')
			for i in range(num_closing_paren):
				pt=pstack.pop()
	
	for node in G.nodes():
		if node in wordnodes:
			G.node[node]['type']='word'
			G.node[node]['color']='green'
		else:
			G.node[node]['type']='nonword'
	
	G=treeStress(G)
	return G

def create_grid_rec(g, node, level):
	neighbors = g.neighbors(node)
	if not neighbors:
		g.node[node]['grid'] = level
		return level
	
	weak = None
	strong = None
	for nbr in neighbors:
		edge = g[node][nbr]
		if not 'label' in edge:
			continue
		elif edge['label'] == '-':
			weak = nbr
		elif edge['label'] == '+':
			strong = nbr
	
	if weak == None or strong == None:
		neighbors.sort(key=lambda val:val[0])
		return create_grid_rec(g, neighbors[0], level)
	
	w_val = create_grid_rec(g, weak, 0)
	level = max(w_val+1, level)
	return create_grid_rec(g, strong, level)

def create_grid(g):
	root = None
	for node in g.nodes():
		if node[0] == 0:
			root = node
			break
	start = g.neighbors(root)[0]
	return create_grid_rec(g, start, 0)

def tree2grid(G):
	create_grid(G)
	sentence = [node for node in G.nodes() if not G.neighbors(node)]
	sentence.sort(key=lambda val:val[0])
	return [(node[1], G.node[node]['grid']) for node in sentence]

def pathsum(G,path,attr='prom',avg=True):
	ea=None
	psum=[]
	for eb in path:
		if ea:
			psum+=[G.edge[ea][eb][attr]]
		ea=eb
	print psum,
	
	psum=[px for px in psum if px!=None]
	if avg:
		return sum(psum)/len(psum)
	return sum(psum)
		
	

def treeStress(G,edgeFrom=None):
	if not edgeFrom:
		edgeLast=None
		for edge in sorted(list( set( [e[0] for e in G.edges()] ) )):
			G.edge[edge]=treeStress(G,edgeFrom=edge)
	else:
		edges=G.edge[edgeFrom]
		edgesReal=[e for e in G.edge[edgeFrom] if G.edge[edgeFrom][e]['type']!='graphic']
		if len(edgesReal)>1:
			edgei=0
			edgeL=None
			for edge in sorted(edges):
				if G.edge[edgeFrom][edge]['type']=='graphic': continue
				edgei+=1
				
				heavy=(edgei==len(edgesReal))
				
				if heavy:
					G.edge[edgeFrom][edge]['weight']=0
					G.edge[edgeFrom][edge]['label']='+'
					G.edge[edgeFrom][edge]['color']='blue'
					G.edge[edgeFrom][edge]['prom']=1
				else:
					G.edge[edgeFrom][edge]['weight']=0
					G.edge[edgeFrom][edge]['prom']=0
					G.edge[edgeFrom][edge]['label']='-'
					G.edge[edgeFrom][edge]['color']='red'
				G.edge[edgeFrom][edge]['minlen']=1
				
				#if edgeL:
				#	G.add_edge(edgeL,edge,type='graphic',weight=1,prom=None,label='',color='white',minlen=0)
					#G.add_edge(edge,edgeL,type='graphic',weight=0,label='',color='green')
				#edgeL=edge

		return edges
	
	return G

# def treeAlign(G,edgeFrom=None):
# 	if not edgeFrom:
# 		edgeLast=None
# 		for edge in sorted(list( set( [e[0] for e in G.edges()] ) )):
# 			G.edge[edge]=treeAlign(G,edgeFrom=edge)
# 	else:
# 		edges=[e for e in G.edge[edgeFrom].keys() if G.edge[]
# 		if len(edges)>1:
# 			edgei=0
# 			edgeL=None
# 			for edge in sorted(edges):
# 				edgei+=1
# 				if edgeL:
# 					G.add_edge(edgeL,edge,type='graphic',weight=0,label=edgeFrom,color='green')
# 				edgeL=edge
# 
# 		return edges
# 	return G

class PhraseToken(object):
	def __init__(self,**args):
		for k,v in args.items():
			setattr(self,k,v)

class PhraseType(object):
	def __init__(self,words,freq=None,**args):
		for k,v in args.items():
			setattr(self,k,v)
		self.words=words
		self.freq=freq
		self.tokens=[]
	
	def __str__(self):
		return " ".join(self.words)
	
	def addToken(self,token):
		self.tokens.append(token)
	
	
	
		


def parse2phrase(ifn,phrasetype='NP',embedlimit=2,shuffle=False,ldlim=None):
	ofn=os.path.basename(ifn)
	f=open(ifn)
	t=str(f.read())
	f.close()
	sents=t.split('<sentence ')

	if shuffle:
		import random
		random.shuffle(sents)

	sentnum=0
	phrases=[]
	phrase=[]
	ld=[]
	for sentence in sents[1:]:
		sentnum+=1
		if ldlim and sentnum>ldlim: break
		parse=sentence.split('<parse>')[1].split('</parse>')[0]
		
		tokens=[]
		for token in sentence.split('<word>')[1:]:
			token=token.split('</word>')[0]
			tokens+=[token]
		sentlen_word=len(tokens)
		#print parse
		pdat=parse.split()
		sentlen_paren=len(pdat)
		wordi=0
		pnumi=-1
		pstack=[]
		words=[]
		wordnodes=[]
		embedlevel=0
		
		for pnum in range(len(pdat)):
			p=pdat[pnum]
			pnumi+=1
			
			pnop=p.replace('(','').replace(')','')
			if not pytxt.noPunc(pnop): continue
			if pnop==phrasetype:
				#print "yes"
				embedlevel=0
				phrase=[]
			
			
			pnode=(pnumi,pnop)
			
			#print pnumi,wordi,pnop,p,embedlevel
			#print phrase
			
			if p.startswith('('):		# is tag	
				#G.edge[pstack[-1]][pnode]['isFinal']=False
				pstack.append(pnode)
				if embedlevel!=None: embedlevel+=1
			else:						# is word
				#G.edge[pstack[-1]][pnode]['isFinal']=True
			
				## get word stats
				word=p.replace(')','')
				word=word.lower()
				
				words+=[word]
				wordnodes+=[pnode]
				stresslevel=0
				wordi+=1
				
				if embedlevel!=None:
					if embedlevel<=embedlimit:
						phrase+=[ {'word':word, 'paren_num':pnumi+1, 'word_num':wordi+1, 'word_sentlen':sentlen_word, 'paren_sentlen':sentlen_paren} ]
				
				## go through tags in stack according to the number of tags which closed
				num_closing_paren=p.count(')')
				
				#print num_closing_paren,pstack
				for i in range(num_closing_paren):
					if embedlevel!=None: embedlevel-=1
					if len(pstack):
						pt=pstack.pop()
					
					#print pt
					#print pt
					if i==num_closing_paren-1:
						if num_closing_paren<=embedlimit and pt[1]==phrasetype:
						#if pt[1]==phrasetype:
							phrases+=[phrase]
							phrase=[]
							embedlevel=None
							
				
				
			
			#print embedlevel
			
			
			
		

	return phrases


def parse2lines(fn):
	#ifn=sys.argv[1]
	ifn='/Lab/Projects/sentence/parsed/middlemarch.txt.xml'
	ofn=os.path.basename(ifn)
	f=open(ifn)
	t=str(f.read())
	f.close()
	sents=t.split('<sentence ')

	ldlim=100
	for nn in range(30,31):
		ld=[]
		dl={}
		df=None
		o=[]
		sentnum=0
		random.shuffle(sents)
		print nn, "?"
		for sentence in sents[1:]:
			tokens=[]
			for token in sentence.split('<word>')[1:]:
				token=token.split('</word>')[0]
				tokens+=[token]

			if len(tokens)!=nn: continue

			try:
				x=[unicode(bb) for bb in tokens]
			except UnicodeDecodeError:
				continue

			sentnum+=1
			if ldlim and sentnum>ldlim: break
			parse=sentence.split('<parse>')[1].split('</parse>')[0]
			pdat=parse.split()
			wordi=0
			y=4
			o+=[['sent'+str(sentnum).zfill(3)," ".join(tokens)]]


			for pnum in range(len(pdat)):
				p=pdat[pnum]
				try:
					w=tokens[wordi]
				except IndexError:
					continue
				pnop=p.replace('(','').replace(')','')


				if pnop==w:
					wordi+=1
					if wordi>=len(tokens): break

					d={}
					d['wordnum']=wordi
					d['depth']=y
					d['sentnum']=str(sentnum).zfill(3)

					try:
						dl['sent'+str(sentnum).zfill(3)]+=[y]
					except KeyError:
						dl['sent'+str(sentnum).zfill(3)]=[]
						dl['sent'+str(sentnum).zfill(3)]+=[y]

					ld.append(d)

				y+=p.count(')')
				y-=p.count('(')


		if not ld: continue
		if ldlim and sentnum<ldlim: continue
		r1=rpyd2.RpyD2(dl)
		r2=rpyd2.RpyD2(ld)
		pytxt.write('sentkey.'+os.path.basename(ifn)+'.'+str(nn).zfill(3)+'.txt',o,toprint=True)
		#r2.plot(x='wordnum',y='depth',col='sentnum',group='sentnum',line=True,point=False)
		#r1.corrgram()
		r1.kclust(cor=True)
		r1.hclust(cor=True)