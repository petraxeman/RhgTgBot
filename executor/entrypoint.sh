#!bin/sh

WORKERS_COUNT=${WORKERS_COUNT:-1}
BIND_PORT=${BIND_PORT:-80}
ACCESS_LOGFILE=${ACCESS_LOGFILE:--}
ERROR_LOGFILE=${ERROR_LOGFILE:--}

echo "[INFO] Starting sx-assistent executor"
echo "[INFO] Selected ${WORKERS_COUNT} workers"
echo "[INFO] Selected ${BIND_PORT} port"
echo "[INFO] Selected ${ACCESS_LOGFILE} access logfile"
echo "[INFO] Selected ${ERROR_LOGFILE} error logfile"

exec hypercorn \
            --workers ${WORKERS_COUNT} \
            --bind 0.0.0.0:${BIND_PORT} \
            --access-logfile ${ACCESS_LOGFILE}
            --error_logfile ${ERROR_LOGFILE}
            main:app