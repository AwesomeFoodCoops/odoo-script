#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
import sys
#from config_prod import odoo_configuration_user
from config_test import odoo_configuration_user
import datetime
import re

###############################################################################
# Odoo Connection
###############################################################################


def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

##################################################################
##########                  SET LOGGER                  ##########
##################################################################
class Logger(object):
    def __init__(self, filename='Default.log'):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

log_file = 'log_' + datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")+'.log'
print "stdout = ./"+log_file
sys.stdout = Logger(log_file)
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")

###############################################################################
# Script
###############################################################################

tab_france_active = [
{'num_echeance':4,'date_echeance':'2017-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':5,'date_echeance':'2017-04-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':6,'date_echeance':'2017-07-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':7,'date_echeance':'2017-10-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':8,'date_echeance':'2018-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':9,'date_echeance':'2018-04-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':10,'date_echeance':'2018-07-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':11,'date_echeance':'2018-10-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':12,'date_echeance':'2019-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':13,'date_echeance':'2019-04-30','restant_du':200000,'interets':2500,'capital':11369.34,'total':13869.34},
{'num_echeance':14,'date_echeance':'2019-07-30','restant_du':188630.66,'interets':2357.88,'capital':11511.46,'total':13869.34},
{'num_echeance':15,'date_echeance':'2019-10-30','restant_du':177119.2,'interets':2213.99,'capital':11655.35,'total':13869.34},
{'num_echeance':16,'date_echeance':'2020-01-30','restant_du':165463.85,'interets':2068.3,'capital':11801.04,'total':13869.34},
{'num_echeance':17,'date_echeance':'2020-04-30','restant_du':153662.81,'interets':1920.79,'capital':11948.55,'total':13869.34},
{'num_echeance':18,'date_echeance':'2020-07-30','restant_du':141714.26,'interets':1771.43,'capital':12097.91,'total':13869.34},
{'num_echeance':19,'date_echeance':'2020-10-30','restant_du':129616.35,'interets':1620.2,'capital':12249.14,'total':13869.34},
{'num_echeance':20,'date_echeance':'2021-01-30','restant_du':117367.21,'interets':1467.09,'capital':12402.25,'total':13869.34},
{'num_echeance':21,'date_echeance':'2021-04-30','restant_du':104964.96,'interets':1312.06,'capital':12557.28,'total':13869.34},
{'num_echeance':22,'date_echeance':'2021-07-30','restant_du':92407.68,'interets':1155.1,'capital':12714.24,'total':13869.34},
{'num_echeance':23,'date_echeance':'2021-10-30','restant_du':79693.44,'interets':996.17,'capital':12873.17,'total':13869.34},
{'num_echeance':24,'date_echeance':'2022-01-30','restant_du':66820.27,'interets':835.25,'capital':13034.09,'total':13869.34},
{'num_echeance':25,'date_echeance':'2022-04-30','restant_du':53786.18,'interets':672.33,'capital':13197.01,'total':13869.34},
{'num_echeance':26,'date_echeance':'2022-07-30','restant_du':40589.17,'interets':507.360000000001,'capital':13361.98,'total':13869.34},
{'num_echeance':27,'date_echeance':'2022-10-30','restant_du':27227.19,'interets':340.34,'capital':13529,'total':13869.34},
{'num_echeance':28,'date_echeance':'2023-01-30','restant_du':13698.19,'interets':171.23,'capital':13698.19,'total':13869.42},
]
tab_cdc = [
{'num_echeance':1,'date_echeance':'2017-03-31','restant_du':400000,'interets':8928.89,'capital':0,'total':8928.89},
{'num_echeance':2,'date_echeance':'2018-03-31','restant_du':400000,'interets':11200,'capital':0,'total':11200},
{'num_echeance':3,'date_echeance':'2019-03-31','restant_du':400000,'interets':11200,'capital':80000,'total':91200},
{'num_echeance':4,'date_echeance':'2020-03-31','restant_du':320000,'interets':8960,'capital':80000,'total':88960},
{'num_echeance':5,'date_echeance':'2021-03-31','restant_du':240000,'interets':6720,'capital':80000,'total':86720},
{'num_echeance':6,'date_echeance':'2022-03-31','restant_du':160000,'interets':4480,'capital':80000,'total':84480},
{'num_echeance':7,'date_echeance':'2023-03-31','restant_du':80000,'interets':2240,'capital':80000,'total':82240},
]
tab_cep = [
{'num_echeance':9,'date_echeance':'2017-01-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':10,'date_echeance':'2017-02-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':11,'date_echeance':'2017-03-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':12,'date_echeance':'2017-04-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':13,'date_echeance':'2017-05-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':14,'date_echeance':'2017-06-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':15,'date_echeance':'2017-07-15','restant_du':200000,'interets':285,'capital':0,'total':285},
{'num_echeance':16,'date_echeance':'2017-08-15','restant_du':200000,'interets':285,'capital':2639.69,'total':2924.69},
{'num_echeance':17,'date_echeance':'2017-09-15','restant_du':197360.31,'interets':281.24,'capital':2643.45,'total':2924.69},
{'num_echeance':18,'date_echeance':'2017-10-15','restant_du':194716.86,'interets':277.47,'capital':2647.22,'total':2924.69},
{'num_echeance':19,'date_echeance':'2017-11-15','restant_du':192069.64,'interets':273.7,'capital':2650.99,'total':2924.69},
{'num_echeance':20,'date_echeance':'2017-12-15','restant_du':189418.65,'interets':269.92,'capital':2654.77,'total':2924.69},
{'num_echeance':21,'date_echeance':'2018-01-15','restant_du':186763.88,'interets':266.14,'capital':2658.55,'total':2924.69},
{'num_echeance':22,'date_echeance':'2018-02-15','restant_du':184105.33,'interets':262.35,'capital':2662.34,'total':2924.69},
{'num_echeance':23,'date_echeance':'2018-03-15','restant_du':181442.99,'interets':258.56,'capital':2666.13,'total':2924.69},
{'num_echeance':24,'date_echeance':'2018-04-15','restant_du':178776.86,'interets':254.76,'capital':2669.93,'total':2924.69},
{'num_echeance':25,'date_echeance':'2018-05-15','restant_du':176106.93,'interets':250.95,'capital':2673.74,'total':2924.69},
{'num_echeance':26,'date_echeance':'2018-06-15','restant_du':173433.19,'interets':247.14,'capital':2677.55,'total':2924.69},
{'num_echeance':27,'date_echeance':'2018-07-15','restant_du':170755.64,'interets':243.33,'capital':2681.36,'total':2924.69},
{'num_echeance':28,'date_echeance':'2018-08-15','restant_du':168074.28,'interets':239.51,'capital':2685.18,'total':2924.69},
{'num_echeance':29,'date_echeance':'2018-09-15','restant_du':165389.1,'interets':235.68,'capital':2689.01,'total':2924.69},
{'num_echeance':30,'date_echeance':'2018-10-15','restant_du':162700.09,'interets':231.85,'capital':2692.84,'total':2924.69},
{'num_echeance':31,'date_echeance':'2018-11-15','restant_du':160007.25,'interets':228.01,'capital':2696.68,'total':2924.69},
{'num_echeance':32,'date_echeance':'2018-12-15','restant_du':157310.57,'interets':224.17,'capital':2700.52,'total':2924.69},
{'num_echeance':33,'date_echeance':'2019-01-15','restant_du':154610.05,'interets':220.32,'capital':2704.37,'total':2924.69},
{'num_echeance':34,'date_echeance':'2019-02-15','restant_du':151905.68,'interets':216.47,'capital':2708.22,'total':2924.69},
{'num_echeance':35,'date_echeance':'2019-03-15','restant_du':149197.46,'interets':212.61,'capital':2712.08,'total':2924.69},
{'num_echeance':36,'date_echeance':'2019-04-15','restant_du':146485.38,'interets':208.74,'capital':2715.95,'total':2924.69},
{'num_echeance':37,'date_echeance':'2019-05-15','restant_du':143769.43,'interets':204.87,'capital':2719.82,'total':2924.69},
{'num_echeance':38,'date_echeance':'2019-06-15','restant_du':141049.61,'interets':201,'capital':2723.69,'total':2924.69},
{'num_echeance':39,'date_echeance':'2019-07-15','restant_du':138325.92,'interets':197.11,'capital':2727.58,'total':2924.69},
{'num_echeance':40,'date_echeance':'2019-08-15','restant_du':135598.34,'interets':193.23,'capital':2731.46,'total':2924.69},
{'num_echeance':41,'date_echeance':'2019-09-15','restant_du':132866.88,'interets':189.34,'capital':2735.35,'total':2924.69},
{'num_echeance':42,'date_echeance':'2019-10-15','restant_du':130131.53,'interets':185.44,'capital':2739.25,'total':2924.69},
{'num_echeance':43,'date_echeance':'2019-11-15','restant_du':127392.28,'interets':181.53,'capital':2743.16,'total':2924.69},
{'num_echeance':44,'date_echeance':'2019-12-15','restant_du':124649.12,'interets':177.62,'capital':2747.07,'total':2924.69},
{'num_echeance':45,'date_echeance':'2020-01-15','restant_du':121902.05,'interets':173.71,'capital':2750.98,'total':2924.69},
{'num_echeance':46,'date_echeance':'2020-02-15','restant_du':119151.07,'interets':169.79,'capital':2754.9,'total':2924.69},
{'num_echeance':47,'date_echeance':'2020-03-15','restant_du':116396.17,'interets':165.86,'capital':2758.83,'total':2924.69},
{'num_echeance':48,'date_echeance':'2020-04-15','restant_du':113637.34,'interets':161.93,'capital':2762.76,'total':2924.69},
{'num_echeance':49,'date_echeance':'2020-05-15','restant_du':110874.58,'interets':158,'capital':2766.69,'total':2924.69},
{'num_echeance':50,'date_echeance':'2020-06-15','restant_du':108107.89,'interets':154.05,'capital':2770.64,'total':2924.69},
{'num_echeance':51,'date_echeance':'2020-07-15','restant_du':105337.25,'interets':150.11,'capital':2774.58,'total':2924.69},
{'num_echeance':52,'date_echeance':'2020-08-15','restant_du':102562.67,'interets':146.15,'capital':2778.54,'total':2924.69},
{'num_echeance':53,'date_echeance':'2020-09-15','restant_du':99784.1300000001,'interets':142.19,'capital':2782.5,'total':2924.69},
{'num_echeance':54,'date_echeance':'2020-10-15','restant_du':97001.6300000001,'interets':138.23,'capital':2786.46,'total':2924.69},
{'num_echeance':55,'date_echeance':'2020-11-15','restant_du':94215.1700000001,'interets':134.26,'capital':2790.43,'total':2924.69},
{'num_echeance':56,'date_echeance':'2020-12-15','restant_du':91424.7400000001,'interets':130.28,'capital':2794.41,'total':2924.69},
{'num_echeance':57,'date_echeance':'2021-01-15','restant_du':88630.3300000001,'interets':126.3,'capital':2798.39,'total':2924.69},
{'num_echeance':58,'date_echeance':'2021-02-15','restant_du':85831.9400000001,'interets':122.31,'capital':2802.38,'total':2924.69},
{'num_echeance':59,'date_echeance':'2021-03-15','restant_du':83029.5600000001,'interets':118.32,'capital':2806.37,'total':2924.69},
{'num_echeance':60,'date_echeance':'2021-04-15','restant_du':80223.1900000001,'interets':114.32,'capital':2810.37,'total':2924.69},
{'num_echeance':61,'date_echeance':'2021-05-15','restant_du':77412.8200000001,'interets':110.31,'capital':2814.38,'total':2924.69},
{'num_echeance':62,'date_echeance':'2021-06-15','restant_du':74598.4400000001,'interets':106.3,'capital':2818.39,'total':2924.69},
{'num_echeance':63,'date_echeance':'2021-07-15','restant_du':71780.0500000001,'interets':102.29,'capital':2822.4,'total':2924.69},
{'num_echeance':64,'date_echeance':'2021-08-15','restant_du':68957.6500000001,'interets':98.26,'capital':2826.43,'total':2924.69},
{'num_echeance':65,'date_echeance':'2021-09-15','restant_du':66131.2200000001,'interets':94.24,'capital':2830.45,'total':2924.69},
{'num_echeance':66,'date_echeance':'2021-10-15','restant_du':63300.7700000001,'interets':90.2,'capital':2834.49,'total':2924.69},
{'num_echeance':67,'date_echeance':'2021-11-15','restant_du':60466.2800000001,'interets':86.16,'capital':2838.53,'total':2924.69},
{'num_echeance':68,'date_echeance':'2021-12-15','restant_du':57627.7500000001,'interets':82.12,'capital':2842.57,'total':2924.69},
{'num_echeance':69,'date_echeance':'2022-01-15','restant_du':54785.1800000001,'interets':78.07,'capital':2846.62,'total':2924.69},
{'num_echeance':70,'date_echeance':'2022-02-15','restant_du':51938.5600000001,'interets':74.01,'capital':2850.68,'total':2924.69},
{'num_echeance':71,'date_echeance':'2022-03-15','restant_du':49087.8800000001,'interets':69.95,'capital':2854.74,'total':2924.69},
{'num_echeance':72,'date_echeance':'2022-04-15','restant_du':46233.1400000001,'interets':65.88,'capital':2858.81,'total':2924.69},
{'num_echeance':73,'date_echeance':'2022-05-15','restant_du':43374.3300000001,'interets':61.81,'capital':2862.88,'total':2924.69},
{'num_echeance':74,'date_echeance':'2022-06-15','restant_du':40511.4500000001,'interets':57.73,'capital':2866.96,'total':2924.69},
{'num_echeance':75,'date_echeance':'2022-07-15','restant_du':37644.4900000001,'interets':53.64,'capital':2871.05,'total':2924.69},
{'num_echeance':76,'date_echeance':'2022-08-15','restant_du':34773.4400000001,'interets':49.55,'capital':2875.14,'total':2924.69},
{'num_echeance':77,'date_echeance':'2022-09-15','restant_du':31898.3000000001,'interets':45.46,'capital':2879.23,'total':2924.69},
{'num_echeance':78,'date_echeance':'2022-10-15','restant_du':29019.0700000001,'interets':41.35,'capital':2883.34,'total':2924.69},
{'num_echeance':79,'date_echeance':'2022-11-15','restant_du':26135.7300000001,'interets':37.24,'capital':2887.45,'total':2924.69},
{'num_echeance':80,'date_echeance':'2022-12-15','restant_du':23248.2800000001,'interets':33.13,'capital':2891.56,'total':2924.69},
{'num_echeance':81,'date_echeance':'2023-01-15','restant_du':20356.7200000001,'interets':29.01,'capital':2895.68,'total':2924.69},
{'num_echeance':82,'date_echeance':'2023-02-15','restant_du':17461.0400000001,'interets':24.88,'capital':2899.81,'total':2924.69},
{'num_echeance':83,'date_echeance':'2023-03-15','restant_du':14561.2300000001,'interets':20.75,'capital':2903.94,'total':2924.69},
{'num_echeance':84,'date_echeance':'2023-04-15','restant_du':11657.2900000001,'interets':16.61,'capital':2908.08,'total':2924.69},
{'num_echeance':85,'date_echeance':'2023-05-15','restant_du':8749.2100000001,'interets':12.47,'capital':2912.22,'total':2924.69},
{'num_echeance':86,'date_echeance':'2023-06-15','restant_du':5836.9900000001,'interets':8.32,'capital':2916.37,'total':2924.69},
{'num_echeance':87,'date_echeance':'2023-07-15','restant_du':2920.6200000001,'interets':4.07,'capital':2920.62,'total':2924.69},
]
#tab_mirova = []
tab_ccoop = [
{'num_echeance':18,'date_echeance':'2017-01-10','restant_du':189470.38,'interets':296.84,'capital':2642.72,'total':2939.56},
{'num_echeance':19,'date_echeance':'2017-02-10','restant_du':186827.66,'interets':292.7,'capital':2646.86,'total':2939.56},
{'num_echeance':20,'date_echeance':'2017-03-10','restant_du':184180.8,'interets':288.55,'capital':2651.01,'total':2939.56},
{'num_echeance':21,'date_echeance':'2017-04-10','restant_du':181529.79,'interets':284.4,'capital':2655.16,'total':2939.56},
{'num_echeance':22,'date_echeance':'2017-05-10','restant_du':178874.63,'interets':280.24,'capital':2659.32,'total':2939.56},
{'num_echeance':23,'date_echeance':'2017-06-10','restant_du':176215.31,'interets':276.07,'capital':2663.49,'total':2939.56},
{'num_echeance':24,'date_echeance':'2017-07-10','restant_du':173551.82,'interets':271.9,'capital':2667.66,'total':2939.56},
{'num_echeance':25,'date_echeance':'2017-08-10','restant_du':170884.16,'interets':267.72,'capital':2671.84,'total':2939.56},
{'num_echeance':26,'date_echeance':'2017-09-10','restant_du':168212.32,'interets':263.53,'capital':2676.03,'total':2939.56},
{'num_echeance':27,'date_echeance':'2017-10-10','restant_du':165536.29,'interets':259.34,'capital':2680.22,'total':2939.56},
{'num_echeance':28,'date_echeance':'2017-11-10','restant_du':162856.07,'interets':255.14,'capital':2684.42,'total':2939.56},
{'num_echeance':29,'date_echeance':'2017-12-10','restant_du':160171.65,'interets':250.94,'capital':2688.62,'total':2939.56},
{'num_echeance':30,'date_echeance':'2018-01-10','restant_du':157483.03,'interets':246.72,'capital':2692.84,'total':2939.56},
{'num_echeance':31,'date_echeance':'2018-02-10','restant_du':154790.19,'interets':242.5,'capital':2697.06,'total':2939.56},
{'num_echeance':32,'date_echeance':'2018-03-10','restant_du':152093.13,'interets':238.28,'capital':2701.28,'total':2939.56},
{'num_echeance':33,'date_echeance':'2018-04-10','restant_du':149391.85,'interets':234.05,'capital':2705.51,'total':2939.56},
{'num_echeance':34,'date_echeance':'2018-05-10','restant_du':146686.34,'interets':229.81,'capital':2709.75,'total':2939.56},
{'num_echeance':35,'date_echeance':'2018-06-10','restant_du':143976.59,'interets':225.56,'capital':2714,'total':2939.56},
{'num_echeance':36,'date_echeance':'2018-07-10','restant_du':141262.59,'interets':221.31,'capital':2718.25,'total':2939.56},
{'num_echeance':37,'date_echeance':'2018-08-10','restant_du':138544.34,'interets':217.05,'capital':2722.51,'total':2939.56},
{'num_echeance':38,'date_echeance':'2018-09-10','restant_du':135821.83,'interets':212.79,'capital':2726.77,'total':2939.56},
{'num_echeance':39,'date_echeance':'2018-10-10','restant_du':133095.06,'interets':208.52,'capital':2731.04,'total':2939.56},
{'num_echeance':40,'date_echeance':'2018-11-10','restant_du':130364.02,'interets':204.24,'capital':2735.32,'total':2939.56},
{'num_echeance':41,'date_echeance':'2018-12-10','restant_du':127628.7,'interets':199.95,'capital':2739.61,'total':2939.56},
{'num_echeance':42,'date_echeance':'2019-01-10','restant_du':124889.09,'interets':195.66,'capital':2743.9,'total':2939.56},
{'num_echeance':43,'date_echeance':'2019-02-10','restant_du':122145.19,'interets':191.36,'capital':2748.2,'total':2939.56},
{'num_echeance':44,'date_echeance':'2019-03-10','restant_du':119396.99,'interets':187.06,'capital':2752.5,'total':2939.56},
{'num_echeance':45,'date_echeance':'2019-04-10','restant_du':116644.49,'interets':182.74,'capital':2756.82,'total':2939.56},
{'num_echeance':46,'date_echeance':'2019-05-10','restant_du':113887.67,'interets':178.42,'capital':2761.14,'total':2939.56},
{'num_echeance':47,'date_echeance':'2019-06-10','restant_du':111126.53,'interets':174.1,'capital':2765.46,'total':2939.56},
{'num_echeance':48,'date_echeance':'2019-07-10','restant_du':108361.07,'interets':169.77,'capital':2769.79,'total':2939.56},
{'num_echeance':49,'date_echeance':'2019-08-10','restant_du':105591.28,'interets':165.43,'capital':2774.13,'total':2939.56},
{'num_echeance':50,'date_echeance':'2019-09-10','restant_du':102817.15,'interets':161.08,'capital':2778.48,'total':2939.56},
{'num_echeance':51,'date_echeance':'2019-10-10','restant_du':100038.67,'interets':156.73,'capital':2782.83,'total':2939.56},
{'num_echeance':52,'date_echeance':'2019-11-10','restant_du':97255.84,'interets':152.37,'capital':2787.19,'total':2939.56},
{'num_echeance':53,'date_echeance':'2019-12-10','restant_du':94468.65,'interets':148,'capital':2791.56,'total':2939.56},
{'num_echeance':54,'date_echeance':'2020-01-10','restant_du':91677.09,'interets':143.63,'capital':2795.93,'total':2939.56},
{'num_echeance':55,'date_echeance':'2020-02-10','restant_du':88881.16,'interets':139.25,'capital':2800.31,'total':2939.56},
{'num_echeance':56,'date_echeance':'2020-03-10','restant_du':86080.85,'interets':134.86,'capital':2804.7,'total':2939.56},
{'num_echeance':57,'date_echeance':'2020-04-10','restant_du':83276.15,'interets':130.47,'capital':2809.09,'total':2939.56},
{'num_echeance':58,'date_echeance':'2020-05-10','restant_du':80467.06,'interets':126.07,'capital':2813.49,'total':2939.56},
{'num_echeance':59,'date_echeance':'2020-06-10','restant_du':77653.57,'interets':121.66,'capital':2817.9,'total':2939.56},
{'num_echeance':60,'date_echeance':'2020-07-10','restant_du':74835.67,'interets':117.24,'capital':2822.32,'total':2939.56},
{'num_echeance':61,'date_echeance':'2020-08-10','restant_du':72013.35,'interets':112.82,'capital':2826.74,'total':2939.56},
{'num_echeance':62,'date_echeance':'2020-09-10','restant_du':69186.61,'interets':108.39,'capital':2831.17,'total':2939.56},
{'num_echeance':63,'date_echeance':'2020-10-10','restant_du':66355.44,'interets':103.96,'capital':2835.6,'total':2939.56},
{'num_echeance':64,'date_echeance':'2020-11-10','restant_du':63519.84,'interets':99.51,'capital':2840.05,'total':2939.56},
{'num_echeance':65,'date_echeance':'2020-12-10','restant_du':60679.79,'interets':95.07,'capital':2844.49,'total':2939.56},
{'num_echeance':66,'date_echeance':'2021-01-10','restant_du':57835.3,'interets':90.61,'capital':2848.95,'total':2939.56},
{'num_echeance':67,'date_echeance':'2021-02-10','restant_du':54986.35,'interets':86.15,'capital':2853.41,'total':2939.56},
{'num_echeance':68,'date_echeance':'2021-03-10','restant_du':52132.94,'interets':81.67,'capital':2857.89,'total':2939.56},
{'num_echeance':69,'date_echeance':'2021-04-10','restant_du':49275.05,'interets':77.2,'capital':2862.36,'total':2939.56},
{'num_echeance':70,'date_echeance':'2021-05-10','restant_du':46412.69,'interets':72.71,'capital':2866.85,'total':2939.56},
{'num_echeance':71,'date_echeance':'2021-06-10','restant_du':43545.84,'interets':68.22,'capital':2871.34,'total':2939.56},
{'num_echeance':72,'date_echeance':'2021-07-10','restant_du':40674.5,'interets':63.72,'capital':2875.84,'total':2939.56},
{'num_echeance':73,'date_echeance':'2021-08-10','restant_du':37798.66,'interets':59.22,'capital':2880.34,'total':2939.56},
{'num_echeance':74,'date_echeance':'2021-09-10','restant_du':34918.32,'interets':54.71,'capital':2884.85,'total':2939.56},
{'num_echeance':75,'date_echeance':'2021-10-10','restant_du':32033.47,'interets':50.19,'capital':2889.37,'total':2939.56},
{'num_echeance':76,'date_echeance':'2021-11-10','restant_du':29144.1,'interets':45.66,'capital':2893.9,'total':2939.56},
{'num_echeance':77,'date_echeance':'2021-12-10','restant_du':26250.2,'interets':41.13,'capital':2898.43,'total':2939.56},
{'num_echeance':78,'date_echeance':'2022-01-10','restant_du':23351.77,'interets':36.58,'capital':2902.98,'total':2939.56},
{'num_echeance':79,'date_echeance':'2022-02-10','restant_du':20448.79,'interets':32.04,'capital':2907.52,'total':2939.56},
{'num_echeance':80,'date_echeance':'2022-03-10','restant_du':17541.27,'interets':27.48,'capital':2912.08,'total':2939.56},
{'num_echeance':81,'date_echeance':'2022-04-10','restant_du':14629.19,'interets':22.92,'capital':2916.64,'total':2939.56},
{'num_echeance':82,'date_echeance':'2022-05-10','restant_du':11712.55,'interets':18.35,'capital':2921.21,'total':2939.56},
{'num_echeance':83,'date_echeance':'2022-06-10','restant_du':8791.34000000002,'interets':13.77,'capital':2925.79,'total':2939.56},
{'num_echeance':84,'date_echeance':'2022-07-10','restant_du':5865.55000000002,'interets':9.19,'capital':2930.37,'total':2939.56},
{'num_echeance':85,'date_echeance':'2022-08-10','restant_du':2935.18000000002,'interets':4.38,'capital':2935.18,'total':2939.56},
]
tab_sifa = [
{'num_echeance':4,'date_echeance':'2017-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':5,'date_echeance':'2017-04-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':6,'date_echeance':'2017-07-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':7,'date_echeance':'2017-10-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':8,'date_echeance':'2018-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':9,'date_echeance':'2018-04-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':10,'date_echeance':'2018-07-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':11,'date_echeance':'2018-10-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':12,'date_echeance':'2019-01-30','restant_du':200000,'interets':2500,'capital':0,'total':2500},
{'num_echeance':13,'date_echeance':'2019-04-30','restant_du':200000,'interets':2500,'capital':11369.34,'total':13869.34},
{'num_echeance':14,'date_echeance':'2019-07-30','restant_du':188630.66,'interets':2357.88,'capital':11511.46,'total':13869.34},
{'num_echeance':15,'date_echeance':'2019-10-30','restant_du':177119.2,'interets':2213.99,'capital':11655.35,'total':13869.34},
{'num_echeance':16,'date_echeance':'2020-01-30','restant_du':165463.85,'interets':2068.29,'capital':11801.05,'total':13869.34},
{'num_echeance':17,'date_echeance':'2020-04-30','restant_du':153662.8,'interets':1920.78,'capital':11948.56,'total':13869.34},
{'num_echeance':18,'date_echeance':'2020-07-30','restant_du':141714.24,'interets':1771.42,'capital':12097.92,'total':13869.34},
{'num_echeance':19,'date_echeance':'2020-10-30','restant_du':129616.32,'interets':1620.2,'capital':12249.14,'total':13869.34},
{'num_echeance':20,'date_echeance':'2021-01-30','restant_du':117367.18,'interets':1467.09,'capital':12402.25,'total':13869.34},
{'num_echeance':21,'date_echeance':'2021-04-30','restant_du':104964.93,'interets':1312.06,'capital':12557.28,'total':13869.34},
{'num_echeance':22,'date_echeance':'2021-07-30','restant_du':92407.65,'interets':1155.09,'capital':12714.25,'total':13869.34},
{'num_echeance':23,'date_echeance':'2021-10-30','restant_du':79693.4,'interets':996.16,'capital':12873.18,'total':13869.34},
{'num_echeance':24,'date_echeance':'2022-01-30','restant_du':66820.22,'interets':835.25,'capital':13034.09,'total':13869.34},
{'num_echeance':25,'date_echeance':'2022-04-30','restant_du':53786.13,'interets':672.32,'capital':13197.02,'total':13869.34},
{'num_echeance':26,'date_echeance':'2022-07-30','restant_du':40589.11,'interets':507.360000000001,'capital':13361.98,'total':13869.34},
{'num_echeance':27,'date_echeance':'2022-10-30','restant_du':27227.13,'interets':340.33,'capital':13529.01,'total':13869.34},
{'num_echeance':28,'date_echeance':'2023-01-30','restant_du':13698.12,'interets':171.219999999999,'capital':13698.12,'total':13869.34},
]

