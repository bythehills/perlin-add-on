import bpy, random, numpy


length = 150 #displayed board size
smallestResLength = 200 #smallest resolution board size
height = 80 #height
gbLength = 10 #scales exponentially per octave, work with divisors of smallest resolution
#10, 20, 40, etc
startLength = length
octaves = 3




def calcGradVec(gradBoard):
    #random unit vector 
    
    for row in range(len(gradBoard)):
        for col in range(len(gradBoard[0])):
            print(row, col)
            dx = random.randrange(0, 100)
            dx = float(dx/100)
            a2 = dx**2
            b2 = (1 - a2) ** 0.5
            dy = b2
            chance = random.randint(0, 3)
            if (chance == 1):
                gradBoard[row][col] = (dx, dy)
            elif (chance == 2):
                gradBoard[row][col] = (-dx, dy)
            elif (chance == 3):
                gradBoard[row][col] = (-dx, -dy)
            else:
                gradBoard[row][col] = (dx, -dy )
    return gradBoard

def calcDotProduct(corner, cur):
    print(type(corner))
    a = corner[0]
    b = corner[1]
    c = cur[0]
    d = cur[1]
    return (a * c + b * d)

def interpolate(a, b, t):
    return a + t *(b  - a)

def perlin(board, octaveGradBoard, x, y):
    #for every pixel, calculate distance from four points
    #REMINDER: COL IS X, ROW IS Y
    perlinCellSize = len(board) // len(octaveGradBoard)
    perlinCols, perlinRows = len(octaveGradBoard), len(octaveGradBoard)
    gradBoard = octaveGradBoard
    col = int((x)//perlinCellSize) 
    row = int((y)//perlinCellSize) 
    cornerVectorTL = octaveGradBoard[row][col]
    
    #Turn (x, y) into decimal points... 
    x = float(x/perlinCellSize)
    y = float(y/perlinCellSize)
    distanceTL = (x - col, y - row)
    #Calculate corner gradient vectors and distance from (x, y)
    if (col + 1 < perlinCols):
        cornerVectorTR = gradBoard[row][col + 1]
        distanceTR = (x - col - 1, y - row)
    else:
        cornerVectorTR = cornerVectorTL
        distanceTR = distanceTL

    if (row + 1 < perlinRows):

        cornerVectorBL = gradBoard[row + 1][col]
        distanceBL = (x - col, y - row - 1)

    else:
        cornerVectorBL = cornerVectorTL
        distanceBL = distanceTL


    if (row + 1 < perlinRows and col + 1 < perlinCols):
        cornerVectorBR = gradBoard[row + 1][col + 1]
        distanceBR = (x - col - 1, y - row - 1)

    else:
        cornerVectorBR = cornerVectorTL
        distanceBR = distanceTL

    #calculate dot product of gradient vector at each of four corners
    #and distance vector (distance from corner point to target point)
    vecTL = calcDotProduct(cornerVectorTL, distanceTL)
    vecTR = calcDotProduct(cornerVectorTR, distanceTR)
    vecBL = calcDotProduct(cornerVectorBL, distanceBL)
    vecBR = calcDotProduct(cornerVectorBR, distanceBR)
    #average TL and TR
    #use smoothstep function
    x1 = col
    Sx = 3 * (x - x1)**2 -  2 * (x - x1)**3
    a = interpolate(vecTL, vecTR, Sx)
    b = interpolate(vecBL, vecBR, Sx)
    y1 = row
    Sy = 3*(y - y1)**2 - 2*(y - y1)**3
    final = interpolate(a, b, Sy)
    return (final + 0.3)

def fillPerlinBoard(board, octaveExp, octaveGradBoard):
    octaveGradBoard = calcGradVec(octaveGradBoard)
    for pX in range(0, len(board)):
      for pY in range(0, len(board)):
        val = perlin(board, octaveGradBoard, pX, pY)
        board[pX][pY] += val * 1/octaveExp #1/1, 1/2, 1/4

          
#perlinBoard is of size[length][length] 
def start():
    scene = bpy.context.scene
    so = bpy.context.active_object
    verts = [] #vertices are in (xyz)
    edges = set() #edges are tuple of two vertices
    faces = [] #faces are tuple of four edges
    curVertCount = 0
    for i in range(0, length + 1): #first create square grid of vertices
        for j in range(0, length + 1):
            verts.append((i, j, 0))

    #create edges
    vertCounter = 0
       
    while vertCounter < len(verts) - 2 - length: #add edges
        if verts[vertCounter][1] != length:
            origVert = vertCounter
            hortVert = vertCounter + 1
            upVert = vertCounter + length + 1
            diagVert = vertCounter + length + 2
            edges.add((origVert, hortVert))
            edges.add((hortVert, diagVert))
            edges.add((diagVert, upVert))
            edges.add((upVert, origVert))
            faces.append((origVert, hortVert, diagVert, upVert)) #add faces
        vertCounter += 1

    #get rid of duplicate edges
    finalEdges = []

    for edge in edges:
        first = edge[0]
        second = edge[1]
        if (second, first) not in edges:
            finalEdges.append((first, second))
    
    board = [[0] * smallestResLength for row in range(smallestResLength)] 
    #stores all perlin values
    for octave in range(1, octaves + 1):
        octaveExp = pow(2, octave-1) #1, 2, 4
        currentGbLength = gbLength * octaveExp #10, 20, 40
        octaveGradBoard = [[0] * currentGbLength for row in range(currentGbLength)] 
        fillPerlinBoard(board, octaveExp, octaveGradBoard)
   
    for face in faces:
        #aka [(0, 1, 2, 3)]
        for i in face: #get each vertex and raise it by index of face
            curVert = verts[i]
            boardRow = curVert[0] #x index
            boardCol = curVert[1] #y index
            if boardRow == length: #aka if vertex is (100, y, z)
                boardRow = length - 1
            if boardCol == length: #aka if vertex is (x, 100, z)
                boardCol = length - 1
            verts[i] = (curVert[0], curVert[1], board[boardRow][boardCol] * height)
           
#    print(verts)

    name = 'New Terrain'
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col = bpy.data.collections.get('Collection')
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, finalEdges, faces)
    for f in mesh.polygons:
        f.use_smooth = True

start()