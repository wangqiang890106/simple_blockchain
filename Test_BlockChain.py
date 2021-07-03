import unittest
from Simple_BlockChain import Simple_Blockchain
import time
from Block import Block
import requests
import json
import threading

##测试
class TestBlockChain(unittest.TestCase):

    def setUp(self):
        ##注册节点
        url = "http://192.168.3.220:6000/nodes/register"
        headers = {'Content-Type': "application/json"}
        data = {"nodes": ['192.168.3.220:6001', '192.168.3.220:6002']}
        res = requests.post(url=url, data=json.dumps(data), headers=headers)

        url = "http://192.168.3.220:6001/nodes/register"
        headers = {'Content-Type': "application/json"}
        data = {"nodes": ['192.168.3.220:6000', '192.168.3.220:6002']}
        res = requests.post(url=url, data=json.dumps(data), headers=headers)

        url = "http://192.168.3.220:6002/nodes/register"
        headers = {'Content-Type': "application/json"}
        data = {"nodes": ['192.168.3.220:6000', '192.168.3.220:6001']}
        res = requests.post(url=url, data=json.dumps(data), headers=headers)

        ##添加一笔交易
        url = "http://192.168.3.220:6000/addtrades"
        headers = {'Content-Type': "application/json"}
        data = {"sender": "A", "recev": "B", "amount": "1"}
        res = requests.post(url=url, data=json.dumps(data), headers=headers)

    def tearDown(self):
        pass


    #测试创世块,手动启动3个节点，验证只有一个创世块
    @unittest.skip
    def test_create_first_block(self):
        url = "http://192.168.3.220:6000/getallchain"
        res = requests.get(url)
        self.assertEqual(len(res.json()['chain']),1)


    #测试添加一笔交易
    @unittest.skip
    def test_add_trades(self):
        trade={"sender":"A", "recev":"B","amount":"1"}
        blockchain = Simple_Blockchain()
        blockchain.addtrades(trade)
        self.assertEqual(len(blockchain.untrades),1)


    #测试没有交易数据的情况下挖矿
    #需要手动启动某个节点进行测试，测试为本地启动，端口6000
    @unittest.skip
    def test_mine_no_trades(self):
        url = "http://192.168.3.220:6000/mine"
        res = requests.get(url)
        self.assertEqual(res.json()['msg'],'没有交易数据可打包')


    #测试有交易数据的情况下正常挖矿
    #需要手动启动某个节点进行测试，测试为本地启动，端口6000
    @unittest.skip
    def test_mine_trades(self):

        ##添加一笔交易
        url = "http://192.168.3.220:6000/addtrades"
        headers = {'Content-Type': "application/json"}
        data = {"sender":"A","recev":"B","amount":"1"}
        res = requests.post(url = url,data=json.dumps(data),headers=headers)

        print(res)
        self.assertEqual(res.json()['msg'],'成功')


        ##挖矿
        url = "http://192.168.3.220:6000/mine"
        res = requests.get(url)
        print((res.json()['msg']))

        ###获取最后一个区块进行验证
        url = "http://192.168.3.220:6000/getallchain"
        res2 = requests.get(url)
        str_json = json.loads(res2.json()['chain'][-1])
        index = str_json['index']

        info = f'块{index}已经被打包'
        self.assertEqual(res.json()['msg'],info)

    #测试注册新节点
    @unittest.skip
    def test_register_nodes(self):

        url = "http://192.168.3.220:6000/nodes/register"
        headers = {'Content-Type': "application/json"}
        data = {"nodes":[6000,6001,6002]}
        requests.post(url = url,data=json.dumps(data),headers=headers)

        url = "http://192.168.3.220:6000/nodes"
        res = requests.get(url)
        print(res.json()['nodes'])


    ##测试节点6000挖矿成功并广播，节点6001是否同步成功
    @unittest.skip
    def test_A_mine_B_recheck(self):

        ##节点6000挖矿
        url = "http://192.168.3.220:6000/mine"
        res = requests.get(url)
        index_6001 = res.json()['index']

        ##节点6001进行验证同步
        url = "http://192.168.3.220:6001/getallchain"
        res2 = requests.get(url)
        str_json = json.loads(res2.json()['chain'][-1])
        index_6002 = str_json['index']

        print('6001'+ str(index_6001))
        print('6002'+ str(index_6002))
        self.assertEqual(index_6001,index_6002)

    #测试节点6000 和 节点6001同时挖矿，一方成功则通知另一方停止
    def test_A_And_B_mine(self):
        t1 = threading.Thread(target=self.thread_mine,args=("192.168.3.220:6000",))
        t2 = threading.Thread(target=self.thread_mine,args=("192.168.3.220:6001",))
        t1.start()
        t2.start()


    def thread_mine(self,node):
        url = f"http://{node}/mine"
        res = requests.get(url)
        if node == "192.168.3.220:6000":self.assertEqual(res.status_code,200)
        if node == "192.168.3.220:6001":self.assertEqual(res.json()['msg'],'挖矿停止')


if __name__ == "__main__":
    unittest.main()
