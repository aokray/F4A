-- Only use if you're using my example/want an easy initially loaded dataset
INSERT INTO datasets
(dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
VALUES('Credit Default Dataset', 'https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients', 2, '{1,2}', 'Removed individuals with missing attributes and reduced sample size to 20,000 from 30,000', 'datasets/creditcarddefault.csv', 'Default Payment', 'Amount of credit given, Gender, Education, Marital Status, Age, September 2005 Repayment status, August 2005 Repayment status, July 2005 Repayment status, June 2005 Repayment status, May 2005 Repayment status, April 2005 Repayment status, September 2005 Bill amount, August 2005 Bill amount, July 2005 Bill amount, June 2005 Bill amount, May 2005 Bill amount, April 2005 Bill amount, Amount Paid in September 2005, Amount Paid in August 2005, Amount Paid in July 2005, Amount Paid in June 2005, Amount Paid in May 2005, Amount Paid in April 2005', 'datasets/creditdefault_index.csv', 'creditdefault', 'Male,Female', '{} {}(s) were predicted to default on their credit card payments.', '{0.09662508,1.0,0.010829457,0.025707789,0.09519589,0.043440394,0.04909572,0.05025714,0.04597779,0.041250426,0.031591933,0.045476377,0.050204314,0.036567736,0.049032938,0.04537611,0.04453411,0.03977989,0.030980077,0.024997076,0.034997515,0.038621,0.032117166}');

INSERT INTO algv
(algv_algname, algv_params)
VALUES('Logistic Regression', true);

INSERT INTO paramsv VALUES ('Logistic Regression', 'C', '{0, inf}');

INSERT INTO algv
(algv_algname, algv_params)
VALUES('Fair PCA', true);

INSERT INTO paramsv VALUES ('Fair PCA', 'C', '{0, inf}');

INSERT INTO paramsv VALUES ('Fair PCA', 'd', '{0, inf}');