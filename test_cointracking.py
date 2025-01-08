# python test_cointracking.py

import copy
import unittest
from datetime import date, timedelta

import cointracking as CT

# ========================================================================================
class TestCT(unittest.TestCase):

    def test_something(self):
        record = CT.Record(
            'type',
            '-1.0',#buy_amount
            'buy_cur',
            '2.0',#buy_value_in_fiat
            '3.0',#sell_amount
            'sell_cur',
            '4.0',#sell_value_in_fiat
            'exchange',
            'trade_date',
            '5000000000000.0',#fee_amount
            'fee_cur',
            'group',
            'comment')
        self.assertEqual(record.type, "type")
        self.assertEqual(record.buyamt, -1.0)
        self.assertEqual(record.buycur, "buy_cur")
        self.assertEqual(record.buyeur, 2.0)
        self.assertEqual(record.sellamt, 3.0)
        self.assertEqual(record.sellcur, "sell_cur")
        self.assertEqual(record.selleur, 4.0)
        self.assertEqual(record.exchange, "exchange")
        self.assertEqual(record.date, "trade_date")        
        self.assertEqual(record.day, "trad")
        self.assertEqual(record.feeamt, 5000000000000.0)
        self.assertEqual(record.feecur, "fee_cur")
        self.assertEqual(record.group, "group")
        self.assertEqual(record.comment, "comment")
        
        
        self.assertEqual(record.xml_header(), '"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"')
        self.assertEqual(record.xml(), 'type,-1.0,buy_cur,2.0,3.0,sell_cur,4.0,exchange_GROUPED,trade_date,5000000000000.0,fee_cur,group,comment')
        self.assertEqual(record.key(), 'exchange,trad,type,buy_cur,sell_cur,fee_cur,comment')
        
        record2 = copy.deepcopy(record)
        self.assertEqual(record, record2)
        
        # TODO: test __equ__ 
        #res = self.type == other.type and self.buycur == other.buycur and self.sellcur == other.sellcur and \
        #    self.feecur == other.feecur and \
        #    self.exchange == other.exchange and self.day == other.day
        record2.type = "type2"
        self.assertNotEqual(record, record2)
        
        # TODO: test __add__
        
        with self.assertRaises(RuntimeError):
            record + record2
            
        record3 = copy.deepcopy(record)
        record4 = record + record3
        self.assertEqual(record4.type, "type")
        self.assertEqual(record4.buyamt, -2.0)
        self.assertEqual(record4.buycur, "buy_cur")
        self.assertEqual(record4.buyeur, 4.0)
        self.assertEqual(record4.sellamt, 6.0)
        self.assertEqual(record4.sellcur, "sell_cur")
        self.assertEqual(record4.selleur, 8.0)
        self.assertEqual(record4.exchange, "exchange")
        self.assertEqual(record4.date, "trade_date")        
        self.assertEqual(record4.day, "trad")
        self.assertEqual(record4.feeamt, 10000000000000.0)
        self.assertEqual(record4.feecur, "fee_cur")
        self.assertEqual(record4.group, "group")
        self.assertEqual(record4.comment, "comment")
        #self.assertEqual(True, False)
        
        
        
        
        
    
            
# ========================================================================================
if __name__ == "__main__":
    unittest.main()