from tkinter import *
import tkinter.ttk as ttk
import sys
import os
from functions import *
from tkinter import filedialog

root = Tk()






"""VARIABILI INIZIALI (DI DEFAULT)"""

#File settings
directory = StringVar(value=os.getcwd())
file = StringVar(value="stack.tif")

#Find beads settings
crossCheckZ = StringVar(value=3)
crossCheckY = StringVar(value=3)
crossCheckX = StringVar(value=3)
noiseThreshold = StringVar(value=100)
beadsCountsMin = StringVar(value=300)
beadsCountsMax = StringVar(value=1000)
beadsDistanceZ = StringVar(value=10.0)
beadsDistanceY = StringVar(value=10.0)
beadsDistanceX = StringVar(value=10.0)

#Analyze single bead
beadCoordZ = StringVar(value=0)
beadCoordY = StringVar(value=0)
beadCoordX = StringVar(value=0)
pixelGaussZbead = StringVar(value=6)
pixelGaussYbead = StringVar(value=5)
pixelGaussXbead = StringVar(value=5)
showSingleBeadPSFplot = StringVar(value=0)

#PSF settings
gaussAmpMin = StringVar(value=100)   # '''da fissare'''
gaussAmpMax = StringVar(value=900)
pixelGaussZ = StringVar(value=6)
pixelGaussY = StringVar(value=5)
pixelGaussX = StringVar(value=5)
showPSFplot = StringVar(value=1)

#General settings (PIXEL E SUBSTACK)
pixelZ = StringVar(value=1.625)   #in fondo inverte 312 controlla che corrispondano xyz ai numeri giusti''' --> Si corrispondono
pixelY = StringVar(value=1.625)
pixelX = StringVar(value=1.625)
wantSubstack = StringVar(value=0)
substackZStart = StringVar(value=0)
substackZEnd = StringVar(value=0)
substackYStart = StringVar(value=0)
substackYEnd = StringVar(value=0)
substackXStart = StringVar(value=0)
substackXEnd = StringVar(value=0)

#MIP contrast
pMin=StringVar(value=200)
pMax=StringVar(value=2000)

#Functions counts
countsPSF=1
countsSaveResults=1
countsSaveBeads=1






"""FUNZIONI PER LA GUI"""

def LoadStack():
    global stackOriginal
    stackOriginal = StackToMatrixW()
    Label1_3.configure(text=str(stackOriginal.shape))
    

def OpenFileDirectory():
    global file, directory
    filename =  filedialog.askopenfilename( title = "Select file",filetypes = (("Tiff files","*.tif"),("all files","*.*")))
    filename = filename[::-1] #ribalta la stringa
    file,directory = filename.split('/',1)
    file = StringVar(value=file[::-1])
    directory = StringVar(value = directory[::-1])
    Entry1_1.configure(textvariable=directory)
    Entry1_2.configure(textvariable=file)
    

def StackToMatrixW():
    path = str(directory.get()) + '/' + str(file.get())
    mat = io.imread(path)
    mat = mat.astype(float)
    return mat


def MakeStack():
    if int(wantSubstack.get()) == 0:
        return copy(stackOriginal)
    else:
        return stackOriginal[int(substackZStart.get()):int(substackZEnd.get())+1, int(substackYStart.get()):int(substackYEnd.get())+1, int(substackXStart.get()):int(substackXEnd.get())+1]
        

def ClickOnImage(event):
    global selectedCoord, substackYStart
    if event.key == '1':
        selectedCoord[0] = int(float(event.ydata)+0.5) 
        selectedCoord[1] = int(float(event.xdata)+0.5)
    if event.key == '2':
        selectedCoord[2] = int(float(event.ydata)+0.5)
        selectedCoord[3] = int(float(event.xdata)+0.5) 
    selC=copy(selectedCoord)
    if selC[0]>selC[2]: #eventualmente scambia le coordinate
        temp=selC[2]
        selC[2]=selC[0]
        selC[0]=temp
    if selC[1]>selC[3]:
        temp=selC[1]
        selC[1]=selC[3]
        selC[3]=temp
    substackYStart.set(selC[0])
    substackYEnd.set(selC[2])
    substackXStart.set(selC[1])
    substackXEnd.set(selC[3])
    
    
def SubstackManualSelection():
    global selectedCoord
    selectedCoord = ar( [0,0, stackOriginal.shape[1]-1, stackOriginal.shape[2]-1] )
    mipImage = np.max(stackOriginal, axis = 0) #Creo la MIPXY da visualizzare
    figSelection, axSelection = plt.subplots() #Creo la finestra
    plt.title('Press \'1\' and \'2\' to select a region')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.imshow(mipImage, cmap='gray', vmin=int(pMin.get()), vmax=int(pMax.get()))
    cid = figSelection.canvas.mpl_connect('key_press_event', ClickOnImage)        
    substackZStart.set(0)
    substackZEnd.set(stackOriginal.shape[0]-1)
    wantSubstack.set(1)
    
    
def PSF_rec():
    stack = MakeStack()
    Listbox1.insert(0, '# PSF gaussian fitting results #')
    global psf1List
    mountainMaxList = MountainMax(stack, int(crossCheckZ.get()), int(crossCheckY.get()), int(crossCheckX.get()), int(noiseThreshold.get()), float(beadsCountsMin.get()), float(beadsCountsMax.get()))
    lowDistanceList = DelLowDistance(stack, mountainMaxList, float(beadsDistanceZ.get()), float(beadsDistanceY.get()), float(beadsDistanceX.get()), float(pixelZ.get()), float(pixelY.get()), float(pixelX.get()))
    psf1List = PSF(stack, lowDistanceList, float(gaussAmpMin.get()), float(gaussAmpMax.get()), int(pixelGaussZ.get()), int(pixelGaussY.get()),  int(pixelGaussX.get()))
    meanStdZ, stdStdZ, sampleNumberZ, errorsZ, ampGZ = GaussianStatistics(psf1List,0)
    meanStdY, stdStdY, sampleNumberY, errorsY, ampGY = GaussianStatistics(psf1List,1)
    meanStdX, stdStdX, sampleNumberX, errorsX, ampGX = GaussianStatistics(psf1List,2)     
    pixDim = [float(pixelZ.get()), float(pixelY.get()),  float(pixelX.get())]
    Listbox1.insert(1, ' ')
    Listbox1.insert(2, '------------ Z Axis -------------')
    Listbox1.insert(3, ' FWHM:  ' + str('%.2f' % (meanStdZ*2.35482)) + ' pixels | ' + str('%.1f' % (meanStdZ*pixDim[0]*2.35482)) + ' \u03BCm')
    Listbox1.insert(4, '    \u03C3:  ' + str('%.2f' % (meanStdZ)) + ' pixels | ' + str('%.1f' % (meanStdZ*pixDim[0])) + ' \u03BCm')
    Listbox1.insert(5, ' \u03C3(\u03C3):  ' + str('%.3f' % (stdStdZ)))
    Listbox1.insert(6, 'Beads:  ' + str(sampleNumberZ-errorsZ))
    Listbox1.insert(7, ' ')
    Listbox1.insert(8, '------------ Y Axis -------------')
    Listbox1.insert(9, ' FWHM:  ' + str('%.2f' % (meanStdY*2.35482)) + ' pixels | ' + str('%.1f' % (meanStdY*pixDim[1]*2.35482)) + ' \u03BCm')
    Listbox1.insert(10, '    \u03C3:  ' + str('%.2f' % (meanStdY)) + ' pixels | ' + str('%.1f' % (meanStdY*pixDim[1])) + ' \u03BCm')
    Listbox1.insert(11, ' \u03C3(\u03C3):  ' + str('%.3f' % (stdStdY)))
    Listbox1.insert(12, 'Beads:  ' + str(sampleNumberY-errorsY))
    Listbox1.insert(13, ' ')
    Listbox1.insert(14, '------------ X Axis -------------')
    Listbox1.insert(15, ' FWHM:  ' + str('%.2f' % (meanStdX*2.35482)) + ' pixels | ' + str('%.1f' % (meanStdX*pixDim[2]*2.35482)) + ' \u03BCm')
    Listbox1.insert(16, '    \u03C3:  ' + str('%.2f' % (meanStdX)) + ' pixels | ' + str('%.1f' % (meanStdX*pixDim[2])) + ' \u03BCm')
    Listbox1.insert(17, ' \u03C3(\u03C3):  ' + str('%.3f' % (stdStdX)))
    Listbox1.insert(18, 'Beads:  ' + str(sampleNumberX-errorsX))
    Listbox1.insert(19, ' ')
    Listbox1.insert(20, ' ')
    Listbox1.insert(0, ' ')
    ampPSF1 = (ampGZ + ampGY + ampGX) / 3
    if int(showPSFplot.get())==1:  
        PlotFittedPSF(meanStdZ, meanStdY, meanStdX, pixDim, ampPSF1)

     
