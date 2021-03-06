function removeAnswer(number, component){
    var component_index = parseInt(component.id.substr(component.id.search('_'), 2).replace(/\D/g, ""));

    for (var i = component_index; i <= 10; ++i){
        if (document.getElementById(`answer${number}_${i + 1}`) != null){
            document.getElementById(`answer${number}_${i}`).value = document.getElementById(`answer${number}_${i + 1}`).value;
        }
        else{
            var parent = document.getElementById(`answers-section-${number}`);
            parent.removeChild(document.getElementById(`answer${number}_${i}l`));
            parent.removeChild(document.getElementById(`answer${number}_${i}`));
            parent.removeChild(document.getElementById(`answer${number}_${i}b`));
            parent.removeChild(document.getElementById(`answer${number}_${i}nl`));
            break;
        }
    }
    if (document.getElementById(`add_answer${number}`).hasAttribute('disabled'))
        document.getElementById(`add_answer${number}`).removeAttribute('disabled');
}

function addAnswer(number, forced){
    var flag = false;
    var last = 0;
    if (!forced){
        if (document.getElementById(`answer${number}_10`) == null){
            for (var i = 1; i <= 10; ++i){
                if (document.getElementById(`answer${number}_${i}`) != null){
                    if (document.getElementById(`answer${number}_${i}`).value.length == 0){
                        flag = true;
                        break;
                    }
                }
                else{
                    last = i - 1;
                    break;
                }
            }
        }
        else{
            flag = true;
        }
    }
    if (!flag){
        var parent = document.getElementById(`answers-section-${number}`);
        var l = document.createElement("label");
        l.id = `answer${number}_${last + 1}l`;
        l.innerHTML = `Answer${last + 1}`;
        var t = document.createElement("textarea");
        t.id = `answer${number}_${last + 1}`;
        t.name = `answer${number}_${last + 1}`;
        t.rows = 2;
        t.cols = 50;
        t.maxLength = 255;
        t.style = "resize: none;";
        var b = document.createElement("input");
        b.id = `answer${number}_${last + 1}b`;
        b.value = "delete";
        b.setAttribute("onclick", `removeAnswer(${number}, this)`);
        b.type = "button";
        var nline = document.createElement("br");
        nline.id = `answer${number}_${last + 1}nl`;
        parent.appendChild(l);
        parent.appendChild(t);
        parent.appendChild(b);
        parent.appendChild(nline);

        if (last == 9)
            document.getElementById(`add_answer${number}`).setAttribute('disabled', 'true');
    }
}

function removeQuestion(component){
    var component_index = parseInt(component.id.substr(8).replace(/\D/g, ""));

    var i = component_index;
    while (document.getElementById(`question${i + 1}`) != null){
        console.log(document.getElementById(`question${i + 1}`));
        document.getElementById(`question${i}`).value = document.getElementById(`question${i + 1}`).value;
        document.getElementById(`multichoice${i}`).checked = document.getElementById(`multichoice${i + 1}`).checked;
        var length1 = 0; var length2 = 0;
        for (var j = 1; j <= 10; ++j){
            if (document.getElementById(`answer${i}_${j}`) == null){
                length1 = j;
                break;
            }
        }
        for (var j = 1; j <= 10; ++j){
            if (document.getElementById(`answer${i + 1}_${j}`) == null){
                length2 = j;
                break;
            }
        }

        for (var j = length1; j < length2; ++j){
            addAnswer(i);
        }

        for (var j = length1; j > length2; --j){
            removeAnswer(i, document.getElementById(`answer${i}_${length2}b`));
        }

        for (var j = 1; j < length2; ++j){
            document.getElementById(`answer${i}_${j}`).value = document.getElementById(`answer${i + 1}_${j}`).value;
        }

        ++i;
    }
    var parent = document.getElementById(`questions-section`);
    parent.removeChild(document.getElementById(`question${i}l`));
    parent.removeChild(document.getElementById(`question${i}b`));
    parent.removeChild(document.getElementById(`question${i}`));
    parent.removeChild(document.getElementById(`multichoice${i}`));
    parent.removeChild(document.getElementById(`multichoice${i}l`));
    parent.removeChild(document.getElementById(`add_answer${i}`));
    parent.removeChild(document.getElementById(`answers-section-${i}`));
    parent.removeChild(document.getElementById(`nline1${i}`));
    parent.removeChild(document.getElementById(`nline2${i}`));
    parent.removeChild(document.getElementById(`pline${i}`));
}

function addQuestion(){
    var flag = false;
    var last = 0;
    if (document.getElementById(`question${i}`) == null){
        for (var i = 1; i <= 10; ++i){
            if (document.getElementById(`question${i}`) != null){
                if (document.getElementById(`question${i}`).value.length == 0){
                    flag = true;
                    break;
                }
                else{
                    for (var j = 1; j <= 10; ++j){
                        if (document.getElementById(`answer${i}_${j}`) != null){
                            if (document.getElementById(`answer${i}_${j}`).value.length == 0){
                                flag = true;
                                break;
                            }
                        }
                    }
                }
            }
            else{
                last = i - 1;
                break;
            }
        }
    }
    else{
        flag = true;
    }
    if (!flag){
        var parent = document.getElementById('questions-section');
        var l = document.createElement("label")
        l.id = `question${last + 1}l`;
        l.innerHTML = `Question${last + 1}`;
        var b = document.createElement("input");
        b.id = `question${last + 1}b`;
        b.value = "delete";
        b.setAttribute("onclick", `removeQuestion(this)`);
        b.type = "button";
        var bAns = document.createElement("input");
        bAns.id = `add_answer${last + 1}`;
        bAns.value = "Add answer";
        bAns.setAttribute("onclick", `addAnswer(${last + 1}, false)`);
        bAns.type = "button";
        var name = document.createElement("textarea");
        name.id = `question${last + 1}`;
        name.name = `question${last + 1}`;
        name.rows = 1;
        name.cols = 50;
        name.maxLength = 255;
        name.style = "resize: none;";

        var choice = document.createElement("input");
        choice.id = `multichoice${last + 1}`;
        choice.type = 'checkbox';
        var choiceL = document.createElement("label");
        choiceL.id = `multichoice${last + 1}l`;
        choiceL.innerHTML = `Enable multichoice`;

        var nline1 = document.createElement("br");
        nline1.id = `nline1${last + 1}`;
        var nline2 = document.createElement("br");
        nline2.id = `nline2${last + 1}`;
        var pline = document.createElement("p");
        pline.id = `pline${last + 1}`;

        var s = document.createElement('section');
        s.id = `answers-section-${last + 1}`;
        parent.appendChild(l);
        parent.appendChild(name);
        parent.appendChild(b);
        parent.appendChild(nline1);
        parent.appendChild(choiceL);
        parent.appendChild(choice);
        parent.appendChild(nline2);
        parent.appendChild(s);
        parent.appendChild(bAns);
        parent.appendChild(pline);
    }
}

function update_messages(messages){
    $("#div_messages").html("");
    $.each(messages, function (i, m) {
                    $("#div_messages").append("<div class='alert alert-"+m.level+"''>"+m.message+"</div>");
                });
            }