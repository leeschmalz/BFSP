# Pseudocode from wikipedia:
# function extended_gcd(a, b)
#     (old_r, r) := (a, b)
#     (old_s, s) := (1, 0)
#     (old_t, t) := (0, 1)
    
#     while r ≠ 0 do
#         quotient := old_r div r
#         (old_r, r) := (r, old_r − quotient × r)
#         (old_s, s) := (s, old_s − quotient × s)
#         (old_t, t) := (t, old_t − quotient × t)
    
#     output "Bézout coefficients:", (old_s, old_t) # a,b st. ax+by = gcd(a,b).
#     output "greatest common divisor:", old_r
#     output "quotients by the gcd:", (t, s)

def inv(x, p):
    """
    calculates (gcd, x, y) s.t. ax + by == gcd mod p
    taken from Wikipedia.

    since we use a prime modulus (b), gcd == 1. 
    therefore: 
    ax + by = 1 mod b
    and since by = 0 mod b
    ax = 1 mod b, in other words, x is the inverse of a mod b
    """
    old_r, r = x, p
    old_s, s = 1, 0
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    return old_s % p

if __name__ == "__main__":
    print(f'inverse of 5 mod 3: {inv(5,3)}')
    print(f'inverse of 2 mod 11: {inv(2,11)}')
    print(f'inverse of 12 mod 97: {inv(12,97)}')