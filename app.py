from flask import Flask, request, jsonify
import numpy as np
from openjij import SQASampler, SASampler

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

        # QUBO行列の設定
        Sij = np.array(Sij)
        Diip = np.array(Diip)
        Kj = np.array(Kj)
        lam1 = 500
        lam2 = 500
        N, M = Sij.shape
        
        qubo = {}

        # Sijの項

        for i in range(N):
            for j in range(M):
                qubo[(i*M+j, i*M+j)] = Sij[i][j]
                
        # Diipの項

        for i1 in range(N):
            for i2 in range(N):
                for j in range(M):
                    if (i1*M+j, i2*M+j) not in qubo.keys():
                        qubo[(i1*M+j, i2*M+j)] = Diip[i1][i2]
                    else:
                        qubo[(i1*M+j, i2*M+j)] += Diip[i1][i2]

        # 制約項
        for i in range(N):
            for j1 in range(M):
                for j2 in range(M):
                    if (i*M+j1, i*M+j2) not in qubo.keys():
                        qubo[(i*M+j1, i*M+j2)] = lam1
                    else:
                        qubo[(i*M+j1, i*M+j2)] += lam1
                    if j1 == j2:
                        qubo[(i*M+j1, i*M+j2)] -= 2 * lam1

        for i1 in range(N):
            for i2 in range(N):
                for j in range(M):
                    if (i1*M+j, i2*M+j) not in qubo.keys():
                        qubo[(i1*M+j, i2*M+j)] = lam2
                    else:
                        qubo[(i1*M+j, i2*M+j)] += lam2
                    if i1 == i2:
                        qubo[(i1*M+j, i2*M+j)] -= 2 * lam2 * Kj[j]
                        
        # 最適化計算               
        sampler = SASampler()
        sampleset = sampler.sample_qubo(qubo, num_reads=10)

        sample_dict = sampleset.first.sample
        sample_array = np.array([sample_dict[i] for i in range(N*M)])
        ans = sample_array.reshape(N, M)
        
        # 結果を返す
        return jsonify({
            "message": "Qij successfully processed",
            "Qij": ans.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


