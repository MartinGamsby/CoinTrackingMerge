import csv
from datetime import datetime
import sys

def convert_csv(input_file, output_file):
    """
    Convert ShakePay CSV format to the specified output format.
    """
    # Define output headers
    output_headers = [
        "Type", "Buy Amount", "Buy Currency", "Sell Amount", "Sell Currency",
        "Fee", "Fee Currency", "Exchange", "Trade-Group", "Comment", "Date",
        "Tx-ID", "Buy Value in Account Currency", "Sell Value in Account Currency",
        "Liquidity pool"
    ]

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=output_headers)
            writer.writeheader()

            for row in reader:
                output_row = dict.fromkeys(output_headers, "")  # Initialize all fields to empty string
                # Common fields
                output_row["Date"] = row["Date"]
                output_row["Exchange"] = "ShakePay"
                output_row["Fee"] = "0"
                output_row["Comment"] = row["Description"]  # Added Description mapping
                
                # Process based on transaction type
                transaction_type = row["Type"]
                
                if transaction_type == "Récompenses":
                    output_row["Type"] = "Income"
                    output_row["Buy Amount"] = row["Montant crédité"]
                    output_row["Buy Currency"] = row["Actif crédité"]
                    output_row["Buy Value in Account Currency"] = row["Coût comptable"]
                    
                elif transaction_type == "Recevoir":
                    output_row["Type"] = "Deposit"
                    output_row["Buy Amount"] = row["Montant crédité"]
                    output_row["Buy Currency"] = row["Actif crédité"]
                    output_row["Buy Value in Account Currency"] = row["Coût comptable"]
                    
                elif transaction_type == "Vente":
                    output_row["Type"] = "Trade"
                    output_row["Sell Amount"] = row["Montant débité"]
                    output_row["Sell Currency"] = row["Actif débité"]
                    output_row["Buy Amount"] = row["Coût comptable"]
                    output_row["Buy Currency"] = row["Devise du coût comptable"]
                    
                elif transaction_type == "Achat":
                    output_row["Type"] = "Trade"
                    output_row["Buy Amount"] = row["Montant crédité"]
                    output_row["Buy Currency"] = row["Actif crédité"]
                    output_row["Sell Amount"] = row["Coût comptable"]
                    output_row["Sell Currency"] = row["Devise du coût comptable"]
                    
                elif transaction_type == "Envoi":
                    output_row["Type"] = "Withdrawal"
                    output_row["Sell Amount"] = row["Montant débité"]
                    output_row["Sell Currency"] = row["Actif débité"]
                    output_row["Sell Value in Account Currency"] = row["Coût comptable"]
                
                writer.writerow(output_row)
                
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    convert_csv(input_file, output_file)
    print(f"Conversion completed successfully. Output written to {output_file}")