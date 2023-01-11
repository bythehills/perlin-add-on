import bpy, random


length = 100 #displayed board
smallestResLength = 400 #actual board size
height = 50 #height
gbLength = 50 #scale

startLength = 100
gradBoard = [[0] * gbLength for row in range(gbLength)] 
#imagine grid overlaid on top of grid


#this is length / gradBoard length (aka how big each cell is)
oct1PerlinBoard = [[0] *  startLength
                for row in range(startLength)]
oct2PerlinBoard = [[0] *  startLength * 2
                for row in range(startLength * 2)]
oct3PerlinBoard = [[0] *  startLength * 4
                for row in range(startLength * 4)]




def calcGradVec():
    for row in range(len(gradBoard)):
        for col in range(len(gradBoard[0])):
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

def calcDotProduct(corner, cur):
    a, b = corner
    c, d, = cur
    return (a * c + b * d)

def interpolate(a, b, t):
    return a + t *(b  - a)

def perlin(board, x, y):
    #for every pixel, calculate distance from four points
    #REMINDER: COL IS X, ROW IS Y
    perlinCellSize = len(board) // len(gradBoard)
    perlinCols, perlinRows = len(gradBoard), len(gradBoard)
    col = int((x)//perlinCellSize) 
    row = int((y)//perlinCellSize) 
#    print("col", col, "row ", row)
#    print("len board", len(board))
#    print("perlinCellSize", perlinCellSize)
#    print("perlinRowScols", perlinCols)
#    print("length gradBoard", len(gradBoard))
    cornerVectorTL = gradBoard[row][col]
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
    x1 = col
    Sx = 3 * (x - x1)**2 -  2 * (x - x1)**3
    a = interpolate(vecTL, vecTR, Sx)
    b = interpolate(vecBL, vecBR, Sx)
    y1 = row
    Sy = 3*(y - y1)**2 - 2*(y - y1)**3
    final = interpolate(a, b, Sy)

    return (final + 0.3)

def fillPerlinBoard(board):
    for pX in range(0, len(board)):
        for pY in range(0, len(board)):
            val = perlin(board, pX, pY)
            board[pX][pY] = val

def fillGrid(board, height):
#newPerlinBoard should be same as length
    fillPerlinBoard(oct1PerlinBoard)
    fillPerlinBoard(oct2PerlinBoard)
    fillPerlinBoard(oct3PerlinBoard)
    for pX in range(0, smallestResLength):
        for pY in range(0, smallestResLength):
            val = oct1PerlinBoard[pX//4][pY//4]
            val2 = oct2PerlinBoard[pX//2][pY//2]
            val3 = oct3PerlinBoard[pX][pY]
#            print("pX", pX, "pY", pY, "height", val2)
            val = val3
            board[pX][pY] = val
          
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
    
    board = [[0] * smallestResLength for row in range(smallestResLength)] #im sorry my 2d list creation is all over the place
    #what da hell is board.. i think it stores perlin values
    calcGradVec()
    fillGrid(board, height)
#    fillPerlinBoard(board)
    print(len(board))

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
            print(boardRow, boardCol)
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