class newrotor(object):

    #starts the rotor
    def __init__(self, key, n_rotors=6):
        self.n_rotors = n_rotors
        self.setkey(key)

    #sets the key for the rotor algorithm
    def setkey(self, key):
        self.key = key
        self.rotors = None
        self.positions = [None, None]

    #encrypts the buffer
    def encrypt(self, buf):
        self.positions[0] = None
        return self.cryptmore(buf, 0)

    #decrypts the buffer
    def decrypt(self, buf):
        self.positions[1] = None
        return self.cryptmore(buf, 1)

    #def for the encryption / decryption
    def cryptmore(self, buf, do_decrypt):
        size, nr, rotors, pos = self.get_rotors(do_decrypt)
        outbuf = b''
        for c in buf:
            if do_decrypt:
                for i in range(nr-1,-1,-1):
                    c = pos[i] ^ rotors[i][c]
            else:
                for i in range(nr):
                    c = rotors[i][c ^ pos[i]]
            outbuf = outbuf + c.to_bytes(1, "big")

            pnew = 0
            for i in range(nr):
                pnew = ((pos[i] + (pnew >= size)) & 0xff) + rotors[i][size]
                pos[i] = pnew % size

        return outbuf

    #gets the rotors position for the encryption / decryption
    def get_rotors(self, do_decrypt):
        nr = self.n_rotors
        rotors = self.rotors
        positions = self.positions[do_decrypt]

        if positions is None:
            if rotors:
                positions = list(rotors[3])
            else:
                self.size = size = 256
                id_rotor = list(range(size+1))

                rand = random_func(self.key)
                E = []
                D = []
                positions = []
                for i in range(nr):
                    i = size
                    positions.append(rand(i))
                    erotor = id_rotor[:]
                    drotor = id_rotor[:]
                    drotor[i] = erotor[i] = 1 + 2*rand(i/2) # increment
                    while i > 1:
                        r = rand(i)
                        i -= 1
                        er = erotor[r]
                        erotor[r] = erotor[i]
                        erotor[i] = er
                        drotor[er] = i
                    drotor[erotor[0]] = 0
                    E.append(tuple(erotor))
                    D.append(tuple(drotor))
                self.rotors = rotors = (
                    tuple(E), tuple(D), size, tuple(positions))
            self.positions[do_decrypt] = positions
        return rotors[2], nr, rotors[do_decrypt], positions

#pseudorandom full algorithm with a key
def random_func(key):
    mask = 0xffff
    x=995
    y=576
    z=767
    for c in map(ord, key):
        x = (((x<<3 | x>>13) + c) & mask)
        y = (((y<<3 | y>>13) ^ c) & mask)
        z = (((z<<3 | z>>13) - c) & mask)

    maxpos = mask >> 1
    mask += 1
    if x > maxpos: x -= mask
    if y > maxpos: y -= mask
    if z > maxpos: z -= mask

    y |= 1

    x = 171 * (int(x) % 177) - 2  * (int(x)//177)
    y = 172 * (int(y) % 176) - 35 * (int(y)//176)
    z = 170 * (int(z) % 178) - 63 * (int(z)//178)
    if x < 0: x += 30269
    if y < 0: y += 30307
    if z < 0: z += 30323

    #pseudorandom algorithm with an X Y Z seed
    def rand(n, seed=[(x, y, z)]):
        x, y, z = seed[0]
        seed[0] = ((171*x) % 30269, (172*y) % 30307, (170*z) % 30323)
        return int(int((x/30269 + y/30307 + z/30323) * n) % n)
    return rand
