# WWInventoryUpdate
Automatic inventory update for wwhardware.com

A python script to pull inventory data from internal database, and push data to a webserver

This script depends on the following packages:
- dask==2022.2.1 
- pandarallel==1.5.7 
- pandas==1.4.0 
- pyodbc==4.0.32 
- requests==2.27.1

### To Run This Script:
1. You will need to edit config_template.py:  
`APIBEARERTOKEN = "YOUR API BEARER TOKEN HERE"`  
Delete the text within quotes and replace it with your bearer token  

2. Rename config_template.py to config.py  

3. Kerberos authentication via the `kinit` command


### Helpful links
 - Kerberos keytabs https://kb.iu.edu/d/aumh
 - Cron formatting for scheduling and automation https://crontab.guru/
 - Pandas is life https://pandas.pydata.org/

