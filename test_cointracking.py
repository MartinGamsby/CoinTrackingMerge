# python test_cointracking.py

import copy
import unittest
from datetime import date, timedelta

import cointracking as CT

from decimal import Decimal

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
            'comment',
            'trade_timestamp')
        self.assertEqual(record.type, "type")
        self.assertEqual(record.buyamt, -1.0)
        self.assertEqual(record.buycur, "buy_cur")
        self.assertEqual(record.buyeur, 2.0)
        self.assertEqual(record.sellamt, 3.0)
        self.assertEqual(record.sellcur, "sell_cur")
        self.assertEqual(record.selleur, 4.0)
        self.assertEqual(record.exchange, "exchange")
        self.assertEqual(record.date, "trade_date")  
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(record.day, "trad")
        else:
            self.assertEqual(record.day, "trade_date")
        self.assertEqual(record.feeamt, 5000000000000.0)
        self.assertEqual(record.feecur, "fee_cur")
        self.assertEqual(record.group, "group")
        self.assertEqual(record.comment, "comment")
        
        
        self.assertEqual(record.xml_header(), '"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"')
        self.assertEqual(record.xml(), 'type,-1.0,buy_cur,2.0,3.0,sell_cur,4.0,exchange,trade_date,5000000000000.0,fee_cur,group,comment')
          
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(record.key(), 'exchange,trad,type,buy_cur,sell_cur,fee_cur,comment')
        else:
            self.assertEqual(record.key(), 'exchange,trade_date,type,buy_cur,sell_cur,fee_cur,comment')
        
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
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(record4.day, "trad")
        else:            
            self.assertEqual(record4.day, "trade_date")
        self.assertEqual(record4.feeamt, 10000000000000.0)
        self.assertEqual(record4.feecur, "fee_cur")
        self.assertEqual(record4.group, "group")
        self.assertEqual(record4.comment, "comment")
        
# ========================================================================================
    def compare_xml(self, records, expected_xml):
        output_xml = records[0].xml_header() + "\n"
        for record in records:
            output_xml += record.xml() + '\n'
        self.maxDiff = None
        
        if output_xml != expected_xml:
            print("=====\n",output_xml,"\n=====")
        self.assertEqual(output_xml, expected_xml)
        
# ========================================================================================
    def print_input(self, all_records):
        for record in all_records:
            print(record)
                
# ========================================================================================
    def print_output(self, output, exchange_trades_input_count):
        for o in output:
            print(o, exchange_trades_input_count[o], "to", len(output[o]), ":")
            for record in output[o]:
                print(record)
        
# ========================================================================================
    def test_2deposits(self):
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_2deposits.xml")
        self.assertEqual(exchange_trades_input_count["Coinbase Staking"], 2)
        
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
                
        records = output["Coinbase Staking"]
        # TODO: Don't use a bool like that...
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 1)
            
            merged = records[0]
            self.assertEqual(merged.buyamt, 15.0)
            self.assertEqual(merged.buyeur, Decimal('3661.20621312'))
            
            
            # This found that it was the WRONG date! It should be the last one.
            # Because the xml isn't sorted in trade time. It's by ... added time or something.
            self.compare_xml(records, 
    '"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,15.00000000,SOL2,3661.20621312,0,,0,Coinbase Staking,2024-04-09 16:57:17,0,SOL2,,\n')
                    
            #write_output(args, output, "test_2deposits.csv")

