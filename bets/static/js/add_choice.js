var choice_count = 2;

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
        "placeholder='Use distinct and non empty descriptions.'" +
        ">";
}
