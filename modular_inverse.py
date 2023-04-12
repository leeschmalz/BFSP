# since we are dealing in finite field, we cannot do normal division.
# these functions help us find multiplicative inverses. 
# TODO: need to revisit this algorithm from number theory
def extended_euclidean_algorithm(a, b):
    """
    Returns (gcd, x, y) s.t. a * x + b * y == gcd
    This function implements the extended Euclidean
    algorithm and runs in O(log b) in the worst case,
    taken from Wikipedia.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t

def inv(n, p):
    """ returns modular multiplicate inverse m s.t. (n * m) % p == 1 """
    gcd, x, y = extended_euclidean_algorithm(n, p) # pylint: disable=unused-variable
    return x % p

if __name__ == "__main__":
    print(f'inverse of 5 mod 3: {inv(5,3)}')
    print(f'inverse of 2 mod 11: {inv(2,11)}')
    print(f'inverse of 12 mod 97: {inv(12,97)}')