# ========================================================================================
    def test_coinbase(self):
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_coinbase.xml", dumb_group_for_early_dates=False, group_dumb_groups=False)
        self.assertEqual(exchange_trades_input_count["Coinbase"], 56)
                
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["Coinbase"]
        
        # TODO: Don't use a bool like that...
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 21)
        
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,50.00000000,CAD,50.00000000,0,,0,Coinbase,2021-02-26 17:43:55,0E-8,,,direct trading funds\n\
Trade,0.00078641,BTC,47.91681062,50.00000000,CAD,50.00004425,Coinbase,2021-02-26 17:43:56,1.99000000,CAD,,\n\
Withdrawal,0,,0,0.00078641,BTC,47.91681062,Coinbase,2021-02-26 17:53:56,0E-8,BTC,,\n\
Deposit,0.00078641,BTC,47.91681062,0,,0,Coinbase,2021-02-26 17:58:14,0E-8,BTC,,\n\
Spend,0,,0,0.00030228,BTC,18.09482540,Coinbase,2021-02-27 12:55:24,0.00004762,BTC,,Coinbase Commerce order receipt: \n\
Withdrawal,0,,0,0.00048413,BTC,33.37531220,Coinbase,2021-03-15 12:55:36,0E-8,BTC,,\n\
Trade,0.00439191,BTC,282.25808606,300.00000000,CAD,299.99983561,Coinbase,2021-03-25 14:22:58,11.51000000,CAD,,\n\
Deposit,300.00000000,CAD,299.99983561,0,,0,Coinbase,2021-03-25 14:22:58,0E-8,CAD,,direct trading funds\n\
Withdrawal,0,,0,0.00439191,BTC,282.25808606,Coinbase,2021-03-25 14:27:33,0.00002338,BTC,,\n\
Deposit,1.20000000,ATOM2,19.76221302,0,,0,Coinbase,2021-07-06 19:26:08,0E-8,ATOM2,,\n\
Withdrawal,0,,0,1.20000000,ATOM2,19.76221302,Coinbase,2021-07-06 19:26:09,0.00250000,ATOM2,,\n\
Deposit,0.00001258,BTC,0.27341687,0,,0,Coinbase,2022-11-29 01:28:38,0E-8,BTC,,\n\
Deposit,0.10000000,BTC,9274.22700000,0,,0,Coinbase,2024-04-04 23:52:09,0E-8,BTC,,\n\
Trade,10.00000000,SOL2,2486.99658263,0.02701109,BTC,2505.06980178,Coinbase,2024-04-05 00:12:05,0.00016110,BTC,,advanced_trade_buy\n\
Trade,168.40375822,RENDER,0E-8,0.02398883,BTC,2224.77854884,Coinbase,2024-04-05 00:16:00,0E-8,RENDER,,\n\
Withdrawal,0,,0,10.00000000,SOL2,2486.99658263,Coinbase,2024-04-05 00:17:25,0E-8,SOL2,,\n\
Trade,5.00000000,SOL2,1242.91803778,0.01254375,BTC,1226.08344994,Coinbase,2024-04-08 11:05:54,0.00004375,BTC,,advanced_trade_buy\n\
Withdrawal,0,,0,5.00000000,SOL2,1174.20963049,Coinbase,2024-04-09 16:57:17,0E-8,SOL2,,\n\
Staking,0.00708067,SOL2,1.54322480,0,,0,Coinbase,2024-04-13 19:12:59,0,SOL2,,\n\
Trade,5.00000000,SOL2,979.20741806,0.01003500,BTC,926.22869370,Coinbase,2024-04-13 20:07:26,0.00003500,BTC,,advanced_trade_buy\n\
Staking,0.09954981,SOL2,20.67178207,0,,0,Coinbase,2024-06-04 06:35:51,0,SOL2,,\n')


