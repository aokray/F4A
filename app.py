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
from algorithms.log_reg import testLR
import json
import numpy as np

app = Flask(__name__)

# Globals necessary here?
dataShortName = None
algorithm = None
algParams = None
features = None

data_names = connect("SELECT dataset_name, dataset_shortname FROM datasets;")
alg_names = connect("SELECT algv_algname FROM algv;")


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
            SELECT paramsv_params FROM paramsv
            WHERE paramsv_alg = '{algorithm}';
        """
        params = connect(params_sql)[0][0]

    return f'{{"{algorithm}": {json.dumps(params)}}}'

@app.route("/runAlg", methods=["GET", "POST", "PUT"])
def runAlg():
    global dataShortName, algorithm, algParams, features
    ret_strs = []
    ret_val = {}

    algParams = request.get_json()

    features = algParams["feat_idxs"]
    del algParams["feat_idxs"]

    if algParams["C"]:
        algParams["C"] = float(algParams["C"])

    dat_info_query = f"""
        SELECT dataset_path, dataset_idxspath, dataset_sensidx, dataset_name, dataset_sensnames, dataset_labeldesc, dataset_resultsstr from datasets
        WHERE dataset_shortname = '{dataShortName}';
    """
    dat_info = connect(dat_info_query)[0]
    dataPath = dat_info[0]
    idxsPath = dat_info[1]
    sens_idx = dat_info[2]
    dataset = dat_info[3]
    sens_names = dat_info[4]
    sens_names = [x.strip() for x in sens_names.split(",")]
    label_desc = dat_info[5]
    res_str = dat_info[6]

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

    cE_str = f"""
        select prun_results from prun
        where prun_alg = '{algorithm}'
        and prun_dataset = '{dataset}'
        and (
                prun_params::jsonb @> '{algParams_json}'::jsonb
                and 
                prun_params::jsonb <@ '{algParams_json}'::jsonb
            )
        and prun_feats = '{feats}';
    """

    checkExisting = connect(cE_str)

    # TODO: Modularize this
    if checkExisting != []:
        results = checkExisting[0][0]
        ret_val["acc"] = results["acc"]
        ret_val["sd"] = results["sd"]
        ret_val["U_up"] = results["U_up"]
        ret_val["U_down"] = results["U_down"]
        ret_val["P_up"] = results["P_up"]
        ret_val["P_down"] = results["P_down"]
        print("I FOUND IT, NO RUNNING THE MODEL NECESSARY")
    else:
        # Generalize this
        results = testLR(
            dataPath, idxsPath, features, algParams, sens_idx - 1, 1, 2
        )
        ret_val["acc"] = results[0]
        ret_val["sd"] = results[1]
        ret_val["U_up"] = results[2]
        ret_val["U_down"] = results[3]
        ret_val["P_up"] = results[4]
        ret_val["P_down"] = results[5]
        
        ins_sql = f"""
            INSERT INTO prun VALUES
                (
                    '{algorithm}',
                    '{dataset}',
                    '{algParams_json}',
                    '{str(json.dumps(ret_val))}',
                    '{feats}'
                );
            COMMIT;
        """

        connect_insert(ins_sql)

    ks = list(ret_val.keys())
    for idx in range(len(ks) - 2):
        if idx < 2:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[0].lower()))
        else:
            ret_strs.append(res_str.format(ret_val[ks[idx + 2]], sens_names[1].lower()))

    return json.dumps([ret_strs, ret_val])
