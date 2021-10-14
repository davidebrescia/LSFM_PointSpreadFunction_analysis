import math
import numpy as np
from copy import copy
from skimage import io
from matplotlib import cm
import matplotlib.pyplot as plt
from scipy import asarray as ar
from scipy import ndimage as ndi
from scipy.optimize import curve_fit
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter






"""FILE"""

def StackToMatrix(directory, file):
    path = directory + '\\' + file
    mat = io.imread(path)
    mat = mat.astype(float)
    return mat






"""GRAFICA"""

def MultipleFrontView(subStack, pMin, pMax):
    num_plots = subStack.shape[0]
    if  subStack.shape[0]<10:
        num_cols = subStack.shape[0]
    else:
        num_cols = 10
    num_rows = num_plots // num_cols
    num_rows += 1 if num_plots % num_cols != 0 else 0
    # fig, axes = plt.subplots(num_rows, num_cols)
    plt.figure()
    # fig, axes = plt.subplots(1, subStack.shape[0])
    # for i, ax in enumerate(axes.ravel()):
    for i in range(num_plots):
        ax = plt.subplot(num_rows, num_cols, i+1)
        ax.imshow(subStack[i, :, :], cmap='gray', vmin=pMin, vmax=pMax)
        ax.set_title(i)
        ax.axis('off')


def MultipleTopView(subStack, pMin, pMax):
    num_plots = subStack.shape[1]
    if  subStack.shape[1]<10:
        num_cols = subStack.shape[1]
    else:
        num_cols = 10
    num_rows = num_plots // num_cols
    num_rows += 1 if num_plots % num_cols != 0 else 0
    # fig, axes = plt.subplots(num_rows, num_cols)
    plt.figure()
    # fig, axes = plt.subplots(1, subStack.shape[0])
    # for i, ax in enumerate(axes.ravel()):
    for i in range(num_plots):
        ax = plt.subplot(num_rows, num_cols, i+1)
        ax.imshow(subStack[:, i, :], cmap='gray', vmin=pMin, vmax=pMax)
        ax.set_title(i)
        ax.axis('off')


def FrontView(stack, z):
    mat = stack[z,:,:]
    plt.imshow(mat, cmap='gray', vmin=pMin, vmax=pMax)
    plt.axis('off')


def TopView(stack, y):
    mat = stack[:,y,:]
    plt.imshow(mat, cmap='gray', vmin=pMin, vmax=pMax)
    plt.axis('off')


def Plot3D(matrix, title, yLabel, xLabel):
    fig = plt.figure()
    ax = fig.gca(projection='3d')    
    X = np.arange(0, matrix.shape[1], 1)
    Y = np.arange(0, matrix.shape[0], 1)
    X, Y = np.meshgrid(X, Y)    
    surf = ax.plot_surface(X,Y,matrix, cmap=cm.coolwarm, antialiased=True)
    fig.colorbar(surf, shrink=0.5, aspect=5) 
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()
    

def Plot3DLines(matrix):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(0, matrix.shape[1], 1)
    Y = np.arange(0, matrix.shape[0], 1)
    X, Y = np.meshgrid(X, Y)
    ax.plot_wireframe(X, Y, matrix, rstride=1, cstride=1)
    plt.show()


def HistogramCalculator(stack, order, minValue, maxValue):
    coords, values = local_maxima_3D(stack, order=order)
    freq,bins=np.histogram(values,range=(minValue,maxValue),bins=maxValue-minValue)
    plt.plot(freq)
    print("Median:",np.median(freq))


def CreateMipXYandXZ(stack, pMin, pMax): #magari aggiungici una variabile in ingresso per decidere se far comparire anche la figura o returnare solo le mip
    mipXY = np.max(stack, axis=0)
    mipXZ = np.max(stack, axis=1)
    mip = ar([mipXZ, mipXY])
    plt.figure()
    for i in range(2):
        ax = plt.subplot(2, 1, i+1)
        ax.imshow(mip[i], cmap='gray', vmin=pMin, vmax=pMax)
        if i==0:
            plt.title("MipXZ")
        if i==1:
            plt.title("MipXY")
    return mipXZ, mipXY


