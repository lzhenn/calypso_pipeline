STRT_YMDH=$1
END_YMDH=$2
CALYPSO_PATH=$3
NTASKS=$4
ARCH_PATH=$5
NML_TMP=$6
INIT_RUN_FLAG=$7
NDOM=$8 # e.g. d01
RST_LEADDAY=$9
RST_ROOT=$ARCH_PATH

echo ">>>>SWAN: Adjust files"
NODELIST='nodelist.p1.fcst'
if [ ! -d "$CALYPSO_PATH" ]; then
    mkdir $CALYPSO_PATH
fi

cp ./domaindb/${NML_TMP}/* ${CALYPSO_PATH}/

WKSP_DIR=`pwd`
cp ./db/${NML_TMP}/swan_d0* ${CALYPSO_PATH}/
if [ $INIT_RUN_FLAG == 0 ]; then
    sed -i "s/&INITIAL/INITIAL/g" ${CALYPSO_PATH}/swan_${NDOM}.in
fi

CMD=""
sed -i "s/ssyyyymmdd.hh/${STRT_YMDH}/g" ${CALYPSO_PATH}/swan_${NDOM}.in
sed -i "s/eeyyyymmdd.hh/${END_YMDH}/g" ${CALYPSO_PATH}/swan_${NDOM}.in
CMD=${CALYPSO_PATH}"/swan_"${NDOM}".in"
#CMD=${CMD}" "${CALYPSO_PATH}"/swan_d0"${IDOM}".in"

# Calypso Root
CALYPSO_ROOT=${CALYPSO_PATH%Projects*}

cd ${CALYPSO_ROOT}
#if [ $INIT_RUN_FLAG == 1 ]; then
#    rm -f *.hot-*
#fi
echo ">>>>SWAN: Run Calypso..."
echo ${CMD}
startTime_s=`date +%s`
mpirun -np ${NTASKS} ./coawstM ${CMD} >& calypso.log
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]
ARCH_DATE=`basename ${ARCH_PATH}`
INIT_HR=${ARCH_DATE:8:2}
ARCH_DATE=${ARCH_DATE:0:8}
INIT_TS=$(date -d "${ARCH_DATE}" +%s)
CURR_TS=$(date -d "${STRT_YMDH:0:8}" +%s)
TIME_DELTA=`expr $CURR_TS - $INIT_TS`
TIME_DELTA=`expr $TIME_DELTA / 86400`

if [ $sumTime -gt 60 ]; then 
    echo ">>>>SWAN: Archive files"
    # archive day 1-n spunup restarts for future usage
    
    if [ $TIME_DELTA -lt 10 ]; then
        RST_DATE=`date -d "${STRT_YMDH:0:8} +1 day" +%Y%m%d`
        sh $WKSP_DIR/utils/collect_ocn_rst.sh $ARCH_DATE${INIT_HR} ${RST_DATE}${INIT_HR} ${CALYPSO_ROOT} $RST_ROOT
    fi

    if [ ! -d "$ARCH_PATH" ]; then
        mkdir $ARCH_PATH
    fi

    sleep 5

    #mv ${CALYPSO_ROOT}/d02bdy* ${ARCH_PATH}
    mv ${CALYPSO_ROOT}/*mat ${ARCH_PATH}
    mv ${CALYPSO_ROOT}/*nc ${ARCH_PATH}
    mv ${CALYPSO_ROOT}/*TXT ${ARCH_PATH}
    echo "Archive Path:"$ARCH_PATH
else
    echo $sumTime"s elapsed for 1-day run, unreasonable run time! Resubmit after 5s"
    exit 1 # not used for hindcast run
    sleep 5
    # try previous day init
    INI_DATE=`date -d "${STRT_YMDH:0:8} -${RST_LEADDAY} day" +%Y%m%d`
    sh $WKSP_DIR/utils/fetch_ocn_rst.sh ${INI_DATE}${INIT_HR} ${STRT_YMDH/./} ${CALYPSO_ROOT} $RST_ROOT
fi
