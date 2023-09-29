from elliptic_curve import Point, bitcoin_curve, bitcoin_G
from hash_functions import sha256
from modular_inverse import inv
import random

class Transaction:
    # class used by the sender to broadcast a transaction to the blockchain
    def __init__(self, sender_pk, receiver_pk, amount):
        self.sender_pk = sender_pk # public key of sender
        self.receiver_pk = receiver_pk
        self.amount = amount
        self.signature = None

        self.message = int( sha256((str(sender_pk.x if sender_pk is not None else None) + str(receiver_pk.x) + str(amount)).encode('utf-8'), return_hex=True), 16)

    def sign(self, sk):
        message = self.message

        if message.bit_length() > bitcoin_curve.n.bit_length():
            message = message >> (message.bit_length() - bitcoin_curve.n.bit_length())  # ensure message is compatible with group order

        nonce = random.randint(1, bitcoin_curve.n - 1)

        r = (bitcoin_G * nonce).x
        s = inv(nonce, bitcoin_curve.n) * (r*sk + message) % bitcoin_curve.n
        
        self.signature = (r, s)

    def verify_signature(self):
        message = self.message

        if self.signature is None:
            raise Exception("Transaction is not signed.")
        
        if message.bit_length() > bitcoin_curve.n.bit_length():
            message = message >> (message.bit_length() - bitcoin_curve.n.bit_length())  # ensure message is compatible with group order
        
        u1 = message * inv(self.signature[1], bitcoin_curve.n)
        u2 = self.signature[0] * inv(self.signature[1], bitcoin_curve.n)

        return (bitcoin_G*u1 + self.sender_pk*u2).x == self.signature[0] % bitcoin_curve.n

if __name__ == '__main__':
    from key_relations import valid_key_pair, privateToPublicKey
    import base58

    sk = int.from_bytes(base58.b58decode(valid_key_pair['sk'])[1:-4], byteorder='big')

    public_key_x = privateToPublicKey(valid_key_pair['sk'], compressed=False)[2:66]
    public_key_y = privateToPublicKey(valid_key_pair['sk'], compressed=False)[66:]
    
    pk = Point(
        x = int(public_key_x, 16),
        y = int(public_key_y, 16),
        curve = bitcoin_curve
    )

    tx = Transaction(sender_pk=pk,
                     receiver_pk=bitcoin_G * 987654321, # some other public key
                     amount=1)
    
    tx.sign(sk=sk)
    print(f'check sig passed with correct key: {tx.verify_signature()}')
    tx.sign(sk=sk+1)
    print(f'check sig failed with incorrect key: {not tx.verify_signature()}')
