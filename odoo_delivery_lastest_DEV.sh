#!/bin/sh

## Script d'installation/montée de version des source LaLouve
## Fait avec amour par Alexandre Pollet (SMILE) et mise à jour avec tendresse par Aurélien DUMAINE

VERT="\\033[1;32m"
NORMAL="\\033[0;39m"
ROUGE="\\033[1;31m"
ROSE="\\033[1;35m"
BLEU="\\033[1;34m"
BLANC="\\033[0;02m"
BLANCLAIR="\\033[1;08m"
JAUNE="\\033[1;33m"
CYAN="\\033[1;36m"

SOURCES_PATH=/home/$USER/sources
CURRENT_PATH=$SOURCES_PATH/current
GIT_BRANCH_URL=https://github.com/AwesomeFoodCoops/odoo-production
GIT_BRANCH="dev"
BDD_TO_UPDATE=$1

OFF_MODE_FILE=/home/$USER/odoo_auto_reload_OFF

echo
echo "$JAUNE" "Positionner le fichier OFF pour empecher le script automatique de lancement d'Odoo s'il est éteint (execution toutes les cinq minutes)" "$NORMAL"
echo
touch $OFF_MODE_FILE



if [ $# -eq 0 ];then
    BDD_TO_UPDATE=louve-erp-dev_$(date +%Y%m%d_%H%M%S)
    #CREATE THE DB
    echo '{"name": "'$BDD_TO_UPDATE'", "type":"POSTGRESQL"}' | curl -d @- --basic --user 774e5440d1f84b379e7ee56a73fb0436: https://api.alwaysdata.com/v1/database/
    echo "$ROUGE" "Aucun nom de base de donné passé en argument : la base de donnée suivante a été créée $BDD_TO_UPDATE" "$NORMAL"
    YESTERDAY=$(date --date yesterday +%Y_%m_%d) 
    lftp ftp://cooplalo:xmTYCwfG@ftp.cooplalouve.fr -e "GET -O /tmp/ /backup-odoo/"$YESTERDAY"__04_10_01/backup_"$YESTERDAY"__04_10_01.dump; quit"
    sleep 3
    CIBLE="/tmp/backup_"$YESTERDAY"__04_10_01.dump"
    pg_restore --no-owner -d $BDD_TO_UPDATE $CIBLE
    rm $CIBLE
fi

echo
echo "$JAUNE" "Arret Odoo" "$NORMAL"
echo
#TODO : handle PID in a more robust way
/home/$USER/init.d/odoo-server stop

echo
echo "$VERT" "...OK" "$NORMAL"
echo


echo
echo "$JAUNE" "Installation des dernieres sources et montée de version Odoo" "$NORMAL"
echo



if [ ! -e "$SOURCES_PATH" ]; then
	mkdir $SOURCES_PATH
fi


if [ -e "$CURRENT_PATH" ]; then
	SAVE_PATH=$SOURCES_PATH/save_current_$(date +%Y%m%d_%H%M%S)
	echo
	echo "$JAUNE" "Sauvegarde anciennes sources vers $SAVE_PATH" "$NORMAL"
	echo
	mv $CURRENT_PATH $SAVE_PATH
	##tar -zcf $SAVE_PATH.tar.gz $SAVE_PATH
fi

echo
echo "$VERT" "...OK" "$NORMAL"
echo

cd $SOURCES_PATH

echo
echo "$JAUNE" "Récupération des sources..." "$NORMAL"
echo "$ROUGE" "Récupération de la branche dev." "$NORMAL"
echo

wget $GIT_BRANCH_URL/archive/$GIT_BRANCH.zip

echo
echo "$VERT" "...OK" "$NORMAL"
echo

echo
echo "$JAUNE" "Decompression des sources..." "$NORMAL"
echo

unzip -q $GIT_BRANCH.zip
DIRNAME=`basename "$GIT_BRANCH_URL"`

mv "$DIRNAME-$GIT_BRANCH" current
rm $GIT_BRANCH.zip

echo
echo "$VERT" "...OK" "$NORMAL"
echo

echo
echo "$JAUNE" "Désactivation de tous les cron dans la base Odoo..." "$NORMAL"
echo
echo "psql -d $BDD_TO_UPDATE -c update ir_cron set active = False;"
psql -d $BDD_TO_UPDATE -c "update ir_cron set active = False;"

echo
echo "$VERT" "...OK" "$NORMAL"
echo

echo
echo "$JAUNE" "Contextualisation des paramètres systèmes dans la  base Odoo..." "$NORMAL"
echo
psql -d $BDD_TO_UPDATE -c "UPDATE ir_config_parameter SET value='https://gestion-dev.cooplalouve.fr' WHERE key='report.url';"
psql -d $BDD_TO_UPDATE -c "UPDATE ir_config_parameter SET value='https://gestion-dev.cooplalouve.fr' WHERE key='web.base.url';"
psql -d $BDD_TO_UPDATE -c "UPDATE ir_config_parameter SET value='https://gestion-dev.cooplalouve.fr' WHERE key='mail.catchall.domain';"
psql -d $BDD_TO_UPDATE -c "UPDATE res_users SET write_date='2017-04-17 11:21:45.31996', password_crypt='$pbkdf2-sha512$19000$B6D0vpcSghDCOMeYcw5ByA$BEWEvWK9oRL2ioIhbTdsfZeG39xqdpszmPpbTCVUI13xWhuzJVQec/luQ7qBbox1lOIqFXJD00ZzstD/CC6Ajw' WHERE login='ESPACE_MEMBRES';"
#password N5Z4HayJ2p8e3t3T

# Desactivate In and Out mail servers
psql -d $BDD_TO_UPDATE -c "UPDATE ir_mail_server SET active='FALSE';"
psql -d $BDD_TO_UPDATE -c "UPDATE fetchmail_server SET active='FALSE';"

echo
echo "$VERT" "...OK" "$NORMAL"
echo

#TODO :
#=> delete all session files from filestore and desactivate all users (and reactivate then at the end of the current script

echo
echo "$JAUNE" "Lancement en mode UPGRADE..." "$NORMAL"
echo
. /home/$USER/sources/current/upgrade_module_list 
echo "Modules à mettre à jour : $MODULE_LIST_TO_UPGRADE"
/home/$USER/louvenv/bin/python $CURRENT_PATH/odoo/openerp-server -c /home/$USER/odoo_conf/openerp-server-upgrade.conf -d $BDD_TO_UPDATE -u "$MODULE_LIST_TO_UPGRADE" --stop-after-init
echo ""
echo "================"
echo ""
echo "Modules à installer : $MODULE_LIST_TO_INSTALL"
/home/$USER/louvenv/bin/python $CURRENT_PATH/odoo/openerp-server -c /home/$USER/odoo_conf/openerp-server-upgrade.conf -d $BDD_TO_UPDATE -i "$MODULE_LIST_TO_INSTALL" --stop-after-init
#TODO : extend this mecanism to MODULE_LIST_TO_UNINSTALL ?
#TODO : extend this mecanism to one-shot migration scripts ?
#TODO : extend this mecanism to cooperative specific modules ?

echo
echo "$VERT" "...OK" "$NORMAL"
echo

echo
echo "$JAUNE" "Redemarrage Odoo en mode PROD" "$NORMAL"
echo

/home/$USER/init.d/odoo-server start

echo
echo "$VERT" "...OK" "$NORMAL"
echo


#TODO : 
#=> ask for restoring file store
#=> ask for deleting other existing DB than $BDD_TO_UPDATE

echo
echo "$JAUNE" "Supprimer le fichier OFF qui empeche le script automatique de lancement d'Odoo s'il est éteint (execution toutes les cinq minutes)" "$NORMAL"
echo
rm $OFF_MODE_FILE