def PrintBeadsList():
    stack = MakeStack()
    mountainMaxList = MountainMax(stack, int(crossCheckZ.get()), int(crossCheckY.get()), int(crossCheckX.get()), int(noiseThreshold.get()), float(beadsCountsMin.get()), float(beadsCountsMax.get()))
    lowDistanceList = DelLowDistance(stack, mountainMaxList, float(beadsDistanceZ.get()), float(beadsDistanceY.get()), float(beadsDistanceX.get()), float(pixelZ.get()), float(pixelY.get()), float(pixelX.get()))
    global psf1List
    psf1List = PSF(stack, lowDistanceList, float(gaussAmpMin.get()), float(gaussAmpMax.get()), int(pixelGaussZ.get()), int(pixelGaussY.get()),  int(pixelGaussX.get()))
    window2 = Tk()
    window2.geometry('335x556+0+0')
    window2.title('Beads List')
    window2.configure(background="#d9d9d9")
    Top2 = Frame(window2, width = 800, height = 50, bg = "#d9d9d9", relief = SUNKEN)
    Top2.pack(side=TOP)
    lblInfo2 = Label(Top2, font = ('arial', 20), text = 'Beads List',bg = "#d9d9d9", fg = "#001289", anchor = 'w')
    lblInfo2.grid(row=0, column=0)
    global listBeads
    listBeads = Listbox (window2, width = 50, height = 30, selectmode = EXTENDED)
    listBeads.pack()
    listBeads.insert(0, '#      Coords        Counts')
    save_list = Button(window2, text = 'Save (.txt)',width = 8, height = 1, command = Save_List)
    save_list.pack()
    [a,b,c] = [0,0,0]
    if int(wantSubstack.get()) == 1:
        [a,b,c] = [int(substackZStart.get()), int(substackYStart.get()), int(substackXStart.get())]
    for i in range (len(psf1List)):
        z = psf1List[i][0][0] + a
        y = psf1List[i][0][1] + b
        x = psf1List[i][0][2] + c
        listBeads.insert(i+1, str(i+1) + ')     [' + str(z)+'  '+str(y)+'  '+str(x) + ']     ' + str(psf1List[i][1]))
    window2.mainloop()


def GenerateMIP():
    global mipXY
    stack = MakeStack()
    mipXZ, mipXY = CreateMipXYandXZ(stack, int(pMin.get()), int(pMax.get()))
           

def BeadPlot():
    coords = [int(beadCoordZ.get()), int(beadCoordY.get()), int(beadCoordX.get())]
    gauss = [int(pixelGaussZbead.get()), int(pixelGaussYbead.get()), int(pixelGaussXbead.get())]
    pixDim = [float(pixelZ.get()), float(pixelY.get()),  float(pixelX.get())]
    parZ, parY, parX = PlotSingleBead(stackOriginal, coords, gauss, pixDim)
    Listbox1.insert(0, '# Single bead [' + str(int(beadCoordZ.get())) + ' ' + str(int(beadCoordY.get())) + ' ' + str(int(beadCoordX.get())) + '] #')
    Listbox1.insert(1, ' ')
    Listbox1.insert(2, '------------ Z Axis -------------')
    Listbox1.insert(3, ' FWHM:  ' + str('%.2f' % (parZ[2]*2.35482)) + ' pixels | ' + str('%.1f' % (parZ[2]*pixDim[0]*2.35482)) + ' \u03BCm')
    Listbox1.insert(4, '    \u03C3:  ' + str('%.2f' % (parZ[2])) + ' pixels | ' + str('%.1f' % (parZ[2]*pixDim[0])) + ' \u03BCm')
    Listbox1.insert(5, ' Amp.:  ' + str('%.1f' % (parZ[0])) + ' counts')
    Listbox1.insert(6, 'Noise:  ' + str('%.1f' % (parZ[3])) + ' counts')
    Listbox1.insert(7, ' ')
    Listbox1.insert(8, '------------ Y Axis -------------')
    Listbox1.insert(9, ' FWHM:  ' + str('%.2f' % (parY[2]*2.35482)) + ' pixels | ' + str('%.1f' % (parY[2]*pixDim[1]*2.35482)) + ' \u03BCm')
    Listbox1.insert(10, '    \u03C3:  ' + str('%.2f' % (parY[2])) + ' pixels | ' + str('%.1f' % (parY[2]*pixDim[1])) + ' \u03BCm')
    Listbox1.insert(11, ' Amp.:  ' + str('%.1f' % (parY[0])) + ' counts')
    Listbox1.insert(12, 'Noise:  ' + str('%.1f' % (parY[3])) + ' counts')
    Listbox1.insert(13, ' ')
    Listbox1.insert(14, '------------ X Axis -------------')
    Listbox1.insert(15, ' FWHM:  ' + str('%.2f' % (parX[2]*2.35482)) + ' pixels | ' + str('%.1f' % (parX[2]*pixDim[2]*2.35482)) + ' \u03BCm')
    Listbox1.insert(16, '    \u03C3:  ' + str('%.2f' % (parX[2])) + ' pixels | ' + str('%.1f' % (parX[2]*pixDim[2])) + ' \u03BCm')
    Listbox1.insert(17, ' Amp.:  ' + str('%.1f' % (parX[0])) + ' counts')
    Listbox1.insert(18, 'Noise:  ' + str('%.1f' % (parX[3])) + ' counts')
    Listbox1.insert(19, ' ')
    Listbox1.insert(0, ' ')
    if int(showSingleBeadPSFplot.get())==1: 
        PlotFittedPSF(parZ[2], parY[2], parX[2], pixDim, (parZ[0]+parY[0]+parX[0])/3 )
    else:
        plt.pyplot.close()


def ShowSingleBead():
    global bead
    coord = [int(beadCoordZ.get()), int(beadCoordY.get()), int(beadCoordX.get())]
    gauss = [int(pixelGaussZbead.get()), int(pixelGaussYbead.get()), int(pixelGaussXbead.get())]
    startZ,endZ = StartEnd(stackOriginal.shape,coord[0],0,gauss[0])
    startY,endY = StartEnd(stackOriginal.shape,coord[1],1,gauss[1])
    startX,endX = StartEnd(stackOriginal.shape,coord[2],2,gauss[2])
    bead = stackOriginal[startZ:endZ,startY:endY, startX:endX]
    mipXZbead,mipXYbead = CreateMipXYandXZ(bead, int(pMin.get()), int(pMax.get()))


def Save_Results():
    global countsSaveResults
    pathPSFResults = 'error'
    pathPSFResults = filedialog.askdirectory(title='Select directory')
    if pathPSFResults == 'error':
        pathPSFResults = ''
    else:
        pathPSFResults = pathPSFResults + '/'
    list_results = list(Listbox1.get(0,END))
    new_file_results = open(pathPSFResults+'PSF_Results(' + str(countsSaveResults) + ').txt', 'w',encoding='utf-8')
    countsSaveResults+=1
    for i in range(len(list_results)):
        new_file_results.write(list_results[i]+'\n')
    new_file_results.close() 
    

def Save_List():
    global countsSaveBeads
    pathSaveBeads = 'error'
    pathSaveBeads = filedialog.askdirectory(title='Select directory')
    if pathSaveBeads == 'error':
        pathSaveBeads = ''
    else:
        pathSaveBeads = pathSaveBeads + '/'
    list_beads = list(listBeads.get(0,END))
    new_file_beads = open(pathSaveBeads+'Beads_List(' + str(countsSaveBeads) + ').txt', 'w')
    countsSaveBeads+=1
    for i in range(len(list_beads)):
        new_file_beads.write(list_beads[i]+'\n')
    new_file_beads.close()