def PlotFittedPSF(stdZp, stdYp, stdXp, pixDim, amp):
    steps=10  #lasciare 10: ogni casella delle matrici che vengono create è 0.1x0.1 um^2
    stdZ=stdZp*pixDim[0]
    stdY=stdYp*pixDim[1]
    stdX=stdXp*pixDim[2]
    centerZ = int(steps *3*stdZ + 0.5) #è la lunghezza dal centro in micrometri nella direzione X
    centerY = int(steps *3*stdY + 0.5)
    centerX = int(steps *3*stdX + 0.5)
    matrixYX = np.zeros([2*centerY+1, 2*centerX+1])
    matrixZX = np.zeros([2*centerZ+1, 2*centerX+1])
    for i in range(matrixYX.shape[0]):
        for j in range(matrixYX.shape[1]):
            matrixYX[i,j] = amp * math.exp( -( ((i/steps-centerY/steps)**2)/(2*(stdY**2)) + ((j/steps-centerX/steps)**2)/(2*(stdX**2) )) )
    for i in range(matrixZX.shape[0]):
        for j in range(matrixZX.shape[1]):
            matrixZX[i,j] = amp * math.exp( -( ((i/steps-centerZ/steps)**2)/(2*(stdZ**2)) + ((j/steps-centerX/steps)**2)/(2*(stdX**2) )) )     
    fig1 = plt.figure(figsize=plt.figaspect(0.4)) #creo una finestra "fig" larga il doppio dell'altezza
    fig1.suptitle("PSF gaussian fit from XY plane") #titolo della finestra
    im1 = fig1.add_subplot(1,2,1) #aggiungo un'immagine in posizione 12
    plt.xlabel("X (\u03BCm)")
    plt.ylabel("Y (\u03BCm)")
    im1.imshow(matrixYX, cmap=cm.coolwarm, interpolation='gaussian', extent=[-(centerX+0.5)/steps,(centerX+0.5)/steps, -(centerY+0.5)/steps,(centerY+0.5)/steps])
    long=1+2*int( ((centerY+0.5)/steps)/pixDim[1] - 0.5 )                      #imposto la griglia dei pixel
    y_ticks = np.arange(-pixDim[1]/2*long, pixDim[1]/2*long+0.00001, pixDim[1]) 
    long=1+2*int( ((centerX+0.5)/steps)/pixDim[2] - 0.5 )  
    x_ticks = np.arange(-pixDim[2]/2*long, pixDim[2]/2*long+0.00001, pixDim[2])
    im1.set_yticks(y_ticks)
    im1.set_xticks(x_ticks)
    im1.grid(which='both', linestyle='-', color='black',linewidth=0.3)
    ax1 = fig1.add_subplot(1, 2, 2, projection='3d') #aggiungo il grafico 3d in posizione 122
    Y = np.arange(-(centerY)/steps, (centerY)/steps+0.00001, 1/steps)
    X = np.arange(-(centerX)/steps, (centerX)/steps+0.00001, 1/steps)
    X, Y = np.meshgrid(X, Y)    
    surf1 = ax1.plot_surface(X,Y, matrixYX, cmap=cm.coolwarm, antialiased=True)
    fig1.colorbar(surf1, shrink=0.5, aspect=5)
    plt.xlabel("X (\u03BCm)")
    plt.ylabel("Y (\u03BCm)")
    ax1.set_zlabel("Counts")
    #ax.axis('equal') #se voglio il grafico 3D con gli assi con le giuste proporzioni (esce male)
    plt.show()
    fig2 = plt.figure(figsize=plt.figaspect(0.4)) #CREO FINESTRA "fig" larga il doppio dell'altezza
    fig2.suptitle("PSF gaussian fit from XZ plane")
    im2 = fig2.add_subplot(1,2,1) #AGGIUNGO IMMAGINE in posizione 12
    plt.xlabel("X (\u03BCm)")
    im2.xaxis.set_label_coords(1.45, -0.005)
    plt.ylabel("Z (\u03BCm)")
    im2.imshow(matrixZX, cmap=cm.coolwarm, interpolation='gaussian', extent=[-(centerX+0.5)/steps,(centerX+0.5)/steps, -(centerZ+0.5)/steps,(centerZ+0.5)/steps])
    long=1+2*int( ((centerZ+0.5)/steps)/pixDim[0] - 0.5 )                      #imposto la griglia dei pixel
    y_ticks = np.arange(-pixDim[0]/2*long, pixDim[0]/2*long+0.00001, pixDim[0]) 
    long=1+2*int( ((centerX+0.5)/steps)/pixDim[2] - 0.5 )
    x_ticks = np.arange(-pixDim[2]/2*long, pixDim[2]/2*long+0.00001, pixDim[2])
    im2.set_yticks(y_ticks)
    plt.xticks(rotation=90)
    im2.set_xticks(x_ticks)
    im2.grid(which='both', linestyle='-', color='black',linewidth=0.3)
    ax2 = fig2.add_subplot(1, 2, 2, projection='3d') #AGGIUNGO GRAFICO 3D in posizione 122
    Y = np.arange(-(centerZ)/steps, (centerZ)/steps+0.00001, 1/steps)
    X = np.arange(-(centerX)/steps, (centerX)/steps+0.00001, 1/steps)
    X, Y = np.meshgrid(X, Y)    
    surf2 = ax2.plot_surface(X,Y, matrixZX, cmap=cm.coolwarm, antialiased=True)
    fig2.colorbar(surf2, shrink=0.5, aspect=5) 
    plt.xlabel("X (\u03BCm)")
    plt.ylabel("Z (\u03BCm)")
    ax2.set_zlabel("Counts")
    #ax2.axis('equal') 
    plt.show()
    
    