# ========================================================================================
    def test_coinbase2(self):
        # dumb_group_for_early_dates is the only difference from test_coinbase
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_coinbase.xml", dumb_group_for_early_dates=True, group_dumb_groups=False)
        self.assertEqual(exchange_trades_input_count["Coinbase"], 56)
                
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["Coinbase"]
        
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 18)
        
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,50.00000000,CAD,50.00000000,0,,0,Coinbase,2021-12-31 23:34:45,0E-8,,,direct trading funds\n\
Deposit,0.00078641,BTC,47.91681062,0,,0,Coinbase,2021-12-31 23:34:45,0E-8,BTC,,\n\
Spend,0,,0,0.00030228,BTC,18.09482540,Coinbase,2021-12-31 23:34:45,0.00004762,BTC,,Coinbase Commerce order receipt: \n\
Trade,0.00517832,BTC,330.17489668,350.00000000,CAD,349.99987986,Coinbase,2021-12-31 23:34:45,13.50000000,CAD,,\n\
Deposit,300.00000000,CAD,299.99983561,0,,0,Coinbase,2021-12-31 23:34:45,0E-8,CAD,,direct trading funds\n\
Withdrawal,0,,0,0.00566245,BTC,363.55020888,Coinbase,2021-12-31 23:34:45,0.00002338,BTC,,\n\
Deposit,1.20000000,ATOM2,19.76221302,0,,0,Coinbase,2021-12-31 23:34:45,0E-8,ATOM2,,\n\
Withdrawal,0,,0,1.20000000,ATOM2,19.76221302,Coinbase,2021-12-31 23:34:45,0.00250000,ATOM2,,\n\
Deposit,0.00001258,BTC,0.27341687,0,,0,Coinbase,2022-12-31 23:34:45,0E-8,BTC,,\n\
Deposit,0.10000000,BTC,9274.22700000,0,,0,Coinbase,2024-04-04 23:52:09,0E-8,BTC,,\n\
Trade,10.00000000,SOL2,2486.99658263,0.02701109,BTC,2505.06980178,Coinbase,2024-04-05 00:12:05,0.00016110,BTC,,advanced_trade_buy\n\
Trade,168.40375822,RENDER,0E-8,0.02398883,BTC,2224.77854884,Coinbase,2024-04-05 00:16:00,0E-8,RENDER,,\n\
Withdrawal,0,,0,10.00000000,SOL2,2486.99658263,Coinbase,2024-04-05 00:17:25,0E-8,SOL2,,\n\
Trade,5.00000000,SOL2,1242.91803778,0.01254375,BTC,1226.08344994,Coinbase,2024-04-08 11:05:54,0.00004375,BTC,,advanced_trade_buy\n\
Withdrawal,0,,0,5.00000000,SOL2,1174.20963049,Coinbase,2024-04-09 16:57:17,0E-8,SOL2,,\n\
Staking,0.00708067,SOL2,1.54322480,0,,0,Coinbase,2024-04-13 19:12:59,0,SOL2,,\n\
Trade,5.00000000,SOL2,979.20741806,0.01003500,BTC,926.22869370,Coinbase,2024-04-13 20:07:26,0.00003500,BTC,,advanced_trade_buy\n\
Staking,0.09954981,SOL2,20.67178207,0,,0,Coinbase,2024-06-04 06:35:51,0,SOL2,,\n')

# ========================================================================================
    def test_coinbase3(self):
        # group_dumb_groups is the only difference from test_coinbase2
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_coinbase.xml", dumb_group_for_early_dates=True, group_dumb_groups=True)
        self.assertEqual(exchange_trades_input_count["Coinbase"], 56)
                
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["Coinbase"]
        
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 18)
        
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,50.00000000,CAD,50.00000000,0,,0,Coinbase,2023-12-31 23:34:45,0E-8,,,direct trading funds\n\
Deposit,0.00078641,BTC,47.91681062,0,,0,Coinbase,2023-12-31 23:34:45,0E-8,BTC,,\n\
Spend,0,,0,0.00030228,BTC,18.09482540,Coinbase,2023-12-31 23:34:45,0.00004762,BTC,,Coinbase Commerce order receipt: \n\
Trade,0.00517832,BTC,330.17489668,350.00000000,CAD,349.99987986,Coinbase,2023-12-31 23:34:45,13.50000000,CAD,,\n\
Deposit,300.00000000,CAD,299.99983561,0,,0,Coinbase,2023-12-31 23:34:45,0E-8,CAD,,direct trading funds\n\
Withdrawal,0,,0,0.00566245,BTC,363.55020888,Coinbase,2023-12-31 23:34:45,0.00002338,BTC,,\n\
Deposit,1.20000000,ATOM2,19.76221302,0,,0,Coinbase,2023-12-31 23:34:45,0E-8,ATOM2,,\n\
Withdrawal,0,,0,1.20000000,ATOM2,19.76221302,Coinbase,2023-12-31 23:34:45,0.00250000,ATOM2,,\n\
Deposit,0.00001258,BTC,0.27341687,0,,0,Coinbase,2023-12-31 23:34:45,0E-8,BTC,,\n\
Deposit,0.10000000,BTC,9274.22700000,0,,0,Coinbase,2024-04-04 23:52:09,0E-8,BTC,,\n\
Trade,10.00000000,SOL2,2486.99658263,0.02701109,BTC,2505.06980178,Coinbase,2024-04-05 00:12:05,0.00016110,BTC,,advanced_trade_buy\n\
Trade,168.40375822,RENDER,0E-8,0.02398883,BTC,2224.77854884,Coinbase,2024-04-05 00:16:00,0E-8,RENDER,,\n\
Withdrawal,0,,0,10.00000000,SOL2,2486.99658263,Coinbase,2024-04-05 00:17:25,0E-8,SOL2,,\n\
Trade,5.00000000,SOL2,1242.91803778,0.01254375,BTC,1226.08344994,Coinbase,2024-04-08 11:05:54,0.00004375,BTC,,advanced_trade_buy\n\
Withdrawal,0,,0,5.00000000,SOL2,1174.20963049,Coinbase,2024-04-09 16:57:17,0E-8,SOL2,,\n\
Staking,0.00708067,SOL2,1.54322480,0,,0,Coinbase,2024-04-13 19:12:59,0,SOL2,,\n\
Trade,5.00000000,SOL2,979.20741806,0.01003500,BTC,926.22869370,Coinbase,2024-04-13 20:07:26,0.00003500,BTC,,advanced_trade_buy\n\
Staking,0.09954981,SOL2,20.67178207,0,,0,Coinbase,2024-06-04 06:35:51,0,SOL2,,\n')


