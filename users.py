from ecdsa import Transaction
from elliptic_curve import bitcoin_G
from network import broadcast
import time
import random

while True:
    # transaction generator
    sender = random.randint(1, 1000000)
    receiver = random.randint(1, 1000000)
    tx = Transaction(sender_pk=bitcoin_G * sender,
                    receiver_pk=bitcoin_G * receiver,
                    amount=random.randint(1, 100),
                    fee=random.randint(1, 100))
    
    tx.sign(sk=sender)
    port = random.sample(list(range(5001, 5006)), 1)
    broadcast((tx, 43), port)
    print(f'tx sent to peer: {port}')
    time.sleep(random.randint(3, 10))