import os
import subprocess
import argparse
import csv
import sys

from decimal import Decimal
from copy import copy

import xml.etree.ElementTree as ET
    
    

# ========================================================================================
GROUP_BY_MONTH_INSTEAD_OF_DAYS = False
GROUP_BY_YEAR_INSTEAD_OF_DAYS = True

ADD_GROUPED_SUFFIX_TO_NAMES = False#True

HIDE_CAD = True

WITHDRAWAL = ["Withdrawal", "Other Fee", "Provide Liquidity", "Return LP Token", "Expense (non taxable)", "Stolen", "Other Expense", "Send Collateral", "Spend", "Donation", "Lost"]
DEPOSIT = ["Deposit", "Staking", "Remove Liquidity", "Receive LP Token", "Airdrop", "Income (non taxable)", "Other Income", "Income", "LP Rewards", "Reward / Bonus", "Interest Income", "Receive Collateral", "Gift / Tip"]

TRANSFER_OUT = WITHDRAWAL#["Withdrawal", "Provide Liquidity", "Return LP Token", "Send Collateral"]
TRANSFER_IN = DEPOSIT#["Deposit", "Remove Liquidity", "Receive LP Token", "Receive Collateral"]#"Staking"

# Remaining are mostly: Trade

# ========================================================================================
def run_uts():
    #retVal = subprocess.run(['python', '-m', 'unittest', 'discover', '.']).returncode == 0
    retVal = subprocess.run(['python', 'test_cointracking.py']).returncode == 0
    
    return retVal
     
# ========================================================================================
class Record(object):

    def __init__(self, type, buyamt, buycur, buyeur, sellamt, sellcur, selleur, exchange, date, feeamt, feecur, group, comment, trade_timestamp):
    
        # TODOOOOOOOOOOOOOO scientific notation!!
        self.type = type
        self.buyamt = Decimal(buyamt) if buyamt else Decimal(0.0)
        self.buycur = buycur
        self.buyeur = Decimal(buyeur) if buyeur else Decimal(0.0)
        self.sellamt = Decimal(sellamt) if sellamt else Decimal(0.0)
        self.sellcur = sellcur
        self.selleur = Decimal(selleur) if selleur else Decimal(0.0)
        self.exchange = exchange
        self.date = date
        self.trade_timestamp = trade_timestamp
        self.day = date.strip().split(' ')[0]
        if GROUP_BY_MONTH_INSTEAD_OF_DAYS:
            self.day = self.day[:7]
        if GROUP_BY_YEAR_INSTEAD_OF_DAYS:
            self.day = self.day[:4]
        
        self.feeamt = Decimal(feeamt) if feeamt else Decimal(0.0)
        self.feecur = feecur
        self.group = group 
        self.comment = comment

# ========================================================================================
    def xml_header(self):
        # Cointracking is stupid, it needs to be in THAT ORDER:
        return '"Type", "Buy Amount", "Buy Currency", "Sell Amount", "Sell Currency", "Fee", "Fee Currency", "Exchange", "Trade-Group", "Comment", "Date", "Tx-ID", "Buy Value in Account Currency", "Sell Value in Account Currency", "Liquidity pool"'
        #return '"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"'
            #"Tx-ID", "Liquidity pool"
        
# ========================================================================================
    def xml(self):
        return '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"'.format(self.type, self.buyamt, 
                                                self.buycur if self.buycur else "", 
                                                self.sellamt,
                                                self.sellcur if self.sellcur else "", 
                                                self.feeamt,
                                                self.feecur if self.feecur else "", 
                                                self.exchange + ("_GROUPED" if ADD_GROUPED_SUFFIX_TO_NAMES else ""), 
                                                self.group if self.group else "", 
                                                self.comment.replace('"','\"') if self.comment else "",
                                                self.date, 
                                                "",#Tx-ID
                                                self.buyeur,
                                                self.selleur,
                                                ""#Liquidity pool
                                                )
                                                
               
# ========================================================================================                                 
    def key(self):
        include_comments = True
        if self.exchange in ["osmosis_blockchain", "Binance", "Hoo"]:
            include_comments = False
            
        if include_comments:
            return "{},{},{},{},{},{},{}".format(self.exchange, self.day, self.type, self.buycur, self.sellcur, self.feecur, self.comment ) # Does this prevent combining trades with a comment?
        else:
            return "{},{},{},{},{},{}".format(self.exchange, self.day, self.type, self.buycur, self.sellcur, self.feecur )
            