mode_test = False

def generer_ecritures(libelle_emprunt, tab_emprunt, compte_capital, compte_interet, compte_banque, journal_banque):
    print ">>>>>>> START "+libelle_emprunt+" >>>>>>>>>>"
    for echeance in tab_emprunt:
        print "================ "+'Echéance #'+str(echeance['num_echeance'])+' du '+echeance['date_echeance']+' emprunt '+libelle_emprunt
        dic = {
            #'name':, #TODO : ajouter la séquence de l'écriture
            'journal_id':journal_banque,
            'date':echeance['date_echeance'],
            'ref':'Echéance #'+str(echeance['num_echeance'])+' emprunt '+libelle_emprunt,
            'move_type':'other',
            'state':'draft',
        }
        print dic
        move_id = None
        if mode_test == False :
            move = openerp.AccountMove.create(dic)
            move_id = move.id
        print "move_id", move_id

        ligne_interet = {
            'move_id': move_id,
            'name':'Interet #'+str(echeance['num_echeance'])+' emprunt '+libelle_emprunt,
            'journal_id':journal_banque,
            'date':echeance['date_echeance'],
            'date_maturity':echeance['date_echeance'],
            'account_id':compte_interet,
            'debit':echeance['interets'],
            }
        print ligne_interet
        ligne_capital = {
            'move_id': move_id,
            'name':'Capital #'+str(echeance['num_echeance'])+' emprunt '+libelle_emprunt,
            'journal_id':journal_banque,
            'date':echeance['date_echeance'],
            'date_maturity':echeance['date_echeance'],
            'account_id':compte_capital,
            'debit':echeance['capital'],
            }
        print ligne_capital
        ligne_banque = {
            'move_id': move_id,
            'name':'Banque #'+str(echeance['num_echeance'])+' emprunt '+libelle_emprunt,
            'journal_id':journal_banque,
            'date':echeance['date_echeance'],
            'date_maturity':echeance['date_echeance'],
            'account_id':compte_banque,
            'credit':echeance['total'],
            }
        print ligne_banque
        if mode_test == False :
            try:
                #moveline_interet_id = openerp.AccountMoveLine.create(ligne_interet, context={'check_move_validity':False})
                moveline_interet_id = openerp.execute_kw('account.move.line', 'create', [ligne_interet],{'context': {'check_move_validity':False}})
                print "moveline_interet_id", moveline_interet_id
            except Exception as e:
                print "ERREUR ligne interet"
                print e.message, e.args
            try:
                #moveline_capital_id = openerp.AccountMoveLine.create(ligne_capital, context={'check_move_validity':False})
                moveline_capital_id = openerp.execute_kw('account.move.line', 'create', [ligne_capital],{'context': {'check_move_validity':False}})
                print "moveline_capital_id", moveline_capital_id
            except Exception as e:
                print "ERREUR ligne capital"
                print e.message, e.args
            try:
                #moveline_banque_id = openerp.AccountMoveLine.create(ligne_banque, context={'check_move_validity':False})
                moveline_banque_id = openerp.execute_kw('account.move.line', 'create', [ligne_banque],{'context': {'check_move_validity':True}})
                print "moveline_banque_id", moveline_banque_id
            except Exception as e:
                print "ERREUR ligne banque"
                print e.message, e.args
        break