def Clear_ListBox():
    Listbox1.delete(0,'end')

    
    
    

    
    
    

"""GUI"""

_bgcolor = '#d9d9d9'  # X11 color: 'gray85'
_fgcolor = '#000000'  # X11 color: 'black'
_compcolor = '#d9d9d9' # X11 color: 'gray85'
_ana1color = '#d9d9d9' # X11 color: 'gray85'
_ana2color = '#ececec' # Closest X11 color: 'gray92'
font10 = "-family Arial -size 20 -weight normal -slant roman "  \
    "-underline 0 -overstrike 0"
font11 = "-family Arial -size 10 -weight normal -slant roman "  \
    "-underline 0 -overstrike 0"
font13 = "-family Arial -size 8 -weight normal -slant roman "  \
    "-underline 0 -overstrike 0"
font15 = "-family Consolas -size 11 -weight normal -slant "  \
    "roman -underline 0 -overstrike 0"
font9 = "-family {Segoe UI} -size 12 -weight normal -slant "  \
    "roman -underline 0 -overstrike 0"
style = ttk.Style()
if sys.platform == "win32":
    style.theme_use('winnative')
style.configure('.',background=_bgcolor)
style.configure('.',foreground=_fgcolor)
style.configure('.',font="TkDefaultFont")
style.map('.',background=
    [('selected', _compcolor), ('active',_ana2color)])

root.geometry("900x556+200+60")
root.title("PSF Reconstruction")
root.configure(background="#d9d9d9")
root.configure(highlightbackground="#d9d9d9")
root.configure(highlightcolor="black")

title = Message(root)
title.place(relx=0.333, rely=0.018, relheight=0.095, relwidth=0.311)

title.configure(background="#d9d9d9")
title.configure(font=font10)
title.configure(foreground="#001289")
title.configure(highlightbackground="#d9d9d9")
title.configure(highlightcolor="black")
title.configure(relief="ridge")
title.configure(text='''PSF Reconstruction''')
title.configure(width=280)

frame_filesettings = LabelFrame(root)
frame_filesettings.place(relx=0.022, rely=0.144, relheight=0.225
        , relwidth=0.289)
frame_filesettings.configure(relief='groove')
frame_filesettings.configure(foreground="black")
frame_filesettings.configure(text='''Open the stack (.tif)''')
frame_filesettings.configure(background="#d9d9d9")
frame_filesettings.configure(highlightbackground="#d9d9d9")
frame_filesettings.configure(highlightcolor="black")
frame_filesettings.configure(width=260)

Label1_1 = Label(frame_filesettings)
Label1_1.place(relx=0.038, rely=0.24, height=21, width=54
        , bordermode='ignore')
Label1_1.configure(activebackground="#f9f9f9")
Label1_1.configure(activeforeground="black")
Label1_1.configure(background="#d9d9d9")
Label1_1.configure(disabledforeground="#a3a3a3")
Label1_1.configure(foreground="#000000")
Label1_1.configure(highlightbackground="#d9d9d9")
Label1_1.configure(highlightcolor="black")
Label1_1.configure(text='''Directory''')

Label1_2 = Label(frame_filesettings)
Label1_2.place(relx=0.115, rely=0.48, height=21, width=34
        , bordermode='ignore')
Label1_2.configure(activebackground="#f9f9f9")
Label1_2.configure(activeforeground="black")
Label1_2.configure(background="#d9d9d9")
Label1_2.configure(disabledforeground="#a3a3a3")
Label1_2.configure(foreground="#000000")
Label1_2.configure(highlightbackground="#d9d9d9")
Label1_2.configure(highlightcolor="black")
Label1_2.configure(text='''File''')

Entry1_1 = Entry(frame_filesettings)
Entry1_1.place(relx=0.269, rely=0.24, height=20, relwidth=0.631
        , bordermode='ignore')
Entry1_1.configure(background="white")
Entry1_1.configure(disabledforeground="#a3a3a3")
Entry1_1.configure(font=font11)
Entry1_1.configure(foreground="#000000")
Entry1_1.configure(highlightbackground="#d9d9d9")
Entry1_1.configure(highlightcolor="black")
Entry1_1.configure(insertbackground="black")
Entry1_1.configure(selectbackground="#c4c4c4")
Entry1_1.configure(selectforeground="black")
Entry1_1.configure(textvariable=directory)

Entry1_2 = Entry(frame_filesettings)
Entry1_2.place(relx=0.269, rely=0.48, height=20, relwidth=0.631
        , bordermode='ignore')
Entry1_2.configure(background="white")
Entry1_2.configure(disabledforeground="#a3a3a3")
Entry1_2.configure(font=font11)
Entry1_2.configure(foreground="#000000")
Entry1_2.configure(highlightbackground="#d9d9d9")
Entry1_2.configure(highlightcolor="black")
Entry1_2.configure(insertbackground="black")
Entry1_2.configure(selectbackground="#c4c4c4")
Entry1_2.configure(selectforeground="black")
Entry1_2.configure(textvariable=file)

Button1_1 = Button(frame_filesettings)
Button1_1.place(relx=0.05, rely=0.72, height=24, width=67
        , bordermode='ignore')
Button1_1.configure(activebackground="#ececec")
Button1_1.configure(activeforeground="#000000")
Button1_1.configure(background="#d9d9d9")
Button1_1.configure(disabledforeground="#a3a3a3")
Button1_1.configure(foreground="#000000")
Button1_1.configure(highlightbackground="#d9d9d9")                       
Button1_1.configure(highlightcolor="black")
Button1_1.configure(pady="0")
Button1_1.configure(text='''Browse...''')
Button1_1.configure(command=OpenFileDirectory)

Button1_2 = Button(frame_filesettings)
Button1_2.place(relx=0.35, rely=0.72, height=24, width=67
        , bordermode='ignore')
Button1_2.configure(activebackground="#ececec")
Button1_2.configure(activeforeground="#000000")
Button1_2.configure(background="#d9d9d9")
Button1_2.configure(disabledforeground="#a3a3a3")
Button1_2.configure(foreground="#000000")
Button1_2.configure(highlightbackground="#d9d9d9")                       
Button1_2.configure(highlightcolor="black")
Button1_2.configure(pady="0")
Button1_2.configure(text='''Load''')
Button1_2.configure(command=LoadStack)

Label1_3 = Label(frame_filesettings)
Label1_3.place(relx=0.615, rely=0.72, height=21, width=94
        , bordermode='ignore')
Label1_3.configure(activebackground="#f9f9f9")
Label1_3.configure(activeforeground="black")
Label1_3.configure(background="#d9d9d9")
Label1_3.configure(disabledforeground="#a3a3a3")
Label1_3.configure(foreground="#000000")
Label1_3.configure(highlightbackground="#d9d9d9")
Label1_3.configure(highlightcolor="black")
Label1_3.configure(text="Empty")

###########

frame_fbsettings = LabelFrame(root)
frame_fbsettings.place(relx=0.022, rely=0.378, relheight=0.279
        , relwidth=0.289)
frame_fbsettings.configure(relief='groove')
frame_fbsettings.configure(foreground="black")
frame_fbsettings.configure(text='''Find beads algorithm settings''')
frame_fbsettings.configure(background="#d9d9d9")
frame_fbsettings.configure(highlightbackground="#d9d9d9")
frame_fbsettings.configure(highlightcolor="black")
frame_fbsettings.configure(width=260)

Label2_1 = Label(frame_fbsettings)
Label2_1.place(relx=0.038, rely=0.194, height=21, width=113
        , bordermode='ignore')
Label2_1.configure(activebackground="#f9f9f9")
Label2_1.configure(activeforeground="black")
Label2_1.configure(background="#d9d9d9")
Label2_1.configure(disabledforeground="#a3a3a3")
Label2_1.configure(foreground="#000000")
Label2_1.configure(highlightbackground="#d9d9d9")
Label2_1.configure(highlightcolor="black")
Label2_1.configure(text='''Cross check (Z, Y, X)''')

Label2_2 = Label(frame_fbsettings)
Label2_2.place(relx=0.115, rely=0.387, height=21, width=94
        , bordermode='ignore')
