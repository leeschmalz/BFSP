class Curve:
    """
    Elliptic Curve over the field of integers modulo a prime.
    Points on the curve satisfy y^2 = x^3 + a*x + b (mod p).
    """
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b
    
    def point_on_curve(self,point):
        """
        Return True if point is on curve else false
        """
        return(( point.x**3 + self.a*point.x + self.b - point.y**2) % self.p == 0)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# secp256k1 uses a = 0, b = 7, so we're dealing with the curve y^2 = x^3 + 7 (mod p)
bitcoin_curve = Curve(
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a = 0x0000000000000000000000000000000000000000000000000000000000000000, # a = 0
    b = 0x0000000000000000000000000000000000000000000000000000000000000007, # b = 7
)

bitcoin_G = Point(
    x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)

if __name__ == '__main__':
    # make sure the secp256k1 generator is on the curve
    print(bitcoin_curve.point_on_curve(bitcoin_G))