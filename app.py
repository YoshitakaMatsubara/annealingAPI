from flask import Flask, request, jsonify
import numpy as np
from openjij import SASampler

app = Flask(__name__)

@app.route('/solve', methods=['POST'])
def solve():
    try:
        # JSONデータの取得
        data = request.get_json()

        # Sij, Diip, Kj を受け取る（チェックあり）
        Sij = data.get('Sij')
        Diip = data.get('Diip')
        Kj = data.get('Kj')

        if Sij is None or Diip is None or Kj is None:
            return jsonify({"error": "Missing one or more required keys: Sij, Diip, Kj"}), 400

        # Sij に2を掛ける
        sij_array = np.array(Sij)
        doubled_sij = (sij_array * 2).tolist()

        # 結果を返す
        return jsonify({
            "message": "Qij successfully processed",
            "Qij": doubled_sij
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


