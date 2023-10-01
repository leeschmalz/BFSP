from hash_functions import sha256
from ecdsa import Transaction
import random
from elliptic_curve import bitcoin_G, bitcoin_curve

class Block:
    def __init__(self, block_height=None, prev_block_hash='', transactions=[]):
        self.block_height = block_height
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        
        self.proof_of_work = None
        self.block_hash = None

    def aggregate_tx_data(self):
        # concatenate all transaction data into a string to be hashed
        transaction_data = ''.join([str(tx.sender_pk.x if tx.sender_pk is not None else None) +
                            str(tx.receiver_pk.x) + 
                            str(tx.amount) +
                            str(tx.message) +
                            str(tx.signature[0] if tx.signature is not None else None) +
                            str(tx.signature[1] if tx.signature is not None else None) for tx in self.transactions])
        
        return transaction_data

    def verify_tx_signatures(self):
        return all(transaction.verify_signature() for transaction in self.transactions)

    def verify_proof_of_work(self, difficulty):
        transaction_data = self.aggregate_tx_data()
        
        block_data_w_pow = self.prev_block_hash + transaction_data + str(self.proof_of_work)
        block_hash = sha256(block_data_w_pow.encode('utf-8'), return_hex=True)
        
        valid_hash = (block_hash == self.block_hash)
        valid_pow = block_hash.startswith('0'*difficulty)

        return valid_hash & valid_pow
    
    def mine(self, difficulty, block_reward, block_reward_receiver, iterations):
        block_reward_tx = Transaction(
              sender_pk=None, 
              receiver_pk=block_reward_receiver, 
              amount=block_reward,
              fee=0
            )
        
        self.transactions += [block_reward_tx]

        transaction_data = self.aggregate_tx_data()

        block_data = self.prev_block_hash + transaction_data

        block_hash = ''
        for _ in range(iterations):
            pow = random.randint(1, bitcoin_curve.n - 1)
            block_data_w_pow = block_data + str(pow)
            block_hash = sha256(block_data_w_pow.encode('utf-8'), return_hex=True)
            if block_hash.startswith('0'*difficulty): # if pow found
                self.proof_of_work = pow
                self.block_hash = block_hash
                return True
            
        return False
    
    def __hash__(self):
        if self.block_hash is None:
            transaction_data = self.aggregate_tx_data()
            return hash(transaction_data)
        else:
            return hash(self.block_hash)
    
    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        
        if self.block_hash is None and other.block_hash is None:
            return self.aggregate_tx_data() == other.aggregate_tx_data()
        elif self.block_hash is not None and other.block_hash is not None:
            return self.block_hash == other.block_hash
        else:
            return False

class Blockchain:
    def __init__(self, block_size):
        self.blocks = []
        self.block_size = block_size # number of transactions limit per block

    def verify_blockchain(self, difficulty):
        block_heights = [block.block_height for block in self.blocks]
        if not all(x + 1 == y for x, y in zip(block_heights, block_heights[1:])):
            print(block_heights)
            return False

        # all sigs and pow are valid
        for block in self.blocks:
            if not (block.verify_proof_of_work(difficulty=difficulty) & block.verify_tx_signatures()):
                print('here')
                print(block.__dict__)
                return False
            
        return True
    
    def transaction_in_chain(self, transaction):
        # simple but inefficient way to do this
        for block in self.blocks:
            for tx in block.transactions:
                if tx == transaction.tx_id:
                    return True
        return False
    
    def __hash__(self):
        if len(self.blocks)==0:
            return hash(None) # empty chains will be equal
        
        self.blockchain_id = self.blocks[-1].block_hash

        return hash(self.blockchain_id)
    
    def __eq__(self, other):
        if not isinstance(other, Blockchain):
            return False
        
        if len(self.blocks)==0 and len(other.blocks)==0:
            return True
        
        if len(self.blocks) != len(other.blocks): # case where either chain is len 0
            return False
        
        # the last block hash is a unique identifier for the entire blockchain
        self.blockchain_id = self.blocks[-1].block_hash
        other.blockchain_id = other.blocks[-1].block_hash

        return self.blockchain_id == other.blockchain_id

if __name__ == '__main__':
    genesis_block = Block(block_height=0,
                          prev_block_hash='',
                          transactions=[])

    import time
    start_time = time.time()

    print('mining block...')
    solved = genesis_block.mine(difficulty=12, 
                       block_reward_receiver=bitcoin_G*42,
                       block_reward=50,
                       iterations=int(2e6))
    
    end_time = time.time()

    elapsed_time = end_time - start_time
    if solved:
        print('\n')
        print(f"valid hash found:")
        print(f"pow {genesis_block.proof_of_work}")
        print(f"block hash {genesis_block.block_hash}")
        print(f"took {round(elapsed_time,2)} seconds")
    else:
        print('not found.')
        print(f"took {round(elapsed_time,2)} seconds")