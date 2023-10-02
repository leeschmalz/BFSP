from elliptic_curve import Point, bitcoin_curve, bitcoin_G
from hash_functions import sha256
from modular_inverse import inv
import random

class Transaction:
    # class used by the sender to broadcast a transaction to the blockchain
    def __init__(self, sender_pk, receiver_pk, amount, fee):
        self.sender_pk = sender_pk
        self.receiver_pk = receiver_pk
        self.amount = amount # TODO need to incorporate this UTXO style, just doing "amount" and "fee" for now
        self.tx_fee = fee # TODO
        self.signature = None

        self.tx_id = sha256((str(sender_pk.x if sender_pk is not None else None) + str(receiver_pk.x) + str(amount)).encode('utf-8'), return_hex=True)
        self.message = int(self.tx_id, 16)

    def sign(self, sk):
        message = self.message

        if message.bit_length() > bitcoin_curve.n.bit_length():
            message = message >> (message.bit_length() - bitcoin_curve.n.bit_length())  # ensure message is compatible with group order

        nonce = random.randint(1, bitcoin_curve.n - 1)

        r = (bitcoin_G * nonce).x
        s = inv(nonce, bitcoin_curve.n) * (r*sk + message) % bitcoin_curve.n
        
        self.signature = (r, s)

        # include the signature in tx_id - guarentee signed messages are universally unique
        self.tx_id = sha256((self.tx_id + str(self.signature[0]) + str(self.signature[1])).encode('utf-8'), return_hex=True)

    def verify_signature(self):
        message = self.message

        if self.sender_pk is None:
            # if there is no sender, this is technically valid (i.e block reward)
            # nodes enforce block reward policy: only winning miner can send the correct block reward transaction
            return True

        if self.signature is None:
            return False # transaction is not signed
        
        if message.bit_length() > bitcoin_curve.n.bit_length():
            message = message >> (message.bit_length() - bitcoin_curve.n.bit_length())  # ensure message is compatible with group order
        
        u1 = message * inv(self.signature[1], bitcoin_curve.n)
        u2 = self.signature[0] * inv(self.signature[1], bitcoin_curve.n)

        return (bitcoin_G*u1 + self.sender_pk*u2).x == self.signature[0] % bitcoin_curve.n

    def __hash__(self):
        return hash(self.tx_id)
    
    def __eq__(self, other):
        # used to discard transactions from the mempool
        if not isinstance(other, Transaction):
            return False
        return self.tx_id == other.tx_id
    
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
                     amount=1,
                     fee=0.00001)
    
    tx.sign(sk=sk)
    print(f'check sig passed with correct key: {tx.verify_signature()}')
    tx.sign(sk=sk+1)
    print(f'check sig failed with incorrect key: {not tx.verify_signature()}')

    tx = Transaction(sender_pk=bitcoin_G * 1,
                     receiver_pk=bitcoin_G * 987654321, # some other public key
                     amount=1,
                     fee=0.00001)
    
    tx.sign(sk=1)
    print(tx.verify_signature())