import sys
import json
from string import ascii_uppercase
from collections import deque

alphabet = list(ascii_uppercase)

# https://en.wikipedia.org/wiki/Enigma_rotor_details
R1 = list("EKMFLGDQVZNTOWYHXUSPAIBRCJ") # Q -> R
R2 = list("AJDKSIRUXBLHWTMCQGZNPYFVOE") # E -> F
R3 = list("BDFHJLCPRTXVZNYEIWGAKMUSQO") # V -> W
R4 = list("ESOVPZJAYQUIRHXLNFTGKDCMWB") # J -> K
R5 = list("VZBRGITYUPSDNHLXAWMJQOFECK") # Z -> A
R6 = list("JPGVOUMFYQBENHZRDKASXLICTW") # Z -> A & M -> N
R7 = list("NZJHGRCXMYSWBOUFAIVLPEKQDT") # Z -> A & M -> N
R8 = list("FKQHTLXOCBJSPDZRAMEWNIUYGV") # Z -> A & M -> N
rotorList = {"R1": (R1, ["Q"]), "R2": (R2, ["E"]), "R3": (R3, ["V"]), "R4": (R4, ["J"]), "R5": (R5, ["Z"]), "R6": (R6 , ["Z", "M"]), "R7": (R7 , ["Z", "M"]), "R8": (R8, ["Z", "M"])}

RA = list("EJMZALYXVBWFCRQUONTSPIKHGD")
RB = list("YRUHQSLDPXNGOKMIEBFZCWVJAT")
RC = list("FVPJIAOYEDRZXWGCTKUQSBNMHL")
reflectorList = {"RA": RA, "RB": RB, "RC": RC}

class Rotor:

    def __init__(self, mapsTo, start, turnover, ring):
        self.pos = start - 1
        self.turnovers = [findIndexInList(alphabet, n) for n in turnover]
        self.mapsTo = deque(mapsTo)
        ringIndex = findIndexInList(self.mapsTo, "A")
        for i in range(ring - 1):
            ringIndex += 1
            for j in range(0,26):
                self.mapsTo[j] = next_alpha(self.mapsTo[j])
        while ringIndex % 26 != findIndexInList(self.mapsTo, alphabet[ring - 1]):
            self.mapsTo.rotate(-1)
        
    def getLetter(self, index):
        i = findIndexInList(alphabet, self.mapsTo[(index + self.pos) % 26]) 
        return (i - self.pos + 26) % 26

    def getLetterTerug(self, index):
        i = findIndexInList(self.mapsTo, alphabet[(index + self.pos) % 26])
        return (i - self.pos + 26) % 26
        
    def rotate(self):
        self.pos = (self.pos + 1) % 26
        for n in self.turnovers:
            if self.pos == n:
                return True
        return False
        
class Reflector:

    def __init__(self, mapsTo):
        self.mapsTo = mapsTo
    
    def getLetter(self, index):
        return findIndexInList(alphabet, self.mapsTo[index])

class Plugboard:

    def __init__(self, wires):
        self.wires = {}
        for i in range(0, 26):
            self.wires[i] = i
        for i, j in wires:
            self.wires[findIndexInList(alphabet, i)] = findIndexInList(alphabet, j)
            self.wires[findIndexInList(alphabet, j)] = findIndexInList(alphabet, i)

    def getLetter(self, index):
        return self.wires[index]

def findIndexInList(lst, c):
    index = 0
    for l in lst:
        if c == l:
            return index 
        index +=1

def next_alpha(s):
    return chr((ord(s.upper())+1 - 65) % 26 + 65)

def encode(txt, rotors, reflector, wires):
    r1data = rotorList[rotors[2]["rotor"]]
    r1 = Rotor(r1data[0], rotors[2]["start"], r1data[1], rotors[2]["ring"])

    r2data = rotorList[rotors[1]["rotor"]]
    r2 = Rotor(r2data[0], rotors[1]["start"], r2data[1], rotors[1]["ring"])

    r3data = rotorList[rotors[0]["rotor"]]
    r3 = Rotor(r3data[0], rotors[0]["start"], r3data[1], rotors[0]["ring"])   
    ref = Reflector(reflectorList[reflector])
    
    pb = Plugboard(wires)

    encoded = ""
    rotate2 = False
    rotate3 = False
    for c in txt:
        if c == " ":
            encoded += " "
        else:
            if rotate3:
                r3.rotate()
                r2.rotate()
                rotate3 = False
            if rotate2:
                rotate3 = r2.rotate()
            rotate2 = r1.rotate()

            index = findIndexInList(alphabet, c)
            index = pb.getLetter(index)
            index = r1.getLetter(index)
            index = r2.getLetter(index)
            index = r3.getLetter(index)
            index = ref.getLetter(index)
            index = r3.getLetterTerug(index)
            index = r2.getLetterTerug(index)
            index = r1.getLetterTerug(index)
            index = pb.getLetter(index)
            encoded += alphabet[index]
            
    return encoded


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No start settings given")
    else:
        data = {}
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        print(encode(sys.argv[2].upper(), data["rotors"], data["reflector"], data["wires"]))
    
    