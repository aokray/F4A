from flask import Flask, escape, request, render_template, redirect, url_for, send_file, jsonify, session
from utilities.dbUtils import config, connect, connect_insert
from utilities.make_plots import make_plots
from algorithms.log_reg import testLR
import json
import numpy as np

app = Flask(__name__)

dataset = None
algorithm = None
algParams = None
features = None

data_names = connect('SELECT dataset_name, dataset_shortname FROM datasets;')
print('00000000000000000000000000000')
print(data_names)

alg_names = connect('SELECT algv_algname FROM algv;')

@app.route('/')
def index():
    connect('SELECT VERSION()')

    return render_template('index.html', dataset_names=data_names, algorithm_names=alg_names, file={})

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/dataSelect', methods=['GET', 'POST', 'PUT'])
def dataSelect():
    global dataset
    ret = []

    dataShortName = request.args.get('dataname')  #request.form['dataset']
    # print(dataset)
    print("DATA SHORT NAME ")
    print(dataShortName)

    # dataShortName = connect('SELECT dataset_shortname FROM datasets WHERE dataset_name = \'' + dataset +'\';')

    # if (len(dataShortName)):
    #     dataShortName = dataShortName[0][0]

    feats = connect('SELECT dataset_featnames FROM datasets WHERE dataset_shortname = \'' + dataShortName +'\'')[0][0]
    print(feats)
    feats_dict = {}
    feat_names = [x.strip() for x in feats.split(',')]

    # all = connect('SELECT * FROM datasets WHERE dataset_name = \'' + dataset +'\'')[0]
    #
    # print(all[4])
    #
    # data = np.loadtxt(all[4],delimiter=',')
    # sample = data[:,0:-1]
    #
    # sens_attr = [x.strip() for x in all[9].split(',')]
    #
    # make_plots(sample, dataShortName, feat_names, all[2]-1, 1, 2, sens_attr[1], sens_attr[0])

    for i in range(len(feat_names)):
        feats_dict[feat_names[i]] = str(dataShortName) + "/" + str(dataShortName) + str(i)

    for key, val in feats_dict.items():
        ret.append({"featname":key, "metric":np.random.rand(1)[0], "dist":val})

    # return json.dumps(feats_dict)
    return json.dumps(ret)

@app.route('/featSelect', methods=['POST', 'PUT'])
def featSelect():
    global features
    #features = request.form['features']
    features = request.get_json()
    print(features)

    features = [int(key) for key, value in features.items()]

    print(features)

    return ''

@app.route('/algSelect', methods=['GET', 'POST', 'PUT'])
def algSelect():
    global algorithm
    algorithm = request.form['algorithm']

    #results = testLR()

    isParams = connect('SELECT algv_params FROM algv WHERE algv_algname = \'' + algorithm + '\';')[0][0]

    print(isParams, type(isParams))

    if (isParams):
        params = connect('SELECT paramsv_params FROM paramsv WHERE paramsv_alg = \'' + algorithm + '\';')[0][0]

    return '{"' + algorithm + '":' + json.dumps(params) + '}'

@app.route('/runAlg', methods=['GET','POST', 'PUT'])
def runAlg():
    global dataset, algorithm, algParams, features
    #dataset = request.form['dataset']
    #algorithm = request.form['algorithm']
    algParams = request.get_json()
    #
    print(algParams)

    features = algParams['feat_idxs']
    del algParams['feat_idxs']

    dataPath = connect('SELECT dataset_path FROM datasets WHERE dataset_name = \'' + dataset + '\';')[0][0]
    idxsPath = connect('SELECT dataset_idxspath FROM datasets WHERE dataset_name = \'' + dataset + '\';')[0][0]
    sens_idx = connect('SELECT dataset_sensidx FROM datasets WHERE dataset_name = \'' + dataset + '\';')[0][0]

    if features == None:
        feats = '{}'
    else:
        feats = '{'
        ready = [str(x)+',' for x in features]
        for elem in ready:
            feats += elem

        feats = feats[:-1] + str('}') if len(feats) > 2 else feats + str('}')

    algParams_json = json.dumps(algParams)
    # algParams_json = json.loads(algParams_json)

    print('LMAO "DEBUGGING"')
    print(feats)
    checkExisting = connect('SELECT prun_results FROM prun WHERE prun_alg = \'' + algorithm + '\' AND prun_dataset = \'' + dataset + '\' AND prun_params = cast(\'' + algParams_json + '\' AS json) AND prun_feats = \'' + feats +'\';')
    checkExisting = connect('SELECT prun_results FROM prun WHERE prun_alg = \'' + algorithm + '\' AND prun_dataset = \'' + dataset + '\' AND prun_feats = \'' + feats +'\';')

    # This is the bit that runs code - probably modularize this
    if checkExisting is not None:
        results = checkExisting[0][0]
        ret_val = {}
        ret_val['acc'] = results['acc']
        ret_val['sd'] = results['sd']
        print('I FOUND IT, NO RUNNING THE MODEL NECESSARY')
    else:
        results = testLR(dataPath, idxsPath, features, float(algParams['C']), sens_idx-1, 1,2)
        ret_val = {}
        ret_val['acc'] = results[0]
        ret_val['sd'] = results[1]
        #connect_insert('INSERT INTO prun (prun_alg, prun_dataset, prun_params, prun_results, prun_feats) VALUES (\'' + algorithm + '\', \'' + dataset + '\', \'' + algParams +'\', \'' + str(json.dumps(ret_val)) + '\', \'' + feats + '\'); COMMIT;')


    return json.dumps(ret_val)
