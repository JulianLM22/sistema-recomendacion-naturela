from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
from surprise.dump import dump, load
import pandas as pd
import psycopg2
from sklearn.preprocessing import MinMaxScaler
import surprise
import csv
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

cur.execute("SELECT * FROM dim_producto_ter ORDER BY pt_id ASC")
rows = cur.fetchall()
pt_df = pd.DataFrame(rows, columns=['codigo_pt', 'producto_terminado', 'pt_id'])
#pt_df.to_csv("Inventario Producto Terminado.csv")

cur.execute("SELECT * FROM datos_cliente ORDER BY id ASC")
rows2 = cur.fetchall()
dc_df = pd.DataFrame(rows2, columns=['id_cliente', 'id', 'tipo_cliente', 'tipo_persona', 'tipo_id', 'nombre_cliente', 'nombre_est','naturaleza', 'ciudad', 'departamento', 'pais'])
#dc_df.to_csv("datos_clientes.csv")

cur.execute("SELECT * FROM datos_ventas ORDER BY id_v ASC")
rows3 = cur.fetchall()
dv_df = pd.DataFrame(rows3, columns=['id_v', 'tipo_cliente', 'tipo_persona', 'tipo_id', 'id_cliente', 'nombre_cliente', 'nombre_est', 'producto_terminado', 'cantidad', 'fecha_pedido'])
dv_df = pd.merge(dv_df, pt_df[['producto_terminado', 'codigo_pt', 'pt_id']], on='producto_terminado', how='outer')
dv_df['codigo_pt'] = dv_df['codigo_pt'].fillna('noCode')
dv_df['pt_id'] = dv_df['pt_id'].fillna(0.0)

#Cerrar conexión DB
cur.close()
conn.close()

# Load dataset and train model on server start

df_compras = dv_df[['id_cliente', 'pt_id', 'cantidad']]
# Agrupar las compras por cliente
compras_por_cliente = df_compras.groupby(['id_cliente','pt_id'])['cantidad'].sum().reset_index()
# Crear un objeto MinMaxScaler
scaler = MinMaxScaler(feature_range=(1, 5))
# Escalar las compras por cliente
compras_por_cliente['cantidad'] = scaler.fit_transform(compras_por_cliente[['cantidad']])
#GUARDA LOS DATOS ESCALADOS
compras_por_cliente.to_csv('scaled_data.csv', index=False)
svd = SVD(verbose=True, n_epochs=10)

@app.route('/train', methods=['POST'])
def train():

    # Cargar datos de ventas de clientes
    reader = Reader(line_format='user item rating ', sep=',', rating_scale=(1, 5), skip_lines=1)
    sales_data = Dataset.load_from_file('scaled_data.csv', reader=reader)
    cross_validate(svd, sales_data, measures=['RMSE', 'MAE'], cv=3, verbose=True)
    # Dividir los datos en conjuntos de entrenamiento y prueba
    trainset1, testset = train_test_split(sales_data, test_size=0.2)
    #tren = trainset1.build_full_trainset() 
    svd.fit(trainset1)
    # Evaluar modelo
    predictions = svd.test(testset)
    # Guardar el modelorrrrrrrrr
    with open('modelo_entrenado.pkl', 'wb') as f:
        pickle.dump(svd, f)
    return jsonify({'prediction': predictions})

