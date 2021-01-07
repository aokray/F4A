var typeItemsChecked = {};

var table = new Tabulator("#dataVisualizationTable", {
    //layout: "fitDataFill",
    height: "600px",
    placeholder: "Please choose a dataset",
    columns: [
        //{title:"Include", field:"include"},
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

//table.setData(tableData);
//table.replaceData(tableData); (OPTIONAL AND POSSIBLY FUCKING ANNOYING TO IMPLEMENT)

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
            url: "/dataSelect?dataname=" + document.getElementById("dataset").value,
            timeout: 0,
            data: $("#dataset").serialize(),
            success: function (data) {
                // $("#dataVisCheckpoint").find("tr:gt(0)").remove();
                formData = JSON.parse(data);
                console.log(formData);

                var dict_keys = Object.keys(formData);

                //    for (i = 0; i < dict_keys.length; i++) {
                //        $('#dataVisCheckpoint').append('<tr>'+'\n'+ '<td class="text-center"><input id = "' + i + '" type="checkbox"/></td>' + '\n' +'<td class="text-center">' + dict_keys[i] +'</td>'
                //                                     + '<td class="text-center">' + '<img class="graph" src="static/creditdefault/'+ formData[dict_keys[i]] + '"></td>'+'\n'+'</tr>');

                //    $('#addFeatsHere').append('<input type="checkbox" id="' + i + '" name="features" value="' + i + '"><label>'+dict_keys[i]+'</label><br>')
                //    }
                table.setData(formData);
            },
        });
    });
});

$("#addFeatsHere").on("click", 'input[type="checkbox"]', function (e) {
    if (e.target.name == "features") {
        typeItemsChecked[e.target.value] = e.target.value;
        $("#" + e.target.id).prop("checked", true);
    }
    e.preventDefault();
    console.log(typeItemsChecked);
    $.ajax({
        type: "POST",
        url: "/featSelect",
        data: JSON.stringify(typeItemsChecked),
        contentType: "application/json",
        dataType: "json",
        success: function (data) {
            console.log(data);
        },
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
    $("#dataVisTable input[type=checkbox]:checked").each(function () {
        var row = $(this).closest("tr")[0];
        feat_idxs.push(parseInt(row.cells[0].firstChild.id));
    });

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

function toggleAll(source) {
    checkboxes = document.getElementsByName("features");
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}

$("#checkAll").click(function () {
    $("input:checkbox").not(this).prop("checked", this.checked);
});
