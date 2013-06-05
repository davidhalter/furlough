// ------------------
// Initializations
// ------------------
var timeline = undefined;
var timeline_data = undefined;

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
    timeline_data.addColumn('number', 'id');
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
        eventMargin: 10,  // minimal margin between events
        eventMarginAxis: 0, // minimal margin beteen events and the axis
        editable: true,
        showNavigation: true
    };

    // Instantiate our timeline object.
    timeline = new links.Timeline(document.getElementById('mytimeline'));

    // register event listeners
    google.visualization.events.addListener(timeline, 'edit', onEdit);

    var now = new Date();
    // Set a customized visible range
    var start = new Date(now.getTime() - 4 * 60 * 60 * 1000);
    var end = new Date(now.getTime() + 8 * 60 * 60 * 1000);
    timeline.setVisibleChartRange(start, end);

    // Draw our timeline with the created data and options
    timeline.draw(timeline_data, options);

    // ajax function to refresh graph
    setInterval(function(){
        $.getJSON('timeline.json', function(data) {fill_timeline(data);});
    }, 1000);
}


function fill_timeline(data){
    // clear table, seams very complicated. strange.
    var num = timeline_data.getNumberOfRows()
    if (num >= 0){
        timeline_data.removeRows(0, num);
    }

    // Create and populate a data table.
    $.each(data, function(index, value) {
        var is_group = false;
        if (typeof value === 'string'){
            is_group = true;
            value = [value, []];
        }
        var name = value[0]
        var values = value[1];
        if (values.length == 0) {
            var date = new Date(1, 01, 01);
            values = [[0, date, date, false, '', '#000000']];
        }
        $.each(values, function(index2, date_tuple) {
            var id = date_tuple[0]
            var start = new Date(date_tuple[1]);
            var end = new Date(date_tuple[2]);
            var content = date_tuple[4];
            var className = content == '' ? 'timeline_hidden' : content.toLowerCase();
            group = '<div class="timeline_hidden">' + index + '</div>'
            if (is_group == true){
                group = group + '<b>' + name + '</b>'
            }else{
                group = group + name
            }
            //console.log([start, end, content, group, className]);
            timeline_data.addRow([id, start, end, content, group, className]);
        });
    });
    /*
    var now = new Date();
    var names = ["Algie", "Barney", "Chris"];
    for (var n = 0, len = names.length; n < len; n++) {
        var name = names[n];
        var end = new Date(now.getTime() - 12 * 60 * 60 * 1000);
        for (var i = 0; i < 5; i++) {
            var start = new Date(end.getTime() + Math.round(Math.random() * 5) * 60 * 60 * 1000);
            var end = new Date(start.getTime() + Math.round(4 + Math.random() * 5) * 60 * 60 * 1000);

            var r = Math.round(Math.random() * 2);
            var availability = (r === 0 ? "Unavailable" : (r === 1 ? "Available" : "Maybe"));
            var group = availability.toLowerCase();
            var content = availability;
            timeline_data.addRow([start, end, content, name, group]);
        }
    }
    */
    timeline.redraw();
}


function getSelectedRow() {
    var row = undefined;
    var sel = timeline.getSelection();
    if (sel.length) {
        if (sel[0].row != undefined) {
            row = sel[0].row;
        }
    }
    return row;
}


function strip(html)
{
    var tmp = document.createElement("DIV");
    tmp.innerHTML = html;
    return tmp.textContent||tmp.innerText;
}

// Make a callback function for the select event
var onEdit = function (event) {
    var row = getSelectedRow();
    var content = timeline_data.getValue(row, 2);
    var availability = strip(content);
    var newAvailability = prompt("Enter status\n\n" +
            "Choose from: Available, Unavailable, Maybe", availability);
    if (newAvailability != undefined) {
        var newContent = newAvailability;
        timeline_data.setValue(row, 2, newContent);
        timeline_data.setValue(row, 4, newAvailability.toLowerCase());
        timeline.draw(timeline_data);
    }
};

var onNew = function () {
    alert("Clicking this NEW button should open a popup window where " +
            "a new status event can be created.\n\n" +
            "Apperently this is not yet implemented...");
};

