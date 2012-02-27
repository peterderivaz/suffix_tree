# Based on http://marknelson.us/1996/08/01/suffix-trees/
from collections import defaultdict

# Guide to understanding the code:
# After k iterations of the main loop you have constructed a suffix tree which contains all suffixes of the complete string that start in the first k characters.
# At the start, this means the suffix tree contains a single root node that represents the entire string (this is the only suffix that starts at 0).
#
# After len(string) iterations you have a suffix tree that contains all suffixes.
#
# During the loop the key is the active point.
# This represents the deepest point in the suffix tree that corresponds to a proper suffix of the first k characters of the string.
# (Proper means that the suffix cannot be the entire string.)
#
# For example, suppose you have seen characters 'abcabc'.
# The active point would represent the point in the tree corresponding to the suffix 'abc'.
#
# The active point is represented by (origin,first,last).
# This means that you are currently at the point in the tree that you get to by starting at node origin and then feeding in the characters in string[first:last]
#
# When you add a new character you look to see whether the active point is still in the existing tree.
# If it is then you are done. Otherwise you need to add a new node to the suffix tree at the active point, fallback to the next shortest match, and check again.
#
# Note 1: The suffix pointers give a link to the next shortest match for each node.
#
# Note 2: When you add a new node and fallback you add a new suffix pointer for the new node. The destination for this suffix pointer will be the node at the shortened active point. This node will either already exist, or be created on the next iteration of this fallback loop.
# 
# Note 3: The canonization part simply saves time in checking the active point. For example, suppose you always used origin=0, and just changed first and last. To check the active point you would have to follow the suffix tree each time along all the intermediate nodes. It makes sense to cache the result of following this path by recording just the distance from the last node.
#




# Consider all substrings ending at current letter
# Active point gives longest pre-existing match (i.e. it is incomplete)
#
# Adding a unique end point will force every suffix to have its own node.
# Otherwise, some suffixes may end at a non-leaf explicit node.
#
# While the active point matches, no new nodes are added.
# Parent nodes only update when new nodes added.
# So at all points, suffix tree is a valid representation of all substrings with start in range allowed.

# Active point is described by origin and characters from first to last.
# When get a mismatch adds new nodes and backtracks to next shorter match, may need to move active point forward (canonicalise)
# Needed so that can test end to see whether it is valid.

class SuffixTree:
    def __init__(self):
        """Returns an empty suffix tree"""
        self.T=''
        self.E={}
        self.nodes=[-1] # 0th node is empty string

    def add(self,s):
        """Adds the input string to the suffix tree.

        This inserts all substrings into the tree.
        End the string with a unique character if you want a leaf-node for every suffix.
        
        Produces an edge graph keyed by (node,character) that gives (first,last,end)
        This means that the edge has characters from T[first:last+1] and goes to node end."""
        origin,first,last = 0,len(self.T),len(self.T)-1
        self.T+=s
        nc = len(self.nodes)
        self.nodes += [-1]*(2*len(s))
        T=self.T
        E=self.E
        nodes=self.nodes
        
        Lm1=len(T)-1
        for last_char_index in xrange(first,len(T)):
            c=T[last_char_index]
            last_parent_node = -1                    
            while 1:
                parent_node = origin
                if first>last:
                    if (origin,c) in E:
                        break             
                else:
                    key = origin,T[first]
                    edge_first, edge_last, edge_end = E[key]
                    span = last - first
                    A = edge_first+span
                    m = T[A+1]
                    if m==c:
                        break
                    E[key] = (edge_first, A, nc)
                    nodes[nc] = origin
                    E[nc,m] = (A+1,edge_last,edge_end)
                    parent_node = nc
                    nc+=1  
                E[parent_node,c] = (last_char_index, Lm1, nc)
                nc+=1  
                if last_parent_node>0:
                    nodes[last_parent_node] = parent_node
                last_parent_node = parent_node
                if origin==0:
                    first+=1
                else:
                    origin = nodes[origin]

                if first <= last:
                    edge_first,edge_last,edge_end=E[origin,T[first]]
                    span = edge_last-edge_first
                    while span <= last - first:
                        first+=span+1
                        origin = edge_end
                        if first <= last:
                            edge_first,edge_last,edge_end = E[origin,T[first]]
                            span = edge_last - edge_first
                
            if last_parent_node>0:
                nodes[last_parent_node] = parent_node
            last+=1
            if first <= last:
                    edge_first,edge_last,edge_end=E[origin,T[first]]
                    span = edge_last-edge_first
                    while span <= last - first:
                        first+=span+1
                        origin = edge_end
                        if first <= last:
                            edge_first,edge_last,edge_end = E[origin,T[first]]
                            span = edge_last - edge_first
        return self

    def walk(self,s):
        """Note this doesn't correctly walk along edges if they have multiple characters"""
        node=0
        for a in s:
            edge=self.E[node,a]
            print edge
            node=edge[2]

    def make_choices(self):
        """Construct a sorted list for each node of the possible continuing characters"""
        choices = self.choices = [list() for n in xrange(len(self.nodes))] # Contains set of choices for each node
        for (origin,c),edge in self.E.items():
            choices[origin].append(c)
        choices=[sorted(s) for s in choices] # should not have any repeats by construction
        return choices
    
    def count_substrings(self,term):
        """Recurses through the tree finding how many substrings are based at each node.
        Strings assumed to use term as the terminating character"""
        C = self.counts = [0]*len(self.nodes)
        choices = self.make_choices()
        def f(node=0):
            t=0
            for c in choices[node]:
                if c==term: continue
                first,last,end = self.E[node,c]
                # All end points along this edge result in new unique substrings
                t+=last-first+1
                t+=f(end)
            C[node]=t
            return t
        return f()

    def count_suffixes(self,term):
        """Recurses through the tree finding how many suffixes are based at each node.
        Strings assumed to use term as the terminating character"""
        C = self.suffix_counts = [0]*len(self.nodes)
        choices = self.make_choices()
        def f(node=0):
            t=0
            X=choices[node]
            if len(X)==0:
                t+=1 # this node is a leaf node
            else:
                for c in X:
                    if c==term:
                        t+=1
                        continue
                    first,last,end = self.E[node,c]
                    t+=f(end)
            C[node]=t
            return t
        return f()
    
            

