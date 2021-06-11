var table = new Tabulator("#dataVisualizationTable", {
    layout: "fitDataStretch",
    height: "600px",
    placeholder: "Please choose a dataset",
    columns: [
        {
            formatter: "rowSelection",
            titleFormatter: "rowSelection",
            hozAlign: "center",
            headerSort: false,
            cellClick: function (e, cell) {
                cell.getRow().toggleSelect();
            },
        },
        { title: "Feature ID", field: "feat_id", visible: false},
        { title: "Feature Name", field: "featname", sorter: "string" },
        { title: "Distance", field: "metric", sorter: "number" },
        {
            title: "Distribution",
            field: "dist",
            hozAlign: "center",
            headerSort: false,
            formatter: "image",
            formatterParams: { height: "250px", width: "250px", urlPrefix: "static/", urlSuffix: ".png" },
        },
    ],
});


function showSubmitButton() {
    var elem = document.getElementById("submitButton");
    var dataSelected = document.getElementById("dataset").value;
    var algSelected = document.getElementById("algorithm").value;

    if (dataSelected && algSelected) {
        elem.style.display = "block";
        document.getElementById("belowSubmit").style.display = "block";
    } else {
        elem.style.display = "none";
    }
}

// Master function to call all needed startup functions
function startUp() {
    //showTable();
    showSubmitButton();
}

function makePlot(res) {
    u_up = res['U_up'];
    u_down = res['U_down'];
    p_up = res['P_up'];
    p_down = res['P_down'];

    var u_tot = u_up + u_down;
    var p_tot = p_up + p_down;

    var up_tot = u_up + p_up;
    var down_tot = u_down + p_down;

    plotLoc = document.getElementById('addPlotHere');

    var data1 = {
            x: ['Men', 'Women'],
            y: [u_up / u_tot, p_up / p_tot],
            name: 'Predicted Default',
            type: 'bar'
    };

    var data2 = {
            x: ['Men', 'Women'],
            y: [u_down / u_down, p_down / p_down],
            name: 'Predicted No Default',
            type: 'bar'
    };

    var data = [data1, data2];
    var layout = {
        barmode: 'group',
        title: 'Percent of Each Group Predicted as Defaulting/Not Defaulting'
    };

    Plotly.newPlot(plotLoc, data, layout);
}

$(function () {
    $("#dataset").change(function (e) {
        showSubmitButton();
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/dataSelect?shortdataname=" + document.getElementById("dataset").value,
            timeout: 0,
            data: $("#dataset").serialize(),
            success: function (data) {
                // $("#dataVisCheckpoint").find("tr:gt(0)").remove();
                formData = JSON.parse(data);

                var dict_keys = Object.keys(formData);

                table.setData(formData);
            },
        });
    });
});

$(function () {
    $("#algorithm").change(function (e) {
        showSubmitButton();
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/algSelect",
            data: $("#algorithm").serialize(),
            success: function (data) {
                var algData = JSON.parse(data);

                var alg_keys = Object.keys(algData);

                var params = algData[alg_keys[0]];

                var param_keys = Object.keys(params);

                // Possibly just a workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                $("#addLMParamsHere")[0].innerHTML = "";

                $("#addLMParamsHere").append(
                    "<br/><p>Optional Hyperparameters for " +
                        $("#algorithm").val() +
                        " are:<br/>"
                );

                for (i = 0; i < param_keys.length; i++) {
                    $("#addLMParamsHere").append(
                        "<p>" +
                            params[param_keys[i]] +
                            ' <input type="text" id="' +
                            params[param_keys[i]] +
                            '" name="lm_hyperp">' +
                            "</p><br/>"
                    );
                }
            },
        });
    });
});

$(function (){
    $("#transformer").change(function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/transformerSelect",
            data: $("#transformer").serialize(),
            success: function(data) {
                var algData = JSON.parse(data);

                console.log('ALGDATA');
                console.log(algData);

                var alg_keys = Object.keys(algData);

                var params = algData[alg_keys[0]];

                var param_keys = Object.keys(params);

                // Possibly just a workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                $("#addTParamsHere")[0].innerHTML = "";

                if (!jQuery.isEmptyObject(params)){
                    $("#addTParamsHere").append(
                        "<br/><p>Optional Hyperparameters for " +
                            $("#transformer").val() +
                            " are:<br/>"
                    );
                }
                
                for (i = 0; i < param_keys.length; i++) {
                    $("#addTParamsHere").append(
                        "<p>" +
                            params[param_keys[i]] +
                            ' <input type="text" id="' +
                            params[param_keys[i]] +
                            '" name="t_hyperp">' +
                            "</p><br/>"
                    );
                }
            },
        });
    });
});

// Probably bad design, ANY submit will go THROUGH THIS FUNCTION.
$(document).on("submit", function (e) {
    // JSON to send to backend format: 
    // returned = {
    //     "features": {},
    //     "lm_hyperparams": {},
    //     "transformer_hyperparams": {}
    // }
    
    var to_backend = {};
    var lm_hyperparams = {};
    var transformer_hyperparams = {};

    for (obj of $("input[name=lm_hyperp]")){
        lm_hyperparams[obj.id] = obj.value;
    }

    to_backend['lm_hyperparams'] = lm_hyperparams;

    for (obj of $("input[name=t_hyperp]")){
        transformer_hyperparams[obj.id] = obj.value;
    }

    to_backend['transformer_hyperparams'] = transformer_hyperparams;

    e.preventDefault();
    var feat_idxs = [];

    for (obj of table.getSelectedData()) {
        feat_idxs.push(obj["feat_id"]);
    }

    to_backend["feat_idxs"] = feat_idxs;
    document.getElementById("results_div").style.display = 'none';

    $(this).find(':input[type=submit]').prop('disabled', true);

    $.ajax({
        type: "POST",
        timeout: 0, // Important because server may be running model for AWHILE
        url: "/runAlg",
        data: JSON.stringify(to_backend),
        contentType: "application/json",
        dataType: "json",
        success: function (data) {
            $("#runModel").prop('disabled', false);
            document.getElementById("loading").style.display = 'none';

            var res = data[1];
            var res_str = data[0];
            
            console.log(res);
            console.log(res_str);

            // Make the results div appear
            document.getElementById("results_div").style.display = 'block';
            $("#accuracy").text("Accuracy: " + res["acc"] + "%");
            $("#sd").text("Statistical Disparity: " + res["sd"]);
            $("#p_up").text(res_str[0]);
            $("#p_down").text(res_str[1]);
            $("#u_up").text(res_str[2]);
            $("#u_down").text(res_str[3]);

            makePlot(res);
        },
        error: function(request, status, error) {
            $("#runModel").prop('disabled', false);
            document.getElementById("loading").style.display = 'none';
            console.log(request);
            alert(new DOMParser().parseFromString(request.responseText, "text/html").documentElement.lastChild.lastElementChild.textContent);
        }
    });
    document.getElementById("loading").style.display = 'block';
});
