# SyntheticTurbulenceTest

## Generating the Mann box of turbulence
### Running HAWC2 to generate Mann box of turbulence 

Download the HAWC2 tool from here: https://www.hawc2.dk/download/pre-processing-tools   
* Choose the 64bit command-line version 2.0 (`mann_turb_x64.zip`)

### Inputs
The inputs to `mann_turb_x64.exe` are different than `windsimu`:
**`mann_turb_x64.exe` inputs**
```
Program     : C:\Users\lcheung\Documents\2020\IEA_Task29\mann_turb\mann_turb_x64.exe
Prefix      : test
Alfaeps     : 1.0
L           : 29.4
Gamma       : 3.0
Seed        : 1209
N_u         : 64
N_v         : 32
N_w         : 32
delta_u     : 2.0
delta_v     : 5
delta_w     : 5
HF comp     : true
```

**`windsimu` input file**
```
3  	    3D  field
3	    3 components
512	    N1
128	    N2
128	    N3
2560	    L1 meters
640	    L2 
640	    L3 
basic	    type
0.04	    alphaeps
35.38	    L
4	    Gamma
-5	    seed
sim09_1     name1
sim09_2	    name2
sim09_3	    name3
```

Translating between the two
```bat
C:\Users\lcheung\Documents\2020\IEA_Task29\mann_turb>mann_turb_x64.exe test 0.04 35.38 4.0 -5 512 128 128 5.0 5.0 5.0 true

-----------------------------------------
Mann_turb_x64 turbulence generation 64bit
DTU Wind Energy, 2014
www.hawc2.dk
-----------------------------------------
Program     : C:\Users\lcheung\Documents\2020\IEA_Task29\mann_turb\mann_turb_x64.exe
Prefix      : sim09
Alfaeps     : 0.04
L           : 35.38
Gamma       : 4.0
Seed        : -5
N_u         : 512
N_v         : 128
N_w         : 128
delta_u     : 5.0
delta_v     : 5.0
delta_w     : 5.0
HF comp     : true

Simulating turbulence ...
memsize100663296
Save turbulence boxes to disk
Finished
```

### Run `boxturb`
- Compile NaluWindUtils with `HYPRE` on:
  In `CMakeLists.txt`, set 
```cmake
option(ENABLE_HYPRE "Enable HYPRE solver interface" on)
```

```bash
$ ./boxturb -i boxturb.yaml
Nalu Turbulent File Processing Utility
Input file: boxturb.yaml
Begin loading WindSim turbulence data
	Loading file: sim09_u.bin
	Loading file: sim09_v.bin
	Loading file: sim09_w.bin
PFMG: Iters = 22; Rel. res. norm = 6.32687e-09
Begin output in NetCDF format: turbulence.nc
NetCDF file written successfully: turbulence.nc
```
