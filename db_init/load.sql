-- Only use if you're using my example/want an easy initially loaded dataset
INSERT INTO datasets
(dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
VALUES('Credit Default Dataset', 'https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients', 2, '{1,2}', 'Removed individuals with missing attributes and reduced sample size to 20,000 from 30,000', 'datasets/creditcarddefault.csv', 'Default on Credit Payment', 'Amount of credit given, Gender, Education, Marital Status, Age, September 2005 Repayment status, August 2005 Repayment status, July 2005 Repayment status, June 2005 Repayment status, May 2005 Repayment status, April 2005 Repayment status, September 2005 Bill amount, August 2005 Bill amount, July 2005 Bill amount, June 2005 Bill amount, May 2005 Bill amount, April 2005 Bill amount, Amount Paid in September 2005, Amount Paid in August 2005, Amount Paid in July 2005, Amount Paid in June 2005, Amount Paid in May 2005, Amount Paid in April 2005', 'datasets/creditdefault_index.csv', 'creditdefault', 'Male,Female', '{} {}(s) were predicted to {}default on their credit card payments.', '{0.09662508,1.0,0.010829457,0.025707789,0.09519589,0.043440394,0.04909572,0.05025714,0.04597779,0.041250426,0.031591933,0.045476377,0.050204314,0.036567736,0.049032938,0.04537611,0.04453411,0.03977989,0.030980077,0.024997076,0.034997515,0.038621,0.032117166}');

INSERT INTO datasets
(dataset_name, dataset_origin, dataset_sensidx, dataset_upvals, dataset_preprocessing, dataset_path, dataset_labeldesc, dataset_featnames, dataset_idxspath, dataset_shortname, dataset_sensnames, dataset_resultsstr, dataset_hdist)
VALUES('COMPAS Dataset', 'https://www.kaggle.com/danofer/compass', 3, '{0, 1}', 'From the Kaggle data, all non-numerical values were removed (e.g. first name, last name)', 'datasets/compas.csv', 'Recidivate after 2 Years', 'Gender, Age, Race, Juvenile Felony Count, Decile Score, Juvenile Misd. Count, Juvenile Other Count, Priors Count, Days Before Screening Arrest, Days from COMPAS, Is Predicted as Recidivating, Is Predicted as Violent Recidivation, Risk of Recidivism Raw Score, Risk of Violent Recidivism Raw Score, Priors Count after 2 Years', 'datasets/compas_index.csv', 'compas', 'All Other, African-American', '{} {}s were predicted to {}recidivate.', '{0.056237081722012784, 0.13793992390361046, 1.0, 0.0948787987402302, 0.23115940649854896, 0.09360175417220817, 0.07267930221636978, 0.17924688325059002, 0.0649493349813091, 0.05174406148026391, 0.09293600672363646, 0.0375390874430841, 0.23115940649854896, 0.22417830634076866, 0.17924688325059002}');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES('Logistic Regression', true, 'Learning Method', 'from sklearn.linear_model import LogisticRegression');

INSERT INTO paramsv VALUES ('Logistic Regression', 'C', '(0,inf)', 'float', '1', 'C is a "regularizer", basically determining how smooth the decision function is. Usually it is set between 0.001 and 10, with smaller values being harsher penalization.');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES ('K Neighbors Classifier', true, 'Learning Method', 'from sklearn.neighbors import KNeighborsClassifier');

INSERT INTO paramsv VALUES ('K Neighbors Classifier', 'n_neighbors', '(0,n)', 'int', '3', 'n_neigbors dictates how many neigboring points are used to predict the new label of a new instance, with <i>integer</i> maximum value n being the size of the dataset. It is usually set between 1 and ~50, depending on the size of the dataset.');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES ('Limited Attribute Effect Regression', false, 'Learning Method', 'from algorithms.limited_attr_effect import LimitedAttributeEffectRegression');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES ('Fair PCA', true, 'Transformer', 'from algorithms.fair_pca import FairPCA');

INSERT INTO paramsv VALUES ('Fair PCA', 'd', '(0,r)', 'int', 'np.ceil(r / 2)', 'd is the reduced <i>integer</i> number of features Fair PCA will construct, with maximum value r being less than the number of features you choose above.');

INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES ('Geometric Fair Representation', true, 'Transformer', 'from algorithms.geo_fair import GeometricFairRepresentation');

INSERT INTO paramsv VALUES ('Geometric Fair Representation', 'lmbda', '[0,1]', 'float', '0', '$\lambda$ is the fairness relaxation parameter, where 0 = fairness constraint is totally enforced, 1 = fairness constraint is not enforced at all.');

-- Crappy(?) (hopefully) temp workaround
INSERT INTO algv
(algv_algname, algv_params, algv_type, algv_import_str)
VALUES('None', false, 'Transformer', '');

-- This is the text the website will load, edit this if you care to do so.
-- Multiline strings in postgres are weird, see https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
INSERT INTO webtext VALUES ('intro',
'<p>Machine learning and artificial intelligence (both terms will fall under the abbreviation of ML throughout this website) are used in many places in the world today, but perhaps most importantly they are being used in impactful decision making settings. '
'This means that ML model predictions are being utilized in a way that directly effects people live''s, and this is concerning given the amount of social bias that''s been shown to be present in the ML predictions. '
'The most famous example of this is in ProPublica''s revolutionary article <a href="https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing">Machine Bias</a> which demonstrated that the recedivism (if a person will re-offend) prediction algorithm COMPAS exhibited racial bias, giving african-american defendants higher risk '
'scores of re-offending than it gave to their white counterparts, even when white defendents had more prior offenses. There are many examples of similar occurences, '
'such as in the (since disabled) <a href="https://www.reuters.com/article/us-amazon-com-jobs-automation-insight/amazon-scraps-secret-ai-recruiting-tool-that-showed-bias-against-women-idUSKCN1MK08G">Amazon hiring algorithm</a> '
'that preferred men over women applicants, or in the algorithm that <a href="https://www.scientificamerican.com/article/racial-bias-found-in-a-major-health-care-risk-algorithm/">gave white patients more time with doctors '
'than black patients</a>.</p>'
'<p>So <i>why</i> are ML models biased? The basic reasons are: 1.) data can encode biases (e.g. if less women apply for tech jobs at a company, implicit sexism can be encoded in the data), 2.) ML '
'methods tend to prefer majority classes by virtue of their construction, and 3.) ML methods don''t "explore", so to an ML system past patterns are predictive of future patterns. For more information a good '
'starting place is <a href="https://arxiv.org/abs/1810.08810">The Frontiers of Fairness in Machine Learning</a>. This website exists to try and educate people about the problem, while also '
'demonstrating some useful concepts around how researchers think about "fairness". If you see a term that''s confusing, hover over it and a tooltip should appear to help out or explain in more depth. Have fun experimenting!'
'<h4>Website Guide</h4>'
'<ol><li>Select dataset, then choose features by clicking the checkboxes. (Some models require the sensitive attribute, others don''t - a notification will appear if this happens).</li>'
'<li>Select a learning method, then optionally a transformer. Either enter a value in the boxes that appear, or leave them blank for defaults to be used.</li>'
'<li>Submit the model - fair warning, this may take up to several minutes in the extreme cases.</li>'
'<li>Try again! Try out different combinations of datasets, features, methods, and hyperparameter values.</li>'
);