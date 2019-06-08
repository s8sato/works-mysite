// document.onkeydown = keydown;

function keydown() {
    key_debug();
    select_description();
//    delete_todo();
    click_new();
    click_all();
    click_trunk();
    click_buds();
    click_focus();
    click_breakdown();
    click_done_undone();
}

function key_debug() {
    target = document.getElementById("message");
    target.innerHTML = "キーが押されました KeyCode :" + event.keyCode;

    target = document.getElementById("messageShift");
    if (event.shiftKey === true) {
        target.innerHTML = "Shiftキーが押されました";
    }
    else {
        target.innerHTML = "";
    }

    target = document.getElementById("messageCtrl");
    if (event.ctrlKey === true) {
        target.innerHTML = "Ctrlキーが押されました";
    }
    else {
        target.innerHTML = "";
    }

    target = document.getElementById("messageAlt");
    if (event.altKey === true) {
        target.innerHTML = "Altキーが押されました";
    }
    else {
        target.innerHTML = "";
    }
}

function select_description() {
    if(event.key === 'j' && active_row < links_description.length){  // jで下へ移動
        active_row ++;
        links_description[active_row].focus();
        note = document.getElementById('note')
        note.innerHTML = notes[active_row].innerHTML
    }
    if(event.key === 'k' && 0 < active_row){  // kで上へ移動
        active_row --;
        links_description[active_row].focus();
        note = document.getElementById('note')
        note.innerHTML = notes[active_row].innerHTML
    }
}

//function delete_todo() {
//    if (event.key === 'e') {
//        del_todos[active_row-1].submit();
//    }
//}

function click_new() {
    if (event.key === 'c') {
        link_new.click();
    }
}

function click_all() {
    if (event.key === 'i') {
        link_all.click();
    }
}

function click_trunk() {
    if (event.key === 'h') {
        link_trunk.click();
    }
}

function click_buds() {
    if (event.key === 'l') {
        link_buds.click();
    }
}

function click_focus() {
    if (event.key === 'f') {
        links_focus[active_row].click();
    }
}

function click_breakdown() {
    if (event.key === 'd') {
        links_breakdown[active_row].click();
    }
}

function click_done_undone() {
    if (event.key === 'e') {
        links_done_undone[active_row].click();
    }
}

function on_focus(element) {
    element.style.backgroundColor="#ffff77";
    element.style.color="#000000";
}

function on_blur(element) {
    element.style.backgroundColor="";
    element.style.color="";
}

let
    textarea = document.getElementById('title'),
    links_description = document.getElementsByClassName('description'),
    link_new = document.getElementById('new'),
    link_all = document.getElementById('all'),
    link_trunk = document.getElementById('trunk'),
    link_buds = document.getElementById('buds'),
    links_focus = document.getElementsByClassName('focus'),
    links_breakdown = document.getElementsByClassName('breakdown'),
    links_done_undone = document.getElementsByClassName('done_undone'),
    notes = document.getElementsByClassName('note'),
    active_row = 0;

if (textarea != null){
    textarea.addEventListener('mouseover', () => {
        if (textarea.style.color === "#FFCC33"){
            textarea.style.color = "#FF33CC";
        } else {
            textarea.style.color = "#FFCC33";
        }
    }, once=false);
}

document.addEventListener('keydown', keydown);
