# BetaBot
AlphaGo's beta counterpart.

game board state (encoded for neural networks): tracked move-by-move with game state tree
tree search: makes predictions on sequence of decisions
neural network: extract game-relevant features w/ CNNs, pool layers, softmax activations on last layer, categorical cross-entropy as loss func
deep learning: build data with Smart Game Format, encode important properties (like num of liberties) in feature planes
reinforcement learning: training agent to learn from experience w/ states, actions, rewards; further collect data from self-play
policy gradients:
value methods:
actor-critic methods:
