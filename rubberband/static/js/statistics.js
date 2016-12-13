let addButton = '<button type="button" class="btn moreFields"><span class="glyphicon glyphicon-plus"></span></button>';
let rmButton = '<button type="button" class="btn btn-warning lessFields"><span class="glyphicon glyphicon-minus"></span></button>';
let buttons = rmButton + "\n" + addButton;

prefillFields();
bindMoreFieldsClickHandler();
bindLessFieldsClickHandler();


function bindMoreFieldsClickHandler() {
    // add new filter fields, move buttons down
    $(".moreFields").click(function() {
        console.log("on click moreFields");
        // TODO: refactor to permit more than 10 filters
        var lessButton = $(".lessFields");
        if (lessButton) {
            lessButton.remove();
        }
        var step = parseInt($(".moreFields").parent().get(0).id.slice(-1)[0]) + 1;
        this.remove();
        addNewField(step);
        $(`#group${step}`).append(buttons);
        bindMoreFieldsClickHandler();
        bindLessFieldsClickHandler();
    });
}


function bindLessFieldsClickHandler() {
// remove last filter, move buttons up
    $(".lessFields").click(function() {
        console.log("called Less");
        var step = parseInt($(".lessFields").parent().get(0).id.slice(-1)[0]) - 1;
        $(".lessFields").parent().remove();
        if (step == 1) {
            $(`#group${step}`).append(addButton);
        } else {
            $(`#group${step}`).append(buttons);
        }
        bindLessFieldsClickHandler();
        bindMoreFieldsClickHandler();
    });
}


function addNewField(count) {
    var html = `<div class="row" id="group${count}">
      <input autocomplete="off" type="text" class="form-control fieldKey" name="field${count}" placeholder="Instance Feature" required>
      <select class="form-control comparator" name="comparator${count}" required>
        <option value="==">=</option>
        <option value="!=" >!=</option>
        <option value="<">&lt;</option>
        <option value="<=">&lt;=</option>
        <option value=">">&gt;</option>
        <option value=">=">&gt;=</option>
      </select>
      <input autocomplete="off" type="text" class="form-control fieldValue" name="value${count}" required>
      <select class="form-control one-or-all" name="oneorall${count}" required>
        <option value="all">For all testsets</option>
        <option value="one">For one testset</option>
      </select>
      </div>
      `
    $(".statsFormFields").append(html);
    initializeTypeahead(count);
}


function initializeTypeahead(count) {
    var testset_id = window.location.pathname.split("/")[2];
    $.get('/instances/' + testset_id, function(data){
        var test_set = Object.keys(data)[0];
        var instances = Object.keys(data[test_set]);
        var availableKeys = Object.keys(data[test_set][instances[0]]);
        $(`[name="field${count}"]`).typeahead({source:availableKeys});
    }, "json");
}


function getParts(query_string) {                                                                   
  /* utility method that parses a query string */                                                 
  var match,                                                                                  
  pl     = /\+/g,  // Regex for replacing addition symbol with a space                        
  search = /([^&=]+)=?([^&]*)/g,                                                              
  decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },                   
  query  = query_string.substring(1);                                                         
																								 
  params = {};                                                                                    
  while (match = search.exec(query))                                                              
    params[decode(match[1])] = decode(match[2]);                                                 
																								 
  return params;                                                                                  
}

function prefillFields() {
  var params = getParts(document.location.search);
  // don't need compare to build the form
  delete params["compare"];
  var numFields = Object.keys(params).length;
  if (numFields == 0) {
      $("#group1").append(addButton);
      initializeTypeahead(1);
  } else {
      $.each(params, function( key, value ) {
        if (value !== "") {
          var domElem = $(`[name="${key}"]`).get(0);
          if (!domElem) {
              addNewField(key.slice(-1)[0]);
              var domElem = $(`[name="${key}"]`).get(0)
          }
          var elemType = domElem.tagName.toLowerCase()
          if (elemType == "select") {
            $(`[name="${key}"] option[value="${value}"]`).attr("selected", "selected");
          } else if (elemType == "input") {
            domElem.value = value;
          }
        }
      });
      numFields = numFields/3;
      if (numFields == 1) {
          $("#group1").append(addButton);
      } else {
          $(`#group${numFields}`).append(buttons);
      }
  }
}
