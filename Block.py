
import json
import hashlib

#区块类
class Block:
    """
    pre_hash:前一个区块的hash
    index:当前区块的索引
    trades:包含的交易
    timestamp:时间戳
    """
    def __init__(self,index,trades,timestamp,pre_hash,proof=0):
        self.index = index
        self.trades = trades
        self.pre_hash = pre_hash
        self.timestamp = timestamp
        self.proof = proof
