#launched every night by system cron
#10 4 * * * /home/louve-erp-prod/nightly_odoo_backup_script.sh

#!/bin/bash
# Auteur :      Aurélien DUMAINE, adapté depuis Nono @ blog.m0le.net
# Date :        17/01/2016
# Version :     1.0

#############
# Variables #
#############

OFF_MODE_FILE=/home/$USER/odoo_auto_reload_OFF
touch $OFF_MODE_FILE

# Une date est généré, pour avoir la date de début de processus de backup
date_start=`date +'%d/%m/%Y @ %H:%M:%S'`;

# Choix du format de la date utilisé pour les dossiers
format_date='%Y_%m_%d__%H_%M_%S'

# Variable de date du jour, en fonction du format choisi
date=`date +${format_date}`;

# Le nom de la base de donnée de prod à sauvegarder
database="louve-erp-prod_cooplalouve";

# Emplacement des filstores Odoo sur cette machine
odoo_filetores_location="/home/louve-erp-prod/.local/share/Odoo/filestore/${database}";

# Le répertoire de création du backup journalier
backup_dir="/home/louve-erp-prod/backup-odoo/${date}";

# Le chemin du fichier sql de backup
filename="${backup_dir}/dump_${date}.sql"

# Le chemin du rapport (celui-ci sera gardé, et envoyé par mail)
rapport=${backup_dir}'/rapport.log';

# Identification FTP
ftp_host='ftp.cooplalouve.fr';
ftp_user='cooplalo';
ftp_pass='xmTYCwfG';


# Identification FTP TROBZ
ftp_host_trobz='lalouve-hotfix.trobz.com:10322';
ftp_user_trobz='lalouve';
ftp_pass_trobz='rIKZs1XhRw';


##########
# Script #
##########

# Création du repertoire de backup + Initialisation du rapport
echo ${backup_dir};
mkdir -p ${backup_dir}
echo 'Rapport du '${date_start} > ${rapport};
echo " " >> ${rapport};

# Stop Odoo Server
echo "Arrêt des services"
/home/louve-erp-prod/init.d/odoo-server stop

#Création du dump de la base de donnée avec Postrges
pg_dump --format=c $database --file=/tmp/backup_${date}.dump

mkdir -p ${backup_dir}/filestores
cp /tmp/backup_${date}.dump ${backup_dir}
cp -r ${odoo_filetores_location} ${backup_dir}/filestores

echo "Etat du dossier local :" >> ${rapport};
ls -lh ${backup_dir} -I rapport* >> ${rapport};
echo " " >> ${rapport};

# Envoie du dossier de sauvegarde vers le FTP
echo "Etat du dossier distant :" >> ${rapport};
lftp ftp://${ftp_user}:${ftp_pass}@${ftp_host} -e "mirror -R ${backup_dir} /backup-odoo/${date} ; ls /backup-odoo/${date} ; quit" >> ${rapport};
lftp sftp://${ftp_user_trobz}:${ftp_pass_trobz}@${ftp_host_trobz} -e "put /tmp/backup_${date}.dump ; quit";

echo " " >> ${rapport};

# Une date est générée, pour avoir la date de fin de processus de backup
date_end=`date +'%d/%m/%Y @ %H:%M:%S'`;
echo " " >> ${rapport};

#Finalisation du rapport
echo 'Fini le '${date_end} >> ${rapport};

# Start Odoo Server
echo "Reprise des services"
/home/louve-erp-prod/init.d/odoo-server start

rm $OFF_MODE_FILE