def PlotSingleBead(stack, coords, gauss, pixDim): #fitta e plotta
    startZ,endZ = StartEnd(stack.shape, coords[0], 0, gauss[0])
    startY,endY = StartEnd(stack.shape, coords[1], 1, gauss[1])
    startX,endX = StartEnd(stack.shape, coords[2], 2, gauss[2])
    arrayZ = stack[startZ:endZ, coords[1], coords[2]]
    arrayY = stack[coords[0], startY:endY, coords[2]]
    arrayX = stack[coords[0], coords[1], startX:endX]
    fig = plt.figure(figsize = plt.figaspect(0.4)) #apre una nuova finestra
    fig.suptitle('Fitted gaussians')
    plotZ = fig.add_subplot(1,3,1) #aggiungo un'immagine in posizione 12
    plt.xlabel("Z (\u03BCm)")
    plt.ylabel("Counts") 
    parZ = BestFit(arrayZ, 1, pixDim[0])
    plotY = fig.add_subplot(1,3,2) #aggiungo un'immagine in posizione 12
    plt.xlabel("Y (\u03BCm)")
    parY = BestFit(arrayY, 1, pixDim[1])
    plotX = fig.add_subplot(1,3,3) #aggiungo un'immagine in posizione 12
    plt.xlabel("X (\u03BCm)")
    parX = BestFit(arrayX, 1, pixDim[2])
    plt.show()
    return parZ, parY, parX
 





"""TROVA BEADS"""

def MountainMax(stack, orderZ, orderY, orderX, thNoise, minValue, maxValue): #funziona con localmaxima3d di lore, monotone, startend. Trova le coordinate e i valori dei massimi locali, centri di parallelepipedi di dimensione [2*orderZ+1, 2*orderY+1, 2*orderX+1], sono massimi locali se da loro verso le croci lungo le direzioni z,y,x decrescono fino alla fine del parallelepipedo (almeno che non siano valori sotto thNoise, in tal caso possono variare come vogliono)  
    coords, values = local_maxima_3D(stack, 1, 1, 1) #vede i massimi locali "assoluti" all'interno del parallelepipedo
    goodList=[]
    for i in range(len(values)):
        if values[i]<minValue or values[i]>maxValue: #elimina i massimi fuori dal range
            values[i]=-1
            continue
        start,end=StartEnd(stack.shape, coords[i][0], 0, orderZ) #CROCE 3D: lungo Z
        temp=list(stack[ start : coords[i][0] , coords[i][1] , coords[i][2] ])
        if Monotone(temp, 1, thNoise)!=1: #fino al Max non è crescente, non è un buon max
            continue
        temp=list(stack[ coords[i][0]+1 : end , coords[i][1] , coords[i][2] ])
        if Monotone(temp, 0, thNoise)!=1: #fino alla fine non è decrescente, non è un buon max
            continue
        start,end=StartEnd(stack.shape, coords[i][1], 1, orderY) #lungo Y
        temp=list(stack[ coords[i][0] , start : coords[i][1] , coords[i][2] ])
        if Monotone(temp, 1, thNoise)!=1: 
            continue
        temp=list(stack[ coords[i][0] , coords[i][1]+1 : end , coords[i][2] ])
        if Monotone(temp, 0, thNoise)!=1: 
            continue
        start,end=StartEnd(stack.shape, coords[i][2], 2, orderX) #lungo X
        temp=list(stack[ coords[i][0] , coords[i][1] , start : coords[i][2] ])
        if Monotone(temp, 1, thNoise)!=1:
            continue
        temp=list(stack[ coords[i][0] , coords[i][1] , coords[i][2]+1 : end ])
        if Monotone(temp, 0, thNoise)!=1:
            continue
        goodList.append([ coords[i], values[i] ]) #Se arriva qui, lungo la croce è verificata la montagna, metti in lista il max
    return goodList