Label2_2.configure(activebackground="#f9f9f9")
Label2_2.configure(activeforeground="black")
Label2_2.configure(background="#d9d9d9")
Label2_2.configure(disabledforeground="#a3a3a3")
Label2_2.configure(foreground="#000000")
Label2_2.configure(highlightbackground="#d9d9d9")
Label2_2.configure(highlightcolor="black")
Label2_2.configure(text='''Noise threshold''')

Spinbox2_1 = Spinbox(frame_fbsettings, from_=1.0, to=9999999.0)
Spinbox2_1.place(relx=0.5, rely=0.194, relheight=0.123
        , relwidth=0.135, bordermode='ignore')
Spinbox2_1.configure(activebackground="#f9f9f9")
Spinbox2_1.configure(background="white")
Spinbox2_1.configure(buttonbackground="#d9d9d9")
Spinbox2_1.configure(disabledforeground="#a3a3a3")
Spinbox2_1.configure(foreground="black")
Spinbox2_1.configure(highlightbackground="black")
Spinbox2_1.configure(highlightcolor="black")
Spinbox2_1.configure(insertbackground="black")
Spinbox2_1.configure(selectbackground="#c4c4c4")
Spinbox2_1.configure(selectforeground="black")
Spinbox2_1.configure(textvariable=crossCheckZ)

Spinbox2_2 = Spinbox(frame_fbsettings, from_=1.0, to=99999.0)
Spinbox2_2.place(relx=0.654, rely=0.194, relheight=0.123
        , relwidth=0.135, bordermode='ignore')
Spinbox2_2.configure(activebackground="#f9f9f9")
Spinbox2_2.configure(background="white")
Spinbox2_2.configure(buttonbackground="#d9d9d9")
Spinbox2_2.configure(disabledforeground="#a3a3a3")
Spinbox2_2.configure(foreground="black")
Spinbox2_2.configure(highlightbackground="black")
Spinbox2_2.configure(highlightcolor="black")
Spinbox2_2.configure(insertbackground="black")
Spinbox2_2.configure(selectbackground="#c4c4c4")
Spinbox2_2.configure(selectforeground="black")
Spinbox2_2.configure(textvariable=crossCheckY)

Spinbox2_3 = Spinbox(frame_fbsettings, from_=1.0, to=9999999.0)
Spinbox2_3.place(relx=0.808, rely=0.194, relheight=0.123
        , relwidth=0.135, bordermode='ignore')
Spinbox2_3.configure(activebackground="#f9f9f9")
Spinbox2_3.configure(background="white")
Spinbox2_3.configure(buttonbackground="#d9d9d9")
Spinbox2_3.configure(disabledforeground="#a3a3a3")
Spinbox2_3.configure(foreground="black")
Spinbox2_3.configure(highlightbackground="black")
Spinbox2_3.configure(highlightcolor="black")
Spinbox2_3.configure(insertbackground="black")
Spinbox2_3.configure(selectbackground="#c4c4c4")
Spinbox2_3.configure(selectforeground="black")
Spinbox2_3.configure(textvariable=crossCheckX)

Entry2_1 = Entry(frame_fbsettings)
Entry2_1.place(relx=0.5, rely=0.387, height=20, relwidth=0.169
        , bordermode='ignore')
Entry2_1.configure(background="white")
Entry2_1.configure(disabledforeground="#a3a3a3")
Entry2_1.configure(font=font11)
Entry2_1.configure(foreground="#000000")
Entry2_1.configure(highlightbackground="#d9d9d9")
Entry2_1.configure(highlightcolor="black")
Entry2_1.configure(insertbackground="black")
Entry2_1.configure(selectbackground="#c4c4c4")
Entry2_1.configure(selectforeground="black")
Entry2_1.configure(textvariable=noiseThreshold)

Label2_3 = Label(frame_fbsettings)
Label2_3.place(relx=0.077, rely=0.581, height=21, width=100
        , bordermode='ignore')
Label2_3.configure(activebackground="#f9f9f9")
Label2_3.configure(activeforeground="black")
Label2_3.configure(background="#d9d9d9")
Label2_3.configure(disabledforeground="#a3a3a3")
Label2_3.configure(foreground="#000000")
Label2_3.configure(highlightbackground="#d9d9d9")
Label2_3.configure(highlightcolor="black")
Label2_3.configure(text='''Beads amp. range''')

Entry2_2 = Entry(frame_fbsettings)
Entry2_2.place(relx=0.5, rely=0.581, height=20, relwidth=0.208
        , bordermode='ignore')
Entry2_2.configure(background="white")
Entry2_2.configure(disabledforeground="#a3a3a3")
Entry2_2.configure(font=font11)
Entry2_2.configure(foreground="#000000")
Entry2_2.configure(highlightbackground="#d9d9d9")
Entry2_2.configure(highlightcolor="black")
Entry2_2.configure(insertbackground="black")
Entry2_2.configure(selectbackground="#c4c4c4")
Entry2_2.configure(selectforeground="black")
Entry2_2.configure(textvariable=beadsCountsMin)

Entry2_3 = Entry(frame_fbsettings)
Entry2_3.place(relx=0.731, rely=0.581, height=20, relwidth=0.208
        , bordermode='ignore')
Entry2_3.configure(background="white")
Entry2_3.configure(disabledforeground="#a3a3a3")
Entry2_3.configure(font=font11)
Entry2_3.configure(foreground="#000000")
Entry2_3.configure(highlightbackground="#d9d9d9")
Entry2_3.configure(highlightcolor="black")
Entry2_3.configure(insertbackground="black")
Entry2_3.configure(selectbackground="#c4c4c4")
Entry2_3.configure(selectforeground="black")
Entry2_3.configure(textvariable=beadsCountsMax)

Label2_4 = Label(frame_fbsettings)
Label2_4.place(relx=0.038, rely=0.774, height=21, width=122
        , bordermode='ignore')
Label2_4.configure(activebackground="#f9f9f9")
Label2_4.configure(activeforeground="black")
Label2_4.configure(background="#d9d9d9")
Label2_4.configure(disabledforeground="#a3a3a3")
Label2_4.configure(foreground="#000000")
Label2_4.configure(highlightbackground="#d9d9d9")
Label2_4.configure(highlightcolor="black")
Label2_4.configure(text='''Min. dist. (\u03BCm) (Z Y X)''')

Entry2_4 = Entry(frame_fbsettings)
Entry2_4.place(relx=0.5, rely=0.774, height=20, relwidth=0.131
        , bordermode='ignore')
Entry2_4.configure(background="white")
Entry2_4.configure(disabledforeground="#a3a3a3")
Entry2_4.configure(font=font13)
Entry2_4.configure(foreground="#000000")
Entry2_4.configure(highlightbackground="#d9d9d9")
Entry2_4.configure(highlightcolor="black")
Entry2_4.configure(insertbackground="black")
Entry2_4.configure(selectbackground="#c4c4c4")
Entry2_4.configure(selectforeground="black")
Entry2_4.configure(textvariable=beadsDistanceZ)

Entry2_5 = Entry(frame_fbsettings)
Entry2_5.place(relx=0.654, rely=0.774, height=20, relwidth=0.131
        , bordermode='ignore')
Entry2_5.configure(background="white")
Entry2_5.configure(disabledforeground="#a3a3a3")
Entry2_5.configure(font=font13)
Entry2_5.configure(foreground="#000000")
Entry2_5.configure(highlightbackground="#d9d9d9")
Entry2_5.configure(highlightcolor="black")
Entry2_5.configure(insertbackground="black")
Entry2_5.configure(selectbackground="#c4c4c4")
Entry2_5.configure(selectforeground="black")
Entry2_5.configure(textvariable=beadsDistanceY)

Entry2_6 = Entry(frame_fbsettings)
Entry2_6.place(relx=0.808, rely=0.774, height=20, relwidth=0.131
        , bordermode='ignore')
Entry2_6.configure(background="white")
Entry2_6.configure(disabledforeground="#a3a3a3")
Entry2_6.configure(font=font13)
Entry2_6.configure(foreground="#000000")
Entry2_6.configure(highlightbackground="#d9d9d9")
Entry2_6.configure(highlightcolor="black")
Entry2_6.configure(insertbackground="black")
Entry2_6.configure(selectbackground="#c4c4c4")
Entry2_6.configure(selectforeground="black")
Entry2_6.configure(textvariable=beadsDistanceX)