@app.route('/predict', methods=['POST'])
def predict():
    import surprise

    # Check if all required fields are present in the request
    if not request.json or 'user_id' not in request.json or 'item_id' not in request.json:
        return jsonify({'error': 'Missing required fields.'}), 400

    try:
        
        # Load trained model
        with open('modelo_entrenado.pkl', 'rb') as f:
            model = pickle.load(f)

        # Check if the model is valid and loaded correctly
        if not isinstance(model, surprise.prediction_algorithms.matrix_factorization.SVD):
            return jsonify({'error': 'Invalid model.'}), 500

        # load data from request
        user_id = request.json['user_id']
        num_items = request.json['item_id']

        # Load data from items
        items = pt_df
        #items = items.rename(columns={'item_id': 'iid'})
        # Get top n recommendations for the user

        # Get Items from User
        user_items = [(model.trainset.to_raw_iid(inner_iid), rating) for (inner_iid, rating) in model.trainset.ur[model.trainset.to_inner_uid(user_id)]]
        ids_raw = [model.trainset.to_raw_iid(iid) for iid in model.trainset.all_items()]
        array = [i[0] for i in user_items if i[0] not in ids_raw]
        double_array = [float(x) for x in array]
        user_unseen_items = list(set(ids_raw)-set(double_array))

        # Make Predictions
        predictions = [model.predict(uid=user_id, iid=str(iid)) for iid in user_unseen_items]

        #Order By value
        top_n = pd.DataFrame(predictions).sort_values(by='est', ascending=False).head(num_items)
        top_n['pt_id'] = top_n['iid'].astype(float)
        
        
        top_n = pd.concat([top_n.set_index('pt_id'), items.set_index('pt_id')], axis=1, join='inner')
        top_n = top_n[['producto_terminado', 'codigo_pt', 'est']].reset_index().to_dict('records')
        # Return prediction
        return jsonify({'prediction': top_n}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/client', methods=['POST'])
def data():
    if not request.json or 'user_id' not in request.json:
        return jsonify({'error': 'Missing required fields.'}), 400

    try:

        # load data from request
        user_id = request.json['user_id']

        #Load clients data
        data = dc_df
        filtered_data = data.loc[data['id_cliente'] == user_id]
        obj = filtered_data.to_dict('records')
        return jsonify({'data': obj}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los valores ingresados por el usuario
        user_id = (request.form['valor1'])
        num_items = (request.form['valor2'])
    # Check if all required fields are present in the request
        if not request.form or 'valor1' not in request.form or 'valor2' not in request.form:
            return render_template('formulario.html', resultado={'error': 'Missing required fields.'})

        try:
            user_id = str(request.form['valor1'])
            num_items = int(request.form['valor2'])
            # Load trained model
            model_tuple = load('model.pkl')
            model = model_tuple[1]

            # Check if the model is valid and loaded correctly
            if not isinstance(model, surprise.prediction_algorithms.matrix_factorization.SVD):
                return jsonify({'error': 'Invalid model.'}), 500

            # load data from request
            #user_id = request.json['user_id']
            #num_items = request.json['item_id']

            # Load data from items
            items = pd.read_csv('nombre_productos.csv', sep=';')
            #items = items.rename(columns={'item_id': 'iid'})
            # Get top n recommendations for the user

            # Get Items from User
            user_items = model.trainset.ur[model.trainset.to_inner_uid(user_id)]
            user_unseen_items = [iid for iid in model.trainset.all_items() if iid not in user_items]

            # Make Predictions
            predictions = [model.predict(uid=user_id, iid=str(iid)) for iid in user_unseen_items]

            #Order By value
            top_n = pd.DataFrame(predictions).sort_values(by='est', ascending=False).head(num_items)
            top_n['item_id'] = top_n['iid'].astype(int)

            top_n = pd.concat([top_n.set_index('item_id'), items.set_index('item_id')], axis=1, join='inner')
            top_n = top_n[['item_name', 'est']].reset_index().to_dict('records')
            # Return prediction
            #return jsonify({'prediction': top_n}), 200
            # Renderizar el template con el resultado
            top_n = pd.DataFrame(top_n)
            top_n = top_n.rename(columns={'item_name': 'Nombre del producto', 'item_id': 'Identificador del producto', 'est': 'Valor recomendación (1-5)'})

            result_dict = top_n.to_dict(orient='records')

            # Renderizar el template con el resultado
            return render_template('resultado.html', resultado=result_dict)

        except Exception as e:
            #return jsonify({'error': str(e)}), 500
            return render_template('formulario.html', resultado={'error': str(e)})

        
    else:
        # Renderizar el template del formulario
        return render_template('formulario.html', resultado={'info': 'Favor diligencie los valores'})

if __name__ == '__main__':
    app.run()
