#!/bin/sh 
#

allgroups='l_h1 l_h2 l_h3 l_h4 l_h5 l_h6 l_h7 l_h8 l_h9 l_v2 l_v3 l_v4 l_v5 l_v6 l_v7 l_v8 l_v9'

for group in $allgroups; do
    python ../../utilities/extractLineTimeSeries.py -g $group post_processing/sampling00000.nc -o 'spectra/%s_%05i.dat'
done