###########

frame_psfsettings = LabelFrame(root)
frame_psfsettings.place(relx=0.022, rely=0.665, relheight=0.243
        , relwidth=0.289)
frame_psfsettings.configure(relief='groove')
frame_psfsettings.configure(foreground="black")
frame_psfsettings.configure(text='''PSF algorithm settings''')
frame_psfsettings.configure(background="#d9d9d9")
frame_psfsettings.configure(highlightbackground="#d9d9d9")
frame_psfsettings.configure(highlightcolor="black")
frame_psfsettings.configure(width=260)

Label4_1 = Label(frame_psfsettings)
Label4_1.place(relx=0.038, rely=0.222, height=21, width=116
        , bordermode='ignore')
Label4_1.configure(activebackground="#f9f9f9")
Label4_1.configure(activeforeground="black")
Label4_1.configure(background="#d9d9d9")
Label4_1.configure(disabledforeground="#a3a3a3")
Label4_1.configure(foreground="#000000")
Label4_1.configure(highlightbackground="#d9d9d9")
Label4_1.configure(highlightcolor="black")
Label4_1.configure(text='''Gaussian amp. range''')

Entry4_1 = Entry(frame_psfsettings)
Entry4_1.place(relx=0.5, rely=0.222, height=20, relwidth=0.208
        , bordermode='ignore')
Entry4_1.configure(background="white")
Entry4_1.configure(disabledforeground="#a3a3a3")
Entry4_1.configure(font=font11)
Entry4_1.configure(foreground="#000000")
Entry4_1.configure(highlightbackground="#d9d9d9")
Entry4_1.configure(highlightcolor="black")
Entry4_1.configure(insertbackground="black")
Entry4_1.configure(selectbackground="#c4c4c4")
Entry4_1.configure(selectforeground="black")
Entry4_1.configure(textvariable=gaussAmpMin)

Entry4_2 = Entry(frame_psfsettings)
Entry4_2.place(relx=0.731, rely=0.222, height=20, relwidth=0.208
        , bordermode='ignore')
Entry4_2.configure(background="white")
Entry4_2.configure(disabledforeground="#a3a3a3")
Entry4_2.configure(font=font11)
Entry4_2.configure(foreground="#000000")
Entry4_2.configure(highlightbackground="#d9d9d9")
Entry4_2.configure(highlightcolor="black")
Entry4_2.configure(insertbackground="black")
Entry4_2.configure(selectbackground="#c4c4c4")
Entry4_2.configure(selectforeground="black")
Entry4_2.configure(textvariable=gaussAmpMax)

Label4_2 = Label(frame_psfsettings)
Label4_2.place(relx=0.038, rely=0.444, height=21, width=116
        , bordermode='ignore')
Label4_2.configure(activebackground="#f9f9f9")
Label4_2.configure(activeforeground="black")
Label4_2.configure(background="#d9d9d9")
Label4_2.configure(disabledforeground="#a3a3a3")
Label4_2.configure(foreground="#000000")
Label4_2.configure(highlightbackground="#d9d9d9")
Label4_2.configure(highlightcolor="black")
Label4_2.configure(text='''Pixel involved (Z Y X)''')

Spinbox4_1 = Spinbox(frame_psfsettings, from_=1.0, to=9999999.0)
Spinbox4_1.place(relx=0.5, rely=0.444, relheight=0.141
        , relwidth=0.135, bordermode='ignore')
Spinbox4_1.configure(activebackground="#f9f9f9")
Spinbox4_1.configure(background="white")
Spinbox4_1.configure(buttonbackground="#d9d9d9")
Spinbox4_1.configure(disabledforeground="#a3a3a3")
Spinbox4_1.configure(foreground="black")
Spinbox4_1.configure(highlightbackground="black")
Spinbox4_1.configure(highlightcolor="black")
Spinbox4_1.configure(insertbackground="black")
Spinbox4_1.configure(selectbackground="#c4c4c4")
Spinbox4_1.configure(selectforeground="black")
Spinbox4_1.configure(textvariable=pixelGaussZ)

Spinbox4_2 = Spinbox(frame_psfsettings, from_=1.0, to=9999999.0)
Spinbox4_2.place(relx=0.654, rely=0.444, relheight=0.141
        , relwidth=0.135, bordermode='ignore')
Spinbox4_2.configure(activebackground="#f9f9f9")
Spinbox4_2.configure(background="white")
Spinbox4_2.configure(buttonbackground="#d9d9d9")
Spinbox4_2.configure(disabledforeground="#a3a3a3")
Spinbox4_2.configure(foreground="black")
Spinbox4_2.configure(highlightbackground="black")
Spinbox4_2.configure(highlightcolor="black")
Spinbox4_2.configure(insertbackground="black")
Spinbox4_2.configure(selectbackground="#c4c4c4")
Spinbox4_2.configure(selectforeground="black")
Spinbox4_2.configure(textvariable=pixelGaussY)

Spinbox4_3 = Spinbox(frame_psfsettings, from_=1.0, to=9999999.0)
Spinbox4_3.place(relx=0.808, rely=0.444, relheight=0.141
        , relwidth=0.135, bordermode='ignore')
Spinbox4_3.configure(activebackground="#f9f9f9")
Spinbox4_3.configure(background="white")
Spinbox4_3.configure(buttonbackground="#d9d9d9")
Spinbox4_3.configure(disabledforeground="#a3a3a3")
Spinbox4_3.configure(foreground="black")
Spinbox4_3.configure(highlightbackground="black")
Spinbox4_3.configure(highlightcolor="black")
Spinbox4_3.configure(insertbackground="black")
Spinbox4_3.configure(selectbackground="#c4c4c4")
Spinbox4_3.configure(selectforeground="black")
Spinbox4_3.configure(textvariable=pixelGaussX)

Checkbutton4_1 = Checkbutton(frame_psfsettings)
Checkbutton4_1.place(relx=0.615, rely=0.741, relheight=0.185
        , relwidth=0.312, bordermode='ignore')
Checkbutton4_1.configure(activebackground="#ececec")
Checkbutton4_1.configure(activeforeground="#000000")
Checkbutton4_1.configure(background="#d9d9d9")
Checkbutton4_1.configure(disabledforeground="#a3a3a3")
Checkbutton4_1.configure(foreground="#000000")
Checkbutton4_1.configure(highlightbackground="#d9d9d9")
Checkbutton4_1.configure(highlightcolor="black")
Checkbutton4_1.configure(justify='left')
Checkbutton4_1.configure(text='''Show plot''')
Checkbutton4_1.configure(variable=showPSFplot)

###########

frame_generalsettings = LabelFrame(root)
frame_generalsettings.place(relx=0.322, rely=0.144, relheight=0.297
        , relwidth=0.344)
frame_generalsettings.configure(relief='groove')
frame_generalsettings.configure(foreground="black")
frame_generalsettings.configure(text='''General settings''')
frame_generalsettings.configure(background="#d9d9d9")
frame_generalsettings.configure(highlightbackground="#d9d9d9")
frame_generalsettings.configure(highlightcolor="black")
frame_generalsettings.configure(width=310)

Label5_1 = Label(frame_generalsettings)
Label5_1.place(relx=0.032, rely=0.182, height=21, width=161
        , bordermode='ignore')
Label5_1.configure(activebackground="#f9f9f9")
Label5_1.configure(activeforeground="black")
Label5_1.configure(background="#d9d9d9")
Label5_1.configure(disabledforeground="#a3a3a3")
Label5_1.configure(foreground="#000000")
Label5_1.configure(highlightbackground="#d9d9d9")
Label5_1.configure(highlightcolor="black")
Label5_1.configure(text='''Pixel dimensions (\u03BCm) (Z Y X)''')

Entry5_1 = Entry(frame_generalsettings)
Entry5_1.place(relx=0.581, rely=0.182, height=20, relwidth=0.11
        , bordermode='ignore')