# ========================================================================================
    def __str__(self):
        if HIDE_CAD:
            if self.type == "Trade":
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} to {:17.8f} {:5}".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, 
                        self.buyamt, self.buycur )            
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} to {:17.8f} {:5}, [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, 
                        self.buyamt, self.buycur,
                        self.feeamt, self.feecur )
            elif self.type in DEPOSIT:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}, [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.feeamt, self.feecur)            
            elif self.type in WITHDRAWAL:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}, [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, self.feeamt, self.feecur)
        else:
            if self.type == "Trade":
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} to {:17.8f} {:5} ({:8.2f}$ to {:8.2f}$)".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, 
                        self.buyamt, self.buycur,
                        self.selleur, self.buyeur )            
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} to {:17.8f} {:5} ({:8.2f}$ to {:8.2f}$), [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, 
                        self.buyamt, self.buycur,
                        self.selleur, self.buyeur, 
                        self.feeamt, self.feecur )
            elif self.type in DEPOSIT:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$)".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.buyeur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$), [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.buyeur, self.feeamt, self.feecur)            
            elif self.type in WITHDRAWAL:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$)".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, self.selleur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$), [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.sellamt, self.sellcur, self.selleur, self.feeamt, self.feecur)
                        
        # else (default)
        if self.feeamt == Decimal(0.0):
            return "{:^24} @ {}: [{:22}] /Buy {:17.8f} {:5} ({:8.2f}$)\t/Sell {:17.8f} {:5} ({:8.2f}$)".format(self.exchange, self.date, self.type,
                self.buyamt, self.buycur, self.buyeur, 
                self.sellamt, self.sellcur, self.selleur )
        else:
            return "{:^24} @ {}: [{:22}] /Buy {:17.8f} {:5} ({:8.2f}$)\t/Sell {:17.8f} {:5} ({:8.2f}$), [{} {} Fee]".format(self.exchange, self.date, self.type,
                self.buyamt, self.buycur, self.buyeur, 
                self.sellamt, self.sellcur, self.selleur, 
                    self.feeamt, self.feecur)
    
# ========================================================================================
    def __eq__(self, other):
        """
        Returns True if two records can be combined (same currencies, same venue, same date)
        """
        res = self.type == other.type and self.buycur == other.buycur and self.sellcur == other.sellcur and \
            self.feecur == other.feecur and \
            self.exchange == other.exchange and self.day == other.day
            #(self.feecur == other.feecur or self.feecur == None or other.feecur == None) and
        #print(f"res: {res}, "
        #    f"t:{self.type == other.type}, "
        #    f"bc:{self.buycur == other.buycur}, "
        #    f"sc:{self.sellcur == other.sellcur}, "
        #    f"fc:{self.feecur == other.feecur}, "
        #    f"ex:{self.exchange == other.exchange}, "
        #    f"day:{self.day == other.day} {self.day} {other.day}")
        return res

# ========================================================================================
    def __add__(self, other):
        """
        Adds two records by adding amounts only.
        """
        
        # self:  Other Fee,0,,0,0.00268445,ETH,7.82931161,ETH Wallet,2023-12-31 23:34:45,0,ETH,MetaMask ETH,
        # other: Other Fee,0,,0,0.00277182,ETH,6.79959556,ETH Wallet,2023-12-31 23:34:45,0E-8,ETH,MetaMask ETH,
        
        if self != other: # __equ__ doesn't test everything... maybe I should do that differently... (Another method, use that for the check in the code too?
            #print(f"\nself:  {self.xml()}\nother: {other.xml()}")
            raise RuntimeError("Need to be the same type and currencies")
        return Record(self.type, self.buyamt + other.buyamt, 
            self.buycur, 
            self.buyeur + other.buyeur,
            self.sellamt + other.sellamt, 
            self.sellcur, 
            self.selleur + other.selleur,
            self.exchange, 
            other.date, 
            self.feeamt + other.feeamt, 
            self.feecur, 
            self.group, 
            self.comment,
            other.trade_timestamp)
    # other.date (or self.date) will screw up some withdrawal/deposit values? So I need to do it only on old exchanges that I stopped using?

# ========================================================================================
def write_csv(args, csv_out, output):
    csv_out = os.path.join("OUTPUT", csv_out)
    with open(csv_out, 'w') as csvfile:
        csvfile.writelines(output[0].xml_header() + '\n')
        for record in output:
            csvfile.write(record.xml() + '\n')
            if args.verbose_output:
                print(str(record))
         
# ========================================================================================       
def append_suffix(filename, suffix):
    return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [suffix])
    
