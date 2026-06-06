import os
import numpy as np

class _Header:
    def __init__(self, path: str) -> None:
        self.path   = path
        with open(self.path) as f:
            self.contents = f.read()

        lines = self.contents.split("\n")[:-1]
        
        self.DTYPE              = lines[0].split(" ")[1]
        self.NMEMB              = int(lines[1].split(":")[1])
        self.NFILE              = int(lines[2].split(":")[1])

        self.filenames              = ()
        self.datalength_per_file    = np.zeros(len(lines)-3,dtype=int) 
        for i in range(3,len(lines)):
            self.filenames+=(lines[i].split(":")[0],)
            self.datalength_per_file[i-3]   = int(lines[i].split(":")[1])

        self.total_data_length         = sum(self.datalength_per_file)

class _BinaryFile:
    def __init__(self,path:str,dtype:np.dtype) -> None:
        self.path = path
        self.dtype = dtype

    def read(self):
        with open (self.path, mode='rb') as file:
            return np.fromfile(file,self.dtype)

def read_binary_file_with_numpy(path:str):
    header = _Header(os.path.join(path,"header"))

    data=np.zeros(header.total_data_length*header.NMEMB,dtype=header.DTYPE)
    for i in range(0,header.NFILE):
        filename = ("{:X}".format(i)).upper().rjust(6,'0')  
        file = _BinaryFile(os.path.join(path,filename),header.DTYPE)
        fill_start_index = sum(header.datalength_per_file[0:i])   * header.NMEMB
        fill_end_index   = sum(header.datalength_per_file[0:i+1]) * header.NMEMB
        data[fill_start_index:fill_end_index]=file.read()

    if header.NMEMB>1: data = data.reshape(header.total_data_length,header.NMEMB)
    
    return data



def read_binary_file_with_bigfile(blockdir: str):
    try:
        import bigfile
    except ImportError:
        raise ImportError(
            "To read data in the BigFile format, the 'bigfile' library is required. "
            "Install it with: pip install bigfile"
        )

    fieldname = os.path.basename(blockdir)
    partname = os.path.basename(os.path.abspath(os.path.join(blockdir, os.pardir))) + '/'
    snapdir = os.path.abspath(os.path.join(blockdir, os.pardir, os.pardir))
    f = bigfile.File(snapdir)
    data = bigfile.Dataset(f[partname], [fieldname])
    return data