Entry5_1.configure(background="white")
Entry5_1.configure(disabledforeground="#a3a3a3")
Entry5_1.configure(font=font13)
Entry5_1.configure(foreground="#000000")
Entry5_1.configure(highlightbackground="#d9d9d9")
Entry5_1.configure(highlightcolor="black")
Entry5_1.configure(insertbackground="black")
Entry5_1.configure(selectbackground="#c4c4c4")
Entry5_1.configure(selectforeground="black")
Entry5_1.configure(textvariable=pixelZ)

Entry5_2 = Entry(frame_generalsettings)
Entry5_2.place(relx=0.71, rely=0.182, height=20, relwidth=0.11
        , bordermode='ignore')
Entry5_2.configure(background="white")
Entry5_2.configure(disabledforeground="#a3a3a3")
Entry5_2.configure(font=font13)
Entry5_2.configure(foreground="#000000")
Entry5_2.configure(highlightbackground="#d9d9d9")
Entry5_2.configure(highlightcolor="black")
Entry5_2.configure(insertbackground="black")
Entry5_2.configure(selectbackground="#c4c4c4")
Entry5_2.configure(selectforeground="black")
Entry5_2.configure(textvariable=pixelY)

Entry5_3 = Entry(frame_generalsettings)
Entry5_3.place(relx=0.839, rely=0.182, height=20, relwidth=0.11
        , bordermode='ignore')
Entry5_3.configure(background="white")
Entry5_3.configure(disabledforeground="#a3a3a3")
Entry5_3.configure(font=font13)
Entry5_3.configure(foreground="#000000")
Entry5_3.configure(highlightbackground="#d9d9d9")
Entry5_3.configure(highlightcolor="black")
Entry5_3.configure(insertbackground="black")
Entry5_3.configure(selectbackground="#c4c4c4")
Entry5_3.configure(selectforeground="black")
Entry5_3.configure(textvariable=pixelX)

TSeparator1 = ttk.Separator(frame_generalsettings)
TSeparator1.place(relx=0.0, rely=0.455, relwidth=1.032
        , bordermode='ignore')

Checkbutton5_1 = Checkbutton(frame_generalsettings)
Checkbutton5_1.place(relx=0.032, rely=0.364, relheight=0.152
        , relwidth=0.455, bordermode='ignore')
Checkbutton5_1.configure(activebackground="#ececec")
Checkbutton5_1.configure(activeforeground="#000000")
Checkbutton5_1.configure(background="#d9d9d9")
Checkbutton5_1.configure(disabledforeground="#a3a3a3")
Checkbutton5_1.configure(foreground="#000000")
Checkbutton5_1.configure(highlightbackground="#d9d9d9")
Checkbutton5_1.configure(highlightcolor="black")
Checkbutton5_1.configure(justify='left')
Checkbutton5_1.configure(text='''Work on a substack''')
Checkbutton5_1.configure(variable=wantSubstack)

Label5_2 = Label(frame_generalsettings)
Label5_2.place(relx=0.129, rely=0.545, height=11, width=13
        , bordermode='ignore')
Label5_2.configure(activebackground="#f9f9f9")
Label5_2.configure(activeforeground="black")
Label5_2.configure(background="#d9d9d9")
Label5_2.configure(disabledforeground="#a3a3a3")
Label5_2.configure(foreground="#000000")
Label5_2.configure(highlightbackground="#d9d9d9")
Label5_2.configure(highlightcolor="black")
Label5_2.configure(text='''Z''')

Label5_3 = Label(frame_generalsettings)
Label5_3.place(relx=0.29, rely=0.545, height=11, width=14
        , bordermode='ignore')
Label5_3.configure(activebackground="#f9f9f9")
Label5_3.configure(activeforeground="black")
Label5_3.configure(background="#d9d9d9")
Label5_3.configure(disabledforeground="#a3a3a3")
Label5_3.configure(foreground="#000000")
Label5_3.configure(highlightbackground="#d9d9d9")
Label5_3.configure(highlightcolor="black")
Label5_3.configure(text='''Y''')

Label5_4 = Label(frame_generalsettings)
Label5_4.place(relx=0.452, rely=0.545, height=11, width=13
        , bordermode='ignore')
Label5_4.configure(activebackground="#f9f9f9")
Label5_4.configure(activeforeground="black")
Label5_4.configure(background="#d9d9d9")
Label5_4.configure(disabledforeground="#a3a3a3")
Label5_4.configure(foreground="#000000")
Label5_4.configure(highlightbackground="#d9d9d9")
Label5_4.configure(highlightcolor="black")
Label5_4.configure(text='''X''')

