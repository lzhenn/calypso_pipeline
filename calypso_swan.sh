STRT_YMDH=$1
END_YMDH=$2
CALYPSO_PATH=$3
NTASKS=$4
ARCH_PATH=$5
NML_TMP=$6
INIT_RUN_FLAG=$7
NDOM=$8

echo ">>>>SWAN: Adjust files"
#cp ./domaindb/${NML_TMP}/* ${CALYPSO_PATH}/
if [ $INIT_RUN_FLAG == 1 ]; then
    cp ./db/${NML_TMP}/swan_d0* ${CALYPSO_PATH}/
else
    for IDOM in `seq 1 $NDOM`
    do
        cp ./db/${NML_TMP}/swan_d0${IDOM}.in.hot ${CALYPSO_PATH}/swan_d0${IDOM}.in
    done
fi

CMD=""
for IDOM in `seq 1 $NDOM`
do
    sed -i "s/ssyyyymmdd.hh/${STRT_YMDH}/g" ${CALYPSO_PATH}/swan_d0${IDOM}.in
    sed -i "s/eeyyyymmdd.hh/${END_YMDH}/g" ${CALYPSO_PATH}/swan_d0${IDOM}.in
    CMD=${CMD}" "${CALYPSO_PATH}"/swan_d0"${IDOM}".in"
done

# Calypso Root
CALYPSO_ROOT=${CALYPSO_PATH%Projects*}
cd ${CALYPSO_ROOT}
echo ">>>>SWAN: Run Calypso..."
mpirun -np ${NTASKS} ./coawstM ${CMD} >& calypso.log

echo ">>>>SWAN: Archive files"

if [ $INIT_RUN_FLAG == 1 ]; then
    cp *.hot-* ./spunup_restart/
fi
if [ ! -d "$ARCH_PATH" ]; then
    mkdir $ARCH_PATH
fi

mv ${CALYPSO_ROOT}/*mat ${ARCH_PATH}
mv ${CALYPSO_ROOT}/*nc ${ARCH_PATH}
mv ${CALYPSO_ROOT}/*TXT ${ARCH_PATH}
