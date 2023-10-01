from blockchain import Block, Blockchain
from ecdsa import Transaction
import pickle
from network import start_server, broadcast
from consensus_parameters import MINING_DIFFICULTY, BLOCK_SIZE
import random
import argparse
import time

# non-mining node:
# 1. listens for newly mined blocks and updates to the longest chain
# 2. check that the block is in consensus with the protocol
# 3. if the block extends current longest chain, add it
# 4. broadcast all updates to longest version of the chain to other nodes and miners

parser = argparse.ArgumentParser(description='Run a mining node.')
parser.add_argument('--home_port', type=int, default=5001, help='Home port for this node.')
args = parser.parse_args()

home_port = args.home_port # port the node will

all_ports = set(range(5001, 5006))
all_ports.discard(home_port)

# each node (mining and non-minig) will establish a connection to 3 other nodes,
# a far overly simplified version of the gossip style bitcoin network
connections = random.sample(list(all_ports), 1)
print(f'broadcasting to peers {connections}')

server_socket = start_server(home_port)
main_chain = Blockchain(block_size=BLOCK_SIZE)
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

    if isinstance(data, Transaction):
        print(f'received transaction from: {address}\n')
        new_transaction = data
        
        if not new_transaction.verify_signature():
            print('received invalid transaction. ignoring.')
            continue
        
        if main_chain.transaction_in_chain(new_transaction):
            print('received transaction already in chain. ignoring.')
            continue


    if isinstance(data, Block):
        print(f'received block from: {address}\n')
        new_block = data
        print(f'received new block with {len(new_block.transactions)-1} transactions.') # -1 to account for block reward
        print(main_chain.__dict__)

        valid_pow = new_block.verify_proof_of_work(difficulty=MINING_DIFFICULTY)
        valid_signatures = new_block.verify_tx_signatures()

        if not (valid_pow and valid_signatures):
            print('received invalid block. ignoring.')
            continue

        if len(main_chain.blocks) == 0:
            main_chain.blocks.append(new_block)
            

        elif new_block.prev_block_hash == main_chain.blocks[-1].block_hash:
            # if the new block extends the main chain, add it
            main_chain.blocks.append(new_block)
            # broadcast((main_chain, home_port), connections)
        else:
            # TODO: node is out of consensus, resolve
            print('received block that doesnt fit on main chain')
            pass
        
    print(f'blocks in main chain: {len(main_chain.blocks)}')