Spinbox5_1 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_1.place(relx=0.097, rely=0.667, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_1.configure(activebackground="#f9f9f9")
Spinbox5_1.configure(background="white")
Spinbox5_1.configure(buttonbackground="#d9d9d9")
Spinbox5_1.configure(disabledforeground="#a3a3a3")
Spinbox5_1.configure(foreground="black")
Spinbox5_1.configure(highlightbackground="black")
Spinbox5_1.configure(highlightcolor="black")
Spinbox5_1.configure(insertbackground="black")
Spinbox5_1.configure(selectbackground="#c4c4c4")
Spinbox5_1.configure(selectforeground="black")
Spinbox5_1.configure(textvariable=substackZStart)

Spinbox5_2 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_2.place(relx=0.097, rely=0.788, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_2.configure(activebackground="#f9f9f9")
Spinbox5_2.configure(background="white")
Spinbox5_2.configure(buttonbackground="#d9d9d9")
Spinbox5_2.configure(disabledforeground="#a3a3a3")
Spinbox5_2.configure(foreground="black")
Spinbox5_2.configure(highlightbackground="black")
Spinbox5_2.configure(highlightcolor="black")
Spinbox5_2.configure(insertbackground="black")
Spinbox5_2.configure(selectbackground="#c4c4c4")
Spinbox5_2.configure(selectforeground="black")
Spinbox5_2.configure(textvariable=substackZEnd)

Spinbox5_3 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_3.place(relx=0.258, rely=0.667, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_3.configure(activebackground="#f9f9f9")
Spinbox5_3.configure(background="white")
Spinbox5_3.configure(buttonbackground="#d9d9d9")
Spinbox5_3.configure(disabledforeground="#a3a3a3")
Spinbox5_3.configure(foreground="black")
Spinbox5_3.configure(highlightbackground="black")
Spinbox5_3.configure(highlightcolor="black")
Spinbox5_3.configure(insertbackground="black")
Spinbox5_3.configure(selectbackground="#c4c4c4")
Spinbox5_3.configure(selectforeground="black")
Spinbox5_3.configure(textvariable=substackYStart)

Spinbox5_4 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_4.place(relx=0.258, rely=0.788, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_4.configure(activebackground="#f9f9f9")
Spinbox5_4.configure(background="white")
Spinbox5_4.configure(buttonbackground="#d9d9d9")
Spinbox5_4.configure(disabledforeground="#a3a3a3")
Spinbox5_4.configure(foreground="black")
Spinbox5_4.configure(highlightbackground="black")
Spinbox5_4.configure(highlightcolor="black")
Spinbox5_4.configure(insertbackground="black")
Spinbox5_4.configure(selectbackground="#c4c4c4")
Spinbox5_4.configure(selectforeground="black")
Spinbox5_4.configure(textvariable=substackYEnd)

Spinbox5_5 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_5.place(relx=0.419, rely=0.667, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_5.configure(activebackground="#f9f9f9")
Spinbox5_5.configure(background="white")
Spinbox5_5.configure(buttonbackground="#d9d9d9")
Spinbox5_5.configure(disabledforeground="#a3a3a3")
Spinbox5_5.configure(foreground="black")
Spinbox5_5.configure(highlightbackground="black")
Spinbox5_5.configure(highlightcolor="black")
Spinbox5_5.configure(insertbackground="black")
Spinbox5_5.configure(selectbackground="#c4c4c4")
Spinbox5_5.configure(selectforeground="black")
Spinbox5_5.configure(textvariable=substackXStart)

Spinbox5_6 = Spinbox(frame_generalsettings, from_=0.0, to=9999999.0)
Spinbox5_6.place(relx=0.419, rely=0.788, relheight=0.115
        , relwidth=0.113, bordermode='ignore')
Spinbox5_6.configure(activebackground="#f9f9f9")
Spinbox5_6.configure(background="white")
Spinbox5_6.configure(buttonbackground="#d9d9d9")
Spinbox5_6.configure(disabledforeground="#a3a3a3")
Spinbox5_6.configure(foreground="black")
Spinbox5_6.configure(highlightbackground="black")
Spinbox5_6.configure(highlightcolor="black")
Spinbox5_6.configure(insertbackground="black")
Spinbox5_6.configure(selectbackground="#c4c4c4")
Spinbox5_6.configure(selectforeground="black")
Spinbox5_6.configure(textvariable=substackXEnd)

Button5_1 = Button(frame_generalsettings)
Button5_1.place(relx=0.613, rely=0.727, height=24, width=101
        , bordermode='ignore')
Button5_1.configure(activebackground="#ececec")
Button5_1.configure(activeforeground="#000000")
Button5_1.configure(background="#d9d9d9")
Button5_1.configure(disabledforeground="#a3a3a3")
Button5_1.configure(foreground="#000000")
Button5_1.configure(highlightbackground="#d9d9d9")
Button5_1.configure(highlightcolor="black")
Button5_1.configure(pady="0")
Button5_1.configure(text='''Manual selection''')
Button5_1.configure(command=SubstackManualSelection)

###########

frame_mainf = LabelFrame(root)
frame_mainf.place(relx=0.322, rely=0.45, relheight=0.207
        , relwidth=0.344)
frame_mainf.configure(relief='groove')
frame_mainf.configure(foreground="black")
frame_mainf.configure(text='''Main functions''')
frame_mainf.configure(background="#d9d9d9")
frame_mainf.configure(highlightbackground="#d9d9d9")
frame_mainf.configure(highlightcolor="black")
frame_mainf.configure(width=310)

ButtonMIP = Button(frame_mainf)
ButtonMIP.place(relx=0.065, rely=0.435, height=24, width=87
        , bordermode='ignore')
ButtonMIP.configure(activebackground="#ececec")
ButtonMIP.configure(activeforeground="#000000")
ButtonMIP.configure(background="#d9d9d9")
ButtonMIP.configure(disabledforeground="#a3a3a3")
ButtonMIP.configure(foreground="#000000")
ButtonMIP.configure(highlightbackground="#d9d9d9")
ButtonMIP.configure(highlightcolor="black")
ButtonMIP.configure(pady="0")
ButtonMIP.configure(text='''Generate MIP''')
ButtonMIP.configure(command=GenerateMIP)

ButtonPSF = Button(frame_mainf)
ButtonPSF.place(relx=0.419, rely=0.348, height=44, width=47
        , bordermode='ignore')
ButtonPSF.configure(activebackground="#ececec")
ButtonPSF.configure(activeforeground="#000000")
ButtonPSF.configure(background="#d9d9d9")
ButtonPSF.configure(disabledforeground="#a3a3a3")
ButtonPSF.configure(font=font9)
ButtonPSF.configure(foreground="#000000")
ButtonPSF.configure(highlightbackground="#d9d9d9")
ButtonPSF.configure(highlightcolor="black")
ButtonPSF.configure(pady="0")
ButtonPSF.configure(text='''PSF''')
ButtonPSF.configure(command=PSF_rec)

ButtonBeadsList = Button(frame_mainf)
ButtonBeadsList.place(relx=0.645, rely=0.435, height=24, width=90
        , bordermode='ignore')
ButtonBeadsList.configure(activebackground="#ececec")
ButtonBeadsList.configure(activeforeground="#000000")
ButtonBeadsList.configure(background="#d9d9d9")
ButtonBeadsList.configure(disabledforeground="#a3a3a3")
ButtonBeadsList.configure(foreground="#000000")
ButtonBeadsList.configure(highlightbackground="#d9d9d9")
ButtonBeadsList.configure(highlightcolor="black")
ButtonBeadsList.configure(pady="0")
ButtonBeadsList.configure(text='''Beads list''')
ButtonBeadsList.configure(command=PrintBeadsList)

###########

frame_singlebead = LabelFrame(root)
frame_singlebead.place(relx=0.322, rely=0.665, relheight=0.243
        , relwidth=0.344)
frame_singlebead.configure(relief='groove')
frame_singlebead.configure(foreground="black")
frame_singlebead.configure(text='''Analyze a single bead''')
frame_singlebead.configure(background="#d9d9d9")
frame_singlebead.configure(highlightbackground="#d9d9d9")
frame_singlebead.configure(highlightcolor="black")
frame_singlebead.configure(width=310)

Label3_1 = Label(frame_singlebead)
Label3_1.place(relx=0.194, rely=0.222, height=21, width=82
        , bordermode='ignore')
Label3_1.configure(activebackground="#f9f9f9")
Label3_1.configure(activeforeground="black")
Label3_1.configure(background="#d9d9d9")
Label3_1.configure(disabledforeground="#a3a3a3")
Label3_1.configure(foreground="#000000")
Label3_1.configure(highlightbackground="#d9d9d9")
Label3_1.configure(highlightcolor="black")
Label3_1.configure(text='''Coords (Z Y X)''')

Label3_2 = Label(frame_singlebead)
Label3_2.place(relx=0.097, rely=0.444, height=21, width=116
        , bordermode='ignore')
Label3_2.configure(activebackground="#f9f9f9")
Label3_2.configure(activeforeground="black")
Label3_2.configure(background="#d9d9d9")
Label3_2.configure(disabledforeground="#a3a3a3")
Label3_2.configure(foreground="#000000")
Label3_2.configure(highlightbackground="#d9d9d9")
Label3_2.configure(highlightcolor="black")
Label3_2.configure(text='''Pixel involved (Z Y X)''')

Spinbox3_1 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_1.place(relx=0.484, rely=0.222, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_1.configure(activebackground="#f9f9f9")
Spinbox3_1.configure(background="white")
Spinbox3_1.configure(buttonbackground="#d9d9d9")
Spinbox3_1.configure(disabledforeground="#a3a3a3")
Spinbox3_1.configure(foreground="black")
Spinbox3_1.configure(highlightbackground="black")
Spinbox3_1.configure(highlightcolor="black")
Spinbox3_1.configure(insertbackground="black")
Spinbox3_1.configure(selectbackground="#c4c4c4")
Spinbox3_1.configure(selectforeground="black")
Spinbox3_1.configure(textvariable=beadCoordZ)


Spinbox3_2 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_2.place(relx=0.645, rely=0.222, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_2.configure(activebackground="#f9f9f9")
Spinbox3_2.configure(background="white")
Spinbox3_2.configure(buttonbackground="#d9d9d9")
Spinbox3_2.configure(disabledforeground="#a3a3a3")
Spinbox3_2.configure(foreground="black")
Spinbox3_2.configure(highlightbackground="black")
Spinbox3_2.configure(highlightcolor="black")
Spinbox3_2.configure(insertbackground="black")
Spinbox3_2.configure(selectbackground="#c4c4c4")
Spinbox3_2.configure(selectforeground="black")
Spinbox3_2.configure(textvariable=beadCoordY)

Spinbox3_3 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_3.place(relx=0.806, rely=0.222, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_3.configure(activebackground="#f9f9f9")
Spinbox3_3.configure(background="white")
Spinbox3_3.configure(buttonbackground="#d9d9d9")
Spinbox3_3.configure(disabledforeground="#a3a3a3")
Spinbox3_3.configure(foreground="black")
Spinbox3_3.configure(highlightbackground="black")
Spinbox3_3.configure(highlightcolor="black")
Spinbox3_3.configure(insertbackground="black")
Spinbox3_3.configure(selectbackground="#c4c4c4")
Spinbox3_3.configure(selectforeground="black")
Spinbox3_3.configure(textvariable=beadCoordX)

Spinbox3_4 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_4.place(relx=0.484, rely=0.444, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_4.configure(activebackground="#f9f9f9")
Spinbox3_4.configure(background="white")
Spinbox3_4.configure(buttonbackground="#d9d9d9")
Spinbox3_4.configure(disabledforeground="#a3a3a3")
Spinbox3_4.configure(foreground="black")
Spinbox3_4.configure(highlightbackground="black")
Spinbox3_4.configure(highlightcolor="black")
Spinbox3_4.configure(insertbackground="black")
Spinbox3_4.configure(selectbackground="#c4c4c4")
Spinbox3_4.configure(selectforeground="black")
Spinbox3_4.configure(textvariable=pixelGaussZbead)

Spinbox3_5 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_5.place(relx=0.645, rely=0.444, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_5.configure(activebackground="#f9f9f9")
Spinbox3_5.configure(background="white")
Spinbox3_5.configure(buttonbackground="#d9d9d9")
Spinbox3_5.configure(disabledforeground="#a3a3a3")
Spinbox3_5.configure(foreground="black")
Spinbox3_5.configure(highlightbackground="black")
Spinbox3_5.configure(highlightcolor="black")
Spinbox3_5.configure(insertbackground="black")
Spinbox3_5.configure(selectbackground="#c4c4c4")
Spinbox3_5.configure(selectforeground="black")
Spinbox3_5.configure(textvariable=pixelGaussYbead)

Spinbox3_6 = Spinbox(frame_singlebead, from_=0.0, to=9999999.0)
Spinbox3_6.place(relx=0.806, rely=0.444, relheight=0.141
        , relwidth=0.145, bordermode='ignore')
Spinbox3_6.configure(activebackground="#f9f9f9")
Spinbox3_6.configure(background="white")
Spinbox3_6.configure(buttonbackground="#d9d9d9")
Spinbox3_6.configure(disabledforeground="#a3a3a3")
Spinbox3_6.configure(foreground="black")
Spinbox3_6.configure(highlightbackground="black")
Spinbox3_6.configure(highlightcolor="black")
Spinbox3_6.configure(insertbackground="black")
Spinbox3_6.configure(selectbackground="#c4c4c4")
Spinbox3_6.configure(selectforeground="black")
Spinbox3_6.configure(textvariable=pixelGaussXbead)

Button3_1 = Button(frame_singlebead)
Button3_1.place(relx=0.1, rely=0.741, height=24, width=67
        , bordermode='ignore')
Button3_1.configure(activebackground="#ececec")
Button3_1.configure(activeforeground="#000000")
Button3_1.configure(background="#d9d9d9")
Button3_1.configure(disabledforeground="#a3a3a3")
Button3_1.configure(foreground="#000000")
Button3_1.configure(highlightbackground="#d9d9d9")
Button3_1.configure(highlightcolor="black")
Button3_1.configure(pady="0")
Button3_1.configure(text='''Show''')
Button3_1.configure(command=ShowSingleBead)

Button3_2 = Button(frame_singlebead)
Button3_2.place(relx=0.41, rely=0.741, height=24, width=67
        , bordermode='ignore')
Button3_2.configure(activebackground="#ececec")
Button3_2.configure(activeforeground="#000000")
Button3_2.configure(background="#d9d9d9")
Button3_2.configure(disabledforeground="#a3a3a3")
Button3_2.configure(foreground="#000000")
Button3_2.configure(highlightbackground="#d9d9d9")
Button3_2.configure(highlightcolor="black")
Button3_2.configure(pady="0")
Button3_2.configure(text='''Analyze''')
Button3_2.configure(command=BeadPlot)

Checkbutton3_1 = Checkbutton(frame_singlebead)
Checkbutton3_1.place(relx=0.685, rely=0.741, relheight=0.152
        , relwidth=0.255, bordermode='ignore')
Checkbutton3_1.configure(activebackground="#ececec")
Checkbutton3_1.configure(activeforeground="#000000")
Checkbutton3_1.configure(background="#d9d9d9")
Checkbutton3_1.configure(disabledforeground="#a3a3a3")
Checkbutton3_1.configure(foreground="#000000")
Checkbutton3_1.configure(highlightbackground="#d9d9d9")
Checkbutton3_1.configure(highlightcolor="black")
Checkbutton3_1.configure(justify='left')
Checkbutton3_1.configure(text='''PSF plot''')
Checkbutton3_1.configure(variable=showSingleBeadPSFplot)



###########

Listbox1 = Listbox(root)
Listbox1.place(relx=0.678, rely=0.144, relheight=0.741
        , relwidth=0.304)
Listbox1.configure(background="white")
Listbox1.configure(disabledforeground="#a3a3a3")
Listbox1.configure(font=font15)
Listbox1.configure(foreground="#000000")
Listbox1.configure(highlightbackground="#d9d9d9")
Listbox1.configure(highlightcolor="black")
Listbox1.configure(selectbackground="#c4c4c4")
Listbox1.configure(selectforeground="black")
Listbox1.configure(width=274)

TextOutput = Label(root)
TextOutput.place(relx=0.789, rely=0.101, height=21, width=67)
TextOutput.configure(activebackground="#f9f9f9")
TextOutput.configure(activeforeground="black")
TextOutput.configure(background="#d9d9d9")
TextOutput.configure(disabledforeground="#a3a3a3")
TextOutput.configure(foreground="#000000")
TextOutput.configure(highlightbackground="#d9d9d9")
TextOutput.configure(highlightcolor="black")
TextOutput.configure(text='''Text output''')

SaveTxt = Button(root)
SaveTxt.place(relx=0.8, rely=0.899, height=24, width=67)
SaveTxt.configure(activebackground="#ececec")
SaveTxt.configure(activeforeground="#000000")
SaveTxt.configure(background="#d9d9d9")
SaveTxt.configure(disabledforeground="#a3a3a3")
SaveTxt.configure(foreground="#000000")
SaveTxt.configure(highlightbackground="#d9d9d9")
SaveTxt.configure(highlightcolor="black")
SaveTxt.configure(pady="0")
SaveTxt.configure(text='''Save (.txt)''')
SaveTxt.configure(command=Save_Results)

ClearListbox = Button(root)
ClearListbox.place(relx=0.889, rely=0.899, height=24, width=67)
ClearListbox.configure(activebackground="#ececec")
ClearListbox.configure(activeforeground="#000000")
ClearListbox.configure(background="#d9d9d9")
ClearListbox.configure(disabledforeground="#a3a3a3")
ClearListbox.configure(foreground="#000000")
ClearListbox.configure(highlightbackground="#d9d9d9")
ClearListbox.configure(highlightcolor="black")
ClearListbox.configure(pady="0")
ClearListbox.configure(text='''Clear''')
ClearListbox.configure(command= Clear_ListBox)

###########

TextPminmax = Label(root)
TextPminmax.place(relx=0.29, rely=0.931, height=21, width=267)
TextPminmax.configure(activebackground="#f9f9f9")
TextPminmax.configure(activeforeground="black")
TextPminmax.configure(background="#d9d9d9")
TextPminmax.configure(disabledforeground="#a3a3a3")
TextPminmax.configure(foreground="#000000")
TextPminmax.configure(highlightbackground="#d9d9d9")
TextPminmax.configure(highlightcolor="black")
TextPminmax.configure(text='''Pixel graphic range''')

PminEntry = Entry(root)
PminEntry.place(relx=0.505, rely=0.931, height=20, relwidth=0.04
        , bordermode='ignore')
PminEntry.configure(background="white")
PminEntry.configure(disabledforeground="#a3a3a3")
PminEntry.configure(font=font13)
PminEntry.configure(foreground="#000000")
PminEntry.configure(highlightbackground="#d9d9d9")
PminEntry.configure(highlightcolor="black")
PminEntry.configure(insertbackground="black")
PminEntry.configure(selectbackground="#c4c4c4")
PminEntry.configure(selectforeground="black")
PminEntry.configure(textvariable=pMin)

PmaxEntry = Entry(root)
PmaxEntry.place(relx=0.552, rely=0.931, height=20, relwidth=0.04
        , bordermode='ignore')
PmaxEntry.configure(background="white")
PmaxEntry.configure(disabledforeground="#a3a3a3")
PmaxEntry.configure(font=font13)
PmaxEntry.configure(foreground="#000000")
PmaxEntry.configure(highlightbackground="#d9d9d9")
PmaxEntry.configure(highlightcolor="black")
PmaxEntry.configure(insertbackground="black")
PmaxEntry.configure(selectbackground="#c4c4c4")
PmaxEntry.configure(selectforeground="black")
PmaxEntry.configure(textvariable=pMax)

#FINE GUI






root.mainloop()