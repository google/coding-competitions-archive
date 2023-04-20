# ====================================================================
# == COPIED FROM //recruiting/codejam/app/custom_judges/redblack.py ==
# ====================================================================

# Copyright (c) 2005 Google Inc.
#
# This code adapted from C source from
# Thomas Niemann's Sorting and Searching Algorithms: A Cookbook
#
# From the title page:
#   Permission to reproduce this document, in whole or in part, is
#   given provided the original web site listed below is referenced,
#   and no additional restrictions apply. Source code, when part of
#   a software project, may be used freely without reference to the
#   author.
#
# Adapted by Chris Gonnerman <chris.gonnerman@newcenturycomputers.net>
#        and Graham Breed
#
# Adapted from RBTree.py for Google use by Jon Snitow (otherjon@)
#

"""
redblack.py
  Original source: "Sorting and Searching Algorithms: A Cookbook", T. Niemann
    ->  implemented as RBTree.py by C. Gonnerman & G. Breed
       * see http://newcenturycomputers.net/projects/rbtree.html
    ->  modified to redblack.py by Jon Snitow (otherjon@google.com)

This module provides a red-black tree class (RBTree), and a thin wrapper
to that class which provides a dictionary-like interface (RBDict).

  rbt = redblack.RBTree()
  rbt.Insert(key1, value1)
  rbt.Insert(key2, value2)
  node = rbt.FindNode(key1)
  value1 = node.value()
  rbt.RemoveNode(node)
  keys = [ n.key() for n in rbt.Nodes() ]

  rbd = redblack.RBDict()
  rbd[key1] = value1
  rbd[key2] = value2
  v = rbd[key1]
  del rbd[key1]
  keys = rbd.keys()  # in sorted order, of course
  for key, value in rbd.items(): print '%s: %s' % (key, value)
"""

# A quick review from your data structures class:
#
# A red-black tree is a type of binary search tree which is partially
# self-balancing.  Red-black trees are never unbalanced by a ratio greater
# than 2:1.  Average-case performance is only slightly better than that of
# a binary search tree, but worst-case performance is much better.
#
# Each node in the tree is "colored" either red or black.  Leaf nodes --
# either NULL nodes or (in this implementation) artificial sentinel nodes --
# are colored black.  In addition to the normal properties of binary search
# trees (e.g. inorder-sortedness), red-black trees maintain the following
# two properties: No red node has a red child, and every simple path from
# an internal node to a leaf has the same number of black nodes (called
# the "black-height" of the internal node).
#
# Since the black-height is the same via all paths to a leaf, and no red node
# has a red child, then the worst-case imbalance is for one leaf-path to be
# all black, and another path to alternate black and red.  In this worst case,
# the tree is unbalanced by a factor of 2:1.

VERSION = "1.0"

BLACK = 'BLACK'
RED = ' RED '


class Node:
  """
  This class represents a node in a red-black tree.
  Features: parent pointer, separate key and value storage, evaluates to
    boolean-false if it is a sentinel node.
  Note that new nodes are RED by default, as per the insertion algorithm.
  """
  def __init__(self, key=None, value=None, color=RED):
    self._left = self._right = self._parent = None
    self._color = color
    self._key = key
    self._value = value
    self._is_sentinel = 0

  def __repr__(self):
    if self._is_sentinel:
      return '[%s] None (sentinel node)' % self._color
    return '[%s] %s : %s' % (self._color, repr(self._key), repr(self._value))

  def __nonzero__(self):
    """
    Some internal code has 'if node: do something'
    This function enables that syntactic sugar.
    """
    return not self._is_sentinel

  # Accessor functions -- no setter for _key, because changing _key could
  #  corrupt the tree.
  #
  def key(self): return self._key
  def value(self): return self._value
  def set_value(self, newval): self._value = newval


