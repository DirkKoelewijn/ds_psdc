# Data sets
Data sets have a four character code to indicate how the data was made. The four characters specify (in this order):

1. What fill method was used
2. Whether categorical values are allowed
3. Whether all observations have been included
4. Whether surgical types were merged that did not occur often

## 1. Fill method (M/S)
#### M: Use mean/mode value
Used `mean()` to fill numerical values, `mode()` to fill categorical values.

#### S: Use separate value
Used `-1` to fill numerical values, `"U"` to fill categorical values.

## 2. Allow categorical values
#### C: Allow categories
Did not change the data set.
#### N: Only allow numerical values
Used `pd.get_dummies()` to convert categories into numerical values.

## 3: Used observartions
#### A: All observations
Did not change the data set.
#### F: Use filled observations only
Excluded rows that have a large amount of missing values.

## 4: Merge surgical types
#### 1: Do not merge
Did not change the data set.
#### 3: Merge types that occur less than <3 times
Combines all surgical types that occur less than <3 times in the type ``Other``