# ========================================================================================
def group_xml(args, xml_in, dumb_group_for_early_dates=True, group_dumb_groups=False, dont_group_with_dep=True):
    if args.simple_group:
        output = []
        exchange_trades_input_count = 0
    else:
        output = {}
        exchange_trades_input_count = {}
    previous = None
    
    
    # TODO: Read xml instead of csv!!
    # (Or convert xml to csv?)
    
    tree = ET.parse(xml_in)
    root = tree.getroot()
    assert( root.tag == "export" )
    
    details = root.iter('export_detail')
    
    assert(details!=None)
    #for detail in details:
    #    print(detail.tag)
    
    username = root.find("./export_detail/username")
    print(username.text)
    assert(username.text == args.username)
    account_currency = root.find("./export_detail/account_currency")
    print(account_currency.text)
    assert(account_currency.text == "CAD")
        
    trades = root.find('./export_trades')
    prev_day = ""
            
    all_records = []
    for t in trades:
        trade = {}
        for i in t.iter():
            trade[i.tag] = i.text
        
        record = Record(
            trade['type'],
            trade['buy_amount'], 
            trade['buy_cur'], 
            trade['buy_value_in_fiat'], 
            trade['sell_amount'], 
            trade['sell_cur'], 
            trade['sell_value_in_fiat'], 
            trade['exchange'], 
            trade['trade_date'], 
            trade['fee_amount'], 
            trade['fee_cur'], 
            trade['group'], 
            trade['comment'],
            trade['trade_timestamp'])
        if args.verbose_input:
            print(record)
        all_records.append(record)
        
    # Sort by <trade_timestamp>
    all_records.sort(key=lambda x: x.trade_timestamp, reverse=False)
    
    last_day = all_records[-1].day
    print(f"last_day {last_day}")
    
    for record in all_records:
        # TO ADD to the class?
        #Maybe only combine if no comments    
        
		#<buy_value_in_btc>0.00212789</buy_value_in_btc>
		#<sell_value_in_btc></sell_value_in_btc>
		#<trade_timestamp>1616782894</trade_timestamp>
		#<tradeid>0x03ee4b61341bdcea4662186915ee9f820bbb5f2e-SNX-0x7a338bc43f580ee8625dc787a16991bfc09f6b312dfc5a67e6f6ee8ca098a58e-D</tradeid>
		#<added_timestamp>1655763208</added_timestamp>
        
        if args.simple_group:
            exchange_trades_input_count += 1
            if previous is None:
                # first row, set as previous
                previous = record
                continue
            
            if record == previous:
                # new row can be combined with previous
                if args.verbose_input_combined:
                    if not args.verbose_input:
                        print(previous)
                    print("\t\t\t\t\tcombining with previous:")
                    if not args.verbose_input:
                        print(record)
                previous += record
                if args.verbose_input_combined:
                    if not args.verbose_input:
                        print("\t\t\t\t\t(combined)")
                        print(previous)
                    
                continue
            
            else:
                # can't be combined, adding previous to output then switch over
                output.append(previous)
                previous = record
        else:
            
            if previous is None:
                # first row, set as previous
                previous = {}
                
            if not record.exchange in exchange_trades_input_count:
                exchange_trades_input_count[record.exchange] = 0
            exchange_trades_input_count[record.exchange]+=1
                                 
            k = record.key()  
            remove_keys = []
            
            is_last_group = last_day == record.day
            is_dumb_group = dumb_group_for_early_dates and not is_last_group
            
            
            if is_dumb_group:
                record = copy(record)
                
                if group_dumb_groups:
                    new_day = str(int(last_day)-1)
                    new_date = new_day+"-12-31 23:34:45"
                    #print(f"new_date: '{new_date}''"+record.date[:5]+"12-31 23:34:45"+"'")
                    record.day = new_day
                else:
                    new_date = record.date[:5]+"12-31 23:34:45"
                    
                record.date = new_date
                
            
            
            if prev_day != record.day:
                
                if args.verbose_input:
                    print("\t\t=============== Change from {} to {} ===============".format(prev_day,record.day))
                prev_day = record.day                
                print("prev_day", prev_day)
                remove_keys = list(previous.keys())                
            elif is_dumb_group:
                for prev_key in previous:
                    if dont_group_with_dep and prev_key == k and (record.type == "Withdrawal" or record.type == "Deposit"):
                        remove_keys.append(prev_key)
                pass
            # Do the same thing (or something similar), for when there's a withdrawal, OR a deposit, in the same exchange...
            elif (record.type in TRANSFER_IN) or (record.type in TRANSFER_OUT):
                is_withdrawal = record.type in WITHDRAWAL
                is_deposit = record.type in DEPOSIT
                
                # TODO: there might be a problem with Kucoing, doing Trade, then Reward/Bonus... for EVERY SINGLE TRADE! ugh... can I remove it from last trade or something?
                currency = record.buycur if is_deposit else record.sellcur
                exchange = record.exchange
                
                for prev_key in previous:                    
                    if dont_group_with_dep and prev_key == k and (record.type == "Withdrawal" or record.type == "Deposit"):
                        remove_keys.append(prev_key)
                    elif prev_key != k and previous[prev_key].exchange == exchange:# and is_prev_deposit != is_deposit:#previous[prev_key].type != record.type:#TODO: Same type ? Nah... that would mess up everything..                    
                        is_prev_withdrawal = previous[prev_key].type in WITHDRAWAL
                        is_prev_deposit = previous[prev_key].type in DEPOSIT
                        # (different or trade..)
                        if (not is_prev_withdrawal and not is_prev_deposit) or is_prev_deposit != is_deposit:
                            #currency (do we need in the next remove_keys condition?
                            #prev_currency = previous[prev_key].buycur if is_prev_deposit else previous[prev_key].sellcur
                            if previous[prev_key].buycur == currency or previous[prev_key].sellcur == currency:
                                remove_keys.append(prev_key)
                            
                                
                if remove_keys:
                    # ONLY IF there are other trades, then also remove the last deposit.
                    # Otherwise, it won't group all deposits.
                    
                    # Well any transaction with the same currency, really...                
                    if previous[prev_key].buycur == currency or previous[prev_key].sellcur == currency:
                        if not prev_key in remove_keys:
                            remove_keys.append(prev_key)
            elif (record.type in WITHDRAWAL) or (record.type in DEPOSIT):
                pass
            else:# Trade (not deposit or withdrawal)
                #print("TODO")
                # If there's a trade, everything previous needs to be accounted for.
                exchange = record.exchange
                
                
                if False:#Need to make it better before adding it:
                    to_add = None
                    if not dumb_group_for_early_dates or is_last_group:
                        for prev_key in previous:
                            if prev_key != k and previous[prev_key].exchange == exchange and record.type == "Trade" and previous[prev_key].type == "Trade":
                                if previous[prev_key].buycur == record.sellcur and previous[prev_key].sellcur == record.buycur:
                                    # TODO::::::::: merge!
                                    #test_to_correct += 1
                                    #print(f"TODO: {k}\nprev: {prev_key} ({test_to_correct})")
                                    to_add = prev_key
                                    break
                                
                    ## REMOVE THIIIIIIIIIIIIIIS! This is just the test!!
                    if to_add != None:                        
                        # Ugh feecur...
                    
                        fake_record = copy(record)
                        
                        fake_record.buyamt = record.sellamt
                        fake_record.buycur = record.sellcur
                        fake_record.buyeur = record.selleur
                        
                        fake_record.sellamt = record.buyamt
                        fake_record.sellcur = record.buycur
                        fake_record.selleur = record.buyeur
                        
                        if fake_record.feecur != previous[to_add].feecur:
                            fake_record.feecur = previous[to_add].feecur#record.sellcur
                            # TODO: This is definitely wrong...                        
                            #fake_record.buyamt -= fake_record.feeamt
                            fake_record.feeamt = 0
                        
                        previous[to_add] += fake_record
                        continue
                
                for prev_key in previous:
                    if prev_key != k and previous[prev_key].exchange == exchange:# and is_prev_deposit != is_deposit:#previous[prev_key].type != record.type:#TODO: Same type ? Nah... that would mess up everything..
                    
                        assert record.buycur != ""
                        assert record.sellcur != ""
                        
                        #TODOooooooooooooooooooooooo:
                        # Oh wait, why not merged?
                        # Trade	2.46340000	DOT3L	0	5.05033483	USDT	6.35566592	Kucoin Trading	2021-12-08 15:40:36	0.00504529	USDT
                        # Trade	2.47700000	DOT3L	0	5.05044670	USDT	6.35580671	Kucoin Trading	2021-12-08 15:40:42	0.00504540	USDT
                        # Oh there was probably a reward/bonus in-between or after or whatever... find it..
                        # Wait, is it not adding the "current" deposit?
                        
                        # TODO: If same day and USD, don't care... (but not really an issue, with the dumb grouping)
                        for currency in [record.buycur, record.sellcur]:
                            if not prev_key in remove_keys:
                                if previous[prev_key].buycur == currency or previous[prev_key].sellcur == currency:
                                    remove_keys.append(prev_key)
                
            if remove_keys:
                if args.verbose_input:
                    print( "===", record, "\n [[")# record.type, exchange, currency, "\n  [[", )
                for prev_key in remove_keys:
                    
                    # TODO: Don't duplicate that...
                    r = previous[prev_key]
                    if not r.exchange in output:
                        output[r.exchange] = []
                    output[r.exchange].append(r)
                    if args.verbose_input:
                        print("\t\t", prev_key, r)
                    previous.pop(prev_key)
                if args.verbose_input:
                    print("  ]]")
                    
            if k in previous:
                if args.verbose_input_combined:
                    if not args.verbose_input:
                        print(previous[k])
                    print("\t\t\t\t\tcombining with previous({})".format(k))
                    if not args.verbose_input:
                        print(record)                        
                        
                previous[k] += record
                
                if args.verbose_input_combined:
                    if not args.verbose_input:
                        print("\t\t\t\t\t(combined)")
                        print(previous[k])
                    
            else:
                previous[k] = record
            
    
    if args.simple_group:
        output.append(previous)
        output.sort(key=lambda x: x.trade_timestamp, reverse=False)
    else:
        print("\t\t=============== output from {} ===============".format(record.day))
        # Same as above:
        for prev_key in previous:
            r = previous[prev_key]
            if not r.exchange in output:
                output[r.exchange] = []
            output[r.exchange].append(r)
        for key in output:
            output[key].sort(key=lambda x: x.trade_timestamp, reverse=False)
    
    return output, exchange_trades_input_count, all_records
    
    