class RBTree:
  """
  This class represents a red-black tree with the traditional tree-like
  interface: tree.Insert(), tree.RemoveNode(), tree.FindNode(), etc.  See also:
  RBDict class, also in this module.
  """

  # RBTree is a friend of Node
  # pylint: disable=protected-access

  def __init__(self, compare=cmp):
    """
    Initialize a red-black tree.
    Args:
      compare (func(key1,key2)) : comparison function taking tree keys as
      inputs, and returning {negative,zero,positive} if key1 {<,=,>} key2.
    """
    self._initialize(compare=compare)

  def _initialize(self, compare):
    """
    helper method called by __init__() and clear()
    """
    # The artificial sentinel node serves as the null leaf nodes.  All leaves
    #  are the same sentinel node, as is the root of an empty tree.
    #
    self._sentinel = Node(key='__SENTINEL__')
    self._sentinel._left = self._sentinel._right = self._sentinel
    self._sentinel._color = BLACK
    self._sentinel._is_sentinel = 1
    self._root = self._sentinel

    self._count = 0
    # changing the comparison function for an existing tree is dangerous!
    self._cmp = compare

  def compare(self): return self._cmp
  def root_node(self): return self._root
  def sentinel_node(self): return self._sentinel

  def __len__(self): return self._count

  def __contains__(self, key):
    return (self.FindNode(key) is not self._sentinel)

  def __nonzero__(self): return (self._count != 0)

  def __del__(self):
    """
    Unlink and deallocate the whole tree.
    """
    if self._root is not self._sentinel:
      nodes_to_unlink = [ self._root ]
      while nodes_to_unlink:
        cur = nodes_to_unlink[0]
        if cur._left is not self._sentinel:
          nodes_to_unlink.append(cur._left)
        if cur._right is not self._sentinel:
          nodes_to_unlink.append(cur._right)
        cur._right = cur._left = cur._parent = None
        cur._key = cur._value = None
        nodes_to_unlink = nodes_to_unlink[1:]

    self._root = None
    self._sentinel = None

  def __cmp__(self, other):
    """Compare the trees by content."""
    get_node_contents = lambda node: (node.key(), node.value())
    self_contents = [get_node_contents(node) for node in self.Nodes()]
    other_contents = [get_node_contents(node) for node in other.Nodes()]
    return cmp(self_contents, other_contents)

  def __str__(self):
    return "<RBTree object with %d nodes>" % self._count

  def BlackHeight(self, node=None):
    """
    Returns the black-height of the given node, or the black-height of the
    root if node is None.
    """
    if node is None: node = self._root
    if node is self._sentinel: return 0

    left_bh = self.BlackHeight(node._left)
    right_bh = self.BlackHeight(node._right)
    assert(left_bh == right_bh)

    if node._color is BLACK:
      return left_bh + 1
    else:
      return left_bh

  def Height(self, node=None):
    """
    Returns the conventional tree-height of the given node, or the height of
    the root if node is None.
    """
    if node is None: node = self._root
    if node is self._sentinel: return 0

    left_h = self.Height(node._left)
    right_h = self.Height(node._right)
    return 1 + max(left_h, right_h)

  def Show(self, show_sentinels=0):
    """
    Displays the red-black tree in the following format:
      [NodeNum] (COLOR) __str__(node)\n
      [NodeNum] (COLOR) __str__(node)\n
       ...
    E.g., for a five-node tree:
       [1] [BLACK] 2 : 'two'                    2
       [2] [BLACK] 1 : 'one'                   / \
       [3] [BLACK] 4 : 'four'                 1   4
       [6] [ RED ] 3 : 'three'                   / \
       [7] [ RED ] 5 : 'five'                   3   5

    The tree is displayed in breadth-first order.  The children of node
      number N are node number 2N (left child) and 2N+1 (right child).

    Args:
      show_sentinels (boolean) : should we print sentinel nodes?
    Returns:
      None
    """
    # Maintain a queue of [ (nodenumber, node) ... ]
    show_queue = [(1, self._root)]
    width = len(str(1 << self.Height()))
    while show_queue:
      nodenum, node = show_queue[0]
      if not node._is_sentinel or show_sentinels:
        print ('[%' + str(width) + 'd] %s') % (nodenum, node)
      if node is not self._sentinel:
        show_queue.append(
            (2 * nodenum, node._left))
        show_queue.append(
            (1 + 2 * nodenum, node._right))
      show_queue = show_queue[1:]

  def _RotateLeft(self, x):
    """
    Perform the transformation below, which preserves the tree's property
    of inorder-sortedness, but will be useful in preserving red-black
    properties.  Connections marked (*) need to be edited, while unmarked
    connections remain the same.
                [S0]                    [S0]
                 |*                      |*
                 X                       Y
               /   \*       ->         /*  \
            [S1]     Y               X      [S3]
                   /*  \           /   \*
               [S2]    [S3]     [S1]   [S2]

    Args:
      x (Node) : the node about which we'll rotate (labeled X, above)
    Returns: None
    """

    y = x._right

    # establish x._right link
    x._right = y._left
    if y._left is not self._sentinel:
      y._left._parent = x

    # establish y._parent link
    if y is not self._sentinel:
      y._parent = x._parent
    if x._parent is not self._sentinel:
      if x is x._parent._left:
        x._parent._left = y
      else:
        x._parent._right = y
    else:
      self._root = y

    # link x and y
    y._left = x
    if x is not self._sentinel:
      x._parent = y

  def _RotateRight(self, x):
    """
    Perform the transformation below, which preserves the tree's property
    of inorder-sortedness, but will be useful in preserving red-black
    properties.  Connections marked (*) need to be edited, while unmarked
    connections remain the same.
                 [S0]                 [S0]
                  |*                   |*
                  X                    Y
                /*   \      ->       /   \*
              Y      [S3]         [S1]     X
            /   \*                       /*  \
         [S1]   [S2]                 [S2]    [S3]

    Args:
      x (Node) : the node about which we'll rotate (labeled X, above)
    Returns: None
    """

    y = x._left

    # establish x._left link
    x._left = y._right
    if y._right is not self._sentinel:
      y._right._parent = x

    # establish y._parent link
    if y is not self._sentinel:
      y._parent = x._parent
    if x._parent is not self._sentinel:
      if x is x._parent._right:
        x._parent._right = y
      else:
        x._parent._left = y
    else:
      self._root = y

    # link x and y
    y._right = x
    if x is not self._sentinel:
      x._parent = y

  def _RecolorAndRebalanceAfterInsert(self, x):
    """
    After inserting Node x, the tree is valid as a generic binary search tree,
    but not necessarily valid as a red-black tree.  Since all newly inserted
    nodes are red, we may have created a red node which is the child of
    another red node.

    This function detects that case, and transforms the tree to create a
    valid red-black tree.  See e.g. Cormen (or any algorithms book) for a
    full explanation.

    Args:
      x (Node) : the node that was just inserted
    Returns: None
    """

    # Check current node.  At this point, the only potential violation is
    # that we may be looking at a red node which is a child of another red
    # node.  If we're looking at the root node, it clearly isn't the child
    # of a red node (or any node), so we're done.  If this node's parent
    # is black, we no longer have a violation, so we're done.  Otherwise,
    # we perform some transformation which fixes the tree locally and
    # propagates the violation toward the root.
    #
    while x is not self._root and x._parent._color is RED:

      if x._parent is x._parent._parent._left:
        y = x._parent._parent._right

        if y._color is RED:
          # uncle is RED -- tree looks like this:
          #             A                           A
          #           /                           /
          #         B                           B
          #       /   \          * OR *       /   \
          #     C (r)   Y (r)               C(r)   Y(r)
          #   /                               \
          # X (r)                               X(r)
          #
          # B must be black -- otherwise we'd have two violations (B,C both
          #  red and B,Y both red).  C,X both red is a violation, but we can
          #  fix it by making C and Y both black and painting B red.  This
          #  maintains the same black-height from root to leaf, and is
          #  therefore valid.  (We have to continue the red checks at (A,B),
          #  however.)
          #
          x._parent._color = BLACK
          y._color = BLACK
          x._parent._parent._color = RED
          x = x._parent._parent

        else:
          # uncle is BLACK -- tree is unbalanced (uncle Y's subtree is locally
          #   shorter than parent C's).  Tree looks like one of these:
          #             A                           A
          #           /                           /
          #         B                           B
          #       /   \          * OR *       /   \
          #     C (r)   Y (b)               C(r)   Y(b)
          #   /                               \
          # X (r)                               X(r)
          # B must be black -- otherwise we'd have a violation (B,C both
          #  red).  We want to transform the tree to make Y's subtree taller
          #  and X's subtree shorter.  Of {B,C,X}, the middle value will
          #  become the new subtree "root".  That middle value is C if X is
          #  a left child, but it is X if X is a right child.  If X is a
          #  right child, we RotateLeft to reduce it to the other case.  Then
          #  to solve the other case, we RotateRight.
          #

          if x is x._parent._right:
            # make x a left child
            x = x._parent
            self._RotateLeft(x)

          # recolor and rotate
          x._parent._color = BLACK
          x._parent._parent._color = RED
          self._RotateRight(x._parent._parent)
      else:

        # mirror image of above code

        y = x._parent._parent._left

        if y._color is RED:
          # uncle is RED -- color parent and uncle BLACK, and grandparent RED
          x._parent._color = BLACK
          y._color = BLACK
          x._parent._parent._color = RED
          x = x._parent._parent

        else:
          # uncle is BLACK -- tree is locally imbalanced
          # perform acrobatics as above
          if x is x._parent._left:
            x = x._parent
            self._RotateRight(x)

          x._parent._color = BLACK
          x._parent._parent._color = RED
          self._RotateLeft(x._parent._parent)

    self._root._color = BLACK

  def Insert(self, key, value):
    """
    Insert the (key, value) pair into the red-black tree, allocating a node
      for this purpose.

    The tree doe not support multiple nodes with equivalent keys (i.e.
      keys for which compare() returns 0).  If you insert a key which already
      exists, this function will quietly overwrite the old value.

    Args:
      key (any immutable)
      value (any)
    Returns:
      (Node) The node created (or commandeered, if key already existed)
    """
    # we aren't interested in the value, we just
    # want the TypeError raised if appropriate
    _ = hash(key)

    # find where node belongs
    current = self._root
    parent = self._sentinel
    while current is not self._sentinel:
      rc = self._cmp(key, current.key())
      if rc == 0:
        current._value = value
        return current
      parent = current
      if rc < 0:
        current = current._left
      else:
        current = current._right

    # setup new node -- note that new nodes are RED be default
    x = Node(key, value)
    x._left = x._right = self._sentinel
    x._parent = parent

    self._count = self._count + 1

    # insert node in tree
    if parent is not self._sentinel:
      if self._cmp(key, parent.key()) < 0:
        parent._left = x
      else:
        parent._right = x
    else:
      self._root = x

    # We now have a valid binary search tree, but we still have to make it
    #  a valid red-black tree...
    #
    self._RecolorAndRebalanceAfterInsert(x)

    return x

  def _RecolorAndRebalanceAfterRemove(self, x):
    """
    Args: x (Node)
    Returns: None

    After removing Node x, the tree is valid as a generic binary search tree,
    but not necessarily valid as a red-black tree.

    Of the three remove cases (removed node has zero, one, or two children),
    Case 1 is harmless.  Case 1 and Case 2 can create successive red nodes,
    however, and this must be fixed.

    This function detects that case, and transforms the tree to create a
    valid red-black tree.  See e.g. Cormen (or any algorithms book) for a
    full explanation.

    Args:
      x (Node) : the node that was just removed
    Returns: None
    """

    # Recoloring and rebalancing after a delete is complicated.  See an
    #  algorithms textbook, e.g. Corman.
    #
    while x is not self._root and x._color is BLACK:
      if x is x._parent._left:
        w = x._parent._right
        if w._color is RED:
          w._color = BLACK
          x._parent._color = RED
          self._RotateLeft(x._parent)
          w = x._parent._right

        if w._left._color is BLACK and w._right._color is BLACK:
          w._color = RED
          x = x._parent
        else:
          if w._right._color is BLACK:
            w._left._color = BLACK
            w._color = RED
            self._RotateRight(w)
            w = x._parent._right

          w._color = x._parent._color
          x._parent._color = BLACK
          w._right._color = BLACK
          self._RotateLeft(x._parent)
          x = self._root

      else:
        # mirror image of the code above
        w = x._parent._left
        if w._color is RED:
          w._color = BLACK
          x._parent._color = RED
          self._RotateRight(x._parent)
          w = x._parent._left

        if w._right._color is BLACK and w._left._color is BLACK:
          w._color = RED
          x = x._parent
        else:
          if w._left._color is BLACK:
            w._right._color = BLACK
            w._color = RED
            self._RotateLeft(w)
            w = x._parent._left

          w._color = x._parent._color
          x._parent._color = BLACK
          w._left._color = BLACK
          self._RotateRight(x._parent)
          x = self._root

    x._color = BLACK

  def DeleteNode(self, z): self.RemoveNode(z)    # common alias

  def RemoveNode(self, z):
    """
    Args: z (Node)
    Returns: None

    This function removes Node z from the tree.  Recall that deleting from
    a binary search tree encompasses three cases:
      (1) z has no children (trivial)
      (2) z has one child (easy)
      (3) z has two children (not so easy)

    In case 2 and case 3, we will be splicing out a node.  In case 2, we'll
    be splicing out z itself.  In case 3, we find the successor node to z,
    which will have no left-hand children.  (If it did, the child would be
    the successor to z...)  Therefore, in case 3, we'll be splicing out
    z's successor.  In either case, we'll call the node we intend to splice
    out "y".

    We know that y has at most one child.  If y and z are different (case 3),
    then y will take z's place in the tree.  In either case, y's child
    (which we'll call "x") will take y's place in the tree.
    """

    if z is None or z is self._sentinel:
      return

    if z._left is self._sentinel or z._right is self._sentinel:
      # y has a self._sentinel node as a child -- case 1 or case 2
      y = z
    else:
      # case 3: find tree successor with a self._sentinel node as a child
      y = z._right
      while y._left is not self._sentinel:
        y = y._left

    # y is the node we'll splice out
    # x is y's only child, or a sentinel if y has no children
    if y._left is not self._sentinel:
      x = y._left
    else:
      x = y._right

    # remove y from the parent chain
    # (we're cheating here -- x may be the sentinel node, and we're using
    #  its parent field as swap space)
    # TODO: rewrite so as not to cheat
    #
    #      A                   A
    #     / \        ->       / \
    #    B   Y               B   X
    #   / \   \             / \ / \
    #   ...    X            ... ...
    #         / \
    #         ...
    x._parent = y._parent
    if y._parent is not self._sentinel:
      # if y is not the root...
      if y is y._parent._left:
        y._parent._left = x
      else:
        y._parent._right = x
    else:
      self._root = x

    if y is not z:
      # we're in Case 3: z had two children
      #                      ___
      #      A              |   |     A              A
      #     / \             | Y |    / \    ->      / \
      #    Z  ...           |___|   Z  ...         Y  ...
      #   / \                      / \            / \
      #    ...                      ...            ...
      #     /       ------>          /              /
      #    Y                        X              X
      #     \                      / \            / \
      #      X                     ...            ...
      #     / \
      #     ...
      z._key = y.key()
      z._value = y.value()

    # The former Z node (now Y) has the same color it had before -- no problem
    #  there.  The only potential issue is that if Y was black, X may be red
    #  and its new parent may also be red.  However, if Y was black, then
    #  we've also messed up the black-height for any path containing Y.  We'll
    #  need to fix things up, if y was black.
    #
    if y._color is BLACK:
      self._RecolorAndRebalanceAfterRemove(x)

    del y
    self._count = self._count - 1

  def FindNode(self, key):
    """
    If the tree contains the key, return the appropriate Node object.
    Args:
      key (any immutable) : key to search for
    Returns:
      Node (if key is found), None otherwise
    """

    # we aren't interested in the value, we just
    # want the TypeError raised if appropriate
    hash(key)

    current = self._root

    while current is not self._sentinel:
      rc = self._cmp(key, current.key())
      if rc == 0:
        return current
      else:
        if rc < 0:
          current = current._left
        else:
          current = current._right

    return self._sentinel

  def Traverse(self, f):
    """
    Perform function f on every node in the tree.
    Args:
      f : function taking one param, a Node object; return value ignored.
    Returns: None
    """
    if self._root is self._sentinel:
      return

    # s will be a stack of parent nodes
    s = [ None ]  # this evaluates to True
    cur = self._root
    while s:
      if cur._left is not self._sentinel:
        s.append(cur)
        cur = cur._left
      else:
        f(cur)
        while cur._right is self._sentinel:
          cur = s.pop()
          if cur is None:
            return
          f(cur)
        cur = cur._right

    # should not get here.
    return

  def NodesByTraversal(self):
    """
    Returns all nodes as a list.
    The Nodes() function below is faster and clearer.  This function exists
      primarily for the internal-consistency unit test.
    """
    result = []
    self.Traverse(result.append)
    return result

  def Nodes(self):
    """Returns all nodes as a list."""
    cur = self.FirstNode()
    result = []
    while cur is not self._sentinel:
      result.append(cur)
      cur = self.NextNode(cur)
    return result

  def FirstNode(self):
    """returns the first node in the tree"""
    cur = self._root
    while cur._left is not self._sentinel:
      cur = cur._left
    return cur

  def LastNode(self):
    """returns the last node in the tree"""
    cur = self._root
    while cur._right is not self._sentinel:
      cur = cur._right
    return cur

  def NextNode(self, node):
    """Returns the node after <node>.

    Args:
      node: Node, of which the next node shall be determined.
    Returns:
      Next node, or sentinel, if node is the first
    """
    cur = node
    if cur._right is not self._sentinel:
      cur = node._right
      while cur._left is not self._sentinel:
        cur = cur._left
      return cur
    while True:
      cur = cur._parent
      if cur is self._sentinel:
        return cur
      if self._cmp(cur.key(), node.key()) >= 0:
        return cur

  def PrevNode(self, node):
    """Returns the node before <node>.

    Args:
      node: Node, of which the previous node shall be determined.
    Returns:
      Previous node, or sentinel, if node is the first
    """
    cur = node
    if cur._left is not self._sentinel:
      cur = node._left
      while cur._right is not self._sentinel:
        cur = cur._right
      return cur
    while True:
      cur = cur._parent
      if cur is self._sentinel:
        return cur
      if self._cmp(cur.key(), node.key()) < 0:
        return cur

  def NextNodeByKey(self, key):
    """Return node with smallest key larger then <key>.

    Given a key -- which may or may not be in the tree! -- find the node
      occurring strictly after that key.

    Args:
      key: The key
    Returns:
      The node, which comes next after the key.
    """
    sentinel = self._sentinel
    cur_node = self._root
    cmp_function = self._cmp

    if cur_node is sentinel:
      return sentinel

    while cur_node is not sentinel:
      cmp_value = cmp_function(key, cur_node.key())
      if cmp_value == 0:
        # Great! key already in tree.. get next node.
        return self.NextNode(cur_node)
      else:
        if cmp_value < 0:
          next_node = cur_node._left
          if next_node is sentinel:
            return cur_node
          cur_node = next_node
        else:
          next_node = cur_node._right
          if next_node is sentinel:
            return self.NextNode(cur_node)
          cur_node = next_node

    # should never get here
    assert False

  def PrevNodeByKey(self, key):
    """Return node with largest key smaller then <key>.

    Given a key -- which may or may not be in the tree! -- find the node
      occurring strictly before that key.

    Args:
      key: The key
    Returns:
      The node, which comes directly before the key.
    """
    sentinel = self._sentinel
    cur_node = self._root

    if cur_node is sentinel:
      return sentinel

    while cur_node is not sentinel:
      cmp_value = self._cmp(key, cur_node.key())
      if cmp_value == 0:
        # Great! key already in tree.. get next node.
        return self.PrevNode(cur_node)
      else:
        if cmp_value < 0:
          next_node = cur_node._left
          if next_node is sentinel:
            return self.PrevNode(cur_node)
          cur_node = next_node
        else:
          next_node = cur_node._right
          if next_node is sentinel:
            return cur_node
          cur_node = next_node

    # should never get here
    assert False


