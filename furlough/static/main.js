// ------------------
// Initializations
// ------------------
var timeline = undefined;
var timeline_data = undefined;
var timeline_last_request = undefined;

if (google !== undefined){
    google.load("visualization", "1");

    // Set callback to run when API is loaded
    google.setOnLoadCallback(drawVisualization);
}

$(document).ready(function(){
    if ($('#mytimeline').length != 0){
        $(window).resize(function(){
            $('#content').height( $(window).height() - $(".navbar").height() 
                            - parseInt($(".navbar").css("margin-bottom"))
                            - parseInt($(".navbar").css("margin-top")) 
                            - parseInt($('#content').css("margin-bottom"))
                            - parseInt($('#content').css("margin-top"))
                            );  
        });
        $(window).resize();

        $('#addOfftime #id_start_date').datepicker({"dateFormat": 'yy-mm-dd'});
        $('#addOfftime #id_end_date').datepicker({"dateFormat": 'yy-mm-dd'});
    }

    $.styleSheetContains = function (f) {
        var hasstyle = false;
        var fullstylesheets = document.styleSheets;
        for (var sx = 0; sx < fullstylesheets.length; sx++) {
            var sheetclasses = fullstylesheets[sx].rules || document.styleSheets[sx].cssRules;
            for (var cx = 0; cx < sheetclasses.length; cx++) {
                if (sheetclasses[cx].selectorText == f) {
                    hasstyle = true; break;
                    //return classes[x].style;               
                }
            }
        }
        return hasstyle;
    };
});

// ------------------
// gui
// ------------------

function addOfftime(clean){
    if (clean == true){
        $.get('/add_offtime.html', function(data) {
            $('#addOfftime div.modal-body').html(data);
            $('#addOfftime #id_start_date').datepicker({"dateFormat": 'yy-mm-dd'});
            $('#addOfftime #id_end_date').datepicker({"dateFormat": 'yy-mm-dd'});
        });
    }else{
        $.post('/add_offtime.html', $('#addOfftime form').serialize(), function(data) {
            if (data == null){
                $('#addOfftime').modal('hide')
                addOfftime(true)
            }else{
                $('#addOfftime div.modal-body').html(data);
                $('#addOfftime #id_start_date').datepicker({"dateFormat": 'yy-mm-dd'});
                $('#addOfftime #id_end_date').datepicker({"dateFormat": 'yy-mm-dd'});
            }
        });
    }
}

/*
function showContent(which) {
    $('#content div.content-element').css({'display': 'None'})

    el = $('#' + which).css({'display': 'block'})
    if (which != 'mytimeline'){
        el.html('<i id="spin" class="icon-refresh icon-spin icon-4x"></i>')
        // get the new stuff with ajax
        $.ajax("ajax/" + which + ".html")
         .done(function(data) {el.html(data);})
         .fail(function() { el.html("ajax error - reload page, contact admin if it happens often."); })
    }
}

*/

// ------------------
// timeline
// ------------------

// Called when the Visualization API is loaded.
function drawVisualization() {
    timeline_data = new google.visualization.DataTable();
    timeline_data.addColumn('number', 'offtime_id');
    timeline_data.addColumn('datetime', 'start');
    timeline_data.addColumn('datetime', 'end');
    timeline_data.addColumn('string', 'content');
    timeline_data.addColumn('string', 'group');
    timeline_data.addColumn('string', 'className');

    // specify options
    var options = {
        width:  "99%",
        height: "99%",
        layout: "box",
        axisOnTop: true,
        eventMargin: 4,  // minimal margin between events
        eventMarginAxis: 0, // minimal margin beteen events and the axis
        editable: false,
        zoomMin: 1000 * 60 * 60 * 24 * 5, // minimal zoom: 5 days
        showNavigation: true
    };

    // Instantiate our timeline object.
    timeline = new links.Timeline(document.getElementById('mytimeline'));

    // register event listeners
    google.visualization.events.addListener(timeline, 'select', select_timeline_object);

    var now = new Date();
    // Set a customized visible range
    var start = new Date(now.getTime() - 4 * 60 * 60 * 1000);
    var end = new Date(now.getTime() + 8 * 60 * 60 * 1000);
    timeline.setVisibleChartRange(start, end);

    // Draw our timeline with the created data and options
    timeline.draw(timeline_data, options);

    // ajax function to refresh graph
    setInterval(function(){
        $.get('timeline.json', function(data) {
            if (data != timeline_last_request){
                //console.log('update timeline data', data);
                timeline_last_request = data;
                fill_timeline(JSON.parse(data));
            }
        }, 'text');
    }, 1000);
}


function fill_timeline(data){
    OFFTIME_TYPE_STR = 'timeline_offtime_type_'

    function add_offtime(name, offtime_id, offtime_type_id, start, end, accepted, deleted){
        is_group = (offtime_id == -1)
        var class_name = is_group ? 'timeline_hidden' : OFFTIME_TYPE_STR + offtime_type_id;
        var content_name = is_group ? '' : data['offtime_types'][offtime_type_id][0];

        var group = '<div class="timeline_hidden">' + counter + '</div>';
        if (is_group){
            group = group + '<b>' + name + '</b>';
        }else{
            group = group + name;
        }
        console.log([start, end, content_name, group, class_name]);
        timeline_data.addRow([offtime_id, start, end, content_name, group, class_name]);
    }

    // clear table, seams very complicated. strange.
    var num = timeline_data.getNumberOfRows()
    if (num >= 0){
        timeline_data.removeRows(0, num);
    }

    // Create and populate a data table.
    var counter = 0
    $.each(data['capabilities'], function(cap_name, persons) {
        if (persons.length){
            var date = new Date(1, 01, 01);
            add_offtime(cap_name, -1, -1, date, date, true, false);
            counter += 1;
            $.each(persons, function(i, person_id) {
                var person_tup = data['persons'][person_id];
                var person_name = person_tup[0];
                var offtimes = person_tup[1];
                $.each(offtimes, function(i, offtime_tup) {
                    var offtime_id = offtime_tup[0];
                    var offtime_type_id = offtime_tup[1];
                    var start = new Date(offtime_tup[2]);
                    var end = new Date(offtime_tup[3]);
                    var accepted = new Date(offtime_tup[4]);
                    var deleted = new Date(offtime_tup[5]);
                    add_offtime(person_name, offtime_id, offtime_type_id, start, end, accepted, deleted);
                });
                counter += 1;
            });
        }
    });

    timeline.redraw();

    $.each(data['offtime_types'], function(offtime_type_id, offtime_tup) {
        var cls = '.' + OFFTIME_TYPE_STR + offtime_type_id
        var offtime_color = offtime_tup[1];
        style = "<style type='text/css'> " + cls + "{background-color: " 
                                    + offtime_color + " !important;} </style>"
        $(style).appendTo("body");
    });
}

var select_timeline_object = function (event) {
    offtime_id = timeline_data.getValue(timeline.getSelection()[0].row, 0)
    console.log('timeline', offtime_id)
};
