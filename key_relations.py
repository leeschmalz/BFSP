from hash_functions import sha256, ripemd160
from elliptic_curve import bitcoin_curve, bitcoin_G
import base58

def decompressPrivateKey(sk_compressed):
    # Decode the compressed private key from base58
    decoded = base58.b58decode(sk_compressed)

    # Drop the last 5 bytes (0x01 byte and the 4-byte checksum)
    decoded = decoded[:-5]

    # Compute the checksum
    double_hash = sha256(sha256(decoded))
    checksum = double_hash[:4]

    # Append the checksum to the private key
    uncompressed = decoded + checksum

    # Encode the uncompressed private key back to base58
    sk = base58.b58encode(uncompressed).decode('utf-8')

    return sk

def privateToPublicKey(private_key, compressed=True):
    '''
    Bitcoin public key is pk * G where G is the bitcoin generator.
    '''
    private_key_bytes = base58.b58decode(private_key)[1:-4]

    private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
    public_key_point = bitcoin_G * private_key_int
    
    x_coord = public_key_point.x.to_bytes(32, byteorder='big').hex().upper()
    y_coord = public_key_point.y.to_bytes(32, byteorder='big').hex().upper()
    if compressed:
        public_key = '02' + x_coord # compressed address uses x coord only
    else:
        public_key = '04' + x_coord + y_coord

    return public_key

def publicKeyToAddress(public_key):
    public_key_bytes = bytes.fromhex(public_key)

    address_bytes = b'\x00' + ripemd160(sha256(public_key_bytes)) # add main net start byte

    # add checksum
    checksum = sha256(sha256(address_bytes))[:4]
    address_bytes += checksum

    address = base58.b58encode(address_bytes).decode('utf-8')

    return address

# used https://www.bitaddress.org/ to generate a valid key pair
# this address holds no funds, obviously
valid_key_pair = {'sk':'5K4Uvj9SXyYcPQWj6eos7sVHpWj8YCuTUMfGW86mtcMFRib3LCt', # private key WIF, 51 characters base58, starts with a '5'
                  'sk_compressed':'L2iNG92FhiaXBtnCowsrDKqsEiCxGjYXqkBuRYLV8o2Nfwov78Zi', # private key WIF compressed, 52 characters base58, starts with a 'K' or 'L'
                  'pk':'04C3C8B653BC9713B1586FE85F71AF7421684176A9F2D0AEE238901DD4F42FC4A1C693F7CA875AB54CB757D138FCC1CD11B3D9FC7D3844247DB0E486147357D056',
                  'pk_compressed':'02C3C8B653BC9713B1586FE85F71AF7421684176A9F2D0AEE238901DD4F42FC4A1',
                  'address':'1DGt5S9jsTJP9kRbg2dpUi3thXNkTyCwhd',
                  'address_compressed':'16TPgEziLH7o67tHbqhzkczVtNXD46E3oj' # public key 
                  }

if __name__ == '__main__':
    print(f"Private key decompression test passed: {decompressPrivateKey(valid_key_pair['sk_compressed']) == valid_key_pair['sk']}")
    print(f"Private key to public key test passed: {privateToPublicKey(valid_key_pair['sk']) == valid_key_pair['pk_compressed']}")
    print(f"Compressed public key to compressed address test passed: {publicKeyToAddress(valid_key_pair['pk_compressed']) == valid_key_pair['address_compressed']}")
    print(f"Public key to address test passed: {publicKeyToAddress(valid_key_pair['pk']) == valid_key_pair['address']}")