let time=0;
let timer_id=null;
let running=false;
let elapsedseconds=0;
let starttime=0;
let endtime=0;
const timerbutton=document.getElementById("timerbutton");
const stopWatch=document.getElementById("stopwatch");
const logoutmodal=document.getElementById("logout-modal");
const modalcontent=document.getElementById("modal-content");
const cancelbtn=document.getElementById("cancel-btn");
const openlogoutmodal=document.getElementById("open-logout-modal");
const notification=document.getElementById("notification");
const expfill=document.getElementById("exp-fill");
const saveform=document.getElementById("save-form");
const currentexp=document.getElementById("current-exp")
const nextexp=document.getElementById("next-exp")
const statuslist=document.getElementById("status-list")
const todayloglist=document.getElementById("today-log-list")
const timer=document.getElementById("timer")
const statusbox=document.getElementById("status-box")

function timerButton(){
    if(running==false){
        running=true;
        starttime=Date.now();
        timerbutton.querySelector("span").textContent="STOP";
        document.getElementById("start_time").value=new Date(starttime).toISOString();
        timer_id=setInterval(() => {
            elapsedseconds=Math.floor((Date.now() - starttime)/1000)
            //変数をループの中で作り直しているだけ書き換えていないためconst可
            const h=String(Math.floor(elapsedseconds/3600)).padStart(2,"0");
            const m=String(Math.floor((elapsedseconds % 3600)/60)).padStart(2,"0");
            const s=String(elapsedseconds %60).padStart(2,"0");
            timer.textContent= `${h}:${m}:${s}`;
        },1000);
    }else{
        
    if(running==true){
        running=false;
    clearInterval(timer_id);

    
    }
    endtime=Date.now()
    document.getElementById("end_time").value=new Date(endtime).toISOString();
    document.getElementById("duration_seconds").value=elapsedseconds;

    saveByFetch();

    timerbutton.querySelector("span").textContent="START";

}
    }

cancelbtn.onclick=function(){
    modalcontent.classList.add("closing");
    modalcontent.addEventListener("animationend",function(){
    logoutmodal.style.display="none";
    modalcontent.classList.remove("closing");
    },{once:true});
}
openlogoutmodal.onclick=function(){
    logoutmodal.style.display="flex";
}

if(notification){
    setTimeout(() => {
        notification.classList.add("hide");

        setTimeout(() =>{
            notification.remove();
        },500);
    },10000);
}
// 同期
// requestAnimationFrame(() =>{
//     exp.style.width = exp.dataset.width + "%";
// });

// 非同期
async function saveByFetch(){
    try{
        const formdata = new FormData(saveform);

        const response = await fetch(saveform.getAttribute("action"), {
            method:"POST",
            body:formdata,
        
        });

        if (!response.ok){
            throw new Error("通信に失敗しました");
        }

        const oldlevel = Math.floor(Number(
            document.querySelector(".LEVEL-value").textContent
        ));

        const data = await response.json();

        if(Math.floor(data.user_level) > oldlevel){
            levelupAnimation();
        }

        currentexp.textContent=data.current_exp;
        nextexp.textContent=data.next_exp;

        expfill.style.width=data.exp_percent + "%";
        document.querySelector(".NAME-value").textContent= data.user_name;
        document.querySelector(".LEVEL-value").textContent= Math.floor(data.user_level);
        document.querySelector(".CLASS-value").textContent=data.job_name;
        
        const statusvalues=document.querySelectorAll(".status-value");
        const statusfills=document.querySelectorAll(".status-fill");

        data.user_status.slice(2).forEach((status,index) => {
            statusvalues[index].textContent=status[3]; 
            percent=status[3];
            statusfills[index].style.width=`${percent}%`;
    });

        document.querySelector("#hp-value").textContent=`${Number(data.user_hp[3])}/${Number(data.user_hp[3])}`;
        document.querySelector("#mp-value").textContent=`${Number(data.user_mp[3])}/${Number(data.user_mp[3])}`;
        

    todayloglist.innerHTML="";

    data.today_logs.forEach(log => {
        todayloglist.innerHTML += `
        <tr>
                <td>${log[2]}</td>
                <td>${log[1]}</td>
                <td>${log[4]} 秒</td>
        </tr>
        `;

    })
    timer.textContent= "00:00:00";
    elapsedseconds=0;

}catch(error){
    console.error(error);
    alert("保存に失敗しました。");
}
}
function levelupAnimation(){
    const levelup=document.getElementById("level-up")
    const userlevel=document.querySelector(".LEVEL-value")
    const animations=[
        [levelup,"levelup-effect"],
        [expfill,"expfill-effect"],
        [statusbox,"statusbox-effect"],
        [userlevel,"userlevel-effect"]
    ];
    
   animations.forEach(([element,effect]) => {
    element.classList.remove(effect);

    void element.offsetWidth;
    element.classList.add(effect);
   })


}