# ========================================================================================
    def test_wallet(self):
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_wallet.xml", dumb_group_for_early_dates=False)
        self.assertEqual(exchange_trades_input_count["ETH Wallet"], 45)
                
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["ETH Wallet"]
        
        # TODO: Don't use a bool like that...
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 38)
        
        # Ugh the 0.013 ETH deposit should not be grouped...
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,48.25676778,C20,217.26034983,0,,0,ETH Wallet,2021-05-26 16:07:27,0E-8,C20,MetaMask ETH,\n\
Deposit,100.00000000,USDT,120.65663480,0,,0,ETH Wallet,2021-05-27 21:17:43,0E-8,USDT,MetaMask ETH,\n\
Deposit,0.01300000,ETH,43.34370596,0,,0,ETH Wallet,2021-05-28 00:43:24,0E-8,ETH,MetaMask ETH,\n\
Trade,36.33531495,C20,121.97867282,100.00000000,USDT,122.86407793,ETH Wallet,2021-06-23 16:43:20,0E-8,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,84.59208273,C20,283.97790545,ETH Wallet,2021-06-23 16:46:08,0E-8,C20,MetaMask ETH,\n\
Other Fee,0,,0,0.00977659,ETH,36.20488193,ETH Wallet,2021-11-02 13:47:09,0,ETH,MetaMask ETH,\n\
Deposit,0.20000000,ETH,1064.90969098,0,,0,ETH Wallet,2021-11-24 20:21:14,0E-8,ETH,MetaMask ETH,\n\
Trade,0.10000000,WETH,534.02886694,0.10508732,ETH,561.01903850,ETH Wallet,2021-11-24 20:40:48,0.00508732,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.03331793,ETH,177.87053974,ETH Wallet,2021-11-24 20:53:34,0,ETH,MetaMask ETH,\n\
Trade,3520000.00000000,MCC7,0E-8,0.09805187,WETH,523.62501115,ETH Wallet,2021-11-24 20:53:34,0E-8,,MetaMask ETH,\n\
Deposit,0.20000000,ETH,1122.07629697,0,,0,ETH Wallet,2021-11-29 20:35:39,0E-8,ETH,MetaMask ETH,\n\
Airdrop,1824630.24008000,MCC7,0E-8,0,,0,ETH Wallet,2021-11-30 03:25:34,0E-8,,MetaMask ETH,\n\
Trade,32000000.00000000,MCC7,0E-8,0.23388450,ETH,1379.49936405,ETH Wallet,2021-11-30 13:13:52,0.01055823,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00505434,ETH,24.77325428,ETH Wallet,2021-12-13 18:15:21,0E-8,ETH,MetaMask ETH,\n\
Deposit,0.20788584,ETH,1003.36542415,0,,0,ETH Wallet,2021-12-14 16:43:34,0E-8,ETH,MetaMask ETH,\n\
Trade,0E-8,ETH,0E-8,37344630.24008000,MCC7,8.23123499,ETH Wallet,2021-12-14 17:50:28,0.02330792,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00573200,ETH,27.84307647,ETH Wallet,2021-12-14 17:50:28,0E-8,ETH,MetaMask ETH,\n\
Trade,45097721.34300000,MCC8,0E-8,0.19319670,ETH,938.44729707,ETH Wallet,2021-12-14 17:51:48,0.01181433,ETH,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,45097721.34300000,MCC8,0E-8,ETH Wallet,2021-12-14 17:51:49,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Other Fee,0,,0,0.00565252,ETH,27.20701890,ETH Wallet,2022-01-05 14:51:45,0E-8,ETH,MetaMask ETH,\n\
Deposit,0.73374020,ETH,2989.68200232,0,,0,ETH Wallet,2022-01-08 01:52:21,0E-8,ETH,MetaMask ETH,\n\
Airdrop,10863.60000000,REFI_DIV,0E-8,0,,0,ETH Wallet,2022-01-08 01:57:19,0E-8,,MetaMask ETH,\n\
Trade,10863.60000000,REFI,47.07396969,0.44864043,ETH,1828.02050077,ETH Wallet,2022-01-08 01:57:19,0.02820692,ETH,MetaMask ETH,\n\
Trade,0.00000100,CAD,0.00000100,10863.60000000,REFI_DIV,0E-8,ETH Wallet,2022-01-08 01:57:20,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,0.00001000,CAD,0.00001000,10863.60000000,REFI,47.07416451,ETH Wallet,2022-01-08 01:57:20,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,1110.60000000,GY,0E-8,0.20340643,ETH,828.79547543,ETH Wallet,2022-01-08 02:01:09,0.02632927,ETH,MetaMask ETH,\n\
Expense (non taxable),0,,0,0.01904957,ETH,79.00773218,ETH Wallet,2022-01-13 16:14:13,0.00904957,ETH,MetaMask ETH,rekt (or something like that) fee -- I got nothing from it in the end\n\
Deposit,90.23075198,C20,450.69315205,0,,0,ETH Wallet,2022-01-18 17:12:10,0E-8,C20,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,1110.60000000,GY,15.73796342,ETH Wallet,2022-02-01 02:01:09,0E-8,,MetaMask ETH,Can\'t sell (project gone)\n\
Other Fee,0,,0,0.00432737,ETH,15.38108147,ETH Wallet,2022-02-28 16:15:59,0E-8,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,90.23075198,C20,29.14229756,ETH Wallet,2022-04-05 00:51:19,0E-8,,MetaMask ETH,Manual entry -- it wasn\'t a 1-1 trade, but Invictus moved from ETH to MATIC, so it\'s the same. The next transaction wasn\'t technically an airdrop, it was the value of the C20 I had in the ETH wallet\n\
Trade,434724795.49968743,PEPE4,133.29771952,0.05882820,ETH,146.93115979,ETH Wallet,2023-04-22 01:59:23,0.00482820,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00200175,ETH,5.00785671,ETH Wallet,2023-04-24 12:58:47,0E-8,ETH,MetaMask ETH,\n\
Trade,0.11679962,ETH,291.92842464,200000000.00000000,PEPE4,373.02769460,ETH Wallet,2023-05-01 13:06:23,0.01304824,ETH,MetaMask ETH,\n\
Deposit,965.08539706,NEXO,1844.78400315,0,,0,ETH Wallet,2024-03-02 18:53:59,0E-8,NEXO,MetaMask ETH,\n\
Trade,0.28469370,ETH,1325.65007746,234724795.49968743,PEPE4,1350.22184894,ETH Wallet,2024-03-02 18:57:47,0E-8,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00185977,ETH,8.61169098,ETH Wallet,2024-03-02 23:18:23,0E-8,ETH,MetaMask ETH,\n\
Trade,0.38620501,ETH,1788.32769644,965.08539706,NEXO,1830.60068464,ETH Wallet,2024-03-02 23:19:35,0.00723852,ETH,MetaMask ETH,\n')

