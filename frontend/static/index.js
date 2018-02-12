function getQuerystringVariable(variable, _default) {
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0; i<vars.length; i++) {
    var pair = vars[i].split("=");
    if(pair[0] == variable){
      return pair[1];
    }
  }
  return _default;
}

function calculateByteLength(normal_val) {
    // https://codereview.stackexchange.com/questions/37512/count-byte-length-of-string
    normal_val = String(normal_val);

    var byteLen = 0;
    for (var i = 0; i < normal_val.length; i++) {
        var c = normal_val.charCodeAt(i);
        byteLen += c < (1 <<  7) ? 1 :
                   c < (1 << 11) ? 2 :
                   c < (1 << 16) ? 3 :
                   c < (1 << 21) ? 4 :
                   c < (1 << 26) ? 5 :
                   c < (1 << 31) ? 6 : Number.NaN;
    }
    return byteLen;
}

function copyToClipbard(text) {
    // https://stackoverflow.com/questions/400212/how-do-i-copy-to-the-clipboard-in-javascript
    var textArea = document.createElement("textarea");

    textArea.style.position = 'fixed';
    textArea.style.top = 0;
    textArea.style.left = 0;
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = 0;
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    textArea.value = text;
    document.body.appendChild(textArea);

    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
}

$(window).on('load', function(){

    var currentDataTable;

    var textArea = document.getElementById('sqlarea');
    var editor = CodeMirror.fromTextArea(textArea, {
        mode: 'text/x-mssql',
        // indentWithTabs: true,
        lineNumbers: true,
    });

    var getEncodedUrl = function() {
        var query = editor.getDoc().getValue();
        if(!query){
            return;
        }
        return window.location.origin + '?sql_query=' + encodeURIComponent(query);
    }

    var sql_query = decodeURIComponent(getQuerystringVariable('sql_query', ''));
    editor.getDoc().setValue(sql_query);



    var dbSchemaBase = ' \
        <li> \
            <div class="collapsible-header"><span title="{tableName}">{tableName}</span></div> \
            <div class="collapsible-body"> \
               <ul></ul> \
            </div> \
        </li> \
    ';

    $.getJSON("/static/dbschema.min.json", function(data) {

        data['tables'].forEach(function(tableName) {

            var $dbTable = $(dbSchemaBase.replace(/{tableName}/g, tableName));

            data['rows'].forEach(function(row) {
                if(row['tableName'] == tableName){

                    var $dbColumn = $('<li></li>');

                    var $columnName = $('<span>' + row.columnName + '</span>');
                    $columnName.attr('title', row.columnName);

                    $dbColumn.append($columnName);
                    $dbColumn.append($('<span>' + row.dataType + '</span>'));
                    $dbTable.find('.collapsible-body > ul').append($dbColumn);
                }
            });

            $('.db-schema > .loader-wrapper').hide();
            $('.db-schema > .collapsible').show();
            $('.collapsible').append($dbTable);
        });
    });

    $.get('/delay', function(data) {
        var delay = data['delay_seconds'];
        if(delay > 60){
            var minutes = Math.floor(delay / 60);
            var seconds = delay - minutes * 60;
            $('#delay').text(minutes + 'm ' + seconds + 's');
        }
        else{
            $('#delay').text(delay + 's');
        }
    });

    var slider = document.getElementById('limit-rows-slider');
    var initialSliderValue = 500;
    noUiSlider.create(slider, {
        start: [initialSliderValue],
        connect: true,
        step: 1,
        orientation: 'horizontal', // 'horizontal' or 'vertical'
        range: {
            'min': 1,
            'max': 5000
        },
        format: wNumb({
            decimals: 0
       })
    });
    var $sliderValue = $('#limit-rows-value');
    $sliderValue.val(initialSliderValue);

    slider.noUiSlider.on('update', function(values, handle) {
        $sliderValue.val(values[handle]);
    });

    $('#limit-rows-value').change(function() {
        slider.noUiSlider.set($(this).val());
    });

    $('i.undo').click(function(){
        if( !$('body').hasClass('isloading')){
            editor.getDoc().undo();
        }
    });
    $('i.redo').click(function(){
        if( !$('body').hasClass('isloading')){
            editor.getDoc().redo();
        }
    });

    $('#share-query').click(function(){
        var url = getEncodedUrl();
        if (calculateByteLength(url)>=8190) {
            Materialize.toast('ERROR: Query length not supported yet.', 4000, 'red')
        }
        else if(url){
            if (url != window.location.href) {
                window.history.pushState({}, "", url);
            }
            copyToClipbard(url);
            Materialize.toast('Copied to clipboard!', 4000);
        }

    })


    $('.example-list > .card').click(function() {
        if( !$('body').hasClass('isloading')){
            // var rawSql = $(this).children('.raw-sql').text().replace('\n', '');
            var currrentDate = new Date().toJSON().slice(0,10).replace(/-/g,'/');
            
            var nextDateRaw = new Date();
            nextDateRaw.setDate(nextDateRaw.getDate() + 1);
            var nextDate = nextDateRaw.toJSON().slice(0,10).replace(/-/g,'/');
            
            var dateWeekAgoRaw = new Date();
            dateWeekAgoRaw.setDate(dateWeekAgoRaw.getDate() - 7);
            var dateWeekAgo = dateWeekAgoRaw.toJSON().slice(0,10).replace(/-/g,'/');

            var rawSql = $(this).children('.raw-sql').attr('sql');
            rawSql = rawSql.replace('${date}', currrentDate);
            rawSql = rawSql.replace('${nextDate}', nextDate);
            rawSql = rawSql.replace('${dateWeekAgo}', dateWeekAgo);
            editor.getDoc().setValue(rawSql);
        }
    });

    $('.export-btn').click(function() {

        var exportFormat = $(this).data('exportFormat');

        var ajax_data = {
            export_format: exportFormat,
            table: currentDataTable,
        }

        xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/export");
        xhttp.setRequestHeader("Content-Type", "application/json; charset=utf-8");
        // blob for binary responses
        xhttp.responseType = exportFormat == 'markdown' ? 'json' : 'blob';
        xhttp.send(JSON.stringify(ajax_data));

        xhttp.onreadystatechange = function() {
            if (xhttp.readyState === 4 && xhttp.status === 200) {
                if(exportFormat == 'markdown' && !xhttp.response['error']){
                    var markdownText = "<pre>" + xhttp.response['result'] + "</pre>";
                    var markdownWindow = window.open("about:blank", "markdown", "_blank");
                    if(markdownWindow){
                        markdownWindow.document.write(markdownText);
                    }
                }
                else{
                    // Trick for making downloadable link
                    var a;
                    a = document.createElement('a');
                    a.href = window.URL.createObjectURL(xhttp.response);
                    // Give a filename
                    a.download = "data." + exportFormat;
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                }
            }
        };

    });

    $('.run-query-btn').click(function(e) {
        e.preventDefault();
        if($('body').hasClass('isloading')){
            alert('Please wait results of the first request.');
            return;
        }

        if( !editor.getDoc().getValue()){
            return;
        }

        $('body').addClass('isloading');

        var ajax_data = {
            query: editor.getDoc().getValue(),
            limit_rows: parseInt($('#limit-rows-value').val())
        }

        $.ajax({
            url: '/api',
            type: 'POST',
            data: JSON.stringify(ajax_data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        })
            .done(function(data) {
                var headers = data['headers'];
                var rows = data['rows'];
                var executionTime = data['execution_time'];

                if(data['error']){
                    $('body').removeClass('isloading');
                    Materialize.toast('Error! ' + data['error'], 8000);
                    return;
                }
                else if( !headers.length && !rows.length){
                    $('body').removeClass('isloading');
                    Materialize.toast('No results!', 4000);
                    return;
                }

                var $header = $('<tr></tr>');
                headers.forEach(function(title_str) {
                    var $title = $('<th>' + title_str + '</th>');
                    $header.append($title);
                });
                $('table > thead').html($header);

                $('table > tbody').html('');
                rows.forEach(function(row) {
                    var $tableRow = $('<tr></tr>');

                    headers.forEach(function(title_str) {
                        var $tableCell = $('<td>' + row[title_str] + '</td>');
                        $tableRow.append($tableCell);
                    });

                    $('table > tbody').append($tableRow);
                });

                if(executionTime > 60){
                    var minutes = Math.floor(executionTime / 60);
                    var seconds = executionTime - minutes * 60;
                    $('#execution_time__value').text(minutes + 'm ' + seconds + 's');
                }
                else{
                    $('#execution_time__value').text(executionTime + 's');
                }
                $('.table__header').css('display', 'block');
                currentDataTable = data;

                $('body').removeClass('isloading');
            })
            .fail(function(data) {
                $('body').removeClass('isloading');
                Materialize.toast('Error!', 4000);
            });

    }); // run-query-btn.click()

}); // $(window).on('load')

