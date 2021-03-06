import numpy as np
import math
import Elements as el
import FileRead as fr
from tkinter import *


file = fr.FileRead("iteration6.txt")
b = file.getBridge()

bridge = next(b)
print(bridge)
nodes = []
trusses = []
forces = []
cost = 0

memberForces = []
memberForcesEq = []

# Load everything to list of objects
for node in bridge['nodes']:
    # Load nodes
    nodes.append(el.Node(node, [float(n) for n in bridge['nodes'][node]]))
    for force in bridge['forces']:
        if node == force[0]:
            f = el.Force(force[0], [float(n) for n in force[1]])
            forces.append(f)
            nodes[-1].external.append(f)
for truss in bridge['trusses']:
    # Load trusses
    trusses.append(el.Truss(truss))
    trusses.append(el.Truss([truss[1], truss[0]]))

# Load trusses into the nodes
for truss in trusses:
    for node in nodes:
        if truss.startID == node.id:
            node.connections.append(truss)
            if truss.startx is None:
                truss.setStart([node.x, node.y])
        elif truss.endID == node.id:
            if truss.endx is None:
                truss.setEnd([node.x, node.y])
    cost += truss.cost / 2

# Iterate through nodes and load equations
# print(["%s%s " % (t.startID, t.endID) for t in trusses])
for node in nodes:
    cost += node.cost
    # Iterate connections to build matrix
    x = []
    y = []
    # Iterate trusses in order given to fill matrix row properly
    # print(["%s%s " % (c.startID, c.endID) for c in node.connections])
    for i in range(0, len(trusses), 2):
        first = trusses[i]
        second = trusses[i+1]
        added = False
        for c in node.connections:
            if first is c or second is c:
                # print(c.xlength/c.length)
                # POSITIVE IF COMPRESSIONS, NEGATIVE IF TENSION
                x.append(c.xlength/c.length)
                y.append(c.ylength/c.length)
                added = True
        if not added:
            x.append(0)
            y.append(0)
    # Add forces
    fx = 0
    fy = 0
    for f in forces:
        addReaction = False
        for e in node.external:
            if e is f:
                dir = f.direction*math.pi/180
                cosdir = math.cos(dir)
                if math.fabs(cosdir) < 1e-14:
                    cosdir = 0
                sindir = math.sin(dir)
                if math.fabs(sindir) < 1e-14:
                    sindir = 0
                if f.val == 0:
                    # Reaction Force
                    x.append(cosdir)
                    y.append(sindir)
                    addReaction = True
                else:
                    # Non reaction force
                    fx += -1 * f.val * cosdir
                    fy += -1 * f.val * sindir
        if f.val == 0 and not addReaction:
            x.append(0)
            y.append(0)
    # Add to matrix
    memberForces.append(x)
    memberForces.append(y)
    memberForcesEq.append(fx)
    memberForcesEq.append(fy)

print([len(n) for n in memberForces])
print(len(nodes))
print(len(memberForcesEq))
#print(np.linalg.det(memberForces))

result = [0 if math.fabs(num) < 1e-14 else num for num in (np.linalg.solve(memberForces, memberForcesEq)).tolist()]

for i in range(0, len(trusses), 2):
    print("%s%s: " % (trusses[i].startID, trusses[i].endID), end='')
    print(result[int(i/2)], end=' ')
    print('T' if result[int(i/2)] < 0 else 'C')
print(result)
print(cost)



def createGui():
    radius = 3
    width = 1000
    height = 750
    centerX = width/2 - 300
    centerY = height / 2 - 100
    scale = 50
    root = Tk()
    w = Canvas(root, width=width, height=height)
    w.pack()

    for i in range(0, len(trusses), 2):
        w.create_line(trusses[i].startx*scale + centerX,\
                      -trusses[i].starty*scale + centerY,\
                      trusses[i].endx*scale + centerX,\
                      -trusses[i].endy*scale + centerY,\
                      fill="red" if result[int(i/2)] > 0 else "green",\
                      width=3)
    for node in nodes:
        w.create_oval(node.x*scale + centerX - radius, -node.y*scale + centerY - radius, node.x*scale + centerX + radius, -node.y*scale + centerY + radius)
        w.create_text(node.x*scale + centerX, -node.y*scale + centerY + 10, text=node.id)
    root.mainloop()

def printLinks():
    for node in nodes:
        print(node.id, end=": ")
        for t in node.connections:
            print(t.startID, "%s(%s)" % (t.endID, t.length), sep='-', end=' ')
        print()

createGui()