class RBDict(RBTree):
  """
  This class wraps the RBTree class with a thin dictionary-like interface.
  """

  def __init__(self, dictionary=None, compare=cmp):
    RBTree.__init__(self, compare)
    for key, value in (dictionary or {}).items():
      self.Insert(key, value)

  def __str__(self):
    # eval(str(self)) returns a regular dictionary
    nodes = self.Nodes()
    nodestrings = ["%s: %s" % (repr(i.key()), repr(i.value())) for i in nodes]
    return "{" + ", ".join(nodestrings) + "}"

  def __repr__(self):
    return "<RBDict object " + str(self) + ">"

  def __getitem__(self, key):
    n = self.FindNode(key)
    if n:
      return n.value()
    raise KeyError

  def __setitem__(self, key, value):
    n = self.FindNode(key)
    if n:
      n._value = value
    else:
      self.Insert(key, value)

  def __delitem__(self, key):
    n = self.FindNode(key)
    if n:
      self.RemoveNode(n)
    else:
      raise KeyError

  def get(self, key, default=None):
    n = self.FindNode(key)
    if n:
      return n.value()
    return default

  def keys(self):
    return map(lambda x: x.key(), self.Nodes())

  def values(self):
    return map(lambda x: x.value(), self.Nodes())

  def items(self):
    return [(i.key(), i.value()) for i in self.Nodes()]

  def has_key(self, key):
    return self.FindNode(key) is not self._sentinel

  def clear(self):
    """delete all entries"""

    self.__del__()
    self._initialize(self._cmp)

  def copy(self):
    """return shallow copy"""
    newrbd = RBDict()
    for key, value in self.items():
      newrbd[key] = value
    return newrbd

  def update(self, other):
    """
    Add all items from the supplied mapping to this one.  This will
     overwrite old entries with new ones.
    Args:
      other (dict-like object) : source of new data
    Returns: None
    """
    for key, value in other.items():
      self[key] = value

  def setdefault(self, key, value=None):
    if self.has_key(key):
      return self[key]
    self[key] = value
    return value

  def __iter__(self):
    cur_node = self.FirstNode()
    sentinel = self._sentinel
    while cur_node is not None and cur_node is not sentinel:
      yield cur_node._key
      if cur_node._parent is None:
        cur_node = self.NextNodeByKey(cur_node._key)
      else:
        cur_node = self.NextNode(cur_node)

  def iteritems(self):
    cur_node = self.FirstNode()
    sentinel = self._sentinel
    while cur_node is not None and cur_node is not sentinel:
      yield (cur_node._key, cur_node._value)
      if cur_node._parent is None:
        cur_node = self.NextNodeByKey(cur_node._key)
      else:
        cur_node = self.NextNode(cur_node)

