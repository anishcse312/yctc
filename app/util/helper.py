def getmimetype(filename):
    mimetypes = {'jpg':'images/jpeg',
                 'jpeg':'images/jpeg',
                 'png':'images/png',
                 'html':'text/html'}
    ext = filename.split('.')[1]
    return mimetypes[ext]