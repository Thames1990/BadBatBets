var choice_count = 1;

/**
 * Adds a choice field to the ChoiceBet creation form
 */
function addChoice() {
    choice_count++;
    var table = document.getElementById('choice_bet_table');
    var row = table.insertRow(table.rows.length);
    var th = document.createElement('th');
    th.innerHTML = "<label for='id_choice_" + choice_count + "'>Choice " + choice_count + ":</label>";
    row.appendChild(th);
    var td = row.insertCell(1);
    td.innerHTML =
        "<input " +
        "id='id_choice_" + choice_count + "' " +
        "maxlength='64' " +
        "name='choice_" + choice_count + "' " +
        "type='text' " +
        "required " +
        "pattern='[a-zA-Z0-9]+' " +
        "oninvalid='setCustomValidity(\"Required. Please only use letters and/or numbers.\")' " +
        "onchange='try{setCustomValidity(\"\")}catch(e){}'" +
        ">";
}