# ===============================================================
# == END OF //recruiting/codejam/app/custom_judges/redblack.py ==
# ===============================================================

# Copyright 2011 Google Inc. All Rights Reserved.

"""Basic utilities for custom judges."""

__author__ = 'darthur@google.com (David Arthur)'

import logging


# Copied from judge.py
def _utils_Tokenize(text, case_sensitive=True):
  """Converts a block of text into a two-dimensional array of strings.

  Args:
    text: A block of text, probably either a contestant or generator output.
    case_sensitive: Whether all text should be converted to lower-case.

  Returns:
    A two-dimensional array of strings. There is one element for each non-blank
    row in the output, and there is one inner element for each token on that
    row. If text contains any characters outside ASCII range 32-126 (with the
    exception of tabs, carriage returns, and line feeds), None is returned.
  """
  if not case_sensitive:
    text = text.lower()
  text = text.replace('\t', ' ').replace('\r', '\n')
  for char in text:
    if not (32 <= ord(char) <= 126) and char != '\n':
      return None
  return [filter(None, row.split(' ')) for row in text.split('\n')
          if row.strip()]


def _utils_TokenizeAndSplitCases(output_file, attempt, num_cases,
                          case_sensitive=False):
  """Tokenizes the generator output file and attempt file by case number.

  This is similar to Tokenize except that:
    - It applies to both output_file and attempt.
    - The results are 3-dimensional vectors split by case number, and with the
      "Case #N:" tokens removed.
    - There could be empty rows due to the previous.
    - The number of cases in the output file and attempt must match num_cases.
    - An error string is returned if something is incorrect.

  Args:
    output_file: The output file, as given in FindError.
    attempt: The attempt file, as given in FindError.
    num_cases: The number of cases in the input file.
    case_sensitive: Whether to run in case-sensitive mode (for everything
      except the word 'Case' itself).

  Returns:
    On success, tokenized_output, tokenized_attempt, None is returned. Each of
    these are 3-dimensional arrays of tokens, sorted by case number, line
    number, and token. On failure, None, None, error is returned.
  """

  def ProcessOneFile(text, num_cases):
    """Similar to TokenizeAndSplitCases except applied to only one file."""

    # Tokenize and validate ASCII-ness. Case insensitive checking allows, for
    # example, contestants to output "case #N:" instead of "Case #N:".

    tokenized_text = _utils_Tokenize(text, case_sensitive=case_sensitive)
    if tokenized_text is None:
      return None, 'Invalid or non-ASCII characters.'

    # Build our result in split text.
    split_text = []
    # Even if case-sensitivity is on, allow the contestant to use any form of
    # 'case', since some contestants may have gotten accustomed to the
    # older, more flexible rules.
    for line in tokenized_text:
      if (len(line) >= 2 and
          line[0].lower() == 'case' and
          line[1].startswith('#')):
        # This line is a "Case #N:" line.
        expected_case = 1 + len(split_text)
        if line[1] != ('#%d:' % expected_case):
          return None, ('Expected "case #%d:", found "%s %s".'
                        % (expected_case, line[0], line[1]))
        if expected_case > num_cases:
          return None, 'Too many cases.'
        split_text.append([line[2:]])
      else:
        # This line is any other kind of line.
        if not split_text:
          return None, 'File does not begin with "case #1:".'
        split_text[-1].append(line)

    # At the end, make sure we had enough cases.
    if len(split_text) < num_cases:
      return None, 'Too few cases.'
    return split_text, None

  # Parse the generator output file. If something is wrong here, log an error.
  split_output, error = ProcessOneFile(output_file, num_cases)
  if error:
    error = 'Invalid generator output file: %s' % error
    logging.error(error)
    return None, None, error

  # Parse the user output file attempt.
  split_attempt, error = ProcessOneFile(attempt, num_cases)
  if error:
    error = 'Invalid attempt file: %s' % error
    return None, None, error
  return split_output, split_attempt, None


