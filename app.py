from flask import (
    Flask,
    escape,
    request,
    render_template,
    redirect,
    url_for,
    send_file,
    jsonify,
    session,
)
from utilities.dbUtils import config, connect, connect_insert
from utilities.make_plots import make_plots
from sklearn.linear_model import LogisticRegression
import json
import numpy as np
from algorithms.handlers import ResultsHandler, DataHandler
from algorithms.fair_pca import FairPCA

app = Flask(__name__)

# Globals necessary here?
dataShortName = None
algorithm = None
algParams = None
features = None

data_names = connect("SELECT dataset_name, dataset_shortname FROM datasets;")
alg_names = connect("SELECT algv_algname FROM algv;")
webtext = connect("SELECT * FROM webtext;")


@app.route("/")
def index():
    connect("SELECT VERSION();")

    return render_template(
        "index.html", dataset_names=data_names, algorithm_names=alg_names, file={}
    )


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/dataSelect", methods=["GET", "POST", "PUT"])
def dataSelect():
    global dataShortName
    ret = []

    dataShortName = request.args.get("shortdataname")

    feats_sql = f"""
        SELECT dataset_featnames, dataset_hdist FROM datasets
        WHERE dataset_shortname = '{dataShortName}';
    """

    query = connect(feats_sql)[0]
    feats = query[0]
    hdists = query[1]
    # sens = connect(data_info_sql)[0][1]
    feat_names = [x.strip() for x in feats.split(",")]
    # sens_names = [x.strip() for x in sens.split(",")]

    # still need until admin page
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
        ret.append(
            {
                "feat_id": i,
                "featname": feat_names[i],
                "metric": hdists[i],
                "dist": str(dataShortName) + "/" + str(dataShortName) + str(i),
            }
        )

    return json.dumps(ret)


@app.route("/algSelect", methods=["GET", "POST", "PUT"])
def algSelect():
    global algorithm
    algorithm = request.form["algorithm"]

    isParams = connect(
        "SELECT algv_params FROM algv WHERE algv_algname = '" + algorithm + "';"
    )[0][0]

    if isParams:
        params_sql = f"""
            SELECT paramsv_param FROM paramsv
            WHERE paramsv_alg = '{algorithm}';
        """
        params = connect(params_sql)

    return f'{{"{algorithm}": {json.dumps(params)}}}'

@app.route("/runAlg", methods=["GET", "POST", "PUT"])
def runAlg():
    global dataShortName, algorithm, algParams, features
    ret_strs = []
    ret_val = {}

    algParams = request.get_json()

    # Features aren't algorithm parameters, but it's easy to ship them to the backend this way for now
    # Delete them so we don't consume them as hyperp's
    features = algParams["feat_idxs"]
    del algParams["feat_idxs"]

    # Temporary measure - only allow real numbers to be hyperparameters, e.g. no changing loss function from L1 to L2
    for key, val in algParams.items():
        algParams[key] = float(algParams[key])

    dat_info_query = f"""
        SELECT dataset_path, dataset_idxspath, dataset_sensidx, dataset_upvals, dataset_name, dataset_sensnames, dataset_labeldesc, dataset_resultsstr from datasets
        WHERE dataset_shortname = '{dataShortName}';
    """

    dat_info = connect(dat_info_query)[0]
    dataPath = dat_info[0]
    idxsPath = dat_info[1]
    sens_idx = dat_info[2]
    sens_vals = dat_info[3]
    dataset = dat_info[4]
    sens_names = dat_info[5]
    sens_names = [x.strip() for x in sens_names.split(",")]
    label_desc = dat_info[6]
    res_str = dat_info[7]

    # TODO: Raise an error here if no features are chosen, on the off-chance that the front-end validation fails
    if features == None:
        feats = "{}"
    else:
        feats = "{"
        ready = [str(x) + "," for x in features]
        for elem in ready:
            feats += elem

        feats = feats[:-1] + str("}") if len(feats) > 2 else feats + str("}")

    algParams_json = json.dumps(algParams)

    # TODO: try to clean this up, but something like this is necessary as the project enters multiple hyperparameter territory
    sel_str = ''
    counter = 0
    for key, val in algParams.items():
        if counter == 0:
            sel_str += f' and hv.prunhv_name = \'{key}\' and hv.prunhv_value = {val}'
        else:
            sel_str += f' AND EXISTS (SELECT 1 FROM prunhv hv{counter} where hv{counter}.prunhv_id = hv.prunhv_id and hv{counter}.prunhv_name = \'{key}\' and hv{counter}.prunhv_value = {val})'

        counter += 1

    cE_str = f"""
        select prun_results from prun
        INNER JOIN prunhv hv on prun_id = hv.prunhv_id
        where prun_alg = '{algorithm}'
        and prun_dataset = '{dataset}'
        and prun_feats = '{feats}'
        {sel_str};
    """

    print(cE_str)

    checkExisting = connect(cE_str)

    print(checkExisting)

    # TODO: Modularize this
    if checkExisting != [] and checkExisting is not None:
        results = checkExisting[0][0]
        
        ret_val["acc"] = results["acc"]
        ret_val["sd"] = results["sd"]
        ret_val["U_up"] = results["U_up"]
        ret_val["U_down"] = results["U_down"]
        ret_val["P_up"] = results["P_up"]
        ret_val["P_down"] = results["P_down"]

        print("I FOUND IT, NO RUNNING THE MODEL NECESSARY")
    else:
        dh = DataHandler(dataPath, idxsPath)
        if algorithm == 'Logistic Regression': 
            results = ResultsHandler(LogisticRegression(max_iter = 1000, **algParams), dh, sens_idx - 1, (sens_vals[0], sens_vals[1]), features).get_results()
        elif algorithm == 'Fair PCA':
            # TODO: Pending frontend algorithm redesign, this will have to do.
            results = ResultsHandler(LogisticRegression(max_iter = 1000, C = algParams['C']), dh, sens_idx - 1, (sens_vals[0], sens_vals[1]), features, transformer = FairPCA(sens_idx - 1, 1, 2, d = int(algParams['d']))).get_results()
        else:
            raise Exception('You cannot run a learning algorithm not in the dropdown menu. How/why did you even do this')

        ret_val["acc"] = results[0]
        ret_val["sd"] = results[1]
        ret_val["U_up"] = results[2]
        ret_val["U_down"] = results[3]
        ret_val["P_up"] = results[4]
        ret_val["P_down"] = results[5]

        get_id = "SELECT MAX(prun_id) from prun;";
        largest_id = connect(get_id)[0][0]
        if largest_id == [] or largest_id == None:
            largest_id = 0
        else:
            largest_id = largest_id + 1
        
        ins_sql = f"""
            INSERT INTO prun (prun_alg, prun_dataset, prun_id, prun_results, prun_feats) VALUES
                (
                    '{algorithm}',
                    '{dataset}',
                    '{largest_id}',
                    '{str(json.dumps(ret_val))}',
                    '{feats}'
                );
            COMMIT;
        """

        args_str = ',\n'.join(("({}, '{}', {})".format(largest_id, key, val)) for key, val in algParams.items())

        ins_sql2 = f"""
            INSERT INTO prunhv (prunhv_id, prunhv_name, prunhv_value) VALUES
            {args_str};
            COMMIT;
        """

        connect_insert(ins_sql)
        connect_insert(ins_sql2)

    ks = list(ret_val.keys())
    for idx in range(len(ks) - 2):
        if idx < 2:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[0].lower()))
        else:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[1].lower()))

    return json.dumps([ret_strs, ret_val])