def Monotone(listValues, increasing, thNoise):  #Se i valori sono sotto una certa soglia (rumore), fregatene del saliscendi
    temp = [x if x > thNoise else thNoise for x in listValues]
    if increasing: #E' debolmente crescente?
        result = all(i <= j for i, j in zip(temp, temp[1:]))
    else: #E' debolmente decrescente?
        result = all(i >= j for i, j in zip(temp, temp[1:]))
    return result


def local_maxima_3D(data, orderZ, orderY, orderX): 
    sizeZ = 1 + 2 * orderZ
    sizeY = 1 + 2 * orderY
    sizeX = 1 + 2 * orderX
    footprint = np.ones((sizeZ, sizeY, sizeX))
    footprint[orderZ, orderY, orderX] = 0
    filtered = ndi.maximum_filter(data, footprint=footprint, mode='constant',cval=99999)  #NON prende le beads il cui parallelepipedo sfora dal bordo della stack, se si vuole considerarle mettere cval=0 (o valore negativo)
    mask_local_maxima = data > filtered
    coords = np.asarray(np.where(mask_local_maxima)).T
    values = data[mask_local_maxima]    
    return coords, values


def StartEnd(shape,coord,axis,radius):
    start=coord-radius
    end=coord+radius+1
    if start<0:
        start=0
    if end>shape[axis]:
        end=shape[axis]
    return start,end  


def DelLowDistance(stack, goodList, minDistanceZ, minDistanceY, minDistanceX, zW, yW, xW): #prende in ingresso una distanza, le dimensioni dei pixel (in micron), la lista delle coord e val dei max, restituisce la lista senza quelle i cui centri sono troppo vicini (dentro un cubo/parallelepipedo dato da minDistance [dovrebbe essere una sfera/ellissoide])
    sizeZ = int( minDistanceZ/zW + 0.5 ) #sono "gli ordini di profondità del parallelepipedo in pixel, dal centro
    sizeY = int( minDistanceY/yW + 0.5 )
    sizeX = int( minDistanceX/xW + 0.5 )
    size = [sizeZ, sizeY, sizeX]
    onesStack=np.zeros_like(stack)
    for i in range(len(goodList)):
        coord = goodList[i][0]
        onesStack[ coord[0], coord[1], coord[2] ] = 1 #adesso onesStack è tutti zeri a parte dove ci sono i massimi, lì c'è 1
    newList=[]
    start=np.zeros(3)
    end=np.zeros(3)
    for i in range(len(goodList)):
        for j in range(3): 
            start[j], end[j] = StartEnd(onesStack.shape, goodList[i][0][j], j, size[j])
        stackTemp = onesStack[int(start[0]):int(end[0]), int(start[1]):int(end[1]), int(start[2]):int(end[2])]
        if CountOnes(stackTemp)==1: #sta funzia restituisce 1 se c'è solo un uno 
            newList.append(goodList[i])        
    return newList


def CountOnes(stackTest):
    stackTest=stackTest.reshape(stackTest.shape[0]*stackTest.shape[1]*stackTest.shape[2])
    counts=list(stackTest).count(1)
    return counts






"""FIT GAUSSIANO"""

def GaussianStatistics(list,coord): #input lista di massimi con i parametri fittati e la coordinata 0,1 o 2. Restituisce media, std delle std gaussiane, poi
    stdG = []
    ampG = []
    errors = 0
    for i in range(len(list)):
        if list[i][2+coord][0] >= 0:   
            stdG.append(list[i][2+coord][2])
            ampG.append(list[i][2+coord][0])
        else:
            errors+=1
    meanStd = np.mean(stdG)
    stdStd = np.std(stdG)
    meanAmp = np.mean(ampG)
    sampleNumber = len(list)
    return meanStd, stdStd, sampleNumber, errors, meanAmp 


