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
    abort,
)
import werkzeug.exceptions as ex
from utilities.dbUtils import config, connect, connect_insert
from utilities.make_plots import make_plots
from sklearn.linear_model import LogisticRegression
import json
import numpy as np
from algorithms.handlers import ResultsHandler, DataHandler
from algorithms.fair_pca import FairPCA
from algorithms.algorithm_defaults import alg_defaults

app = Flask(__name__)

# Globals necessary here?
dataShortName = None
algorithm = None
transformer = None
features = None

data_names = connect("SELECT dataset_name, dataset_shortname FROM datasets;")
alg_names = connect("SELECT algv_algname FROM algv WHERE algv_type = 'Learning Method';")
trans_names = connect("SELECT algv_algname FROM algv WHERE algv_type = 'Transformer' EXCEPT (SELECT 'None');")
webtext = connect("SELECT * FROM webtext;")


@app.route("/")
def index():
    connect("SELECT VERSION();")

    return render_template(
        "index.html", dataset_names=data_names, algorithm_names=alg_names, transformer_names=trans_names #, file={}
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
    feat_names = [x.strip() for x in feats.split(",")]

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


@app.route("/algSelect", methods=["POST"])
def algSelect():
    global algorithm, transformer
    alg_type = request.args.get('alg_type')
    alg = request.args.get('alg')

    if alg_type == 'lm':
        algorithm = alg
    elif alg_type == 'transformer':
        if alg == 'None':
            return f'{{"{alg}": {{}}}}'
        transformer = alg

    else:
        abort(500, 'Unknown algorithm type passed to the backend, please contact administrator and reload the page.')

    
    isParams = connect(
        "SELECT algv_params FROM algv WHERE algv_algname = '" + algorithm + "';"
    )[0][0]

    if isParams:
        params_sql = f"""
            SELECT paramsv_param, paramsv_domain, paramsv_desc FROM paramsv
            WHERE paramsv_alg = '{algorithm if alg_type == 'lm' else transformer}';
        """
        params = connect(params_sql)[0]

    info_dict = {}
    info_dict['param'] = params[0]
    info_dict['domain'] = params[1]
    info_dict['desc'] = params[2]

    return f'{{"{alg}": {json.dumps(info_dict)}}}'

# TODO: make this more modular
@app.route("/runAlg", methods=["POST"])
def runAlg():
    global dataShortName, algorithm, transformer, features
    ret_strs = []
    ret_val = {}

    data = request.get_json()
    lm_hyperparams = data['lm_hyperparams']
    transformer_hyperparams = data['transformer_hyperparams']

    features = data["feat_idxs"]

    def_hyperp_query_str = """
        SELECT paramsv_default FROM paramsv 
        WHERE paramsv_param = '{}';
    """
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

    dh = DataHandler(dataPath, idxsPath)
    n = dh.dataset.shape[0]
    p = dh.dataset.shape[1] - 1

    # Temporary measure - only allow real numbers to be hyperparameters, e.g. no changing loss function from L1 to L2
    # Use of eval() begins to unravel this measure
    for key, val in lm_hyperparams.items():
        if val is None or val == '':
            def_val = connect(def_hyperp_query_str.format(key))[0][0]
            lm_hyperparams[key] = eval(def_val)
        else:
            lm_hyperparams[key] = float(lm_hyperparams[key])

    for key, val in transformer_hyperparams.items():
        if val is None or val == '':
            def_val = connect(def_hyperp_query_str.format(key))[0][0]
            transformer_hyperparams[key] = eval(def_val)
        else:
            transformer_hyperparams[key] = int(transformer_hyperparams[key])

    
    if features is None or features == []:
        abort(500, 'You must select at least one feature in the checklist above.')
    else:
        feats = "{"
        ready = [str(x) + "," for x in features]
        for elem in ready:
            feats += elem

        feats = feats[:-1] + str("}") if len(feats) > 2 else feats + str("}")


    # TODO: try to clean this up, but something like this is necessary as the project enters multiple hyperparameter territory
    sel_str = ''
    counter = 0
    for key, val in lm_hyperparams.items():
        if counter == 0:
            sel_str += f' and hv.prunhv_name = \'{key}\' and hv.prunhv_value = {val}\n'
        else:
            sel_str += f' AND EXISTS (SELECT 1 FROM prunhv hv{counter} where hv{counter}.prunhv_id = hv.prunhv_id and hv{counter}.prunhv_name = \'{key}\' and hv{counter}.prunhv_value = {val})\n'

        counter += 1

    for key, val in transformer_hyperparams.items():
        sel_str += f' AND EXISTS (SELECT 1 FROM prunhv hv{counter} where hv{counter}.prunhv_id = hv.prunhv_id and hv{counter}.prunhv_name = \'{key}\' and hv{counter}.prunhv_value = {val})\n'
        
        counter += 1

    cE_str = f"""
    select prun_results from prun
    INNER JOIN prunhv hv on prun_id = hv.prunhv_id
    where prun_lm_alg = '{algorithm}'
    and prun_t_alg = '{transformer}'
    and prun_dataset = '{dataset}'
    and prun_feats = '{feats}'
    {sel_str};
    """

    checkExisting = connect(cE_str)

    # TODO: Modularize this (further?)
    if checkExisting != [] and checkExisting is not None:
        results = checkExisting[0][0]
        
        ret_val["acc"] = round(results["acc"], 3)
        ret_val["sd"] = round(results["sd"], 3)
        ret_val["U_up"] = results["U_up"]
        ret_val["U_down"] = results["U_down"]
        ret_val["P_up"] = results["P_up"]
        ret_val["P_down"] = results["P_down"]

        print("I FOUND IT, NO RUNNING THE MODEL NECESSARY")
    else:
        lm_string = algorithm.replace(' ', '')

        # Set lm and transformer vars
        if lm_string in alg_defaults:
            lm_hyperparams.update(alg_defaults[lm_string])

        lm = eval(lm_string + '(**lm_hyperparams)')
        
        if transformer is not None:
            transformer_string = transformer.replace(' ', '')
            
            if transformer_string in alg_defaults:
                transformer_hyperparams.update(alg_defaults[transformer_string])

            t = eval(transformer_string + '(**transformer_hyperparams)')
        else:
            t = None

        try:
            results = ResultsHandler(lm, dh, sens_idx-1, (sens_vals[0], sens_vals[1]), features, transformer = t).get_results()
        except Exception as e:
            # Simply returns a 500 error and spits out the exception the learning method returns - not great
            # TODO: make the error codes MUCH better (DB table maybe?)
            abort(500, e)

        ret_val["acc"] = 100 * round(results[0], 5)
        ret_val["sd"] = round(results[1], 3)
        ret_val["U_up"] = results[2]
        ret_val["U_down"] = results[3]
        ret_val["P_up"] = results[4]
        ret_val["P_down"] = results[5]

        get_id = "SELECT MAX(prun_id) from prun;";
        largest_id = connect(get_id)[0][0]
        if largest_id == [] or largest_id is None:
            largest_id = 0
        else:
            largest_id = largest_id + 1
        
        ins_sql = f"""
            INSERT INTO prun (prun_lm_alg, prun_t_alg, prun_dataset, prun_id, prun_results, prun_feats) VALUES
                (
                    '{algorithm}',
                    '{transformer}',
                    '{dataset}',
                    '{largest_id}',
                    '{str(json.dumps(ret_val))}',
                    '{feats}'
                );
            COMMIT;
        """

        # Both this and the next if statement delete default arguments
        # TODO: clean this up, it's so ugly
        if lm_string in alg_defaults:
            for key, val in alg_defaults[lm_string].items():
                del lm_hyperparams[key]

        if transformer is not None:
            if transformer_string in alg_defaults:
                for key, val in alg_defaults[transformer_string].items():
                    del transformer_hyperparams[key]

        args_str = ',\n'.join(("({}, '{}', {})".format(largest_id, key, val)) for key, val in lm_hyperparams.items())

        if transformer is not None:
            args_str += ',\n'
            args_str += ',\n'.join(("({}, '{}', {})".format(largest_id, key, val)) for key, val in transformer_hyperparams.items())

        ins_sql2 = f"""
            INSERT INTO prunhv (prunhv_id, prunhv_name, prunhv_value) VALUES
            {args_str};
            COMMIT;
        """

        connect_insert(ins_sql)
        connect_insert(ins_sql2)

    # TODO: Clean up this putrid mess
    ks = list(ret_val.keys())
    # print('KS--------------------')
    # print(ks)
    for idx in range(len(ks) - 2):
        if idx < 2:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[0].lower()))
        else:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[1].lower()))

    return json.dumps([ret_strs, ret_val, {'label_str': label_desc}, {'sens_names': sens_names}])
