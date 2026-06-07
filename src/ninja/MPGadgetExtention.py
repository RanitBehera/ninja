import os
import numpy
import ninja.MPGadget as mpg


class _METALS:
    H = 0
    He = 1
    C = 2
    N = 3
    O = 4
    Ne = 5
    Mg = 6
    Si = 7
    Fe = 8
    LABELS = ['H', 'He', 'C', 'N', 'O', 'Ne', 'Mg', 'Si', 'Fe']


class _Units(mpg._Units):
    def print(self):
        CELL_WIDTH=16
        print("UNITS (in h=1)",'-'*32)
        print("-","Length".ljust(CELL_WIDTH),':',self.Length,"cm")
        print("-","Mass".ljust(CELL_WIDTH),':',self.Mass,"g")
        print("-","Velocity".ljust(CELL_WIDTH),':',self.Velocity,"cm/s")
        print("-","Density".ljust(CELL_WIDTH),':',self.Density,"g/cm3")
        print("-","Time".ljust(CELL_WIDTH),':',self.Time,"s")
        print("-","Energy".ljust(CELL_WIDTH),':',self.Energy)
        print("-","InternalEnergy".ljust(CELL_WIDTH),':',self.InternalEnergy)
        # CHECKED: the units match with stdout units when h=1


class _PARTHeader(mpg._PARTHeader):
    def __init__(self, path:str):
        super().__init__(path)
        self.Units      = _Units(self._header)


class _PIGHeader(mpg._PIGHeader):
    def __init__(self, path:str):
        super().__init__(path)
        self._COHEADER_WARNING_PRINTED = False
        
    @property
    def LinkedHeader(self):
        if "RPIG_" in self.path:
            linked_header_path = self.path.replace("RPIG","PART")
        elif "PIG_" in self.path:
            linked_header_path = self.path.replace("PIG","PART")

        if os.path.exists(linked_header_path):
            return _PARTHeader(linked_header_path)
        else:
            snap_path=os.path.abspath(self.path + "../../../../")
            avail_PART=[d for d in os.listdir(snap_path)
                        if d.startswith("PART_") and os.path.isdir(snap_path+os.sep+d)]



            coheader_path = snap_path + os.sep + avail_PART[0] + os.sep+ "Header/attr-v2"
            coheader = _PARTHeader(coheader_path)

            if not self._COHEADER_WARNING_PRINTED:
                print(f"Linked Header for PIG or RPIG : Corresponding PART header not found. Creating from Cosnapshot {avail_PART[0]}.")
                self._COHEADER_WARNING_PRINTED = True

            # Fix fields which are different from coheader
            coheader.Redshift=self.Redshift
            coheader.Time=self.Time
            coheader._header["TotNumPart"] = [None, None, None, None, None, None]

            return coheader
        

class _PART(mpg._PART):
    def __init__(self, path):
        super().__init__(path)
        self.Header = _PARTHeader(os.path.join(self.path,"Header/attr-v2"))

    def print_box_info(self,cell_width=16):
        print("- Simulation".ljust(cell_width),":",self.sim_name,flush=True)
        print("- Snapshot".ljust(cell_width),":",self.snap_name,flush=True)
        print("- Redshift".ljust(cell_width),":",f"{self.Header.Redshift():.02f}",flush=True)



class _PIG(mpg._PIG):
    def __init__(self, path):
        super().__init__(path)
        self.Header     = _PIGHeader(os.path.join(self.path,"Header/attr-v2"))

    def print_box_info(self,cell_width=16):
        print("- Simulation".ljust(cell_width),":", self.sim_name,flush=True)
        print("- Snapshot".ljust(cell_width),":", self.snap_name,flush=True)
        print("- Redshift".ljust(cell_width),":", f"{self.Header.Redshift():.02f}",flush=True)

    def GetParticleBlockNonMPI(self,ptype=None):
        # Calculates particle blocks to directly access the group chunk
        # This is faster then mask based filtering with GroupID
        lbt=self.FOFGroups.LengthByType().T
        cum_lbt=numpy.cumsum(lbt,axis=1)

        # offset so directly access with tgid indexing instead of off by one
        # This is because tgid starts with 1 based indexing
        zeros = numpy.zeros((cum_lbt.shape[0],1))
        block_start = numpy.int64(numpy.hstack((zeros,zeros,cum_lbt)))
        block_end = numpy.int64(numpy.hstack((zeros,cum_lbt,zeros)))

        if ptype is not None:
            block_start=block_start[ptype]
            block_end=block_end[ptype]

        return block_start,block_end