def PSF(stack, goodList, ampMin, ampMax, deepZ, deepY, deepX):  #ampMin e max della gaussiana    parGauss[2]*2.35482*pixelW>=rifractionLimit va bene? Per noi no perché rumore può farlo andare sotto il limite, ma quei dati sotto il limite vanno usati per correggere la stocasticità del rumore quando si fa la media delle varianze gaussiane
    for i in range(len(goodList)):
        parGaussZ=BestFit(BeadAreaZ(stack, goodList, i, deepZ), 0, 1) #A BeadArea interessa solo che gli passi la lista di coordinate
        parGaussY=BestFit(BeadAreaY(stack, goodList, i, deepY), 0, 1)
        parGaussX=BestFit(BeadAreaX(stack, goodList, i, deepX), 0, 1)  
        if parGaussZ[0]<ampMin or parGaussZ[0]>ampMax: #Se la gaussiana non ha ampiezza nel range desiderato (outlier), viene markata con -1
            if parGaussZ[0]!=-2 and parGaussZ[0]!=-3: #se è -2 c'è già stato il runtime error
                parGaussZ[0]=-1
        if parGaussY[0]<ampMin or parGaussY[0]>ampMax:
            if parGaussY[0]!=-2 and parGaussY[0]!=-3: #se è -2 c'è già stato il runtime error
                parGaussY[0]=-1    
        if parGaussX[0]<ampMin or parGaussX[0]>ampMax:
            if parGaussX[0]!=-2 and parGaussX[0]!=-3: #se è -2 c'è già stato il runtime error
                parGaussX[0]=-1         
        (goodList[i]).append(parGaussZ)
        (goodList[i]).append(parGaussY)
        (goodList[i]).append(parGaussX)
    return goodList


def BeadAreaZ(stack, list, i, radiusZ):
    start=list[i][0][0]-radiusZ
    end=list[i][0][0]+radiusZ+1
    if start<0:
        start=0
    if end>stack.shape[0]:
        end=stack.shape[0]
    array=stack[ start:end, list[i][0][1], list[i][0][2] ]
    return array


def BeadAreaY(stack, list, i, radiusY):
    start=list[i][0][1]-radiusY
    end=list[i][0][1]+radiusY+1
    if start<0:
        start=0
    if end>stack.shape[1]:
        end=stack.shape[1]
    array=stack[ list[i][0][0], start:end, list[i][0][2] ]
    return array


def BeadAreaX(stack, list, i, radiusX):
    start=list[i][0][2]-radiusX
    end=list[i][0][2]+radiusX+1
    if start<0:
        start=0
    if end>stack.shape[2]:
        end=stack.shape[2]
    array=stack[ list[i][0][0], list[i][0][1], start:end ]
    return array


def BestFit(array, plot, pixelDimension):
    parameters=np.zeros(4)
    x=np.arange(0, array.shape[0], 1)
    mean = sum(x * array) / sum(array)
    init_vals= [max(array), mean, 1, min(array)]
    try:
        params,extras=curve_fit(Gaussian, x, array, p0=init_vals)
    except RuntimeError:
        parameters[0]=-2
        return parameters
    if plot==1:
        plt.plot (x*pixelDimension, array, 'o')
        m = np.arange(0, array.shape[0], 0.1)
        plt.plot(m*pixelDimension, Gaussian(m,params[0],params[1],params[2],params[3]))
    wid = params[2]
    if wid>=0:    
        std=np.sqrt(wid/2)
    else:  #ha trovato una wid negativa, non va bene, restituisce -3
        params[0] = -3
        return parameters
    parameters = np.array([params[0],params[1], std, params[3]])
    return parameters


def Gaussian(x, amp, cen, wid, d):
    y = amp * np.exp(-(x-cen)**2 / wid)+d
    return y






"""CALCOLO AUTOMATICO DI PARAMETRI UTILI"""

