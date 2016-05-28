var counter = 1;

function addChoice(choice) {
    var newchoice = document.createElement('div');
    newchoice.innerHTML = "Choice " + (counter + 1) + "<br><input type='text' name='choices'>";
    document.getElementById(choice).appendChild(newchoice);
    counter++;
}
