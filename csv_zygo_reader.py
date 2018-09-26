def csvZygo_reader(wfile,intensity=False,header=False,*args,**kwargs):
    """read .csv zygo files, returns data,x,y.
    
    Height map is returned unless intensity is set to True to return Intensity map in same format.
    If header is set, return header.
    
    Vincenzo Cotroneo 2018 vcotroneo@cfa.harvard.edu
    """
    
    with open(wfile) as myfile:
        raw = myfile.readlines()
       
    head,d=raw[:15],raw[15:]
    if header: return head

    nx,ny = list(map( int , head[8].split()[:2] )) 
    # coordinates of the origin of the
    #connected phase data matrix. They refer to positions in the camera coordinate system.
    #The origin of the camera coordinate system (0,0) is located in the upper left corner of the
    #video monitor.     
    origin = list(map(int,head[3].split()[:2]))  
    
    #These integers are the width (columns) and height (rows)
    #of the connected phase data matrix. If no phase data is present, these values are zero.
    connected_size=list(map(int,head[3].split()[2:4]))
    
    #This real number is the interferometric scale factor. It is the number of
    # waves per fringe as specified by the user
    IntfScaleFactor=float(head[7].split()[1])
    
    #This real number is the wavelength, in meters, at which the interferogram was measured.
    WavelengthIn=float(head[7].split()[2])
    
    #This integer indicates the sign of the data. The data sign may be normal (0) or
    #inverted (1).
    DataSign = int(head[10].split()[7])
    #This real number is a phase correction factor required when using a
    #Mirau objective on a microscope. A value of 1.0 indicates no correction factor was
    #required. 
    Obliquity = float(head[7].split()[4])
    
    #This integer indicates the resolution of the phase data points. A value of 0
    #indicates normal resolution, with each fringe represented by 4096 counts. A value of 1
    #indicates high resolution, with each fringe represented by 32768 counts.
    phaseres = int(head[10].split()[0])
    if phaseres==0:
        R = 4096
    elif phaseres==1:
        R = 32768
    else:
        raise ValueError
    
    #This real number is the lateral resolving power of a camera pixel in
    #meters/pixel. A value of 0 means that the value is unknown
    CameraRes = float(head[7].split()[6])
    if CameraRes==0:
        CameraRes=1.

    #pdb.set_trace()
    ypix=kwargs.pop('ypix',CameraRes)
    ytox=kwargs.pop('ytox',1.)
    zscale=kwargs.pop('zscale',WavelengthIn*1000000.)#original unit is m, convert to um
    
    datasets=[np.array(aa.split(),dtype=int)  for aa in ' '.join(map(str.strip,d)).split('#')[:-1]]
    #here rough test to plot things
    d1,d2=datasets  #d1 intensity, d2 phase
    d1,d2=d1.astype(float).reshape(ny,nx),d2.astype(float).reshape(*connected_size[::-1])
    d1[d1>65535]=np.nan
    d2[d2>=2147483640]=np.nan
    d2=d2*IntfScaleFactor*Obliquity/R*zscale #in um
    
    dd2=d1*np.nan #d1 is same size as sensor
    dd2[origin[1]:origin[1]+connected_size[1],origin[0]:origin[0]+connected_size[0]]=d2
    d2=dd2

    #this defines the position of row/columns, starting from
    x=np.arange(nx)*ypix*ytox*nx/(nx-1)
    y=np.arange(ny)*ypix*ny/(ny-1)   
    
    return  (d1,x,y) if intensity else (d2,x,y)   