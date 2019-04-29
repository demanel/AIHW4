"""
MCTS starter code. This is the only file you'll need to modify, although
you can take a look at game1.py to get a sense of how the game is structured.

@author Bryce Wiedenbeck
@author Anna Rafferty (adapted from original)
"""

# These imports are used by the starter code.
import random
import argparse
import game1

# You will want to use this import in your code
import math
import numpy

# Whether to display the UCB rankings at each turn.
DISPLAY_BOARDS = False

# UCB_CONST value - you should experiment with different values
UCB_CONST = .5


class Node(object):
    """Node used in MCTS"""

    def __init__(self, state, parent_node):
        """Constructor for a new node representing game state
        state. parent_node is the Node that is the parent of this
        one in the MCTS tree. """
        self.state = state
        self.parent = parent_node
        self.children = {} # maps moves (keys) to Nodes (values); if you use it differently, you must also change addMove
        self.visits = 0
        self.value = float("nan")
        # Note: you may add additional fields if needed

    def addMove(self, move):
        """
        Adds a new node for the child resulting from move if one doesn't already exist.
        Returns true if a new node was added, false otherwise.
        """
        if move not in self.children:
            state = self.state.nextState(move)
            self.children[move] = Node(state, self)
            return True
        return False

    def getValue(self):
        """
        Gets the value estimate for the current node. Value estimates should correspond
        to the win percentage for the player at this node (accounting for draws as in
        the project description).
        """
        return self.value

    def updateValue(self, outcome):
        """Updates the value estimate for the node's state.
        outcome: +1 for 1st player win, -1 for 2nd player win, 0 for draw."""
        "*** YOUR CODE HERE ***"
        # NOTE: which outcome is preferred depends on self.state.turn()

        self.visits += 1.0
        normalizedOutcome = (outcome + 1.0) / 2.0
        relativeOutcome = normalizedOutcome
        if numpy.isnan(self.value):
            self.value = relativeOutcome
        else:
            self.value = (self.value * (self.visits - 1.0) / self.visits) + (relativeOutcome / self.visits)

        #raise NotImplementedError("You must implement this method")

    def UCBWeight(self):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        "*** YOUR CODE HERE ***"
        return self.value + UCB_CONST * math.sqrt(math.log(self.parent.visits) / self.visits)
        # value = self.value
        # if numpy.isnan(value):
        #     value = .5
        # UCB_self = value + UCB_CONST*math.sqrt(math.log(self.parent.visits+1.0)/(self.visits+1.0))
        # UCB_sum = 0.0
        # for siblingMove in self.parent.children:
        #     sibling = self.parent.children[siblingMove]
        #     childValue = sibling.value
        #     if numpy.isnan(childValue):
        #         childValue = .5
        #     UCB_sum += childValue + UCB_CONST*math.sqrt(math.log(sibling.parent.visits+1.0)/(sibling.visits+1.0))
        # return UCB_self/UCB_sum

def MCTS(root, rollouts):
    """Select a move by Monte Carlo tree search.
    Plays rollouts random games from the root node to a terminal state.
    In each rollout, play proceeds according to UCB while all children have
    been expanded. The first node with unexpanded children has a random child
    expanded. After expansion, play proceeds by selecting uniform random moves.
    Upon reaching a terminal state, values are propagated back along the
    expanded portion of the path. After all rollouts are completed, the move
    generating the highest value child of root is returned.
    Inputs:
        node: the node for which we want to find the optimal move
        rollouts: the number of root-leaf traversals to run
    Return:
        The legal move from node.state with the highest value estimate
    """
    "*** YOUR CODE HERE ***"
    # NOTE: you will need several helper functions
    #current goal: make this loop for rollout times, making sure to expand correct node each time
    for i in range(rollouts):
        currentNode = root
        nodeToExpand = select(currentNode)
        terminalValue = rollout(nodeToExpand)
        nodeToExpand.updateValue(terminalValue)
        #need to propogate up through parents
        #is root node's parent initialized as None??
        while nodeToExpand.parent != None:
            nodeToExpand.parent.updateValue(terminalValue)
            nodeToExpand = nodeToExpand.parent
    bestMove = None
    if root.state.turn == 1:
        max = -2
        for move in root.state.getMoves():
            print move, root.children[move].getValue()
            if root.children[move].getValue() > max:
                bestMove = move
                max = root.children[move].getValue()
    else:
        min = 2
        for move in root.state.getMoves():
            print move, root.children[move].getValue()
            if root.children[move].getValue() < min:
                bestMove = move
                min = root.children[move].getValue()
    return bestMove


def rollout(node):
    #Note: rollout does NOT update previous nodes

    if node.state.isTerminal():
        return node.state.value()
    else:
        move = random.choice(node.state.getMoves())
        return rollout(Node(node.state.nextState(move), node))

