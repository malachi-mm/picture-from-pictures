#!/usr/bin/env python
import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import cv2
import csv



#---------------------------------------------------

#this function get folder and check if it including pictures file (and return the names of the pictures and how much picture have)
def GetFolder():
    # Get the folder containin:g the images from the user
    folder = sg.popup_get_folder('Image folder to open', default_path='')
    if not folder:
        sg.popup_cancel('Cancelling')
        return 0, 0

    # PIL supported image types
    img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")
    
    # get list of files in folder
    flist0 = os.listdir(folder)
    
    # create sub list of image files (no sub folders, no wrong file types)
    fnames = [f for f in flist0 if os.path.isfile(
        os.path.join(folder, f)) and f.lower().endswith(img_types)]
    
    num_files = len(fnames)                # number of iamges found
    if num_files == 0:
        sg.popup('No files in folder')
        return 0, 0 # SystemExit()

    del flist0                             # no longer needed
    return folder, fnames



# ------------------------------------------------------------------------------
# use PIL to read data of one image
# ------------------------------------------------------------------------------
# the 2 next is actually the same, the first get image and the second get diraction
def get_img_data_im(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = f
    a = 1
    #resize the picture to be not too big
    if img.size[0] > 720:
        a = img.size[0]/720
    if img.size[1]/a > 520:
        a = img.size[1]/520
    #resizeing
    img = img.resize((int(img.size[0]/a),int(img.size[1]/a)), Image.ANTIALIAS)

    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    a = 1
    #resize the picture to be not too big
    if img.size[0] > 720:
        a = img.size[0]/720
    if img.size[1]/a > 520:
        a = img.size[1]/520
    #resizeing
    img = img.resize((int(img.size[0]/a),int(img.size[1]/a)), Image.ANTIALIAS)

    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)
# ------------------------------------------------------------------------------


def lookAtThePicture(folder,fnames,num_files):
    # make these 2 elements outside the layout as we want to "update" them later
    # initialize to the first file in the list
    filename = os.path.join(folder, fnames[0])  # name of first file in list
    image_elem = sg.Image(data=get_img_data(filename, first=True))
    filename_display_elem = sg.Text(filename, size=(80, 3))
    file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))
    
    # define layout, show and read the form
    col = [[filename_display_elem],
           [image_elem]]

    col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
                 [sg.Button('OK', size=(8, 2)),sg.Button('Cancel', size=(8, 2)), file_num_display_elem]]
    
    layout = [[sg.Column(col_files), sg.Column(col)]]
    
    window = sg.Window('Image Browser', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)
    
    # loop reading the user input and displaying image, filename
    i = 0
    while True:
        # read the form
        event, values = window.read()
        #print(event, values)
        # perform button and keyboard operations
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            return False #if not, we close the plane
        elif event == 'OK':
            window.close()
            return True #if it is good, we continue
        elif event in ('MouseWheel:Down', 'Down:40', 'Next:34'):
            i += 1
            if i >= num_files:
                i -= num_files
            filename = os.path.join(folder, fnames[i])
        elif event in ('MouseWheel:Up', 'Up:38', 'Prior:33'):
            i -= 1
            if i < 0:
                i = num_files + i
            filename = os.path.join(folder, fnames[i])
        elif event == 'listbox':            # something from the listbox
            f = values["listbox"][0]            # selected filename
            filename = os.path.join(folder, f)  # read this file
            i = fnames.index(f)                 # update running index
        else:
            filename = os.path.join(folder, fnames[i])
    
        # update window with new image
        image_elem.update(data=get_img_data(filename, first=True))
        # update window with filename
        filename_display_elem.update(filename)
        # update page display
        file_num_display_elem.update('File {} of {}'.format(i+1, num_files))

    window.close()
    return False


#-----------------------------------
def length(a,b): #help function for the last part
    return (a[0]-b[0])**2 +(a[1]-b[1])**2 +(a[2]-b[2])**2 

