from flask import Flask, request, jsonify, render_template
import pymysql
import logging
import os

app = Flask(__name__)

# Configuração do banco de dados utilizando variáveis de ambiente (ou valores padrão)
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "<2010.guicae"),
    "database": os.getenv("DB_NAME", "sensor_data")
}

# Configuração do logger para mostrar mensagens de depuração
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            cursorclass=pymysql.cursors.DictCursor  # Facilita o acesso aos resultados
        )
        logging.debug("Conexão com o banco estabelecida.")
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        raise

@app.route('/', methods=['GET', 'POST'])
def home():
    logging.debug(f"Rota '/' chamada com método {request.method}")
    if request.method == 'POST':
        logging.debug("POST recebido na raiz")
        return jsonify({'message': 'Requisição POST recebida na raiz!'}), 200
    return render_template('index.html')

@app.route('/api/sensor', methods=['POST'])
def receive_data():
    logging.debug("Endpoint /api/sensor chamado")
    try:
        # Força a leitura do JSON mesmo se o header não estiver configurado corretamente
        data = request.get_json(force=True)
        logging.debug(f"Dados recebidos: {data}")
    except Exception as e:
        logging.error(f"Erro ao ler JSON: {e}")
        return jsonify({'status': 'error', 'message': 'JSON inválido'}), 400

    if not data:
        logging.error("Nenhum dado recebido")
        return jsonify({'status': 'error', 'message': 'Dados não fornecidos ou inválidos'}), 400

    posicao = data.get('posicao_movimentada')
    estado = data.get('estado_sensor')

    if posicao is None or estado is None:
        logging.error("Parâmetros faltando no JSON")
        return jsonify({'status': 'error', 'message': 'Parâmetros faltando'}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "INSERT INTO movimentacoes (posicao, estado) VALUES (%s, %s)"
            logging.debug(f"Executando query: {query} com posicao={posicao} e estado={estado}")
            cursor.execute(query, (posicao, estado))
        conn.commit()
        logging.debug("Dados inseridos com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inserir dados no banco: {e}")
        return jsonify({'status': 'error', 'message': 'Erro no servidor'}), 500
    finally:
        try:
            conn.close()
            logging.debug("Conexão com o banco fechada.")
        except Exception as e:
            logging.error(f"Erro ao fechar a conexão: {e}")

    return jsonify({'status': 'success'}), 200

@app.route('/api/movimentacoes', methods=['GET'])
def get_movimentacoes():
    logging.debug("Endpoint /api/movimentacoes chamado")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = (
                "SELECT id, posicao, estado, "
                "DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as formatted_timestamp "
                "FROM movimentacoes ORDER BY timestamp DESC"
            )
            logging.debug(f"Executando query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
    except Exception as e:
        logging.error(f"Erro ao recuperar dados: {e}")
        return jsonify({'status': 'error', 'message': 'Erro no servidor'}), 500
    finally:
        try:
            conn.close()
            logging.debug("Conexão com o banco fechada.")
        except Exception as e:
            logging.error(f"Erro ao fechar a conexão: {e}")

    movimentacoes = [
        {
            'id': row['id'],
            'posicao': row['posicao'],
            'estado': row['estado'],
            'timestamp': row['formatted_timestamp']
        }
        for row in rows
    ]
    return jsonify(movimentacoes)

if __name__ == '__main__':
    # Em produção, desative o debug para maior segurança
    app.run(debug=True, host='0.0.0.0')