class _Sim(mpg._Folder):
    def __init__(self, simdir:str, snap_dir_name = "SNAPS"):
        super().__init__(simdir)
        self.snapdir = simdir + os.sep + snap_dir_name
        self.sim_name = os.path.basename(os.path.abspath(self.snapdir + "../../"))


    def SnapNumFromRedshift(self,redshift):
        # Get Snapnumbers and Scale Factors
        sn,a = numpy.loadtxt(self.snapdir+os.sep+"Snapshots.txt").T
        # Convert Snapnumbers type to "integer"
        sn = [int(sni) for sni in sn]
        # Convert Scale Factors to Redshifts
        z = (1/a)-1
        # Get indices where the difference between requested redshift and table row is less then tolerance
        _TOLERANCE = 0.001
        indices = numpy.array([i for i, zi in enumerate(z) if abs(zi - redshift) <= _TOLERANCE])

        if len(indices)==1:
            # If only one element --> requested redshift exists
            return sn[indices[0]]
        elif len(indices)==0:
            # If zero element --> requested redshift doesn't exists
            return None
        else:
            # If more than one element --> requested redshift appears twice, check it.
            RuntimeError("More than one box found. Try decereasing the tolerance or check for duplicate snaps.")
            return None

    def PART(self,snap_num:int=None,z:float=None):
        if snap_num is None:
            if z is None:raise ValueError("Either Snapnumber or Redshift is needed.")
            else:snap_num = self.SnapNumFromRedshift(z)

        if not isinstance(snap_num,int):raise TypeError
        return _PART(os.path.join(self.snapdir,f"PART_{snap_num:03}"))

    def PIG(self,snap_num:int=None,z:float=None,original=True):
        if original:
            if snap_num is None:
                if z is None:raise ValueError("Either Snapnumber or Redshift is needed.")
                else:snap_num = self.SnapNumFromRedshift(z)
            
            if not isinstance(snap_num,int):raise TypeError
            return _PIG(os.path.join(self.snapdir,f"PIG_{snap_num:03}"))
        else:
            return self.RPIG(snap_num,z)

    def RPIG(self,snap_num:int=None,z:float=None):
        if snap_num is None:
            if z is None:raise ValueError("Either Snapnumber or Redshift is needed.")
            else:snap_num = self.SnapNumFromRedshift(z)
            
        if not isinstance(snap_num,int):raise TypeError
        
        rpig_dir = os.path.join(self.snapdir,f"RPIG_{snap_num:03}")
        if os.path.exists(rpig_dir):
            return _PIG(rpig_dir)
        else:
            raise FileNotFoundError("RPIG is not Found. Makesure to create it. Otherwise use original=True")


from ninja import _SIM_NAME_HINTS
def Simulation(path:str=None,name:_SIM_NAME_HINTS=None) -> _Sim:
    if (path is None) and (name is None):
        raise ValueError("ERROR : Please provide either path or name of the simulation.")
    
    if (path is not None) and (name is not None):
        raise ValueError("ERROR : Both path and name are provided. Please provide only one of them.")
    
    if (name is not None) and (path is None):
        # Get simulation root path from system environment variable if present,
        # else use current working directory : "${cwd}/simulations"
        # User can create a symbolic link to the simulations folder in the current working directory for ease of use.
        sim_root = os.getenv("MPGADGET_SIM_ROOT", os.path.join(os.getcwd(),"simulations"))
        path = os.path.join(sim_root,name)

    if not os.path.exists(path):
        raise ValueError("ERROR : Path does not exist.",path)

    if not os.path.isdir(path):
        raise ValueError("ERROR : Path is not a directory.",path)

    return _Sim(path)













