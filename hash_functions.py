# using haslib for now. these are a giant *somewhat uninteresting* mess of bit mixing and modular operations
# TODO: implement from-scratch versions
import hashlib

def sha256(bytes, return_hex=False):
    if return_hex:
        return hashlib.sha256(bytes).hexdigest()
    else:
        return hashlib.sha256(bytes).digest()

def ripemd160(bytes):
    hasher = hashlib.new("ripemd160")
    hasher.update(bytes)
    return hasher.hexdigest()

if __name__ == "__main__":
    verify_sha256  = sha256(b'hello world', return_hex=True)=='b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    verify_ripemd160 = ripemd160(b'hello world')=='98c615784ccb5fe5936fbc0cbe9dfdb408d92f0f'
    print(f"sha256 hello world hash verification passed: {verify_sha256}")
    print(f"ripemd160 hello world hash verification passed: {verify_ripemd160}")