def _utils_ToInteger(s, minimum_value=None, maximum_value=None):
  """Returns int(s) if s is an integer in the given range. Otherwise None.

  The range is inclusive. Also, leading zeroes and negative zeros are not
  allowed.

  Args:
    s: A string to convert to an integer.
    minimum_value: If not-None, then s must be at least this value.
    maximum_value: If not-None, then s must be at most this value.

  Returns:
    An integer in the given range or None.
  """
  try:
    value = int(s)
    if len(s) > 1 and s.startswith('0'):
      return None
    if s.startswith('-0'):
      return None
    if minimum_value is not None and value < minimum_value:
      return None
    if maximum_value is not None and value > maximum_value:
      return None
    return value
  except ValueError:
    return None


def _utils_ToFloat(s):
  """Returns float(s) if s is a float. Otherwise None.

  Disallows infinities and nans.

  Args:
    s: A string to convert to a float.

  Returns:
    An float or None.
  """
  try:
    x = float(s)
    if x not in [float('inf'), float('-inf')] and x == x:  # not NaN
      return x
    else:
      return None
  except ValueError:
    return None
"""A custom judge for the Rural Planning problem."""

__author__ = 'tomek@google.com (Tomek Czajka)'



def ParseInput(input_file):
  """Parse input.

  Args:
    input_file: str
  Returns:
    list of list of (int, int)
  """
  lines = input_file.splitlines()
  ntc = int(lines[0])
  test_cases = []
  index = 1
  for _ in xrange(ntc):
    n = int(lines[index])
    index += 1
    test_case = []
    for _ in xrange(n):
      x, y = map(int, lines[index].split())
      index += 1
      test_case.append((x, y))
    test_cases.append(test_case)
  return test_cases