# ========================================================================================
def write_output(args, output, exchange_trades_input_count, csv_out):
    if output:
        total_in = 0
        total_out = 0
        if args.verbose_output:
            print("\n\t = = = = = = = = = =    S A V I N G    T O    F I L E    = = = = = = = = = =\n")
        if args.simple_group:
            write_csv(args, csv_out, output)
            print("Exported {} records (from {} input records)".format(len(output), exchange_trades_input_count))
            total_in = exchange_trades_input_count
            total_out = len(output)
        else:
            all_outputs = []
            for o in output:
                write_csv(args, append_suffix(csv_out, "grouped_"+o+"_"+str(exchange_trades_input_count[o])+"_to_" +str(len(output[o]))), output[o])# TODO: Better name
                print("Exported {} records (from {} input records) for {}".format(len(output[o]), exchange_trades_input_count[o], o))
                total_in += exchange_trades_input_count[o]
                total_out += len(output[o])
                
                #if o not in ["Okex Trading", "BitBuy", "Coinbase Pro"]:
                all_outputs.extend(output[o])
            
            write_csv(args, append_suffix(csv_out, "all_"+"_"+str(total_in)+"_to_" +str(len(all_outputs))), all_outputs)
            print("Exported {} records (from {} input records) for all".format(total_out, total_in))
            
            
        print("Exported total {} records (from {} input records)".format(total_out, total_in))
       
