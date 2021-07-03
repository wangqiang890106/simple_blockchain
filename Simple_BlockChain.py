from Block import Block
import time
import hashlib
IF_FIRST_BLOCK = False
import json

#区块链管理类
class Simple_Blockchain:
    def __init__(self):
        self.chain = []
        self.untrades = []
        self.stop_mine = False

        #初始化链的时候默认创建创世块
        self.create_first_block()

    #创世块
    def create_first_block(self):
        global  IF_FIRST_BLOCK
        if not IF_FIRST_BLOCK:
            first_block = Block(0,0,[],"0")
            self.chain.append(first_block)
            IF_FIRST_BLOCK = True


    #返回链最后一个区块
    @property
    def last_block(self):
        return self.chain[-1]

    # 创建新的区块
    def new_block(self,proof,pre_hash=None):
        pre_hash = pre_hash or self.hash(self.chain[-1])
        trades = self.untrades
        timestamp = time.time()
        block = Block(len(self.chain),trades,timestamp,pre_hash,proof)
        self.untrades = []
        self.chain.append(block)
        return block


    #工作量证明
    #循环计算sha256的前4位满足是0
    #如果其他节点打包成功，接受到同步信息停止循环挖矿
    def pow(self,last_proof):
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            if self.stop_mine:
                return -1
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        guess = F"{last_proof}{proof}"
        guess = guess.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    #添加一笔交易
    def addtrades(self,trade):
        self.untrades.append(trade)


    @staticmethod
    def hash(block):
        block_string = json.dumps(block, default=Simple_Blockchain.Block2dict).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def Block2dict(block):
        return {
            'index':block.index,
            'trades':block.trades,
            'pre_hash':block.pre_hash,
            'timestamp': block.timestamp,
            'proof':block.proof
        }

    ##验证链是否有效
    ##循环判断
    def valid_chain(self,chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            ##当前区块的pre_hash是否等于上一个区块的hash
            if block['previous_hash'] != self.hash(last_block):
                return False

            ##当前区块的proof与前一个区块的proof sha256是否前置4个0
            if not self.valid_proof(last_block['proof'],block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

