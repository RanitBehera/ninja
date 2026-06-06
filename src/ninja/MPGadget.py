import os
import numpy
import struct
from typing import Literal
import astropy.units as u
import ninja.DataReader as dr


class _Folder:
    def __init__(self,path:str) -> None:
        self.path = path
        self.name = os.path.basename(self.path)
        self.parent_path = os.path.abspath(os.path.join(path, os.pardir))

    def size(self,units:Literal["B","KB","MB","GB","TB"]="B"):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        units_power = {"KB":1,"MB":2,"GB":3,"TB":4}[units]
        total_size /= 1024**units_power
        
        return total_size


class _Node(_Folder):
    def __init__(self, path: str) -> None:
        super().__init__(path)

    def _print_field(self):
        field = self.name
        pdir = os.path.basename(os.path.dirname(self.path))
        print(f"- Reading : {pdir} > {field}")


    def Read(self,print_read:bool=False,use_bigfile:bool=False) -> numpy.ndarray:
        if print_read:
            self._print_field()

        if use_bigfile:
            return dr.read_binary_file_with_bigfile(self.path)
        else:
            return dr.read_binary_file_with_numpy(self.path)
        
    
    def __call__(self, print_read:bool=False, use_bigfile:bool=False) -> numpy.ndarray:
        return self.Read(print_read, use_bigfile)


class _NodeGroup(_Folder):
    def __init__(self,path):
        super().__init__(path)
    
    def AddNode(self,subdir_name) -> _Node:
        return _Node(os.path.join(self.path,subdir_name))


class _Gas(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)
        self.DelayTime                   = self.AddNode("DelayTime")
        self.Density                     = self.AddNode("Density")
        self.EgyWtDensity                = self.AddNode("EgyWtDensity")
        self.ElectronAbundance           = self.AddNode("ElectronAbundance")
        self.Generation                  = self.AddNode("Generation")
        self.GroupID                     = self.AddNode("GroupID")
        self.HeIIIIonized                = self.AddNode("HeIIIIonized")
        self.ID                          = self.AddNode("ID")
        self.InternalEnergy              = self.AddNode("InternalEnergy")
        self.Mass                        = self.AddNode("Mass")
        self.Metallicity                 = self.AddNode("Metallicity")
        self.Metals                      = self.AddNode("Metals")
        self.NeutralHydrogenFraction     = self.AddNode("NeutralHydrogenFraction")
        self.Position                    = self.AddNode("Position")
        self.Potential                   = self.AddNode("Potential")
        self.SmoothingLength             = self.AddNode("SmoothingLength")
        self.StarFormationRate           = self.AddNode("StarFormationRate")
        self.Velocity                    = self.AddNode("Velocity")


class _DarkMatter(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)
        self.GroupID                     = self.AddNode("GroupID")
        self.ID                          = self.AddNode("ID")
        self.Mass                        = self.AddNode("Mass")
        self.Position                    = self.AddNode("Position")
        self.Potential                   = self.AddNode("Potential")
        self.Velocity                    = self.AddNode("Velocity")


class _Neutrino(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)
        self.GroupID                     = self.AddNode("GroupID")
        self.ID                          = self.AddNode("ID")
        self.Mass                        = self.AddNode("Mass")
        self.Position                    = self.AddNode("Position")
        self.Potential                   = self.AddNode("Potential")
        self.Velocity                    = self.AddNode("Velocity")


class _Star(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)
        self.BirthDensity                = self.AddNode("BirthDensity")
        self.Generation                  = self.AddNode("Generation")
        self.GroupID                     = self.AddNode("GroupID")
        self.ID                          = self.AddNode("ID")
        self.LastEnrichmentMyr           = self.AddNode("LastEnrichmentMyr")
        self.Mass                        = self.AddNode("Mass")
        self.Metallicity                 = self.AddNode("Metallicity")
        self.Metals                      = self.AddNode("Metals")
        self.Position                    = self.AddNode("Position")
        self.Potential                   = self.AddNode("Potential")
        self.SmoothingLength             = self.AddNode("SmoothingLength")
        self.StarFormationTime           = self.AddNode("StarFormationTime")
        self.TotalMassReturned           = self.AddNode("TotalMassReturned")
        self.Velocity                    = self.AddNode("Velocity")


