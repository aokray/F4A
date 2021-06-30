-- Only use if you're using my example/want an easy initially loaded dataset
INSERT INTO datasets
(dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
VALUES('Credit Default Dataset', 'https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients', 2, '{1,2}', 'Removed individuals with missing attributes and reduced sample size to 20,000 from 30,000', 'datasets/creditcarddefault.csv', 'Default on Credit Payment', 'Amount of credit given, Gender, Education, Marital Status, Age, September 2005 Repayment status, August 2005 Repayment status, July 2005 Repayment status, June 2005 Repayment status, May 2005 Repayment status, April 2005 Repayment status, September 2005 Bill amount, August 2005 Bill amount, July 2005 Bill amount, June 2005 Bill amount, May 2005 Bill amount, April 2005 Bill amount, Amount Paid in September 2005, Amount Paid in August 2005, Amount Paid in July 2005, Amount Paid in June 2005, Amount Paid in May 2005, Amount Paid in April 2005', 'datasets/creditdefault_index.csv', 'creditdefault', 'Male,Female', '{} {}(s) were predicted to default on their credit card payments.', '{0.09662508,1.0,0.010829457,0.025707789,0.09519589,0.043440394,0.04909572,0.05025714,0.04597779,0.041250426,0.031591933,0.045476377,0.050204314,0.036567736,0.049032938,0.04537611,0.04453411,0.03977989,0.030980077,0.024997076,0.034997515,0.038621,0.032117166}');

-- INSERT INTO datasets
-- (dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
-- VALUES('Communities and Crime Dataset', 'http://archive.ics.uci.edu/ml/datasets/communities+and+crime', 1, '{0, 1}', 'Binarized the original value into (1:high % African-American Residents) if it is >=50% and (0:low % African-American Residents) otherwise.', 'datasets/crimecommunity.csv', 'Have High Crime Rate', '', 'datasets/crimecommunity_index.csv', 'crimecommunity', 'High % African-American, Low % African-American', 'RESULTS STR', '{HDIST}')

-- Fix this
INSERT INTO datasets
(dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
VALUES('COMPAS Dataset', 'https://www.kaggle.com/danofer/compass', 15, '{0, 1}', 'See ProPublica data methodology article: https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm', 'datasets/compas.csv', 'Recidivate', 'FEATURES', 'datasets/compas_index.csv', 'compas', 'African-American, White', 'RESULTS STR', '{0.07755449734087821, 0.14197632729959805, 0.09914505256103662, 0.17706486024521342, 0.08547080656938746, 0.05687761191582584, 0.14914908382127753, 0.07608005489457614, 0.05265561198360348, 0.03644170079832681, 0.17706486024521342, 0.196127217572154, 0.14914908382127753, 0.021142805314642965}')

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES('Logistic Regression', true, 'Learning Method', 'from sklearn.linear_model import LogisticRegression');

INSERT INTO paramsv VALUES ('Logistic Regression', 'C', '{0, inf}', '1', 'C is a "regularizer", usually it is set between 0.01 and 10.');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES('Fair PCA', true, 'Transformer', 'from algorithms.fair_pca import FairPCA');

-- Crappy (hopefully) temp workaround
INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES('None', false, 'Transformer', '');

INSERT INTO paramsv VALUES ('Fair PCA', 'd', '{0, inf}', 'int(p / 2)', 'd is the reduced number of features, must be less than the # you chose above!');