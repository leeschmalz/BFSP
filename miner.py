from network import start_server, broadcast
import pickle
from ecdsa import Transaction
from blockchain import Block, Blockchain
import threading
from elliptic_curve import bitcoin_G

CURRENT_DIFFICULTY = 5
payout_pk = bitcoin_G*42

block_to_mine = Block()
new_block_available = threading.Event()

def mine_block():
    global block_to_mine
    while True:
        if new_block_available.is_set():
            new_block_available.clear()
            block_to_mine1 = block_to_mine # make a copy that cannot be updated by threading

            if len(block_to_mine1.transactions):
                block_to_mine1.mine(difficulty=CURRENT_DIFFICULTY, block_reward=6.25, block_reward_receiver=payout_pk)
                print(block_to_mine1.verify_proof_of_work(difficulty=5))
                broadcast(block_to_mine1, [5002]) # yew!
                block_to_mine = Block()

def assemble_next_block(mempool, blockchain):
    # grab the highest fee transactions transactions
    new_block = Block(prev_block_hash=blockchain.blocks[-1].block_hash,
                      block_height=blockchain.blocks[-1].block_height+1, # increment block height
                      transactions=[])

    sorted_txs = sorted(mempool, key=lambda tx: tx.tx_fee, reverse=True)

    for i, tx in enumerate(sorted_txs):
        if i >= blockchain.block_size:
            break
        new_block.transactions.append(tx)

    return new_block    

def manage_mempool():
    global block_to_mine
    
    server_socket = start_server(5001)

    main_chain = Blockchain() # start with an empty blockchain
    mempool = set()
    while True:
        client_socket, _ = server_socket.accept()
        data = client_socket.recv(1024)
        data = pickle.loads(data)

        # messages can be Blockchain, Block, or Transaction
        if isinstance(data, Blockchain):
            new_blockchain = data
            if not new_blockchain.verify_blockchain(difficulty=CURRENT_DIFFICULTY):
                # check that this blockchain is valid
                print('received invalid blockchain. ignoring.')
                continue

            if len(new_blockchain.blocks) > len(main_chain.blocks):
                # if the new chain is longer than current main chain, switch to it
                main_chain = new_blockchain
                for block in main_chain.blocks:
                    for tx in block.transactions:
                        # discard all transactions in the new main chain from the mempool
                        mempool.discard(tx)

        elif isinstance(data, Block):
            new_block = data
            if not (new_block.verify_proof_of_work(difficulty=CURRENT_DIFFICULTY) and new_block.verify_tx_signatures()):
                print('received invalid block. ignoring.')
                continue

            if new_block.prev_block_hash == main_chain.blocks[-1].block_hash:
                # if the new block extends the main chain, add it
                main_chain.blocks.append(new_block)

        elif isinstance(data, Transaction):
            new_transaction = data
            if not new_transaction.verify_signature():
                print('received invalid transaction. ignoring.')
                continue
            
            if main_chain.transaction_in_chain(new_transaction):
                print('received transaction already in chain. ignoring.')
                continue

            mempool.add(new_transaction)

        block_to_mine = assemble_next_block(mempool=mempool, blockchain=main_chain)
        new_block_available.set() # alert the mining process to switch to new block

mining_thread = threading.Thread(target=mine_block)
mining_thread.start()

mempool_thread = threading.Thread(target=manage_mempool)
mempool_thread.start()