class _BlackHole(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)
        self.BlackholeAccretionRate      = self.AddNode("BlackholeAccretionRate")
        self.BlackholeDensity            = self.AddNode("BlackholeDensity")
        self.BlackholeJumpToMinPot       = self.AddNode("BlackholeJumpToMinPot")
        self.BlackholeKineticFdbkEnergy  = self.AddNode("BlackholeKineticFdbkEnergy")
        self.BlackholeMass               = self.AddNode("BlackholeMass")
        self.BlackholeMinPotPos          = self.AddNode("BlackholeMinPotPos")
        self.BlackholeMseed              = self.AddNode("BlackholeMseed")
        self.BlackholeMtrack             = self.AddNode("BlackholeMtrack")
        self.BlackholeProgenitors        = self.AddNode("BlackholeProgenitors")
        self.BlackholeSwallowID          = self.AddNode("BlackholeSwallowID")
        self.BlackholeSwallowTime        = self.AddNode("BlackholeSwallowTime")
        self.Generation                  = self.AddNode("Generation")
        self.GroupID                     = self.AddNode("GroupID")
        self.ID                          = self.AddNode("ID")
        self.Mass                        = self.AddNode("Mass")
        self.Position                    = self.AddNode("Position")
        self.Potential                   = self.AddNode("Potential")
        self.SmoothingLength             = self.AddNode("SmoothingLength")
        self.StarFormationTime           = self.AddNode("StarFormationTime")
        self.Swallowed                   = self.AddNode("Swallowed")
        self.Velocity                    = self.AddNode("Velocity")


class _FOFGroups(_NodeGroup):
    def __init__(self,path):
        super().__init__(path)

        self.BlackholeAccretionRate      = self.AddNode("BlackholeAccretionRate")
        self.BlackholeMass               = self.AddNode("BlackholeMass")
        self.FirstPos                    = self.AddNode("FirstPos")
        self.GasMetalElemMass            = self.AddNode("GasMetalElemMass")
        self.GasMetalMass                = self.AddNode("GasMetalMass")
        self.GroupID                     = self.AddNode("GroupID")
        self.Imom                        = self.AddNode("Imom")
        self.Jmom                        = self.AddNode("Jmom")
        self.LengthByType                = self.AddNode("LengthByType")
        self.Mass                        = self.AddNode("Mass")
        self.MassByType                  = self.AddNode("MassByType")
        self.MassCenterPosition          = self.AddNode("MassCenterPosition")
        self.MassCenterVelocity          = self.AddNode("MassCenterVelocity")
        self.MassHeIonized               = self.AddNode("MassHeIonized")
        self.MinID                       = self.AddNode("MinID")
        self.StarFormationRate           = self.AddNode("StarFormationRate")
        self.StellarMetalElemMass        = self.AddNode("StellarMetalElemMass")
        self.StellarMetalMass            = self.AddNode("StellarMetalMass")


class Attribute:
    def __init__(self,path:str) -> None:
        self.path = path

    def Read(self,plain_text:bool=False):
        with open(self.path) as f:
            attr_v2=f.read()
        if plain_text:
            return attr_v2
        struct_dtype_map={'i4':'i','i8':'q','u4':'I','u8':'Q','f4':'f','f8':'d','S1':'c',}
        attr_v2_dict={}
        for line in attr_v2.split("\n"):
            if line=="":continue
            chunks      = line.split(" ")
            key         = chunks[0]
            endianess   = chunks[1][0]
            dtype       = chunks[1][1:]
            length      = int(chunks[2])
            fmt = endianess + struct_dtype_map[dtype]*length
            val = list(struct.unpack(fmt,bytes.fromhex(chunks[3])))
            if dtype=='S1':val=b''.join(val)#.decode("utf-8")
            if length==1:val=val[0]
            attr_v2_dict[key]= val
        return attr_v2_dict


class _Units:
    def __init__(self,header:dict):
        # Units are in CGS with h=1
        self.Length             = header["UnitLength_in_cm"]*u.cm
        self.Mass               = header["UnitMass_in_g"]*u.g
        self.Velocity           = header["UnitVelocity_in_cm_per_s"] * u.cm / u.s
        self.Density            = self.Mass/(self.Length**3)
        self.Time               = self.Length/self.Velocity
        self.Energy             = self.Mass * (self.Velocity**2)
        self.InternalEnergy     = self.Energy/self.Mass
        self.StarFormationRate  = u.M_sun/u.yr 

        # SFR unit is Msun/Yr
        # sfr_params.UnitSfr_in_solar_per_year = (units.UnitMass_in_g / SOLAR_MASS) / (units.UnitTime_in_s / SEC_PER_YEAR);
        # SPHP(i).Sfr = dM /dtime * sfr_params.UnitSfr_in_solar_per_year; 
        # SIMPLE_PROPERTY_FOF(StarFormationRate, Sfr, float, 1)
        # MyFloat Sfr; /* Star formation rate in Msun/year.