def NoiseCalculator(stack): #DA MODIFICARE, SOSTITUIRE RICERCA MAX
    death=3
    mean=0
    std=0
    stack2=copy(stack)
    arrayNoise=ar(range(3))
    stackDim=stack.shape
    coords,values=local_maxima_3D(stack,order=2)
    for i in range(coords.shape[0]):
        for z in range(coords[i,0]-death-3,coords[i,0]+death+3):
            if z>0 and z<stackDim[0]:
                for y in range(coords[i,1]-death,coords[i,1]+death):
                    if y>0 and y<stackDim[1]:
                        for x in range(coords[i,2]-death,coords[i,2]+death):
                            if x>0 and x<stackDim[2]:
                                stack2[z,y,x]= -1
    stack2 = np.where(stack2>200, -1, stack2)
    arrayTemp=StackToArray(stack2)
    arrayNoise=np.zeros(len(arrayTemp))
    num=0
    for i in range(arrayTemp.shape[0]):
        if arrayTemp[i]!=-1:
            arrayNoise[num]=arrayTemp[i]
            num+=1
    arrayNoise=arrayNoise[0:num]
    mean=np.mean(arrayNoise)
    std=np.std(arrayNoise)
    return mean, std, arrayNoise, stack2






"""OBSOLETE O INUTILIZZATE"""

def FindSimm(stack, gap, ts):
    listCoords=[]
    listValues=[]
    coords,values=local_maxima_3D(stack,order=2)
    for i in range(coords.shape[0]):
        z=coords[i,0]
        y=coords[i,1]
        x=coords[i,2]
        if z>1 and z<stack.shape[0]-1 and y>1 and y<stack.shape[1]-1 and x>1 and x<stack.shape[2]-1:
            a=stack[z,y-1,x]
            b=stack[z,y,x-1]
            c=stack[z,y+1,x]
            d=stack[z,y,x+1]
            mean=(a+b+c+d)/4
            if abs(a-mean)<=gap and abs(b-mean)<=gap and abs(c-mean)<=gap and abs(d-mean)<=gap and values[i]>=ts:
                listCoords.append([z,y,x])
                listValues.append(values[i])
    coordsSimm=np.array(listCoords)
    valuesSimm=np.array(listValues)
    return coordsSimm,valuesSimm

    
def GaussianGenerator(array, mean,sigma,amp):
    if min(array)<0:
        dist=abs(min(array))
        array+=dist
    else:
        dist=0
    x=ar(range(len(array)))
    nStep=len(x)*10
    gauss=np.arange(0, float(len(x)), len(x)/nStep)
    axisX=np.arange(0, float(len(x)), len(x)/nStep)
    for i in range(nStep):
        gauss[i]=amp*math.exp(-(gauss[i]-mean)**2/(2*sigma**2))
    gauss-=dist
    array-=dist
    return axisX, gauss


def MeanSigmaAmp(array): #restituisce la mean e la sigma di un array. ATTENZIONE: Array non può avere valori negativi, altrimenti la stima non è attendibile o dà errore (perché nel calcolo di sigma, f(x) è una distribuzione)
    if min(array)<0:
        dist=abs(min(array))
        array+=dist
    else:
        dist=0
    x = ar(range(len(array)))
    mean = sum(x * array) / sum(array)
    sigma = np.sqrt(sum(array*(x - mean)**2) / sum(array))
    amp=max(array)
    array-=dist
    return mean,sigma,amp


def SqmCalculator(array, axisX,gauss):
    j=int(len(axisX)/len(array))
    sqm=0
    for i in range(len(array)):
        sqm += (array[i]-gauss[i*j])**2
    return sqm   
    

def FindGoodMax(stack, order, minValue, maxValue):
    coords,values=local_maxima_3D(stack, order)
    goodList=[]
    for i in range(len(values)):
        if values[i]>=minValue and values[i]<=maxValue:
            goodList.append([coords[i], values[i]])
    return goodList


def FindMaxZ(stack): #restituisce la z del piano verticale con la somma maggiore
    zMax=0
    sumMax=0
    for z in range(stack.shape[0]):
        sum = 0
        for y in range(stack.shape[1]): 
            for x in range(stack.shape[2]):
                sum += stack[z,y,x]
        if sum>sumMax: 
            zMax = z
            sumMax=sum
    return zMax   
    
    
def FindMaxInStack(stack): #restituisce le coordinate del punto più luminoso in una stack
    value = np.amax(stack)
    zMax,yMax,xMax = np.where(stack == value)
    return zMax,yMax,xMax,value  