def select(node):
    #Note: rollout does NOT update previous nodes
    if len(node.state.getMoves()) != len(node.children):
        candidates = []
        for move in node.state.getMoves():
            if move not in node.children:
                candidates.append(move)
        chosenMove = random.choice(candidates)
        node.addMove(chosenMove)
        return node.children[chosenMove]

    children = []
    UCBs = []
    if node.state.isTerminal():
        return node
    for move in node.children:
        child = node.children[move]
        children.append(child)
        UCBs.append(child.UCBWeight())
    weights = [UCBs[i] / sum(UCBs) for i in range(len(UCBs))]
    newNode = numpy.random.choice(children, 1, weights)[0]
    return select(newNode)



def parse_args():
    """
    Parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--rollouts", type=int, default=0, help="Number of root-to-leaf "+\
                    "play-throughs that MCTS should run). Default=0 (random moves)")
    p.add_argument("--numGames", type=int, default=0, help="Number of games "+\
                    "to play). Default=1")
    p.add_argument("--second", action="store_true", help="Set this flag to "+\
                    "make your agent move second.")
    p.add_argument("--displayBoard", action="store_true", help="Set this flag to "+\
                    "make display the board at each MCTS turn with MCTS's rankings of moves.")
    p.add_argument("--rolloutsSecondMCTSAgent", type=int, default=0, help="If non-0, other player "+\
                    "will also be an MCTS agent and will use the number of rollouts set with this "+\
                    "argument. Default=0 (other player is random)")
    p.add_argument("--ucbConst", type=float, default=.5, help="Value for the UCB exploration"+\
                    "constant. Default=.5")
    args = p.parse_args()
    if args.displayBoard:
        global DISPLAY_BOARDS
        DISPLAY_BOARDS = True
    global UCB_CONST
    UCB_CONST = args.ucbConst
    return args


def random_move(node):
    """
    Choose a valid move uniformly at random.
    """
    move = random.choice(node.state.getMoves())
    node.addMove(move)
    return move

def run_multiple_games(num_games, args):
    """
    Runs num_games games, with no printing except for a report on which game
    number is currently being played, and reports final number
    of games won by player 1 and draws. args specifies whether player 1 or
    player 2 is MCTS and how many rollouts to use. For multiple games, you
    probably do not want to include the --displayBoard option in args, as
    this will do lots of printing and make running relatively slow.
    """
    player1GamesWon = 0
    draws = 0
    for i in range(num_games):
        print "Game " + str(i)
        node = play_game(args)
        winner = node.state.value()
        if winner == 1:
            player1GamesWon += 1
        elif winner == 0:
            draws += 1
    print "Player 1 games won: " + str(player1GamesWon) + "/" + str(num_games)
    print "Draws: " + str(draws) + "/" + str(num_games)

def play_game(args):
    """
    Play one game against another player.
    args specifies whether player 1 or player 2 is MCTS (
    or both if rolloutsSecondMCTSAgent is non-zero)
    and how many rollouts to use.
    Returns the final terminal node for the game.
    """
    # Make start state and root of MCTS tree
    start_state = game1.new_game()
    root1 = Node(start_state, None)
    if args.rolloutsSecondMCTSAgent != 0:
        root2 = Node(start_state, None)

    # Run MCTS
    node = root1
    if args.rolloutsSecondMCTSAgent != 0:
        node2 = root2
    while not node.state.isTerminal():
        if (not args.second and node.state.turn == 1) or \
                (args.second and node.state.turn == -1):
            move = MCTS(node, args.rollouts)
            if DISPLAY_BOARDS:
                print game1.show_values(node)
        else:
            if args.rolloutsSecondMCTSAgent == 0:
                move = random_move(node)
            else:
                move = MCTS(node2, args.rolloutsSecondMCTSAgent)
                if DISPLAY_BOARDS:
                    print game1.show_values(node2)
        node.addMove(move)
        node = node.children[move]
        if args.rolloutsSecondMCTSAgent != 0:
            node2.addMove(move)
            node2 = node2.children[move]
    return node




def main():
    """
    Play a game of connect 4, using MCTS to choose the moves for one of the players.
    args on command line set properties; see parse_args() for details.
    """
    # Get commandline arguments
    args = parse_args()

    if args.numGames > 1:
        run_multiple_games(args.numGames, args)
    else:
        # Play the game
        node = play_game(args)

        # Print result
        winner = node.state.value()
        print game1.print_board(node.state)
        if winner == 1:
            print "Player 1 wins"
        elif winner == -1:
            print "Player 2 wins"
        else:
            print "It's a draw"


if __name__ == "__main__":
    main()
