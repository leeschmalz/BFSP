from network import start_server, broadcast
import pickle
from transaction import Transaction
from blockchain import Block, Blockchain
import threading
from elliptic_curve import bitcoin_G
from consensus_parameters import MINING_DIFFICULTY, BLOCK_SIZE, BLOCK_REWARD
import argparse
import random
import time

# Miner node:
# 1. listens for transactions from users, completed blocks from other miners/nodes, and updates to longest chain from miners/nodes
# 2. manages a mempool of transactions that are eligible to be included
# 3. greedily packages transactions from the mempool into blocks with highest tx fees
# 4. attempts to mine the block by solving the pow
# 5. if a solution is found, broadcast to other miners / nodes immediately. 
#    if this new block makes it into the longest chain, the miner is rewarded with the block reward and transaction fee

parser = argparse.ArgumentParser(description='Run a mining node.')
parser.add_argument('--home_port', type=int, default=5001, help='Home port for this node.')
parser.add_argument('--private_key', type=int, default=42, help='Private key of the wallet that earns mining rewards.')
args = parser.parse_args()

home_port = args.home_port # port the node will

all_ports = set(range(5001, 5006))
all_ports.discard(home_port)

# each node (mining and non-minig) will establish a connection to 3 other nodes,
# a far overly simplified version of the gossip style bitcoin network
connections = random.sample(list(all_ports), 1)
print(f'broadcasting to peers {connections}')

payout_pk = bitcoin_G*args.private_key

block_to_mine = Block()
new_block_available = threading.Event()

def mine_block():
    global best_block_to_mine
    while True:
        if new_block_available.is_set():
            new_block_available.clear()
            best_block_to_mine1 = best_block_to_mine # make a copy that cannot be updated by threading

            if len(best_block_to_mine1.transactions):
                print(f'mining block with {len(best_block_to_mine1.transactions)} transactions. fee value: {sum([tx.tx_fee for tx in best_block_to_mine1.transactions])}')

                block_solved = best_block_to_mine1.mine(difficulty=MINING_DIFFICULTY, 
                                                        block_reward=BLOCK_REWARD, 
                                                        block_reward_receiver=payout_pk, 
                                                        iterations=int(2e6), # number of hash iterations before checking for a better block to mine
                                                        )
                
                if block_solved:
                    print('block solved.')
                    broadcast((best_block_to_mine1, home_port), [home_port] + connections) # ensure you broadcast to your own port to update main_chain & mempool
                    best_block_to_mine = Block()
                    best_block_to_mine1 = Block()
                else:
                    print('getting new block.')

def assemble_best_block(mempool, blockchain):
    # grab the highest fee transactions within the block size limit
    best_block_to_mine = Block(prev_block_hash=blockchain.blocks[-1].block_hash,
                                block_height=blockchain.blocks[-1].block_height+1, # increment block height
                                transactions=[])

    sorted_txs = sorted(mempool, key=lambda tx: tx.tx_fee, reverse=True)

    for i, tx in enumerate(sorted_txs):
        if i >= blockchain.block_size:
            break
        best_block_to_mine.transactions.append(tx)

    return best_block_to_mine    

def manage_mempool():
    global best_block_to_mine
    
    server_socket = start_server(home_port)

    main_chain = Blockchain(block_size=BLOCK_SIZE) # start with an empty blockchain
    mempool = set()
    seen_messages_buffer = []
    while True:
        client_socket, _ = server_socket.accept()

        data = client_socket.recv(1000000)
        data = pickle.loads(data)
        address = data[1]
        data = data[0]

        if address >= 5000 and address <= 5010 and (address not in connections):
            print(f'added connection {address}')
            connections.append(address)
            # when a new connection appears, send them the main_chain one block at a time
            for block in main_chain.blocks:
                broadcast((block, home_port), [address])
                time.sleep(2)

        if data in seen_messages_buffer:
            continue
        seen_messages_buffer = (seen_messages_buffer[-19:] + [data]) if len(seen_messages_buffer) >= 20 else (seen_messages_buffer + [data])

        broadcast((data, home_port), connections)

        if isinstance(data, Block):
            print(f'received block from: {address}\n')
            new_block = data
            if not (new_block.verify_proof_of_work(difficulty=MINING_DIFFICULTY) and new_block.verify_tx_signatures()):
                print('received invalid block. ignoring.')
                continue

            if len(main_chain.blocks) == 0:
                # if this is the genesis block
                main_chain.blocks.append(new_block)
                for tx in new_block.transactions:
                    mempool.discard(tx)

            elif new_block.prev_block_hash == main_chain.blocks[-1].block_hash:
                # if the new block extends the main chain, add it
                main_chain.blocks.append(new_block)
                for tx in new_block.transactions:
                    mempool.discard(tx)

            else:
                # TODO: node may be out of consensus, look for a longer chain
                pass

        if isinstance(data, Transaction):
            print(f'received transaction from: {address}\n')
            new_transaction = data
            if not new_transaction.verify_signature():
                print('received invalid transaction. ignoring.')
                continue
            
            if main_chain.transaction_in_chain(new_transaction):
                print('received transaction already in chain. ignoring.')
                continue

            mempool.add(new_transaction)
            print(f'transactions in mempool: {len(mempool)}')

        if len(main_chain.blocks):
            best_block_to_mine = assemble_best_block(mempool=mempool, blockchain=main_chain)
            new_block_available.set() # alert the mining process to switch to new block
        print(f'blocks in main chain: {len(main_chain.blocks)}')
        
mining_thread = threading.Thread(target=mine_block)
mining_thread.start()

mempool_thread = threading.Thread(target=manage_mempool)
mempool_thread.start()