from ecdsa import Transaction
from blockchain import Block, Blockchain
from elliptic_curve import bitcoin_G
from network import broadcast
from consensus_parameters import MINING_DIFFICULTY, BLOCK_SIZE
import time
import random

# create the genesis block and broadcast it

receivers = random.sample(list(range(5001, 5005)), 1)
print(f'seed chain will be broadcasted to {receivers}.')

print('mining the genesis block.')
genesis_block = Block(block_height=0,
                    prev_block_hash='',
                    transactions=[])
genesis_block.mine(difficulty=MINING_DIFFICULTY, block_reward=50, block_reward_receiver=bitcoin_G * 42, iterations=int(1e12))

broadcast((genesis_block, 42), receivers)
print(f'seed chain broadcasted.')