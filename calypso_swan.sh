STRT_YMDH=$1
END_YMDH=$2
CALYPSO_PATH=$3
NTASKS=$4
ARCH_PATH=$5
NML_TMP=$6
INIT_RUN_FLAG=$7

echo ">>>>SWAN: Adjust files"
#cp ./domaindb/${NML_TMP}/* ${CALYPSO_PATH}/
if [ $INIT_RUN_FLAG == 1 ]; then
    cp ./db/${NML_TMP}/swan_d01.in ${CALYPSO_PATH}/swan_d01.in
else
    cp ./db/${NML_TMP}/swan_d01.in.hot ${CALYPSO_PATH}/swan_d01.in
fi

sed -i "s/ssyyyymmdd.hh/${STRT_YMDH}/g" ${CALYPSO_PATH}/swan_d01.in
sed -i "s/eeyyyymmdd.hh/${END_YMDH}/g" ${CALYPSO_PATH}/swan_d01.in

# Calypso Root
CALYPSO_ROOT=${CALYPSO_PATH%Projects*}
cd ${CALYPSO_ROOT}
echo ">>>>SWAN: Run Calypso..."
mpirun -np ${NTASKS} ./coawstM ${CALYPSO_PATH}/swan_d01.in >& calypso.log

echo ">>>>SWAN: Archive files"

if [ $INIT_RUN_FLAG == 1 ]; then
    cp calypso.hot* ./spunup_restart/
fi
if [ ! -d "$ARCH_PATH" ]; then
    mkdir $ARCH_PATH
fi

mv ${CALYPSO_ROOT}/*mat ${ARCH_PATH}
mv ${CALYPSO_ROOT}/*TXT ${ARCH_PATH}
