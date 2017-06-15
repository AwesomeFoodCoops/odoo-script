# this script is launched every 5 minutes by a system cron
#*/5 * * * * bash /home/louve-erp-dev/reload_if_down.sh >> /home/louve-erp-dev/reload_if_down.log

USER=$(whoami)
##########

PIDFILE=/home/$USER/init.d/odoo-server.pid
OFF_MODE_FILE=/home/$USER/odoo_auto_reload_OFF
checkrunning() {
    RESULT=$(wget --no-check-certificate -q -O- https://gestion-dev.cooplalouve.fr/web/login | grep -c Odoo)
    echo "$RESULT"
    return $RESULT
}

echo "$(date +%Y%m%d_%H%M%S) ====== Auto-starting Odoo scrit ======"
echo "$(date +%Y%m%d_%H%M%S) ====== Run by $USER ======"

if [ -f $OFF_MODE_FILE ];then
   echo "$(date +%Y%m%d_%H%M%S) OFF mode activated. Exiting"
   exit 0
fi

if checkrunning; then
    echo "Auto-restart of Odoo service by $USER at $(date +%Y%m%d_%H%M%S)." | mail -s "Odoo restarted by $USER" "dsi.erp@cooplalouve.fr"
    echo "$(date +%Y%m%d_%H%M%S) Starting odoo"
    /home/$USER/init.d/odoo-server start
    echo "$(date +%Y%m%d_%H%M%S) Odoo is now running."

else
    echo "$(date +%Y%m%d_%H%M%S) No need to sart oddo. Already running."
fi
