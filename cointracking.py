import os
import subprocess
import argparse
import csv
import sys

from decimal import Decimal

import xml.etree.ElementTree as ET
    
    

# ========================================================================================
GROUP_BY_MONTH_INSTEAD_OF_DAYS = False
GROUP_BY_YEAR_INSTEAD_OF_DAYS = True

INCLUDE_COMMENTS = True

ADD_GROUPED_SUFFIX_TO_NAMES = True

HIDE_CAD = True

# ========================================================================================
def run_uts():
    retVal = subprocess.run(['python', '-m', 'unittest', 'discover', '.']).returncode == 0
    
    return retVal
     
# ========================================================================================
class Record(object):

    def __init__(self, type, buyamt, buycur, buyeur, sellamt, sellcur, selleur, exchange, date, feeamt, feecur, group, comment):
    
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
        return '"Type", "Buy Amount", "Buy Currency", "Buy Value in Account Currency", "Sell Amount", "Sell Currency", "Sell Value in Account Currency", "Exchange", "Date", "Fee", "Fee Currency", "Trade-Group", "Comment"'
            #"Tx-ID", "Liquidity pool"
        
# ========================================================================================
    def xml(self):
        return "{},{},{},{},{},{},{},{},{},{},{},{},{}".format(self.type, self.buyamt, 
                                                self.buycur if self.buycur else "", 
                                                self.buyeur, self.sellamt,
                                                self.sellcur if self.sellcur else "", 
                                                self.selleur, 
                                                self.exchange + ("_GROUPED" if ADD_GROUPED_SUFFIX_TO_NAMES else ""), 
                                                self.date, self.feeamt, 
                                                self.feecur if self.feecur else "", 
                                                self.group if self.group else "", 
                                                self.comment if self.comment else "")
                                                
               
# ========================================================================================                                 
    def key(self):
        if INCLUDE_COMMENTS:
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
            elif self.type in ["Deposit", "Staking", "Remove Liquidity", "Receive LP Token", "Airdrop", "Income (non taxable)", "Other Income", "Income", "LP Rewards", "Reward / Bonus", "Interest Income", "Receive Collateral", "Gift / Tip"]:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5}, [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.feeamt, self.feecur)            
            elif self.type in ["Withdrawal", "Other Fee", "Provide Liquidity", "Return LP Token", "Expense (non taxable)", "Stolen", "Other Expense", "Send Collateral", "Spend", "Donation", "Lost"]:
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
            elif self.type in ["Deposit", "Staking", "Remove Liquidity", "Receive LP Token", "Airdrop", "Income (non taxable)", "Other Income", "Income", "LP Rewards", "Reward / Bonus", "Interest Income", "Receive Collateral", "Gift / Tip", "Lost"]:
                if self.feeamt == Decimal(0.0):
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$)".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.buyeur)
                else:
                    return "{:^24} @ {}: {:22} {:17.8f} {:5} ({:8.2f}$), [{} {} Fee]".format(self.exchange, self.date, self.type,
                        self.buyamt, self.buycur, self.buyeur, self.feeamt, self.feecur)            
            elif self.type in ["Withdrawal", "Other Fee", "Provide Liquidity", "Return LP Token", "Expense (non taxable)", "Stolen", "Other Expense", "Send Collateral", "Spend", "Donation"]:
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
        return res

# ========================================================================================
    def __add__(self, other):
        """
        Adds two records by adding amounts only.
        """
        if self != other: # __equ__ doesn't test everything... maybe I should do that differently... (Another method, use that for the check in the code too?
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
            self.comment)
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
def group_xml(args, xml_in, csv_out):

    if args.simple_group:
        output = []
    else:
        output = {}
        exchange_trades_input_count = {}
    previous = None
    header = None

    
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
    assert(username.text == "MG-062022")
    account_currency = root.find("./export_detail/account_currency")
    print(account_currency.text)
    assert(account_currency.text == "CAD")
        
    trades = root.find('./export_trades')
    prev_day = ""
            
    for t in trades:
        trade = {}
        for i in t.iter():
            trade[i.tag] = i.text
            #print(i.tag, i.text)
            
        #def __init__(self, buyamt, buycur, buyeur, sellamt, sellcur, selleur, exchange, date):
        #print(trade)
        
        #record = Record(*row)
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
            trade['comment'])
        if args.verbose_input:
            print(record)
                        
        # TO ADD to the class?
        #Maybe only combine if no comments    
        
		#<buy_value_in_btc>0.00212789</buy_value_in_btc>
		#<sell_value_in_btc></sell_value_in_btc>
		#<trade_timestamp>1616782894</trade_timestamp>
		#<tradeid>0x03ee4b61341bdcea4662186915ee9f820bbb5f2e-SNX-0x7a338bc43f580ee8625dc787a16991bfc09f6b312dfc5a67e6f6ee8ca098a58e-D</tradeid>
		#<added_timestamp>1655763208</added_timestamp>
        
        if args.simple_group:
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
            
            # TODO: Do the same thing (or something similar), for when there's a withdrawal, OR a deposit, in the same exchange...
            if prev_day != record.day:
                if args.verbose_input:
                    print("\t\t=============== Change from {} to {} ===============".format(prev_day,record.day))
                prev_day = record.day
                
                print("prev_day", prev_day)
                
                for prev_key in previous:                    
                    print("prev_key", prev_key)#Ugh ... how did I do that again ... I need to make a unit test...
                    r = previous[prev_key]
                    if not r.exchange in output:
                        output[r.exchange] = []
                    output[r.exchange].append(r)
                    if args.verbose_input:
                        print(prev_key, r)
                previous = {}
                
            k = record.key()
            #print(k + " ::: ")
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
    else:
        print("\t\t=============== output from {} ===============".format(record.day))
        # Same as above:
        for prev_key in previous:
            r = previous[prev_key]
            if not r.exchange in output:
                output[r.exchange] = []
            output[r.exchange].append(r)
    
    
    if output:
        if args.verbose_output:
            print("\n\t = = = = = = = = = =    S A V I N G    T O    F I L E    = = = = = = = = = =\n")
        if args.simple_group:
            write_csv(args, csv_out, output)
            print("Exported {} records (from {} input records)".format(len(output), len(trades)))
        else:
            for o in output:
                write_csv(args, append_suffix(csv_out, "grouped_"+o+"_"+str(exchange_trades_input_count[o])+"_to_" +str(len(output[o]))), output[o])# TODO: Better name
                print("Exported {} records (from {} input records) for {}".format(len(output[o]), exchange_trades_input_count[o], o))
            


                      
# ========================================================================================
def main(): 
    parser = argparse.ArgumentParser(description='Budget')

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
    parser.add_argument('--short',
                        action="store_true", default=False)
    #parser.add_argument('--currency', default="CAD")
           
    args = parser.parse_args()
    
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
                
        if args.short:
            group_xml(args, "CoinTracking_Trade_Table_SHORT.xml", "CoinTracking_Trade_Table_SHORT.csv")
        else:
            group_xml(args, "CoinTracking_Trade_Table.xml", "CoinTracking_Trade_Table.csv")
    
        
 
# ========================================================================================
if __name__ == "__main__":

    main()
