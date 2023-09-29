from hash_functions import sha256
from ecdsa import Transaction
import random
from elliptic_curve import bitcoin_G, bitcoin_curve

class Block:
    def __init__(self, block_height, prev_block_hash, transactions):
        self.block_height = block_height
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.block_size = len(transactions)
        
        self.proof_of_work = None # make the first guess
        self.block_hash = None

    def verify_proof_of_work(self):
        pass

    def mine(self, difficulty, block_reward, block_reward_receiver):
        block_reward_tx = Transaction(
              sender_pk=None, 
              receiver_pk=block_reward_receiver, 
              amount=block_reward
            )
        
        self.transactions += [block_reward_tx]
        transaction_data = ''.join([str(tx.sender_pk.x if tx.sender_pk is not None else None) +
                                    str(tx.receiver_pk.x) + 
                                    str(tx.amount) +
                                    str(tx.message) +
                                    str(tx.signature[0] if tx.signature is not None else None) +
                                    str(tx.signature[1] if tx.signature is not None else None) for tx in self.transactions])
        
        block_data = self.prev_block_hash + transaction_data
        block_data_w_pow = block_data + str(self.proof_of_work)
        
        block_hash = sha256(block_data_w_pow.encode('utf-8'), return_hex=True)
        while not block_hash.startswith('0'*difficulty):
            pow = random.randint(1, bitcoin_curve.n - 1)
            block_data_w_pow = block_data + str(pow)
            block_hash = sha256(block_data_w_pow.encode('utf-8'), return_hex=True)

        self.proof_of_work = pow
        self.block_hash = block_hash

class Blockchain:
    def __init__(self):
        self.blocks = []

if __name__ == '__main__':
    genesis_block = Block(block_height=0,
                          prev_block_hash='',
                          transactions=[])

    import time
    start_time = time.time()

    print('mining block...')
    genesis_block.mine(difficulty=5, 
                       block_reward_receiver=bitcoin_G*42,
                       block_reward=50)
    
    end_time = time.time()

    elapsed_time = end_time - start_time
    print('\n')
    print(f"valid hash found:")
    print(f"pow {genesis_block.proof_of_work}")
    print(f"block hash {genesis_block.block_hash}")
    print(f"took {round(elapsed_time,2)} seconds")