// ------------------
// Initializations
// ------------------
var timeline = undefined;
var timeline_data = undefined;
var timeline_last_request = undefined;
var edit_offtime_id = undefined;

if (google !== undefined){
    google.load("visualization", "1");

    // Set callback to run when API is loaded
    google.setOnLoadCallback(drawVisualization);
}

$(document).ready(function(){
    if ($('#mytimeline').length != 0){
        $(window).resize(function(){
            /*
            $('#content').height( $(window).height() - $(".navbar").height() 
                            - parseInt($(".navbar").css("margin-bottom"))
                            - parseInt($(".navbar").css("margin-top")) 
                            - parseInt($('#content').css("margin-bottom"))
                            - parseInt($('#content').css("margin-top"))
                            );  
            */
        });
        //$(window).resize();

        setDatePicker();
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
//
function setDatePicker(){
    $('#addOfftime #id_start_date').datepicker({"dateFormat": 'yy-mm-dd'});
    $('#addOfftime #id_end_date').datepicker({"dateFormat": 'yy-mm-dd'});
}

function addOfftime(clean){
    if (clean == true){
        $.get('/ajax/add_offtime.html', function(data) {
            edit_offtime_id = undefined;
            $('#addOfftime div.modal-body').html(data);
            setDatePicker();
        });
    }else{
        var input = $('#addOfftime form').serialize();
        if (edit_offtime_id == undefined){
            url = '/ajax/add_offtime.html'
        }else{
            url = '/ajax/edit_offtime/' + edit_offtime_id + '.html'
        }
        $.post(url, input, function(data) {
            if (data == null){
                $('#addOfftime').modal('hide')
                addOfftime(true)
            }else{
                $('#addOfftime div.modal-body').html(data);
                setDatePicker();
            }
        });
    }
}

function editOfftime(id){
    $.get('/ajax/edit_offtime/' + id + '.html', function(data) {
        edit_offtime_id = id;
        $('#addOfftime div.modal-body').html(data);
        $('#addOfftime').modal('show')
        setDatePicker();
    });
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
        height: "auto",
        minHeight: 400,
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

    var s = new Date();
    s.setDate(s.getDate() - 90);
    var e = new Date();
    e.setDate(e.getDate() + 270);
    timeline.setVisibleChartRange(s, e)

    // ajax function to refresh graph
    setInterval(function(){
        $.get('ajax/timeline.json', function(data) {
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

    function add_offtime(person_id, name, offtime_id, offtime_type_id, start, end, approved){
        is_group = (person_id == -1)
        if (approved){
            var class_name = offtime_id == -1 ? 'timeline_hidden' : OFFTIME_TYPE_STR + offtime_type_id;
        }else{
            var class_name = 'timeline_unapproved'
        }
        var content_name = offtime_id == -1 ? '' : data['offtime_types'][offtime_type_id][0];

        function pad(num, size) {
            // add leading zeros
            var s = num+"";
            while (s.length < size) s = "0" + s;
            return s;
        }
        var group = '<div class="timeline_hidden">' + pad(counter, 5) + '</div>';
        if (is_group){
            group = group + '<b>' + name + '</b>';
        }else{
            group = group + '<a href="#" onclick="return show_person_detail(' + person_id + ')">' + name + '</a>';
        }
        //console.log([start, end, content_name, group, class_name]);
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
            add_offtime(-1, cap_name, -1, -1, date, date, true, false);
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
                    var approved = offtime_tup[4];
                    add_offtime(person_id, person_name, offtime_id, offtime_type_id, start, end, approved);
                });
                if (!offtimes.length){
                    add_offtime(person_id, person_name, -1, -1, date, date, true, false);
                }
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


function show_person_detail(person_id){
    $.get('/ajax/person_detail/' + person_id + '.html', function(data) {
        $('#offtime').html(data);
    });
    return false;
}

function replace_offtime(offtime_id, action){
    var temp = offtime_id;
    if (action !== undefined){
        temp += '/' + action
    }
    $.get('/ajax/offtime/' + temp + '.html', function(data) {
        $('#offtime').html(data);
    });
    return false;
}


var select_timeline_object = function (event) {
    var s = timeline.getSelection()[0];
    if (s){
        replace_offtime(timeline_data.getValue(s.row, 0));
    }
};