def Sign(x):
  if x < 0:
    return -1
  elif x == 0:
    return 0
  else:
    return 1


def Minus(p, q):
  """Vector subtraction."""
  return (p[0] - q[0], p[1] - q[1])


def CrossProduct(p, q):
  """Vector cross product."""
  return p[0] * q[1] - p[1] * q[0]


def HalfConvexHull(points):
  """Computes the bottom half of the convex hull.

  Args:
    points: sorted list of points
  Returns:
    list of points
  """
  hull = []
  for p in points:
    while len(hull) >= 2 and CrossProduct(
        Minus(hull[-1], hull[-2]), Minus(p, hull[-2])) <= 0:
      hull.pop()
    hull.append(p)
  return hull


def ConvexHull(points):
  """Computes the convex hull.

  Args:
    points: list of points
  Returns:
    list of points
  """
  sorted_points = sorted(points)
  hull = HalfConvexHull(sorted_points)
  hull.pop()
  sorted_points.reverse()
  hull.extend(HalfConvexHull(sorted_points))
  hull.pop()
  return hull


def AreaTimes2(polygon):
  """Computes twice the area of a simple polygon."""
  area = 0
  n = len(polygon)
  for i in xrange(n):
    area += CrossProduct(polygon[i], polygon[(i+1) % n])
  return abs(area)