# ========================================================================================
    def test_wallet2(self):
        # dumb_group_for_early_dates is the only difference from test_wallet
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_wallet.xml", dumb_group_for_early_dates=True, group_dumb_groups=False)
        self.assertEqual(exchange_trades_input_count["ETH Wallet"], 45)
        
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["ETH Wallet"]
        
        # TODO: Don't use a bool like that...
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 31)
        
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,48.25676778,C20,217.26034983,0,,0,ETH Wallet,2021-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Deposit,100.00000000,USDT,120.65663480,0,,0,ETH Wallet,2021-12-31 23:34:45,0E-8,USDT,MetaMask ETH,\n\
Trade,36.33531495,C20,121.97867282,100.00000000,USDT,122.86407793,ETH Wallet,2021-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,84.59208273,C20,283.97790545,ETH Wallet,2021-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Trade,0.10000000,WETH,534.02886694,0.10508732,ETH,561.01903850,ETH Wallet,2021-12-31 23:34:45,0.00508732,ETH,MetaMask ETH,\n\
Trade,3520000.00000000,MCC7,0E-8,0.09805187,WETH,523.62501115,ETH Wallet,2021-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Airdrop,1824630.24008000,MCC7,0E-8,0,,0,ETH Wallet,2021-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Trade,32000000.00000000,MCC7,0E-8,0.23388450,ETH,1379.49936405,ETH Wallet,2021-12-31 23:34:45,0.01055823,ETH,MetaMask ETH,\n\
Deposit,0.62088584,ETH,3233.69511806,0,,0,ETH Wallet,2021-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.05388086,ETH,266.69175242,ETH Wallet,2021-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Trade,0E-8,ETH,0E-8,37344630.24008000,MCC7,8.23123499,ETH Wallet,2021-12-31 23:34:45,0.02330792,ETH,MetaMask ETH,\n\
Trade,45097721.34300000,MCC8,0E-8,0.19319670,ETH,938.44729707,ETH Wallet,2021-12-31 23:34:45,0.01181433,ETH,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,45097721.34300000,MCC8,0E-8,ETH Wallet,2021-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Deposit,0.73374020,ETH,2989.68200232,0,,0,ETH Wallet,2022-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Trade,10863.60000000,REFI,47.07396969,0.44864043,ETH,1828.02050077,ETH Wallet,2022-12-31 23:34:45,0.02820692,ETH,MetaMask ETH,\n\
Airdrop,10863.60000000,REFI_DIV,0E-8,0,,0,ETH Wallet,2022-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Trade,0.00000100,CAD,0.00000100,10863.60000000,REFI_DIV,0E-8,ETH Wallet,2022-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,0.00001000,CAD,0.00001000,10863.60000000,REFI,47.07416451,ETH Wallet,2022-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,1110.60000000,GY,0E-8,0.20340643,ETH,828.79547543,ETH Wallet,2022-12-31 23:34:45,0.02632927,ETH,MetaMask ETH,\n\
Expense (non taxable),0,,0,0.01904957,ETH,79.00773218,ETH Wallet,2022-12-31 23:34:45,0.00904957,ETH,MetaMask ETH,rekt (or something like that) fee -- I got nothing from it in the end\n\
Deposit,90.23075198,C20,450.69315205,0,,0,ETH Wallet,2022-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,1110.60000000,GY,15.73796342,ETH Wallet,2022-12-31 23:34:45,0E-8,,MetaMask ETH,Can\'t sell (project gone)\n\
Other Fee,0,,0,0.00997989,ETH,42.58810037,ETH Wallet,2022-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,90.23075198,C20,29.14229756,ETH Wallet,2022-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry -- it wasn\'t a 1-1 trade, but Invictus moved from ETH to MATIC, so it\'s the same. The next transaction wasn\'t technically an airdrop, it was the value of the C20 I had in the ETH wallet\n\
Trade,434724795.49968743,PEPE4,133.29771952,0.05882820,ETH,146.93115979,ETH Wallet,2023-12-31 23:34:45,0.00482820,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00200175,ETH,5.00785671,ETH Wallet,2023-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Trade,0.11679962,ETH,291.92842464,200000000.00000000,PEPE4,373.02769460,ETH Wallet,2023-12-31 23:34:45,0.01304824,ETH,MetaMask ETH,\n\
Deposit,965.08539706,NEXO,1844.78400315,0,,0,ETH Wallet,2024-03-02 18:53:59,0E-8,NEXO,MetaMask ETH,\n\
Trade,0.28469370,ETH,1325.65007746,234724795.49968743,PEPE4,1350.22184894,ETH Wallet,2024-03-02 18:57:47,0E-8,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00185977,ETH,8.61169098,ETH Wallet,2024-03-02 23:18:23,0E-8,ETH,MetaMask ETH,\n\
Trade,0.38620501,ETH,1788.32769644,965.08539706,NEXO,1830.60068464,ETH Wallet,2024-03-02 23:19:35,0.00723852,ETH,MetaMask ETH,\n')

