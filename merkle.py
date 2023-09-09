import requests
from pprint import pprint
import json
from hash_functions import sha256

def byte_swap(hex_string):
    # reverse endian-ness of hex string
    return "".join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))

class MerkleNode:
    def __init__(self, children=[], hash256=None):
        self.children = children

        if hash256 is None: # calculate parent hash from children
            # dealing with the annoying (hex to byte) x (litte endian to big endian) representations:
            # 1. byte swap endian-ness for both children
            # 2. concatenate children
            # 3. convert to bytes
            # 4. double sha256 (hash256)
            # 5. convert to hex
            # 6. byte swap endian-ness
            self.hash256 = (
                byte_swap(
                    sha256(sha256(
                            bytes.fromhex(
                                byte_swap(children[0].hash256) + byte_swap(children[1].hash256) # 1, 2
                            ) # 3
                        )
                    ) # 4
                    .hex() # 5
                ) # 6
            )
        else:
            self.hash256 = hash256

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves

    def assemble(self):
        self.nodes = self.leaves
        layer = self.leaves

        while len(layer)>1:
            children = []
            parent_layer = []

            if len(layer)%2==1:
                layer.append(layer[-1])

            for node in layer:
                if len(children)<2:
                    children.append(node)
                if len(children)==2:
                    parent_layer.append(MerkleNode(children=children))
                    children = []

            
            self.nodes += parent_layer
            layer = parent_layer
    
    def get_root(self):
        return self.nodes[-1].hash256
    
if __name__ == '__main__':
    # test using a real block and merkle root from blockchain.info
    url = 'https://blockchain.info/rawblock/0000000000000000000117b51c3d21681ddae3cc9e81cd9985cff86296e9c238'
    response = requests.get(url)
    block_data = response.json()

    merkle_leaves = [MerkleNode(hash256 = tx['hash']) for tx in block_data['tx']]
    
    tree = MerkleTree(leaves=merkle_leaves)
    tree.assemble()

    print(f'calculated root: {tree.get_root()}')
    print(f"root from blockchain.info: {block_data['mrkl_root']}")
    print(f"passed: {tree.get_root()==block_data['mrkl_root']}")
