#
# Converts the file to a more default and usable CSV format by:
# - Replacing commas by points for the decimal notation
# - Replacing semicolons by commas as separator
# - Replace "NULL" by actually empty values%
#
with open('source.csv', 'r') as file_in, open('raw.csv', 'w') as file_out:
    for line in file_in.readlines():
        line = line.replace(',', '.').replace(';', ',').replace('NULL', '')
        file_out.write(line)
