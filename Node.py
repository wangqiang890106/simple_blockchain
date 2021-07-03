from flask import Flask
from flask import jsonify
from flask import request
import requests
import json
from Block import Block
import time
from Simple_BlockChain import Simple_Blockchain
from uuid import uuid4

app = Flask(__name__)

blockchain = Simple_Blockchain()

node_identifier = str(uuid4()).replace('-','')

nodes = set()

##每个节点的资产，默认为0，每次挖矿一个奖励1
asset = 0


#挖矿
@app.route('/mine', methods=['GET'])
def mine():
    global asset

    last_block = blockchain.last_block
    last_proof = last_block.proof

    proof = blockchain.pow(last_proof)

    if proof == -1:
        response = {'msg': '挖矿停止'}
        return jsonify(response), 200


    ##挖矿区块获得奖励
    blockchain.untrades.append({"sender":"0","recev":node_identifier,"amount":"1"})
    asset += 1

    pre_hash = Simple_Blockchain.hash(last_block)

    print(proof,pre_hash)
    block = blockchain.new_block(proof,pre_hash)

    ##广播通知其他节点
    broadcast_to_nodes(block)

    response = {
        'message':"New Block Forged",
        'index':block.index,
        'transactions':block.trades,
        'proof':block.proof,
        'previous_hash':block.pre_hash,
    }
    return jsonify(response),200


#添加一笔交易
@app.route('/addtrades',methods=['POST'])
def new_trades():
    revData = request.get_json(force=True)
    print("************")
    print(revData)
    required = ["sender", "recev","amount"]
    for field in required:
        if not all(k in revData for k in required):
            response = {'msg':'参数缺失'}
            return jsonify(response), 400
        revData["timestamp"] = time.time()
    blockchain.addtrades(revData)
    response = {'msg':'成功'}
    return jsonify(response), 200


##向某个节点注册节点
@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json(force=True)
    l_nodes = values.get('nodes')
    if not l_nodes:
        response = {'msg': '参数错误'}
        return jsonify(response), 400
    for node in l_nodes:
        global nodes
        nodes.add(node)

    response = {'msg':'新节点已经注册','nodes':list(nodes)}

    return jsonify(response),201

##获取某个节点所维护的节点
@app.route('/nodes/',methods=['GET'])
def allnodes():
    global nodes
    response = {'nodes':list(nodes)}
    return jsonify(response),201


##挖出新矿的节点对其他节点进行广播
def broadcast_to_nodes(block):
    global nodes
    print(nodes)
    for node in nodes:

        ##通知其他节点停止挖矿
        url = f"http://{node}/stopmine"
        requests.get(url)


        ##通知其他节点添加区块
        url = f"http://{node}/add_block"
        headers = {'Content-Type': "application/json"}
        requests.post(url = url,data=json.dumps(block,default=Simple_Blockchain.Block2dict),headers=headers)



##广播通知其他节点停止挖矿
@app.route('/stopmine',methods=['GET'])
def broadcast_stop_mine():
    blockchain.stop_min = True
    response = {'msg': '停止成功'}
    return jsonify(response), 400



#返回所有区块
@app.route('/getallchain', methods=['GET'])
def full_chain():
    res = []
    for block in blockchain.chain:
        blockstr = json.dumps(block, default=Simple_Blockchain.Block2dict)
        res.append(blockstr)
    response={'chain':res,'length':len(res)}
    return jsonify(response),200


#添加新块
@app.route('/add_block',methods=['POST'])
def add_block():
    block_data = request.get_json()
    proof = block_data['proof']
    pre_hash = Simple_Blockchain.hash(blockchain.chain[-1])
    add = blockchain.new_block(proof,pre_hash)

    if not add:
        return "区块未被添加", 400

    return "区块已经添加", 201


##节点冲突解决
@app.route('/resolve/conflicts',methods=['GET'])
def resolve_conflicts(self):
    global nodes
    neithbours = nodes
    new_chain = None
    max_length = len(self.chain)
    for node in neithbours:
        response = requests.get(f'http://{node}/getallchain')
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            if length > max_length and self.valid_chain(chain):
                max_length = length
                new_chain = chain
    if new_chain:
        response = {'message':'链被替换','new_chain':blockchain.chain}
    else:
        response = {'message':'权威链','chain':blockchain.chain}

    return jsonify(response),200



#不同的节点 需要修改为不同的端口
if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=6000)
    #app.run(host='0.0.0.0',port=6001)
    app.run(host='0.0.0.0',port=6002)