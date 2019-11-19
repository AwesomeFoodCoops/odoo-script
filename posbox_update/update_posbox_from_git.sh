gitaggregate -c repos.yml

SRC_PATH="/home/pi/odoo-src"
DST_PATH="/home/pi/odoo-dev"

echo "Cleaning $DST_PATH..."
rm -rf "$DST_PATH"
mkdir -p "$DST_PATH/addons"

for addon in web web_kanban; do
    echo "Creating symlink for $addon.."
    ln -s "$SRC_PATH/odoo/addons/$addon" "$DST_PATH/addons/$addon"
done

for addon in $(find $SRC_PATH/odoo/addons/hw_* -maxdepth 0 -type d -printf "%f\n"); do
    echo "Creating symlink for $addon.."
    ln -s "$SRC_PATH/odoo/addons/$addon" "$DST_PATH/addons/$addon"
done

for dir in extra_addons OCA_addons louve_addons intercoop_addons; do
    for addon in $(find $SRC_PATH/$dir/hw_* -maxdepth 0 -type d -printf "%f\n"); do
        echo "Creating symlink for $dir/$addon"
        ln -s "$SRC_PATH/$dir/$addon" "$DST_PATH/addons/$addon"
    done
done

# Linking odoo src
ln -s "$SRC_PATH/odoo/openerp" "$DST_PATH/openerp"
ln -s "$SRC_PATH/odoo/odoo.py" "$DST_PATH/odoo.py"

