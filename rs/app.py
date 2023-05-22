from flask import Flask, request, jsonify
from flask_cors import CORS
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
from surprise.dump import dump, load
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import psycopg2
from sklearn.preprocessing import MinMaxScaler
import pickle

app = Flask(__name__)
CORS(app)

#DB connection and configuration to use

conn = psycopg2.connect(
    database="indicadores",
    user="indicadores",
    password="N4tur3l4",
    host="ec2-34-202-165-117.compute-1.amazonaws.com",
    port="5433"
)
cur = conn.cursor()

# Load dataset and train model on server start

cur.execute("SELECT * FROM datos_pt ORDER BY id ASC")#
rows4 = cur.fetchall()#
df = pd.DataFrame(rows4, columns=['id_pt', 'codigo_pt', 'producto_terminado', 'categoria'])#

cur.execute("SELECT * FROM dim_producto_ter ORDER BY pt_id ASC")
rows = cur.fetchall()
pt_df = pd.DataFrame(rows, columns=['codigo_pt', 'producto_terminado', 'pt_id'])

cur.execute("SELECT * FROM datos_cliente ORDER BY id ASC")
rows2 = cur.fetchall()
dc_df = pd.DataFrame(rows2, columns=['id_cliente', 'id', 'tipo_cliente', 'tipo_persona', 'tipo_id', 'nombre_cliente', 'nombre_est','naturaleza', 'ciudad', 'departamento', 'pais'])

cur.execute("select  pt.id_cliente,  pt.producto_terminado, CASE WHEN max-min = 0  THEN 1 ELSE round(4*(pt.cantidad - acum.min)/(max-min)+1) END as cantidad from( SELECT  id_cliente,  producto_terminado, sum(cantidad) cantidad FROM public.datos_ventas group by id_cliente,  producto_terminado) pt inner join (select id_cliente, max(cantidad) max, min(cantidad)min from (SELECT  id_cliente,  producto_terminado, sum(cantidad) cantidad FROM public.datos_ventas group by id_cliente,  producto_terminado) t2 group by id_cliente )acum on acum.id_cliente = pt.id_cliente")
rows3 = cur.fetchall()
dv_df = pd.DataFrame(rows3, columns=['id_cliente', 'producto_terminado', 'cantidad'])
dv_df = pd.merge(dv_df, df[['producto_terminado', 'codigo_pt', 'id_pt']], on='producto_terminado', how='outer')
dv_df['id_pt'] = dv_df['id_pt'].fillna(0.0)
data_final = dv_df[['id_cliente', 'id_pt', 'cantidad']]

#Cerrar conexión DB
cur.close()
conn.close()

# #GUARDA LOS DATOS ESCALADOS
data_final.to_csv('scaled_data.csv', index=False)
svd = SVD(verbose=True, n_epochs=10)

@app.route('/train', methods=['POST'])
def train():

    # Cargar datos de ventas de clientes
    reader = Reader(line_format='user item rating ', sep=',', rating_scale=(1, 5), skip_lines=1)
    sales_data = Dataset.load_from_file('scaled_data.csv', reader=reader)
    cross_validate(svd, sales_data, measures=['RMSE', 'MAE'], cv=3, verbose=True)
    # Dividir los datos en conjuntos de entrenamiento y prueba
    trainset1, testset = train_test_split(sales_data)
    svd.fit(trainset1)
    # Evaluar modelo
    predictions = svd.test(testset)
    # Guardar el modelo
    with open('modelo_entrenado.pkl', 'wb') as f:
        pickle.dump(svd, f)
    return jsonify({'prediction': predictions})

@app.route('/predict', methods=['POST'])
def predict():
    import surprise

    # Verifica si los campos requeiridos están presentes en la petición
    if not request.json or 'user_id' not in request.json or 'item_id' not in request.json:
        return jsonify({'error': 'Missing required fields.'}), 400

    try:
        
        # Carga el modelo entrenado
        with open('modelo_entrenado.pkl', 'rb') as f:
            model = pickle.load(f)

        # Verifica si el modelo es válido y se cargó correctamente
        if not isinstance(model, surprise.prediction_algorithms.matrix_factorization.SVD):
            return jsonify({'error': 'Invalid model.'}), 500

        # Carga los datos de la petición
        user_id = request.json['user_id']
        num_items = request.json['item_id']

        # Carga el dataset de productos
        items = df

        # Carga los productos que el usuario no ha comprado
        user_items = [(model.trainset.to_raw_iid(inner_iid), rating) for (inner_iid, rating) in model.trainset.ur[model.trainset.to_inner_uid(user_id)]]
        ids_raw = [model.trainset.to_raw_iid(iid) for iid in model.trainset.all_items()]
        array = [i[0] for i in user_items if i[0] in ids_raw]
        user_unseen_items = list(set(ids_raw)-set(array))

        # Predicciones
        predictions = [model.predict(uid=user_id, iid=str(iid)) for iid in user_unseen_items]

        #Ordenar los resultados
        top_n = pd.DataFrame(predictions).sort_values(by='est', ascending=False).head(num_items)
        top_n['id_pt'] = top_n['iid'].astype(int)
        
        # Concatenar los resultados con los datos de productos
        top_n = pd.concat([top_n.set_index('id_pt'), items.set_index('id_pt')], axis=1, join='inner')
        top_n = top_n[['producto_terminado', 'codigo_pt', 'est']].reset_index().to_dict('records')
        # Retornar los resultados
        return jsonify({'prediction': top_n}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/client', methods=['POST'])
def data():
    if not request.json or 'user_id' not in request.json:
        return jsonify({'error': 'Missing required fields.'}), 400

    try:

        # Carga los datos de la petición
        user_id = request.json['user_id']

        #Carga de datos de los clientes
        data = dc_df
        filtered_data = data.loc[data['id_cliente'] == user_id]
        obj = filtered_data.to_dict('records')
        return jsonify({'data': obj}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