class AttemptFailedException(Exception):
  pass


class IntersectionException(AttemptFailedException):
  def __init__(self, segment1, segment2):
    AttemptFailedException.__init__(
        self, 'Self-intersection: %s %s' % (segment1, segment2))


def CheckNoDuplicates(numbers):
  """Checks that there are no duplicates.

  Args:
    numbers: list of ints
  Raises:
    AttemptFailedException: if there is a duplicate
  """
  x = sorted(numbers)
  for i in xrange(len(x)-1):
    if x[i] == x[i+1]:
      raise AttemptFailedException('Repeated number %d' % x[i])


def CompareSegments(segment1, segment2):
  """Checks whether segment1 lies below or above segment2.

  Both segments go left to right.
  There is a vertical line intersecting the interiors of both segments
  ("vertical" according to the (x, y) ordering).

  Args:
    segment1: (point, point)
    segment2: (point, point)
  Returns:
    -1 if segment1 lies below segment2
    +1 if segment1 lies above segment2
    0 if they are equal
  Raises:
    IntersectionException: if segments are different and intersect somewhere
        other than at endpoints
  """
  if segment1 == segment2: return 0
  (a, b) = segment1
  (c, d) = segment2
  a_side = Sign(CrossProduct(Minus(d, c), Minus(a, c)))
  b_side = Sign(CrossProduct(Minus(d, c), Minus(b, c)))
  c_side = Sign(CrossProduct(Minus(b, a), Minus(c, a)))
  d_side = Sign(CrossProduct(Minus(b, a), Minus(d, a)))
  if c_side == 0 and d_side == 0:
    # colinear
    raise IntersectionException(segment1, segment2)
  elif a == c:
    return b_side
  elif b == d:
    return a_side
  elif a_side == b_side:
    return a_side
  elif c_side == d_side:
    return -c_side
  else:
    raise IntersectionException(segment1, segment2)


