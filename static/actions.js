// At the very least, cannot be declared in the function because on each hover it resets the counter
// and slows the page down with a typeset every hover
var hover_count = 0;

// Force the mobile page to load in landscape
screen.orientation.lock('landscape');

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
        { title: "Feature Name", field: "featname", sorter: "string", headerTooltip: "Click the checkboxes to use this feature in the model"},
        { title: "Distance", field: "metric", sorter: "number", headerTooltip: "Hellinger Distance, 0 = Distributions are the same, 1 = Distributions are totally different" },
        {
            title: "Distribution",
            field: "dist",
            hozAlign: "center",
            headerSort: false,
            headerTooltip: "These images show how the values of one subpopulation relates to another subpopulation (e.g. how much men pay in one month vs how much women pay in one month). More overlap means the two wubpopulations are more similar.",
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
    showSubmitButton();
}


function makePlot(res, label_str, up_names) {
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
            // x: ['Men', 'Women'],
            x: [up_names[0], up_names[1]],
            y: [u_up / u_tot, p_up / p_tot],
            name: 'Predicted to ' + label_str,
            type: 'bar'
    };

    var data2 = {
            x: [up_names[0], up_names[1]],
            y: [u_down / u_tot, p_down / p_tot],
            name: 'Predicted No ' + label_str,
            type: 'bar'
    };

    var data = [data1, data2];
    var layout = {
        barmode: 'group',
        title: '% Per Group Predicted to ' + label_str + '/Not '+ label_str,
        legend: {
            x: 0.7,
            y: 1.1
        }
    };

    // Necessary?
    var config = {
        responsive: true
    };

    Plotly.newPlot(plotLoc, data, layout, config);
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
                all_data = JSON.parse(data);
                formData = all_data['formData'];
                sens_name = all_data['sens_name'];

                $('#sens_feature_info')[0].innerHTML = 'Sensitive Feature: ' + sens_name;

                var dict_keys = Object.keys(formData);

                table.setData(formData);
            },
        });

        $('html, body').animate({
            scrollTop: $("#dataset").offset().top
        }, 900);
    });
});

$(function () {
    $("#algorithm").change(function (e) {
        showSubmitButton();
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/algSelect?alg=" + document.getElementById('algorithm').value + '&alg_type=lm',
            data: $("#algorithm").serialize(),
            success: function (data) {
                // Possibly just a workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                $("#addLMParamsHere")[0].innerHTML = "";

                var algData = JSON.parse(data);

                var alg = Object.keys(algData);

                if (alg.length) {
                    var params_data = algData[alg];

                    var param = params_data['param'];

                    var domain = params_data['domain'];
                    var desc = params_data['desc'];

                    var l_bracket = domain.slice(0,1);
                    var dom = domain.slice(1, domain.length-1);
                    var r_bracket = domain.slice(domain.length-1, domain.length);
                    domain = dom.split(',');

                    // Check if the second command is the latex command inf
                    if (domain[1] == 'inf') {
                        domain[1] = '\\' + domain[1];
                    }

                // Possibly just a workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                // $("#addLMParamsHere")[0].innerHTML = "";

                
                    $("#addLMParamsHere").append(
                        "<br/><p>Optional Hyperparameter(s) for " +
                            $("#algorithm").val() +
                            ":<br/>"
                    );

                    // TODO: expand to allow more than one hyperp by adjusting return format and parsing methodology
                    for (i = 0; i < 1; i++) {
                        $("#addLMParamsHere").append(
                            "<p><span class='lm_tooltip' title='" +
                                desc +
                                "'>" +
                                param +
                                ' </span><input type="text" id="' +
                                param +
                                '" name="lm_hyperp">' +
                                " Valid Values: $" +
                                l_bracket +
                                domain[0] +
                                ',' +
                                domain[1] +
                                r_bracket +
                                "$</p><br/>"
                        );
                    }
                }
                // TODO: Why is THIS necessary here?
                hover_count = 0;
                MathJax.typeset();
            },
        });

        // It's lit!
        $('html, body').animate({
            scrollTop: $("#addLMParamsHere").offset().top
        }, 900);
    });
});

