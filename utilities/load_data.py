import netCDF4 as nc
from pathlib import Path
import numpy as np
import sys
sys.path.append('../utilities')
import windspectra

class AmrWindData:

  def __init__(self, casedir):
    try:
      self.read_amrwind_spectra(casedir)
    except:
      self.process_amrwind_spectra(casedir)
      self.read_amrwind_spectra(casedir)

  def read_amrwind_spectra(self, casedir):
    with nc.Dataset(casedir+'/avg_spectra.nc') as a:
      self.f = a['f'][:]
      self.xloc = a['xloc'][:]
      self.suu = a['suu'][:,:]
      self.svv = a['svv'][:,:]
      self.sww = a['sww'][:,:]

  def process_amrwind_spectra(self, casedir):
    self.Suu_avg = {}
    self.Svv_avg = {}
    self.Sww_avg = {}
    self.favg = {}
    nm80_dia = 80.0
    with nc.Dataset(casedir+'/sampling00000.nc') as a:
      tvec = a['time'][:]
      s_groups = list(a.groups.keys())
      num_points = a['l_h1'].dimensions['num_points'].size
      xlocations = (a['l_h1']['coordinates'][:,0] - a['l_h1']['coordinates'][0,0])/nm80_dia
      nx = np.size(xlocations)
      f,suu = windspectra.getWindSpectra(tvec[1:], a[s_groups[0]]['velocityx'][1:,0])
      Nband_avg = 3
      favg, suu_avg = windspectra.NarrowToOctaveBand(f, suu, Nband_avg)
      nfreq = np.size(favg)

      with nc.Dataset(casedir+'/avg_spectra.nc',mode='w',format='NETCDF3_CLASSIC') as d:
        d.createDimension("nx", nx)
        d.createDimension("nfreq", nfreq)
        nc_f = d.createVariable("f","f8",("nfreq",))
        nc_xloc = d.createVariable("xloc","f8","nx")
        nc_suu = d.createVariable("suu","f8",("nx","nfreq"))
        nc_svv = d.createVariable("svv","f8",("nx","nfreq"))
        nc_sww = d.createVariable("sww","f8",("nx","nfreq"))
        nc_f[:] = favg
        nc_xloc[:] = xlocations
        for i_x, x in enumerate(xlocations):
          print('x = %f'%x)
          suu = np.average([ windspectra.getWindSpectra(tvec[1:], a[g]['velocityx'][1:,i_x])[1] for g in s_groups ], 0)
          favg, suu_avg = windspectra.NarrowToOctaveBand(f, suu, Nband_avg)
          nc_suu[i_x,:] = suu_avg
          svv = np.average([ windspectra.getWindSpectra(tvec[1:], a[g]['velocityy'][1:,i_x])[1] for g in s_groups ], 0)
          favg, svv_avg = windspectra.NarrowToOctaveBand(f, svv, Nband_avg)
          nc_svv[i_x,:] = svv_avg
          sww = np.average([ windspectra.getWindSpectra(tvec[1:], a[g]['velocityz'][1:,i_x])[1] for g in s_groups ], 0)
          favg, sww_avg = windspectra.NarrowToOctaveBand(f, sww, Nband_avg)
          nc_sww[i_x,:] = sww_avg

class MannTurbData:

  def __init__(self,casedir):
    try:
      self.read_mann_turb_spectra(casedir)
    except:
      self.process_mann_turb_spectra(casedir)
      self.read_mann_turb_spectra(casedir)

  def read_mann_turb_spectra(self, casedir):
    with nc.Dataset(casedir+'/avg_spectra.nc') as a:
      self.f = a['f'][:]
      self.suu = a['suu'][:]
      self.svv = a['svv'][:]
      self.sww = a['sww'][:]


  def process_mann_turb_spectra(self, casedir):
    ncbox={}
    with nc.Dataset(casedir+'/turbulence.nc') as d:
      #print(d.variables)
      ncbox['ndim'] = d.dimensions['ndim'].size
      ncbox['nx']   = d.dimensions['nx'].size
      ncbox['ny']   = d.dimensions['ny'].size
      ncbox['nz']   = d.dimensions['nz'].size
      ncbox['L']    = d.variables['box_lengths'][:]
      ncbox['dx']   = d.variables['dx'][:]
      ncbox['uvel'] = d.variables['uvel'][:,:,:]
      ncbox['vvel'] = d.variables['vvel'][:,:,:]
      ncbox['wvel'] = d.variables['wvel'][:,:,:]

    # Get the timei vector
    Uavg = 10.0
    tvec = ncbox['dx'][0]/Uavg*np.arange(ncbox['nx'])

    # Set the scaling factors
    ds=5.0
    eps=2.5 #2*ds
    gaussScale = np.sqrt(1.0/(eps*np.sqrt(np.pi)*ds))

    # Average over the entire inlet plane of turbulence
    Suu = []
    Svv = []
    Sww = []
    itotal = 0
    print("Working...")
    for i in range(ncbox['ny']):
        sys.stdout.write("\r%d%%" % int(i*100.0/ncbox['ny']))
        sys.stdout.flush()
        for j in range(ncbox['nz']):
            f, tSuu = windspectra.getWindSpectra(tvec, ncbox['uvel'][:,i,j])
            f, tSvv = windspectra.getWindSpectra(tvec, ncbox['vvel'][:,i,j])
            f, tSww = windspectra.getWindSpectra(tvec, ncbox['wvel'][:,i,j])
            Suu = tSuu if len(Suu) == 0 else Suu + tSuu
            Svv = tSuu if len(Svv) == 0 else Svv + tSvv
            Sww = tSuu if len(Sww) == 0 else Sww + tSww
            itotal += 1
    Suu = Suu/float(itotal)
    Svv = Svv/float(itotal)
    Sww = Sww/float(itotal)
    print("")
    print("Done.")

    # Octave band average
    Nband=3
    Mannf, MannSuu = windspectra.NarrowToOctaveBand(f, Suu, Nband)
    Mannf, MannSvv = windspectra.NarrowToOctaveBand(f, Svv, Nband)
    Mannf, MannSww = windspectra.NarrowToOctaveBand(f, Sww, Nband)

    with nc.Dataset(casedir+'/avg_spectra.nc',mode='w',format='NETCDF3_CLASSIC') as d:
      d.createDimension("nfreq",np.size(Mannf))
      nc_f = d.createVariable("f","f8",("nfreq"))
      nc_suu = d.createVariable("suu","f8",("nfreq"))
      nc_svv = d.createVariable("svv","f8",("nfreq"))
      nc_sww = d.createVariable("sww","f8",("nfreq"))
      nc_f[:] = Mannf
      nc_suu[:] = MannSuu
      nc_svv[:] = MannSvv
      nc_sww[:] = MannSww