# ========================================================================================
    def test_wallet3(self):
        # group_dumb_groups is the only difference from test_wallet2
        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_wallet.xml", dumb_group_for_early_dates=True, group_dumb_groups=True)
        self.assertEqual(exchange_trades_input_count["ETH Wallet"], 45)
        
        #self.print_input(all_records)
        #self.print_output(output, exchange_trades_input_count)
        
        records = output["ETH Wallet"]
        
        # TODO: Don't use a bool like that...
        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.assertEqual(len(records), 31)
        
            self.compare_xml(records, 
'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
Deposit,48.25676778,C20,217.26034983,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Deposit,100.00000000,USDT,120.65663480,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,USDT,MetaMask ETH,\n\
Trade,36.33531495,C20,121.97867282,100.00000000,USDT,122.86407793,ETH Wallet,2023-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,84.59208273,C20,283.97790545,ETH Wallet,2023-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Trade,0.10000000,WETH,534.02886694,0.10508732,ETH,561.01903850,ETH Wallet,2023-12-31 23:34:45,0.00508732,ETH,MetaMask ETH,\n\
Trade,3520000.00000000,MCC7,0E-8,0.09805187,WETH,523.62501115,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Airdrop,1824630.24008000,MCC7,0E-8,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Trade,32000000.00000000,MCC7,0E-8,0.23388450,ETH,1379.49936405,ETH Wallet,2023-12-31 23:34:45,0.01055823,ETH,MetaMask ETH,\n\
Deposit,0.62088584,ETH,3233.69511806,0,,0,ETH Wallet,2023-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.05388086,ETH,266.69175242,ETH Wallet,2023-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Trade,0E-8,ETH,0E-8,37344630.24008000,MCC7,8.23123499,ETH Wallet,2023-12-31 23:34:45,0.02330792,ETH,MetaMask ETH,\n\
Trade,45097721.34300000,MCC8,0E-8,0.19319670,ETH,938.44729707,ETH Wallet,2023-12-31 23:34:45,0.01181433,ETH,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,45097721.34300000,MCC8,0E-8,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Deposit,0.73374020,ETH,2989.68200232,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Trade,10863.60000000,REFI,47.07396969,0.44864043,ETH,1828.02050077,ETH Wallet,2023-12-31 23:34:45,0.02820692,ETH,MetaMask ETH,\n\
Airdrop,10863.60000000,REFI_DIV,0E-8,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,\n\
Trade,0.00000100,CAD,0.00000100,10863.60000000,REFI_DIV,0E-8,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,0.00001000,CAD,0.00001000,10863.60000000,REFI,47.07416451,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry - can\'t sell (project failed) - wrong date in transaction\n\
Trade,1110.60000000,GY,0E-8,0.20340643,ETH,828.79547543,ETH Wallet,2023-12-31 23:34:45,0.02632927,ETH,MetaMask ETH,\n\
Expense (non taxable),0,,0,0.01904957,ETH,79.00773218,ETH Wallet,2023-12-31 23:34:45,0.00904957,ETH,MetaMask ETH,rekt (or something like that) fee -- I got nothing from it in the end\n\
Deposit,90.23075198,C20,450.69315205,0,,0,ETH Wallet,2023-12-31 23:34:45,0E-8,C20,MetaMask ETH,\n\
Trade,0.00001000,CAD,0.00001000,1110.60000000,GY,15.73796342,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,Can\'t sell (project gone)\n\
Other Fee,0,,0,0.00997989,ETH,42.58810037,ETH Wallet,2023-12-31 23:34:45,0,ETH,MetaMask ETH,\n\
Withdrawal,0,,0,90.23075198,C20,29.14229756,ETH Wallet,2023-12-31 23:34:45,0E-8,,MetaMask ETH,Manual entry -- it wasn\'t a 1-1 trade, but Invictus moved from ETH to MATIC, so it\'s the same. The next transaction wasn\'t technically an airdrop, it was the value of the C20 I had in the ETH wallet\n\
Trade,434724795.49968743,PEPE4,133.29771952,0.05882820,ETH,146.93115979,ETH Wallet,2023-12-31 23:34:45,0.00482820,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00200175,ETH,5.00785671,ETH Wallet,2023-12-31 23:34:45,0E-8,ETH,MetaMask ETH,\n\
Trade,0.11679962,ETH,291.92842464,200000000.00000000,PEPE4,373.02769460,ETH Wallet,2023-12-31 23:34:45,0.01304824,ETH,MetaMask ETH,\n\
Deposit,965.08539706,NEXO,1844.78400315,0,,0,ETH Wallet,2024-03-02 18:53:59,0E-8,NEXO,MetaMask ETH,\n\
Trade,0.28469370,ETH,1325.65007746,234724795.49968743,PEPE4,1350.22184894,ETH Wallet,2024-03-02 18:57:47,0E-8,ETH,MetaMask ETH,\n\
Other Fee,0,,0,0.00185977,ETH,8.61169098,ETH Wallet,2024-03-02 23:18:23,0E-8,ETH,MetaMask ETH,\n\
Trade,0.38620501,ETH,1788.32769644,965.08539706,NEXO,1830.60068464,ETH Wallet,2024-03-02 23:19:35,0.00723852,ETH,MetaMask ETH,\n')

