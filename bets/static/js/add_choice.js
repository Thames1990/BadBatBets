var counter = 1;

function addChoice() {
    var table = document.getElementById('choice_bet_table');
    var row = table.insertRow(table.rows.length);
    var th = document.createElement('th');
    th.innerHTML = "<label>Choice " + (counter + 1) + ":</label>";
    row.appendChild(th);
    var td = row.insertCell(1)
    td.innerHTML = "<input id='id_choice_" + (counter + 1) + "' maxlength='64' name='choices' type='text'>";
    counter++;
}
