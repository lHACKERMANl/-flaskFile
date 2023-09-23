from flask import Flask, request, jsonify
import os
import pandas as pd

app = Flask(__name__)

# Создайте папку для хранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Словарь для хранения загруженных данных
data_dict = {}


def allowed_file(filename):
    # Проверка разрешенных расширений файлов (например, только .csv)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


@app.route('/upload', methods=['POST'])
def upload_file():
    # Проверка наличия файла в запросе
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # Проверка наличия имени файла и допустимого расширения
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)

        # Считывание данных из CSV-файла
        data = pd.read_csv(filename)

        # Сохранение данных в словаре, используя имя файла как ключ
        data_dict[file.filename] = data

        return jsonify({"message": "File uploaded successfully"}), 201

    return jsonify({"error": "Invalid file format"}), 400


@app.route('/files', methods=['GET'])
def get_files_list():
    # Получение списка загруженных файлов
    file_list = list(data_dict.keys())
    return jsonify({"files": file_list})


@app.route('/data/<string:filename>', methods=['GET'])
def get_data(filename):
    # Получение данных из конкретного файла с опциональной фильтрацией и сортировкой
    data = data_dict.get(filename)

    if data is None:
        return jsonify({"error": "File not found"}), 404

    # Применение фильтрации и сортировки, если они указаны в запросе
    filters = request.args.getlist('filter')
    sort_by = request.args.getlist('sort_by')

    if filters:
        for f in filters:
            data = data.query(f)

    if sort_by:
        data = data.sort_values(by=sort_by)

    return data.to_json(orient='records'), 200


if __name__ == '__main__':
    app.run(debug=True)
