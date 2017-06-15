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
GIT_BRANCH="9.0"
BDD_TO_UPDATE=$1

OFF_MODE_FILE=/home/$USER/odoo_auto_reload_OFF

FTP_USER="cooplalo"
FTP_PASSWORD="xmTYCwfG"
FTP_SERVER="ftp.cooplalouve.fr"

if [ $# -eq 0 ];then
    #echo "$ROUGE" "Merci de fournir le nom de la BDD à mettre à jour" "$NORMAL"
    #exit 1
    BDD_TO_UPDATE="louve-erp-prod_cooplalouve"
fi


echo
echo "$JAUNE" "Installation des dernieres sources et montée de version Odoo ?" "$NORMAL"
echo
read -p "Oui (Y/y) ? " ANSWER
echo
if [ ! "$ANSWER" = "Y" ] && [ ! "$ANSWER" = "y" ]; then
    echo "...Annulation"
    exit 1
fi


echo
echo "$JAUNE" "Positionner le fichier OFF pour empecher le script automatique de lancement d'Odoo s'il est éteint (execution toutes les cinq minutes)" "$NORMAL"
echo
touch $OFF_MODE_FILE

echo
echo "$JAUNE" "Arret Odoo" "$NORMAL"
echo
#TODO : handle PID in a more robust way
/home/$USER/init.d/odoo-server stop

echo
echo "$VERT" "...OK" "$NORMAL"
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


echo
echo "$JAUNE" "Sauvergarde de la base de donnée (hors filestore) sur le FTP" "$NORMAL"
echo
BACKUP_FILE="/tmp/backup_$(date +%Y%m%d_%H%M%S).dump"
pg_dump --format=c $BDD_TO_UPDATE --file=$BACKUP_FILE
lftp ftp://$FTP_USER:$FTP_PASSWORD@$FTP_SERVER -e "PUT -O /backup-odoo/ $BACKUP_FILE; quit"


echo
echo "$VERT" "...OK" "$NORMAL"
echo

cd $SOURCES_PATH

echo
echo "$JAUNE" "Récupération des sources..." "$NORMAL"
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

echo
echo "$JAUNE" "Supprimer le fichier OFF qui empeche le script automatique de lancement d'Odoo s'il est éteint (execution toutes les cinq minutes)" "$NORMAL"
echo
rm $OFF_MODE_FILE
