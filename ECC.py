from modular_inverse import inv

class Curve:
    """
    Elliptic Curve over the field of integers modulo a prime.
    Points on the curve satisfy y^2 = x^3 + a*x + b (mod p).
    """
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b
    
class Point():
    def __init__(self, x, y, curve):
        self.curve = curve
        self.x = x
        self.y = y

    def is_on_curve(self):
        return(( self.x**3 + self.curve.a*self.x + self.curve.b - self.y**2) % self.curve.p == 0)

    def __add__(self, other):
        '''
        Elliptic curve addition. Return the point that intersects the curve and is aligned with self and other.
        '''
        if self.curve != other.curve:
            raise ValueError("Cannot add points on different curves.")

        if not isinstance(other, Point):
            raise TypeError("Unsupported operand type. Expected Point object.")

        # if self is identity
        if self.x == None:
            return other

        # if other is identity
        if other.x == None:
            return self

        if self.x == other.x and self.y != other.y:
            return Point(None, None, self.curve)

        if self.x == other.x:
            # if the points are the same, we want the slope of the tanget line
            slope = (3 * self.x**2 + self.curve.a) * inv(2 * self.y, self.curve.p)
        else:
            # otherwise, the slope between the points
            slope = (other.y - self.y) * inv(other.x - self.x, self.curve.p)

        xr = (slope**2 - self.x - other.x) % self.curve.p
        yr = (-(slope*(xr - self.x) + self.y)) % self.curve.p

        return Point(xr, yr, self.curve)


# secp256k1 uses a = 0, b = 7, so we're dealing with the curve y^2 = x^3 + 7 (mod p)
bitcoin_curve = Curve(
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a = 0x0000000000000000000000000000000000000000000000000000000000000000,
    b = 0x0000000000000000000000000000000000000000000000000000000000000007,
)

bitcoin_G = Point(
    x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
    curve = bitcoin_curve
)

if __name__ == '__main__':
    # make sure the secp256k1 generator is on the curve
    print(bitcoin_G.is_on_curve())
    # make sure 2G is on the curve
    print((bitcoin_G + bitcoin_G).is_on_curve())