################################
cpt_capital_CCOOP = 946 # 164100 - Empt CCoop n°06/15016720 - 200k€ 1.88% 84 mois
cpt_capital_CEP = 947 # 164200 - Empt CEp 9744071 - 200KE 1,71% 84m
cpt_capital_SIFA = 953 # 164500 - Empt SIFA - 200k€ 5% 28 trimestres
cpt_capital_FranceActive = 1025 # 164300 - Empt FranceActive - 200k€ 5% 28
cpt_capital_CDC = 1026 # 164400 - Empt CDC - 400k€ 2,8% 7 années

cpt_interet_CCOOP = 948 # 661110 - Int/ EMP 1 CCoop 200K 84m
cpt_interet_CEP = 949 # 661120 - Int/ EMP 2 CEp 200K 84m
cpt_interet_SIFA = 	952 # 661710 - Empt Part. SIFA 200K Intérêts
cpt_interet_FranceActive = 1028 # 661130 - Int/ EMP 3 FranceActive 200K 28 trimestres
cpt_interet_CDC = 1029 # 661140 - Int/ EMP 4 CDC 400K 7 années

if odoo_configuration_user['url'] == 'https://gestion-dev.cooplalouve.fr':
    #cpt_capital_SIFA = 953 # 164500 - Empt SIFA - 200k€ 5% 28 trimestres
    #cpt_capital_CCOOP = 946 # 164100 - Empt CCoop n°06/15016720 - 200k€ 1.88% 84 mois
    #cpt_capital_CEP = 947 # 164200 - Empt CEp 9744071 - 200KE 1,71% 84m
    cpt_capital_FranceActive = 1027 # 164300 - Empt FranceActive - 200k€ 5% 28
    cpt_capital_CDC = 1028 # 164400 - 	Empt CDC - 400k€ 2,8% 7 années
    #cpt_interet_CCOOP = 948 # 661110 - Int/ EMP 1 CCoop 200K 84m
    #cpt_interet_CEP = 949 # 661120 - Int/ EMP 2 CEp 200K 84m
    #cpt_interet_SIFA = 	952 # 661710 - Empt Part. SIFA 200K Intérêts
    cpt_interet_FranceActive = 1030 # 661130 - Int/ EMP 3 FranceActive 200K 28 trimestres
    cpt_interet_CDC = 1031 # 661140 - Int/ EMP 4 CDC 400K 7 années

cpt_banque_CCOOP_courant = 739 # 512110 - CCOOP Compte courant
cpt_banque_CEP_courant = 743 # 512210 - CEP Compte courant
journal_CCOOP_courant = 46
journal_CEP_courant = 49

#############################
generer_ecritures("Crédit coopératif", tab_ccoop, cpt_capital_CCOOP, cpt_interet_CCOOP,cpt_banque_CCOOP_courant,journal_CCOOP_courant)
#generer_ecritures("Caisse d'épargne", tab_cep, cpt_capital_CEP, cpt_interet_CEP,cpt_banque_CEP_courant,journal_CEP_courant)
#generer_ecritures("SIFA", tab_sifa, cpt_capital_SIFA, cpt_interet_SIFA,cpt_banque_CCOOP_courant,journal_CCOOP_courant)
#generer_ecritures("France Active", tab_france_active, cpt_capital_FranceActive, cpt_interet_FranceActive,x)
#generer_ecritures("CDC", tab_cdc, cpt_capital_CDC, cpt_interet_CDC,cpt_banque_CCOOP_courant,journal_CCOOP_courant)
#generer_ecritures("MIROVA", tab_cep, x,x,x)



print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")
