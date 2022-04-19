STRT_YMDH=$1
END_YMDH=$2
CALYPSO_PATH=$3
NTASKS=$4
ARCH_PATH=$5
NML_TMP=$6
INIT_RUN_FLAG=$7
RST_LEADDAY=$8

RST_ROOT=/home/pathop/njord/data/restart/clps2/

RST_ROOT=/home/pathop/njord/data/restart/clps/
echo ">>>>SWAN: Adjust files"
NODELIST='nodelist.p1.fcst'
#cp ./domaindb/${NML_TMP}/* ${CALYPSO_PATH}/


WKSP_DIR=`pwd`
if [ $INIT_RUN_FLAG == 1 ]; then
    cp ./db/${NML_TMP}/swan_d01.in.hot ${CALYPSO_PATH}/swan_d01.in
else
    cp ./db/${NML_TMP}/swan_d01.in.hot ${CALYPSO_PATH}/swan_d01.in
fi
sed -i "s/ssyyyymmdd.hh/${STRT_YMDH}/g" ${CALYPSO_PATH}/swan_d01.in
sed -i "s/eeyyyymmdd.hh/${END_YMDH}/g" ${CALYPSO_PATH}/swan_d01.in

# Calypso Root
CALYPSO_ROOT=${CALYPSO_PATH%Projects*}
cp ./db/nodelist* ${CALYPSO_ROOT}

cd ${CALYPSO_ROOT}
if [ $INIT_RUN_FLAG == 1 ]; then
    rm -f *.hot-*
    mv ./spunup_restart/* ./
fi
echo ">>>>SWAN: Run Calypso..."
startTime_s=`date +%s`
mpirun -iface=ib0 -f ${NODELIST} -np ${NTASKS} ./coawstM ${CALYPSO_PATH}/swan_d01.in >& calypso.log
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]

ARCH_DATE=`basename ${ARCH_PATH}`
INIT_HR=${ARCH_DATE:8:2}
ARCH_DATE=${ARCH_DATE:0:8}
INIT_TS=$(date -d "${ARCH_DATE}" +%s)
CURR_TS=$(date -d "${STRT_YMDH:0:8}" +%s)
TIME_DELTA=`expr $CURR_TS - $INIT_TS`
TIME_DELTA=`expr $TIME_DELTA / 86400`


if [ $sumTime -gt 600 ]; then 
    echo ">>>>SWAN: Archive files"

    if [ $INIT_RUN_FLAG == 1 ]; then
        cp njord_init_d01.hot* ./spunup_restart/
    fi
    # archive day 1-n spunup restarts for future usage
    
    if [ $TIME_DELTA -lt 10 ]; then
        RST_DATE=`date -d "${STRT_YMDH:0:8} +1 day" +%Y%m%d`
        sh $WKSP_DIR/utils/collect_ocn_rst.sh $ARCH_DATE${INIT_HR} ${RST_DATE}${INIT_HR} ${CALYPSO_ROOT} $RST_ROOT
    fi


    if [ ! -d "$ARCH_PATH" ]; then
        mkdir $ARCH_PATH
    fi

    sleep 5
    mv ${CALYPSO_ROOT}/*mat ${ARCH_PATH}
    mv ${CALYPSO_ROOT}/*TXT ${ARCH_PATH}

    # clean outdated archived data
    CLEAN_DATE=`date -d "-30 days" "+%Y%m%d"`
    CLEAN_DIR=`dirname ${ARCH_PATH}`
    CLEAN_DIR=${CLEAN_DIR}/${CLEAN_DATE}${INIT_HR}
    rm -rf $CLEAN_DIR
    # clean outdated restart files
    CLEAN_DATE=`date -d "-5 days" "+%Y%m%d"`
    CLEAN_DIR=${RST_ROOT}/I${CLEAN_DATE}R*
    rm -rf $CLEAN_DIR

else
    echo $sumTime"s elapsed for 1-day run, unreasonable run time!"
    # try previous day init
    INI_DATE=`date -d "${STRT_YMDH:0:8} -${RST_LEADDAY} day" +%Y%m%d`
    sh $WKSP_DIR/utils/fetch_ocn_rst.sh ${INI_DATE}${INIT_HR} ${STRT_YMDH/./} ${CALYPSO_ROOT} $RST_ROOT
fi
