// ------------------
// Initializations
// ------------------
var timeline = undefined;
var data = undefined;

google.load("visualization", "1");

// Set callback to run when API is loaded
google.setOnLoadCallback(drawVisualization);

$(window).resize(function(){
    $('#content').height( $(window).height() - $(".navbar").height() 
                    - parseInt($(".navbar").css("margin-bottom"))
                    - parseInt($(".navbar").css("margin-top")) 
                    - parseInt($('#content').css("margin-bottom"))
                    - parseInt($('#content').css("margin-top"))
                    );  
})
$(window).resize();

// ------------------
// gui
// ------------------

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


// ------------------
// timeline
// ------------------

// Called when the Visualization API is loaded.
function drawVisualization() {
    // Create and populate a data table.
    data = new google.visualization.DataTable();
    data.addColumn('datetime', 'start');
    data.addColumn('datetime', 'end');
    data.addColumn('string', 'content');
    data.addColumn('string', 'group');
    data.addColumn('string', 'className');

    // create some random data
    var names = ["Algie", "Barney", "Chris"];
    for (var n = 0, len = names.length; n < len; n++) {
        var name = names[n];
        var now = new Date();
        var end = new Date(now.getTime() - 12 * 60 * 60 * 1000);
        for (var i = 0; i < 5; i++) {
            var start = new Date(end.getTime() + Math.round(Math.random() * 5) * 60 * 60 * 1000);
            var end = new Date(start.getTime() + Math.round(4 + Math.random() * 5) * 60 * 60 * 1000);

            var r = Math.round(Math.random() * 2);
            var availability = (r === 0 ? "Unavailable" : (r === 1 ? "Available" : "Maybe"));
            var group = availability.toLowerCase();
            var content = availability;
            data.addRow([start, end, content, name, group]);
        }
    }

    // specify options
    var options = {
        width:  "100%",
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

    // Draw our timeline with the created data and options
    timeline.draw(data, options);

    // Set a customized visible range
    var start = new Date(now.getTime() - 4 * 60 * 60 * 1000);
    var end = new Date(now.getTime() + 8 * 60 * 60 * 1000);
    timeline.setVisibleChartRange(start, end);
}

function getRandomName() {
    var names = ["Algie", "Barney", "Grant", "Mick", "Langdon"];

    var r = Math.round(Math.random() * (names.length - 1));
    return names[r];
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
    var content = data.getValue(row, 2);
    var availability = strip(content);
    var newAvailability = prompt("Enter status\n\n" +
            "Choose from: Available, Unavailable, Maybe", availability);
    if (newAvailability != undefined) {
        var newContent = newAvailability;
        data.setValue(row, 2, newContent);
        data.setValue(row, 4, newAvailability.toLowerCase());
        timeline.draw(data);
    }
};

var onNew = function () {
    alert("Clicking this NEW button should open a popup window where " +
            "a new status event can be created.\n\n" +
            "Apperently this is not yet implemented...");
};