#-------------------------------------------------------------------------
#read the file of the picture and make new file with resizeing pictures (64x64)
#and it's write the avrage of every picture in csv file, this will be helpful in the last part
def smallData(folder, fnames):
    width = int(64)
    height = int(64)
    dim = (width, height) #the new size
    with open('avr.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'r','g','b']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)#write the header 
        
        writer.writeheader()
        for i in fnames:
            try: 
                img = Image.open(os.path.join(folder, i)) #read the picture
                
                #print(i),
                #print(img.size)
                img = img.resize((64,64), Image.ANTIALIAS) #resize 
                img.save('./small/'+i) #save in the new file

                #calculate avrage
                img2 = img.resize((1, 1), Image.ANTIALIAS) #make the picture to 1 pixel
                color = img2.getpixel((0, 0)) #get the pixel
                writer.writerow({'name': i, 'r': int(color[0]+0.5), 'g': int(color[1]+0.5), 'b': int(color[2]+0.5)}) #enter the pixel settings into the csv file

            except: #sometime picture is ilegali or can't reading
                print('oops')

#----------------------------------------------------
#if you play this once before you can use the small file again (so click 'YES'
#if not you need make one (so click 'NO'

layout = [[sg.Text('Hi, are you made a small data images?\n(if you don\'t know what I mean you need choose "NO")')],
                     [sg.Button('YES', size=(8, 2)), sg.Button('NO', size=(8, 2))]]
window1 = sg.Window('START',layout)
event, values = window1.read()
window1.close()
if event == 'NO': #if you need make new one
    folder, fnames = GetFolder() #take the place of the new data file from the user
    num_files = len(fnames)
    while not lookAtThePicture(folder,fnames,num_files): #the user can check the picture, if this good he click 'ok' and continue, else he can coose anthor one
        if(folder ==0):
            SystemExit()
            
        folder, fnames = GetFolder()
        num_files = len(fnames)

    smallData(folder,fnames) #make the small data file
        
elif event == sg.WIN_CLOSED:
    SystemExit()

#---- press YES (or finshe the first part)
Back = True
Targ = False
while Back:
    Back = False
    #choose the target picture
    event, TargetDir = sg.Window('My Script',
                        [[sg.Text('choose your target picture')],
                        [sg.In(), sg.FileBrowse()],
                        [sg.Open(), sg.Cancel()]]).read(close=True)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    imgTarget = Image.open(TargetDir[0])

    #make the window (image, slider and buttons)
    imageT = sg.Image(data=get_img_data(TargetDir[0], first=True))
    pixelsT = sg.Text('size: {} x {}'.format(imgTarget.size[0],imgTarget.size[1]))
    layout = [[imageT],
              [sg.Text('Slider Demonstration'), sg.Text('', key='_OUTPUT_')],  
                [sg.T('0',key='_LEFT_'),  
                 sg.Slider((1,100), key='_SLIDER_', orientation='h', enable_events=True, disable_number_display=True),  
                 sg.T('0', key='_RIGHT_')],  
                [sg.Button('OK'), sg.Button('Back'), pixelsT]]  

    #show the window
    window = sg.Window('Window Title', layout)  

    #this loop make how sharp you want the picture
    while True:             # Event Loop  
        event, values = window.read()  
        #print(event, values)
        #print(type(values['_SLIDER_']))
        
        image = Image.open(TargetDir[0])
        sizeT = image.size
        #make the picture become more or less sharp
        image = image.resize((int(image.size[0]/int(values['_SLIDER_'])),int(image.size[1]/int(values['_SLIDER_']))), Image.ANTIALIAS)
        pixelsT.update('size: {} x {}'.format(image.size[0],image.size[1])) #update the size
        imageH = image.resize(sizeT, Image.ANTIALIAS)
        imageT.update(data=get_img_data_im(imageH, first=True)) #update the image sharp
        
        if event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == 'OK': #if the user think that sharp enough, continue
            window.close()
            imgTarget = image
            print("a few seconds/minutes and we finished")
            Targ = True #if this true we can continue the last part
            break
        elif event == 'Back':
            window.close()
            Back = True #if this true you can choose anthor picture
            break
        window['_LEFT_'].update(values['_SLIDER_'])  
        window['_RIGHT_'].update(values['_SLIDER_'])  

window.close()

if Targ == True:
    names = []
    BGR = []

    #read the avrage from the cdv file
    with open('avr.csv') as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        header = next(csvReader)
        for row in csvReader:
            names.append(row[0])
            BGR.append([int(row[1]),int(row[2]),int(row[3]) , 0])


    os.chdir('./small')
    list_im = os.listdir()
    #print(imgTarget.size)
    new_im = Image.new('RGB', (imgTarget.size[0]*64,imgTarget.size[1]*64))

    #calaulte which picture's color is closer to spesific pixel
    for i in range(imgTarget.size[0]):
        for j in range(imgTarget.size[1]):
            pixel = imgTarget.getpixel((i,j))
            len_list = []
            for k in BGR:
                len_list.append(length(k,pixel))
    
            p = 0
            for n in range(len(len_list)):
                if(len_list[p] > len_list[n]):
                    p = n

            #paste the closest image in the place
            im = Image.open(names[p])
            new_im.paste(im, (i*64,j*64))
    
    
    os.chdir('..')

    #save the new picture
    new_im.save('target.jpg')

    #messeage where is the trget picture
    print(os.getcwd())
    sg.Window('Done',
                        [[sg.Text('Hi!, we finshied make your target,\n you can find your picture in:\n' + os.getcwd() + '/target.jpg')],
                        [sg.OK()]]).read(close=True)
    













    