$(function (){
    $("#transformer").change(function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/algSelect?alg=" + document.getElementById('transformer').value + '&alg_type=transformer',
            data: $("#transformer").serialize(),
            success: function(data) {
                var algData = JSON.parse(data);

                var alg = Object.keys(algData);

                if (alg == 'None'){
                    $("#addTParamsHere")[0].innerHTML = "";
                    return;
                }

                var params_data = algData[alg];

                var param = params_data['param'];
                var print_param = null;
                if (param == 'lmbda') {
                    print_param = '\\' + param;
                } else {
                    print_param = param;
                }

                var domain = params_data['domain'];
                var desc = params_data['desc'];

                var l_bracket = domain.slice(0,1);
                var dom = domain.slice(1, domain.length-1);
                var r_bracket = domain.slice(domain.length-1, domain.length);
                domain = dom.split(',');

                // Check if the second command is the latex command inf
                if (domain[1] == 'inf'){
                    domain[1] = '\\' + domain[1];
                }

                // Possibly just a workaround - just ensure that the hyperparameter div is absolutely empty
                //  before adding a new hyperparameter section
                $("#addTParamsHere")[0].innerHTML = "";

                $("#addTParamsHere").append(
                    "<br/><p>Optional Hyperparameter(s) for " +
                        $("#transformer").val() +
                        ":<br/>"
                );

                // TODO: expand to allow more than one hyperp by adjusting return format and parsing methodology
                for (i = 0; i < 1; i++) {
                    $("#addTParamsHere").append(
                        "<p><span class='t_tooltip' title='" +
                            desc + 
                            "'>$" +
                            print_param +
                            '$ </span><input type="text" id="' +
                            param +
                            '" name="t_hyperp">' +
                            " Valid Values: $" +
                            l_bracket +
                            domain[0] +
                            ',' +
                            domain[1] +
                            r_bracket +
                            "$</p><br/>"
                    );
                }

                MathJax.typeset();
            },
        });
        hover_count = 0;
        $('html, body').animate({
            scrollTop: $("#addTParamsHere").offset().top
        }, 900);

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

            var res_str = data[0];
            var res = data[1];
            var label_str = data[2]['label_str'];
            var up_names = data[3]['sens_names'];

            // Make the results div appear
            document.getElementById("results_div").style.display = 'block';
            $("#accuracy").text("Accuracy: " + res["acc"] + "%");
            $("#sd").text("Statistical Disparity: " + res["sd"]);
            $("#eo").text("Does This Model Approximately Satisfy Equalized Odds? : " + (res['eo'] ? "Yes" : "No"));
            $("#eo")[0].title ='<p>' + up_names[0] + ':</p><p>Average TPR: ' + res['rates'][0] + '</p><p>Average FPR: ' + res['rates'][1] + '</p><br><p>' + up_names[1] + '</p><p>Average TPR: ' + res['rates'][2] + '</p><p>Average FPR: ' + res['rates'][3] + '</p>';
            $("#p_up").text(res_str[0]);
            $("#p_down").text(res_str[1]);
            $("#u_up").text(res_str[2]);
            $("#u_down").text(res_str[3]);

            $("#modal-info_zp")[0].innerHTML = 'Uh oh! Be wary of these results, your model has predicted no ' +
            up_names[0].toLowerCase() +
            ' or ' +
            up_names[1].toLowerCase() +
            ' will ' +
            label_str.toLowerCase() +
            ' at all! Even if the accuracy is relatively high, this model will predict no one will ever ' +
            label_str.toLowerCase() +
            ', meaning it is equivalent to just assuming no one will ever ' +
            label_str.toLowerCase() +
            '. Try adding more features and see what happens!';

            $("#modal-info_btpr")[0].innerHTML = 'Uh oh! Be wary of these results, your model has predicted less than half of those who should  ' +
            label_str.toLowerCase() +
            ', in one group or the other, actually will. If you still see a high accuracy, it is because the model is predicted many false positives (people in the opposite situation) correctly. ' +
            'This is because the problem is "inbalanced", meaning more people will not '+ 
            label_str.toLowerCase() + 
            ' , as opposed to those that should predicted to ' +
            label_str.toLowerCase() + '.'
            ;

            if (res['U_up'] <= 1 && res['P_up'] <= 1) {
                $("#warningModal_zero_positives").modal('show');
            }

            if(res['rates'][0] < 0.5 || res['rates'][2] < 0.5) {
                $("#warningModal_bad_tpr").modal('show');
            }

            makePlot(res, label_str, up_names);

            $('html, body').animate({
                scrollTop: $("#results").offset().top
            }, 900);
        },
        error: function(request, status, error) {
            $("#runModel").prop('disabled', false);
            document.getElementById("loading").style.display = 'none';
            $('#modal-info_backend_error')[0].innerHTML = new DOMParser().parseFromString(request.responseText, "text/html").documentElement.lastChild.lastElementChild.textContent;
            $("#warningModal_backend").modal('show');
        }
    });

    document.getElementById("loading").style.display = 'block';
    $('html, body').animate({
        scrollTop: $("#loading").offset().top
    }, 900);
});

$(document).ready(function () {
    $('.tooltipst').tooltipster({
        content: $('<div>THIS IS THE LOGO!</div>'),
        // Doesn't work :(
        theme: 'tooltipster-punk'
    });
});


// This garbage is needed for tooltips on dynamically created content.
// TODO: figure out how to make this work for n hyperparameters (altho probably just hardcoding in 2-3 is fine)
$('body').on('mouseover mouseenter', '.lm_tooltip', function(){
    $(this).tooltipster();
    $(this).tooltipster('show');
});


$('body').on('mouseover mouseenter', '.t_tooltip', function(){
    hover_count++;

    $(this).tooltipster();
    $(this).tooltipster('show');

    if (hover_count < 2) {
        MathJax.typeset();
    }
});

$('body').on('mouseover mouseenter', '.eo', function(){
    $(this).tooltipster({contentAsHTML: true});
    $(this).tooltipster('show');
});