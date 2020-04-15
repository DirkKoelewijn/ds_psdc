import pandas as pd
import re


# Converts the raw data to a regular CSV file
def raw_to_csv(raw_file, data_file):
    with open(raw_file, 'r') as file_in, open(data_file, 'w') as file_out:
        for line in file_in.readlines():
            line = line.replace(',', '.').replace(';', ',').replace('NULL', '').replace('Onbekend', '')
            file_out.write(line)


# Function static variables
uppercase_replacements = [
    'Aneurysma Spurium',
    'Corpus Alienum',
    'Laterae Clavicula',
    'fistel Thoraxwand',
    'Blaasbiopten',
    'Aortabroek Prothese'
]
regex_replacements = {
    r'[\s\.]+': ' ',
    r'([A-Z]+[a-z\s-]*)\s*([A-Z][a-z][a-z\s-]*[a-z]+)': r'\1 + \2',
    r'([A-Z]+[a-z\s-]*[a-z])([A-Z]{3})': r'\1 + \2',
    r'([A-Z]{3})([A-Z]{3})': r'\1 + \2',
    r'(.*)(^|\s)[Oo]pen($|\s(procedure)*)(.*)': r'\1 \5+ open',
}
replacements = {
    'via ': '',
    'm b v ': '',
    'ë': 'e',
    'Sleeve resectie': 'Sleeve-resectie',
    'Percardiectomie': 'Pericardectomie',
    'Ascendensvervanging': 'Vervanging aorta ascendens',
    'Vervanging aorta ascendens met aortaboog': 'Vervanging aorta ascendens + Vervanging aortaboog',
    'Vervanging aortawortel aorta ascendens en boog': 'Vervanging aortawortel + Vervanging aorta ascendens + '
                                                      'Vervanging aortaboog',
    'VATS': '+ VATS +',
    'minithoracotomie': '+ minithoracotomie',
    'Endoscopische': 'Endoscopisch +',
    'Poging tot': '',
    'Rethoracotomie met hart-longmachine tijdens dezelfde opname': 'Rethoracotomie',
    'Bilobectomie open procedure': 'Bilobectomie',
    'Sluiten bronchusfistel thoracotomie': 'Sluiten bronchusfistel',
    'Reconstructie van de aorta of haar directe zijtakken zoals de arteria subclavia': 'Reconstructie aortawortel',
    'TVP shaving': 'TVP',
}


# Splits the surgery type
def split_surgery_types(df, merge_threshold=1, merge_value='Other'):
    # Get the surgical types as list
    types = df.Operatietype.tolist()

    # Loop through the types and split into multiple
    for i, s in enumerate(types):
        # Convert to string
        s = str(s)

        # Loop through and apply replacements
        for k in uppercase_replacements:
            s = str(s).replace(k, k.lower())
        for k, v in regex_replacements.items():
            s = re.sub(k, v, s)
        for k, v in replacements.items():
            s = str(s).replace(k, v)

        # Split strings by the '+' symbol
        s = re.split(r'\s*\+\s*', s)

        # Make sure the types are non-empty, stripped and at least start with a capital
        types[i] = [str(a).strip()[0].upper() + str(a).strip()[1:] for a in s if len(a) > 0]

    # Get all surgical types
    x = [a for b in types for a in b]

    # Get the types to remove (remove those who appear less than the merge threshold)
    remove = [a for a in set(x) if x.count(a) < merge_threshold]

    # Replace the types to remove by the merge value
    for i, v in enumerate(types):
        for j, u in enumerate(v):
            if u in remove:
                types[i][j] = merge_value

    # Get all unique surgical types, sorted.
    keys = sorted(set([a for b in types for a in b]))

    # Remove NaN and the merge value
    keys.remove('Nan')
    if (len(remove)) > 0:
        keys.remove(merge_value)

    # Add new columns for the other values
    i = 0
    for i, k in enumerate(keys):
        # Generate column for k
        c = ['J' if k in l else float('nan') if 'Nan' in l else 'N' for l in types]
        df.insert(1 + i, k, c, True)

    # Add merge value column with count
    if (len(remove)) > 0:
        c = [l.count(merge_value) if 'Nan' not in l else float('nan') for l in types]
        df.insert(i + 2, merge_value, c, True)

    return df


numeric_columns = ['Leeftijd', 'Euroscore1', 'Euroscore2', 'BMI', 'CCS', 'NYHA', 'Geplande operatieduur',
                   'Operatieduur', 'Ziekenhuis ligduur', 'IC ligduur', 'Aantal anastomosen']

# Fill na method: M (Mode or mean), S (Separate category or -1)
fill = ['M', 'S']
allow = ['C', 'N']
rows = ['A', 'F']
thresholds = [1, 3]

# Create new datasets
if __name__ == '__main__':
    # Set new CSV name
    data_csv = 'data/data.csv'

    # Rewrite to new CSV and load data
    raw_to_csv('data/raw.csv', data_csv)
    df = pd.read_csv(data_csv)
    df_obj = df.select_dtypes(['object'])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    df.to_csv(data_csv, index=False)

    for (f, a, r, t) in [(f, a, r, t) for f in fill for a in allow for r in rows for t in thresholds]:
        df = pd.read_csv(data_csv)

        # Remove rows that do not have the Operatieduur variable
        df = df[df.Operatieduur.notnull()]

        # Split surgical types, merge by t, drop Operatietype
        df = split_surgery_types(df, merge_threshold=t)
        df = df.drop(columns=['Operatietype', 'Geplande operatieduur', 'Ziekenhuis ligduur', 'IC ligduur'])

        # If rows = F (Filled), remove rows with a lot of empty values (where Geslacht is missing)
        if r == 'F':
            df = df[df.Geslacht.notnull()]

        # Fill NA values
        for c in df.columns:
            if c in numeric_columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
                if f == 'M':
                    df[c] = df[c].fillna(df[c].mean())
                else:
                    df[c] = df[c].fillna(-1)
            else:
                if f == 'M':
                    mode = df[df[c].notnull()][c].mode()[0]
                    df[c] = df[c].fillna(mode)
                else:
                    df[c] = df[c].fillna('U')

        # If allow == N (Numerical): Convert categories to numerical values
        if a == 'N':
            df = pd.get_dummies(df)

        df.to_csv('data/data-%s%s%s%s.csv' % (f, a, r, t), index=False)

        print('Null values:', 'data/data-%s%s%s%s.csv' % (f, a, r, t), df.isnull().sum().sum())
