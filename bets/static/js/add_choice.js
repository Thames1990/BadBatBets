var counter = 1;

function addChoice() {
    counter++;
    var table = document.getElementById('choice_bet_table');
    var row = table.insertRow(table.rows.length);
    var th = document.createElement('th');
    th.innerHTML = "<label for='id_choice_" + counter + "'>Choice " + counter + ":</label>";
    row.appendChild(th);
    var td = row.insertCell(1);
    td.innerHTML = "<input id='id_choice_" + counter + "' maxlength='64' name='choice_" + counter + "' type='text'>";
}