# TODO: Need to add to_add in contracking.py
## ========================================================================================
#    def test_trades(self):
#        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_trades.xml")
#        self.assertEqual(exchange_trades_input_count["Kucoin Trading"], 124)
#                
#        #self.print_input(all_records)
#        #self.print_output(output, exchange_trades_input_count)
#        
#        records = output["Kucoin Trading"]
#        
#        # TODO: Don't use a bool like that...
#        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
#            self.assertEqual(len(records), 4)
#        
#            self.compare_xml(records, 
#'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
#Trade,33.52680000,KCS,513.28362754,0.01681135,BTC,510.02840918,Kucoin Trading,2022-06-14 05:20:27,0.00003384,BTC,,\n\
#Reward / Bonus,0.00000420,BTC,0.10838170,0,,0,Kucoin Trading,2022-06-20 09:31:00,0,BTC,,\n\
#Other Fee,0,,0,0.00764043,KCS,0.10091379,Kucoin Trading,2022-06-20 10:30:39,0,KCS,,\n\
#Reward / Bonus,3.5E-7,BTC,0.00935106,0,,0,Kucoin Trading,2022-06-20 10:30:40,0E-8,,,\n')
        
## ========================================================================================
#    def test_dot(self):
#        output, exchange_trades_input_count, all_records = CT.group_xml(CT.get_args(), "test_dot.xml")
#        self.assertEqual(exchange_trades_input_count["Kucoin Trading"], 7)
#                
#        self.print_input(all_records)
#        self.print_output(output, exchange_trades_input_count)
#        
#        records = output["Kucoin Trading"]
#        
#        # TODO: Don't use a bool like that...
#        if CT.GROUP_BY_YEAR_INSTEAD_OF_DAYS:
#            self.assertEqual(len(records), 1)
#        
#            self.compare_xml(records, 
#'"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"\n\
#Trade,9.88080000,DOT3L,0,20.19761768,USDT,25.48579770,Kucoin Trading,2021-12-08 15:40:42,0.02017744,USDT,,\n')
        
    
            
# ========================================================================================
if __name__ == "__main__":
    unittest.main()