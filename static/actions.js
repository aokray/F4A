var typeItemsChecked = {};

var table = new Tabulator("#dataVisualizationTable", {
    //layout: "fitDataFill",
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
        { title: "Similarity", field: "metric", sorter: "number" },
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

function showTable() {
    // var elem = document.getElementById("dataVisTable");
    var elem2 = document.getElementById("dataCheckboxes");
    var dataSelected = document.getElementById("dataset").value;

    if (dataSelected) {
        // elem.style.display = "block";
        elem2.style.display = "block";
    } else {
        // elem.style.display = "none";
        elem2.style.display = "none";
    }
}

function showSubmitButton() {
    var elem = document.getElementById("submitButton");
    var dataSelected = document.getElementById("dataset").value;
    var algSelected = document.getElementById("algorithm").value;

    if (dataSelected && algSelected) {
        elem.style.display = "block";
    } else {
        elem.style.display = "none";
    }
}

// Master function to call all needed startup functions
function startUp() {
    //showTable();
    showSubmitButton();
}

$(function () {
    $("#dataset").change(function (e) {
        showSubmitButton();
        e.preventDefault();
        console.log(document.getElementById("dataset").value);
        $.ajax({
            type: "POST",
            url: "/dataSelect?shortdataname=" + document.getElementById("dataset").value,
            timeout: 0,
            data: $("#dataset").serialize(),
            success: function (data) {
                // $("#dataVisCheckpoint").find("tr:gt(0)").remove();
                formData = JSON.parse(data);
                console.log(formData);

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
                console.log(data);
                var algData = JSON.parse(data);
                console.log(algData);

                var alg_keys = Object.keys(algData);

                var params = algData[alg_keys[0]];

                var param_keys = Object.keys(params);

                // Workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                $("#addParamsHere")[0].innerHTML = "";

                $("#addParamsHere").append(
                    "<br/><p>Optional Hyperparameters for " +
                        $("#algorithm").val() +
                        " are:<br/>"
                );

                for (i = 0; i < param_keys.length; i++) {
                    $("#addParamsHere").append(
                        "<p>" +
                            param_keys[i] +
                            "  (" +
                            params[param_keys[i]] +
                            '):  <input type="text" id="' +
                            param_keys[i] +
                            '" name="hyperp">' +
                            "</p><br/>"
                    );
                }
            },
        });
    });
});

// Probably bad design, ANY submit will go THROUGH THIS FUNCTION.
$(document).on("submit", function (e) {
    var hypers = {};
    console.log($("input[name=hyperp]").val());
    hypers[$("input[name=hyperp]")[0].id] = $("input[name=hyperp]").val();
    console.log(JSON.stringify(hypers));
    e.preventDefault();
    var feat_idxs = [];

    for (obj of table.getSelectedData()) {
        feat_idxs.push(obj["feat_id"]);
    }

    hypers["feat_idxs"] = feat_idxs;

    console.log(feat_idxs);
    // TODO: Disable the fucking button, ezpz
    $.ajax({
        type: "POST",
        timeout: 0, // Important because server may be running model for AWHILE
        url: "/runAlg",
        data: JSON.stringify(hypers),
        contentType: "application/json",
        dataType: "json",
        success: function (data) {
            console.log(data);
            // Need to parse sub JSON file?
            //algData = JSON.parse(data);
            //console.log(algData);
            // TODO: On success, re-enable the button
            //$("#runModel").attr('onclick','this.style.opacity = "0.6"; return false;');
            // document.getElementById("runModel").disabled = true;

            //$("#runModel").attr('onclick','this.style.opacity = "1"; return true;');
            // document.getElementById("runModel").disabled = false;
            $("#accuracy").text("Accuracy: " + data["acc"]);
            $("#sd").text("SD: " + data["sd"]);
        },
    });
    //return false;
});