# ========================================================================================
def get_args():
    parser = argparse.ArgumentParser(description='CoinTracking')
    
    parser.add_argument('--username', action='store', type=str, default="TEST",
                        help='The username of the export to parse.')
    parser.add_argument('--utOnly',
                        action="store_true", default=False,
                        help='Unit tests')
    parser.add_argument('--verbose_input',
                        action="store_true", default=False)
    parser.add_argument('--verbose_input_combined',
                        action="store_true", default=False)
    parser.add_argument('--verbose_output',
                        action="store_true", default=False)
    parser.add_argument('--simple_group',
                        action="store_true", default=False)
    parser.add_argument('--filename', action='store', type=str, default="CoinTracking_Trade_Table.xml",
                        help='The file of the input to parse.')
    #parser.add_argument('--currency', default="CAD")
    return parser.parse_args()
    
                      
# ========================================================================================
def main(): 
    args = get_args()
    
    if not run_uts():
        print(" ========================================================== ")
        print(" ======================= FAILED UTS ======================= ")
        print(" ========================================================== ")
        sys.exit(1)
        
    if not args.utOnly:
        print(" ========================================================== ")
        print(" ======================= PASSED UTS ======================= ")
        print(" ========================================================== ")
        print("")
        
        if args.username == "TEST":
            print("Please specify a username with --username")
        else:
            output, exchange_trades_input_count, all_records = group_xml(args, args.filename)
            write_output(args, output, exchange_trades_input_count, "CoinTracking_Trade_Table.csv")
            #output, exchange_trades_input_count, all_records = group_xml(args, r"C:\Users\Martin\Downloads\Martin-shakepay-2025-01-13-crypto_transactions_summary-STRIPPED-converted.xml")
            #write_output(args, output, exchange_trades_input_count, "Martin-shakepay-2025-01-13-crypto_transactions_summary-STRIPPED-converted.csv")

    
        
 
# ========================================================================================
if __name__ == "__main__":

    main()
