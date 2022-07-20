from asyncio.windows_events import NULL
from unicodedata import decimal
from django.http import HttpResponse
from django.shortcuts import render
from io import StringIO
import psycopg2
import pandas as pd
import numpy as np
from os.path import exists
import datetime
import requests
from inventory_accuracy.models import SQ00

# Create your views here.
def cost(request):
    return render(request,'inventory_accuracy\cost.html') 
    
def upload_files(request):
    #get current year and week
    year=datetime.datetime.today().isocalendar()[0]
    week=datetime.datetime.today().isocalendar()[1]
    conn = psycopg2.connect(host='localhost',dbname='db_dashboard',user='postgres',password='Mounaruto',port='5432')
    # file= r"C:\Users\DELL\Downloads\2022 07 12 Z_LISTE_INV.xlsx"
    file= r"C:\Users\DELL\2022 07 12 Z_LISTE_INV.xlsx"
    file_exists=exists(file)
    print(file_exists)
    message_error= 'Unable to upload files, not exist or unreadable!'
    if file_exists:
        import_files(file,year,week,conn)
        home(request)
    else:
        return render(request,'inventory_accuracy\index.html',{'message_error':message_error})    
    # print('#'*50)
    # print(file_exists)
    # print('#'*50)
def home(request):
    all_sq00_data= SQ00.objects.all()
    data_of_2000=SQ00.objects.filter(division=2000).all()
    inventory_accuracy_results(all_sq00_data)

    return render(request,'inventory_accuracy\index.html',{'all_sq00_data':all_sq00_data,
    'count':inventory_accuracy_results.count,
    'cost_per_division':inventory_accuracy_results.cost_per_division,
    'total_deviation_cost':inventory_accuracy_results.total_deviation_cost})
    


def inventory_accuracy_results(sq00_data):
    df=pd.DataFrame(list(sq00_data.values()))
    # count
    inventory_accuracy_results.count=df.shape[0]

    url = f'https://api.exchangerate.host/latest'
    response = requests.get(url)
    data = response.json()
    df['rate']=df['dev'].map(data['rates'])

    #currency conversion
    df['deviation_cost_euro']=df['deviation_cost'].astype(float)*df['rate']
    #new KPI   
    df['type_of_measurement']=np.where( ( (df['unit']=='G') | (df['unit']=='KG') ), 'weighd','counted')
    # Pour un article pesé : Stock accuracy = 100% si l’écart < 3% et l’écart < 250€ sinon la réf est considéré en écart
    df.insert(0, 'stock_accuracy', None)
    df['stock_accuracy']=np.where ( ( (df['type_of_measurement']=='weighd') & (df['deviation'] < 0.03) & (df['deviation_cost_euro']< 250)) , 1 , df['stock_accuracy'] )
    # Pour un article compté : Stock accuracy = 100% si l’écart < 1% et l’écart < 250€ sinon la réf est considéré en écart
    df['stock_accuracy']=np.where ( ( (df['type_of_measurement']=='counted') & (df['deviation'] < 0.01) & (df['deviation_cost_euro']< 250)) , 1 , df['stock_accuracy'] )

    #deviation cost per division
    inventory_accuracy_results.cost_per_division=df.groupby(  ['year','week','division'])['deviation_cost_euro'].sum().reset_index() 
    inventory_accuracy_results.total_deviation_cost=df['deviation_cost'].sum()
    print(inventory_accuracy_results.cost_per_division)
    print(inventory_accuracy_results.total_deviation_cost)
    print(inventory_accuracy_results.count)


def import_files(file,year,week,conn):
    df=pd.read_excel(file)
#dropping the duplicate of columns
    df=df.drop(df.columns[ [9,11,14,16] ],axis=1)

    #rename columns
    df.rename(columns = {'Doc.inven.':'inventory_doc',
                        'Article':'material',
                        'Désignation article':'designation',
                        'TyAr':'type',
                        'UQ':'unit',
                        'Mag.':'store',
                        'Fourn.':'supplier',
                        'Quantité théorique':'theoritical_quantity',
                        'Quantité saisie':'entred_quantity',
                        'écart enregistré':'deviation',
                        'Ecart (montant)':'deviation_cost',
                        'Dev..1':'dev',
                        'Div.':'division',
                        'Sup':'delete',
                        'Dte cptage':'date_catchment',
                        'Rectifié par':'corrected_by',
                        'Cpt':'catchment',
                        'Réf.inventaire':'refecrence_inventory',
                        'N° inventaire':'inventory_number',
                        'TyS':'Tys'},  inplace = True)

    #Adding the year and week columns
    
    #insert year and week in first and second position
    df.insert(0, 'year', year)
    df.insert(1, 'week', week)
    df["division"]=df["division"].fillna(0).astype(int)
    df["store"]=df["store"].fillna(0).astype(int)
    df["Tys"]=df["Tys"].fillna(0).astype(int)
    list_inv = StringIO()
    #convert file to csv
    list_inv.write(df.to_csv( header=None, index=False ,sep=';'))
    # This will make the cursor at index 0
    list_inv.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=list_inv,
            #file name in DB
            table="inventory_accuracy_sq00",
            columns=[
                    'year',
                    'week',
                    'inventory_doc',
                    'material',
                    'designation',
                    'type',
                    'unit',
                    'division',
                    'store',
                    'supplier',
                    'theoritical_quantity',
                    'entred_quantity',
                    'deviation',
                    'deviation_cost',
                    'dev',  
                    'date_catchment',
                    'corrected_by',
                    'catchment',
                    'delete',
                    'refecrence_inventory',
                    'inventory_number',
                    'Tys'         
            ],
            null="",
            sep=";",
        )

    conn.commit()