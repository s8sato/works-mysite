// document.onkeydown = keydown;

function keydown() {
    key_debug();
    select_todo();
    delete_todo();
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

function select_todo() {
    if(event.key === 'j' && active_row < todos.length){  // jで下へ移動
        active_row ++;
        todos[active_row].focus();
    }
    if(event.key === 'k' && 0 < active_row){  // kで上へ移動
        active_row --;
        todos[active_row].focus();
    }
}

function delete_todo() {
    if (event.key === 'e') {
        del_todos[active_row-1].submit();
    }
}

function on_focus(element) {
    element.style.backgroundColor="#FFCC33";
    element.style.color="#000000";
}

function on_blur(element) {
    element.style.backgroundColor="#33FFCC";
    element.style.color="#999999";
}

let
    textarea = document.getElementById('title1'),
    todos = document.getElementsByClassName('todo'),
    del_todos = document.getElementsByClassName('del_todo'),
    active_row = 0
;

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
