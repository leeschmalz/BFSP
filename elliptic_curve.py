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

    def double(self):
        return self + self

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
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return TypeError("Expected Point object.")
        return self.x == other.x and self.y == other.y and self.curve == other.curve
    
    def __mul__(self, other):
        '''
        This will be used with giant private keys. Use double and add algorithm for efficiency.
        '''
        if not isinstance(other, int):
            return TypeError("Expected Scalar.")

        track = [(1, self)] # use an external tracker so we have comparators defined '<', '<='

        while track[-1][0]*2 < other: # double until the next double exceeds i
            track.append((track[-1][0]*2, track[-1][1].double()))

        for int1, point1 in reversed(track): # add doubles in reverse until result is achieved
            if (track[-1][0] + int1) <= other:
                track.append((track[-1][0] + int1, track[-1][1] + point1))

        return track[-1][1]



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
    print(f'bitcoin generator is on curve: {bitcoin_G.is_on_curve()}')
    print(f'add method test passed: {(bitcoin_G + bitcoin_G).is_on_curve()}')
    print(f'double method test passed: {bitcoin_G.double() == (bitcoin_G + bitcoin_G)}')
    print(f'double-and-add method test passed: {(bitcoin_G*5) == (bitcoin_G + bitcoin_G + bitcoin_G + bitcoin_G + bitcoin_G)}')

