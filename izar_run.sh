casename=$1
module load nvhpc
python prc/wireles.py clean $casename
python prc/wireles.py pre $casename
python prc/wireles.py solve $casename

