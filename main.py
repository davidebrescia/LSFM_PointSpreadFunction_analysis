
''' PSF RECONSTRUCTION '''


Menu_Mode = 1     # 0: Modalità classica, parametri testuali qui sotto 
                  # 1: Modalità Menu nel Variable Explorer

"""MENU"""

if not ( 'Menu' in globals() ) or ( not Menu_Mode ): #Imposta il Menu
    
    print("Loading...")
    
    from functions import *
    
    OpenStack = {
        "1. ON/OFF": 1,
        "2. Directory": 'C:/Users/davide/Desktop/Università/Lab progettuale - Tesi/Codice/PSF with GUI/Stacks',
        "3. File": 'stack75_Reduced_Lateral.tif',
    }
    
    CreateSubstack = {      #tutte le funzioni verranno eseguite sulla substack, se si vuole selezionare tutti i valori della stack lungo una direzione, immettere lungo quell'asse un valore negativo o outofrange
            "1. ON/OFF": 0,
            "2. Zstart": 0,
            "3. Zend": 9999,
            "4. Ystart": 0,
            "5. Yend": 9999,
            "6. Xstart": 0,
            "7. Xend": 9999
    }
    
    FrontView = {
        "1. ON/OFF": 0,
        "2. Black pixel": 0,
        "3. White pixel": 500
    }
    
    TopView = {
        "1. ON/OFF": 0,
        "2. Black pixel": 0,
        "3. White pixel": 500
    }
    
    CreateMipXYandMipXZ = {
        "1. ON/OFF": 0,
        "2. Black pixel": 0,
        "3. White pixel": 500 
    }
    
    ManualPsf_1 = {
       "1. ON/OFF": 1,
       "2. Pixel dimensions (um)": [1.625, 1.625, 1.625],
       "3. Order of the crossCheck": [3, 3, 3],
       "4. Noise threshold": 100,
       "5. Range for the beads intensity": [200, 1000],       
       "6. Required beads distance (um)": [12, 12, 12],
       "7. Range for the gaussians amplitude": [100, 900],       
       "8. Pixels involved in the gaussian plot": [7, 5, 5]
    }
    
    SingleBeadPSF = {
       "1. ON/OFF": 0,
       "2. Bead coordinates": [0,0,0],
       "3. Pixels involved in the gaussian plot": [0,0,0]
    }
    
    Menu = {
        "1. Open stack": OpenStack,
        "2. Create Substack": CreateSubstack,
        "3. Front view": FrontView,
        "4. Top view": TopView,
        "5. Create MipXY and MipXZ": CreateMipXYandMipXZ,
        "6. PSF calculator": ManualPsf_1,
        "7. PSF single bead": SingleBeadPSF 
    }




"""LEGEND"""

#1. Open stack
openStack = Menu["1. Open stack"]["1. ON/OFF"]
directory = Menu["1. Open stack"]["2. Directory"]
file = Menu["1. Open stack"]["3. File"]

#2. Create sub stack
createSubstack = Menu["2. Create Substack"]["1. ON/OFF"]
zsCs = Menu["2. Create Substack"]["2. Zstart"] 
zeCs = Menu["2. Create Substack"]["3. Zend"]
ysCs = Menu["2. Create Substack"]["4. Ystart"] 
yeCs = Menu["2. Create Substack"]["5. Yend"]
xsCs = Menu["2. Create Substack"]["6. Xstart"] 
xeCs = Menu["2. Create Substack"]["7. Xend"]

#3. Front view
frontView = Menu["3. Front view"]["1. ON/OFF"]
pMinfv = Menu["3. Front view"]["2. Black pixel"]   
pMaxfv = Menu["3. Front view"]["3. White pixel"]  

#4. Top view
topView = Menu["4. Top view"]["1. ON/OFF"]
pMintv = Menu["4. Top view"]["2. Black pixel"]   
pMaxtv = Menu["4. Top view"]["3. White pixel"]  
           
#5. MIP
createMipXYandXZ = Menu["5. Create MipXY and MipXZ"]["1. ON/OFF"]
pMinMip = Menu["5. Create MipXY and MipXZ"]["2. Black pixel"]  
pMaxMip = Menu["5. Create MipXY and MipXZ"]["3. White pixel"]              

#6. Manual Psf1
psf_1 = Menu["6. PSF calculator"]["1. ON/OFF"]
pixDim = Menu["6. PSF calculator"]["2. Pixel dimensions (um)"]
cchOrd = Menu["6. PSF calculator"]["3. Order of the crossCheck"]
noiseTh1 = Menu["6. PSF calculator"]["4. Noise threshold"]
intRan = Menu["6. PSF calculator"]["5. Range for the beads intensity"]
disOrd = Menu["6. PSF calculator"]["6. Required beads distance (um)"]
hiGaRange = Menu["6. PSF calculator"]["7. Range for the gaussians amplitude"]
gaussOr1 = Menu["6. PSF calculator"]["8. Pixels involved in the gaussian plot"]

#7. Single bead PSF
singleBeadPSF = Menu["7. PSF single bead"]["1. ON/OFF"]
coordsSb = Menu["7. PSF single bead"]["2. Bead coordinates"]
gaussOrSb = Menu["7. PSF single bead"]["3. Pixels involved in the gaussian plot"]