class _PARTHeader:
    def __init__(self, path: str) -> None:
        self.path       = path
        self._header    = Attribute(self.path).Read()
        self.text       = Attribute(self.path).Read(plain_text=True)
        self.Units      = _Units(self._header)
        
    def BoxSize(self):                    return self._header["BoxSize"]
    def CMBTemperature(self):             return self._header["CMBTemperature"]
    def CodeVersion(self):                return self._header["CodeVersion"]
    def CompilerSettings(self):           return self._header["CompilerSettings"]
    def DensityKernel(self):              return self._header["DensityKernel"]
    def HubbleParam(self):                return self._header["HubbleParam"]
    def MassTable(self):                  return self._header["MassTable"]
    def Omega0(self):                     return self._header["Omega0"]
    def OmegaBaryon(self):                return self._header["OmegaBaryon"]
    def OmegaLambda(self):                return self._header["OmegaLambda"]
    def RSDFactor(self):                  return self._header["RSDFactor"]
    def Time(self):                       return self._header["Time"]
    def TimeIC(self):                     return self._header["TimeIC"]
    def TotNumPart(self):                 return self._header["TotNumPart"]
    def TotNumPartInit(self):             return self._header["TotNumPartInit"]
    def UnitLength_in_cm(self):           return self._header["UnitLength_in_cm"]
    def UnitMass_in_g(self):              return self._header["UnitMass_in_g"]
    def UnitVelocity_in_cm_per_s(self):   return self._header["UnitVelocity_in_cm_per_s"]
    def UsePeculiarVelocity(self):        return self._header["UsePeculiarVelocity"]
    # ----- Extra
    def Redshift(self):                   return (1/self.Time()) - 1

    def __call__(self):
        return self._header
    

class _PIGHeader:
    def __init__(self, path: str) -> None:
        self.path       = path
        self._header    = Attribute(self.path).Read()
        self.text       = Attribute(self.path).Read(plain_text=True)

    def BoxSize(self):                    return self._header["BoxSize"]
    def CMBTemperature(self):             return self._header["CMBTemperature"]
    def HubbleParam(self):                return self._header["HubbleParam"]
    def MassTable(self):                  return self._header["MassTable"]
    def NumFOFGroupsTotal(self):          return self._header["NumFOFGroupsTotal"]
    def NumPartInGroupTotal(self):        return self._header["NumPartInGroupTotal"]
    def Omega0(self):                     return self._header["Omega0"]
    def OmegaBaryon(self):                return self._header["OmegaBaryon"]
    def OmegaLambda(self):                return self._header["OmegaLambda"]
    def RSDFactor(self):                  return self._header["RSDFactor"]
    def Time(self):                       return self._header["Time"]
    def UsePeculiarVelocity(self):        return self._header["UsePeculiarVelocity"]
    # ----- Extra
    def Redshift(self):                   return (1/self.Time()) - 1

    def __call__(self):
        return self._header
    

class _PART(_Folder):
    def __init__(self,path):
        super().__init__(path)

        self.Gas        = _Gas(os.path.join(self.path,"0"))
        self.DarkMatter = _DarkMatter(os.path.join(self.path,"1"))
        self.Neutrino   = _Neutrino(os.path.join(self.path,"2"))
        self.Star       = _Star(os.path.join(self.path,"4"))
        self.BlackHole  = _BlackHole(os.path.join(self.path,"5"))

        self.Header     = _PARTHeader(os.path.join(self.path,"Header/attr-v2"))
        
        self.sim_name   = os.path.basename(os.path.abspath(self.path + "../../../"))
        self.snap_name  = os.path.basename(os.path.abspath(self.path))
        self.redshift_name  = f"z{self.Header.Redshift():.02f}".replace(".",'p')


class _PIG(_Folder):
    def __init__(self,path):
        super().__init__(path)

        self.Gas        = _Gas(os.path.join(self.path,"0"))
        self.DarkMatter = _DarkMatter(os.path.join(self.path,"1"))
        self.Neutrino   = _Neutrino(os.path.join(self.path,"2"))
        self.Star       = _Star(os.path.join(self.path,"4"))
        self.BlackHole  = _BlackHole(os.path.join(self.path,"5"))

        self.Header     = _PIGHeader(os.path.join(self.path,"Header/attr-v2"))
        self.FOFGroups  = _FOFGroups(os.path.join(self.path,"FOFGroups"))

        self.sim_name   = os.path.basename(os.path.abspath(self.path + "../../../"))
        self.snap_name  = os.path.basename(os.path.abspath(self.path))
        self.redshift_name  = f"z{self.Header.Redshift():.02f}".replace(".",'p')