def CheckSimplePolygon(polygon):
  """Checks if a polygon doesn't intersect itself.

  Args:
    polygon: a list of at least 3 distinct points
  Raises:
    IntersectionException: if not a simple polygon
  """
  # An O(n log n) sweep algorithm.
  n = len(polygon)
  assert n >= 3
  # Sweep left to right. Add segments at left-most points, delete at right-most
  # points. Delete has priority over add.
  segments = []  # both ways
  for i in xrange(n):
    p = polygon[i]
    q = polygon[(i+1) % n]
    segments.append((p, q))
    segments.append((q, p))
  segments.sort()
  tree = RBTree(compare=CompareSegments)
  for (p, q) in segments:
    if p < q:
      tree.Insert((p, q), None)  # may raise IntersectionException
    else:
      # FindNode may also raise IntersectionException, which would have been
      # detected anyway at a later time.
      node = tree.FindNode((q, p))
      assert node is not tree.sentinel_node()
      # Fetch the next segment if any.
      next_node = tree.NextNode(node)
      if next_node is tree.sentinel_node():
        next_seg = None
      else:
        next_seg = next_node.key()
      # Remove.
      tree.RemoveNode(node)
      # Now check if new neighbors intersect by re-inserting next_seg.
      if next_seg is not None:
        # next_node is no longer valid, because RemoveNode moves keys between
        # other nodes (!?). So we look it up again.
        next_node = tree.FindNode(next_seg)  # may raise IntersectionException
        tree.RemoveNode(next_node)
        tree.Insert(next_seg, None)  # may raise IntersectionException


def JudgeCase(test_case, attempt):
  """Judge a single test case.

  Args:
    test_case: list of points
    attempt: list of lists of strings (tokens)
  Raises:
    AttemptFailedException: if attempt is wrong
  """
  n = len(test_case)
  if len(attempt) != 1:
    raise AttemptFailedException('Expected 1 line, got %d lines' % len(attempt))
  if len(attempt[0]) != n:
    raise AttemptFailedException(
        'Expected %d tokens, got %d tokens' % (n, len(attempt[0])))
  permutation = []
  for token in attempt[0]:
    p = _utils_ToInteger(token, minimum_value=0, maximum_value=n-1)
    if p is None:
      raise AttemptFailedException(
          'Expected an integer in [0, %d), got %s' % (n, token))
    permutation.append(p)

  CheckNoDuplicates(permutation)
  polygon = [test_case[p] for p in permutation]
  CheckSimplePolygon(polygon)

  hull_area = AreaTimes2(ConvexHull(test_case))
  area = AreaTimes2(polygon)
  if 2 * area <= hull_area:
    raise AttemptFailedException(
        'Area too small: %d/2 out of %d/2' % (area, hull_area))


def FindError(unused_self, input_file, output_file, attempt):
  """Judges an attempt.

  Args:
    input_file: input
    output_file: must have the right number of test cases, but contents
      are ignored
    attempt: solution attempt
  Returns:
    None if the attempt is correct or a str error otherwise.
  """
  input_cases = ParseInput(input_file)
  unused_output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error is not None: return error
  for tc in xrange(len(input_cases)):
    try:
      JudgeCase(input_cases[tc], attempt_cases[tc])
    except AttemptFailedException as e:
      return 'Case #%d: %s' % (tc + 1, e.message)
  return None  # Huge success!

import sys
if __name__ == "__main__":
  if sys.argv[1] == '-2':
    sys.exit(0)
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