""" INSTRUCTIONS """

if openStack:
    stack = StackToMatrix(directory, file)
    substack = copy(stack)
    print('Stack dimensions are: ', stack.shape)

if createSubstack:
    substack = stack[ zsCs:zeCs+1, ysCs:yeCs+1, xsCs:xeCs+1]

if frontView:
    MultipleFrontView(substack, pMinfv, pMaxfv)
        
if topView:
    MultipleTopView(substack, pMintv, pMaxtv)
    
if createMipXYandXZ:
    mipXZ, mipXY = CreateMipXYandXZ(substack, pMinMip, pMaxMip)

if psf_1:
     mountainMaxList = MountainMax(substack, cchOrd[0], cchOrd[1], cchOrd[2], noiseTh1, intRan[0], intRan[1])
     lowDistanceList = DelLowDistance(substack, mountainMaxList, disOrd[0], disOrd[1], disOrd[2], pixDim[0], pixDim[1], pixDim[2])
     psf1List = PSF(substack, lowDistanceList, hiGaRange[0], hiGaRange[1], gaussOr1[0], gaussOr1[1], gaussOr1[2])
     meanStdZ, stdStdZ, sampleNumberZ, errorsZ, ampGZ = GaussianStatistics(psf1List,0)
     meanStdY, stdStdY, sampleNumberY, errorsY, ampGY = GaussianStatistics(psf1List,1)
     meanStdX, stdStdX, sampleNumberX, errorsX, ampGX = GaussianStatistics(psf1List,2)     
     print("\n### PSF gaussian fitting results ###")
     print("\n~~~~~~~~~~ Z Axis ~~~~~~~~~~~")
     print(" FWHM: ",'%.2f' % (meanStdZ*2.35482),"pixels |",'%.1f' % (meanStdZ*pixDim[0]*2.35482),"\u03BCm")
     print("    \u03C3: ",'%.2f' % (meanStdZ),"pixels |",'%.1f' % (meanStdZ*pixDim[0]),"\u03BCm")
     print(" \u03C3(\u03C3): ",'%.3f' % (stdStdZ))
     print("Beads: ",sampleNumberZ-errorsZ)
     print("\n~~~~~~~~~~ Y Axis ~~~~~~~~~~~")
     print(" FWHM: ",'%.2f' % (meanStdY*2.35482),"pixels |",'%.1f' % (meanStdY*pixDim[1]*2.35482),"\u03BCm")
     print("    \u03C3: ",'%.2f' % (meanStdY),"pixels |",'%.1f' % (meanStdY*pixDim[1]),"\u03BCm")
     print(" \u03C3(\u03C3): ",'%.3f' % (stdStdY))
     print("Beads: ",sampleNumberY-errorsY)
     print("\n~~~~~~~~~~ X Axis ~~~~~~~~~~~")
     print(" FWHM: ",'%.2f' % (meanStdX*2.35482),"pixels |",'%.1f' % (meanStdX*pixDim[2]*2.35482),"\u03BCm")
     print("    \u03C3: ",'%.2f' % (meanStdX),"pixels |",'%.1f' % (meanStdX*pixDim[2]),"\u03BCm")
     print(" \u03C3(\u03C3): ",'%.3f' % (stdStdX))
     print("Beads: ",sampleNumberX-errorsX)
     print("\n(Settings:",cchOrd,noiseTh1,intRan,disOrd,hiGaRange,gaussOr1,")")
     #Fa il grafico della PSF teorica 3D: lungo XY e XZ, genera 2 matrici le cui dimensioni dipendono (in micrometri) dalla std
     ampPSF1 = (ampGZ + ampGY + ampGX) / 3
     PlotFittedPSF(meanStdZ, meanStdY, meanStdX, pixDim, ampPSF1)
     
if singleBeadPSF:
    
    parametersZSb, parametersYSb, parametersXSb = PlotSingleBead(substack, coordsSb, gaussOrSb, pixDim)  #questa funzione plotta in una sola finestra i 3 plot gaussiani della singola bead, in più restituisce 3 array che contengono ciascuno i 4 parametri della gaussiana fittata (in pixel). Ha bisogno dei pixDim in ingresso, quindi nell'interfaccia utente i pixDim si possono mettere come casella "generale" in alto.
    
    print("\nSingle Bead PSF:")
    print("Settings: ",coordsSb," ",gaussOrSb)
    print("\nZ axis:")
    print("Amplitude:",'%.3f' % (parametersZSb[0]))
    print("Mean:",'%.3f' % (parametersZSb[1]))
    print("Std:",'%.3f' % (parametersZSb[2]))
    print("Noise:",'%.3f' % (parametersZSb[3]))
    print("\nY axis:")
    print("Amplitude:",'%.3f' % (parametersYSb[0]))
    print("Mean:",'%.3f' % (parametersYSb[1]))
    print("Std:",'%.3f' % (parametersYSb[2]))
    print("Noise:",'%.3f' % (parametersYSb[3]))
    print("\nX axis:")
    print("Amplitude:",'%.3f' % (parametersXSb[0]))
    print("Mean:",'%.3f' % (parametersXSb[1]))
    print("Std:",'%.3f' % (parametersXSb[2]))
    print("Noise:",'%.3f' % (parametersXSb[3]))
    
    
    
    
    
    
    
    
    
    