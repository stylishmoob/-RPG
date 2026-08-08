import { useState,useRef,useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import type { HomeDataType,savedataType } from "../types/api";

import styles from "../styles/home.module.css";

function Home() {
    const [HomeData,setHomeData] = useState<HomeDataType | null>(null);

    const [CategoryId,setCategoryId] = useState(
        localStorage.getItem("CategoryId") ?? ""
    );
    const navigate = useNavigate();

    const user_categories = HomeData?.user_categories ?? [];

    const saveId = localStorage.getItem("CategoryId");

    const exists = user_categories.some(
        category => String(category.id) === saveId
    );

    const [StartTime,setStartTime] = useState<string | null>(null);   
    const [DurationSeconds,setDurationSeconds] = useState(0);
    const [IsRunning,setIsRunning] = useState(false);
    const [SaveMessage,setSaveMessage] = useState("");

    const timerIdRef = useRef<number | null>(null);
    const startTimerRef = useRef<number>(0);
    const elapsedSecondsRef = useRef<number>(0);
   
    const [isLogoutModalOpen,setIsLogoutModalOpen] = useState(false);

    useEffect(() => {
        fetchHomeData();
    },[navigate]);

    useEffect(() => {
        if (user_categories.length === 0) return;

        if (exists){
        setCategoryId(saveId!);
        }else{
        setCategoryId(String(user_categories[0].id));
        }
    },[user_categories]);

    useEffect(() => {
        localStorage.setItem("CategoryId",CategoryId);
    },[CategoryId]);

    if (!HomeData){
        return <div>Loading...</div>;
    }

    const HP = HomeData.user_statuses.find(s => s.name === "HP");
    const MP = HomeData.user_statuses.find(s => s.name === "MP");

     if (!HP || !MP){
        return <div>ステータスデータが不足しています</div>;
    }   

    async function fetchHomeData(){
            try{
                const response = await fetch("/api/home");
                if(response.status === 401){
                    navigate("/login");
                    return;
                }
                if(!response.ok){
                    throw new Error("データの取得に失敗しました");
                }
                const data: HomeDataType = await response.json();
                setHomeData(data);
            } catch (error){
                console.error(error);
            }
        }

    async function logout() {
        try{
            const response = await fetch("/api/logout", {
                method: "POST",
            });

            if (!response.ok) {
                console.error("ログアウトに失敗しました");
                return;              
            }
        
            navigate("/login");

        }catch(error){
            console.error("通信エラー",error);
        }
    }

    function formatTime(totalSeconds:number){
        const h = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
        const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
        const s = String(totalSeconds % 60).padStart(2, "0");

        return `${h}:${m}:${s}`;
    }

    async function timerButton() {
        if(!IsRunning){

            setSaveMessage("");
            setIsRunning(true);
            const now = Date.now();

            startTimerRef.current=now; 
            setStartTime(new Date(now).toISOString());

            timerIdRef.current = window.setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTimerRef.current) / 1000);

                elapsedSecondsRef.current = elapsed;
                setDurationSeconds(elapsed);
            },1000);
        }else{
            setIsRunning(false);

            if (timerIdRef.current != null){
                clearInterval(timerIdRef.current);
                timerIdRef.current=null;
            }

            const endTime = new Date().toISOString();
            const durationseconds = elapsedSecondsRef.current;

            setDurationSeconds(durationseconds);

            try{
                const result = await saveByFetch({
                category_id: CategoryId,
                start_time: StartTime,
                end_time: endTime,
                duration_seconds: durationseconds,});

                await fetchHomeData();

                setSaveMessage("保存しました");
                console.log(result);
                }catch(error){
                    console.error(error);
                    setSaveMessage("保存に失敗しました");
                }
            

            elapsedSecondsRef.current = 0;
            setDurationSeconds(0);
        }
    }

    async function saveByFetch(data: savedataType){
            const response = await fetch("/api/save_action", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify(data),
        });
            if (!response.ok){
                throw new Error("保存に失敗しました");
            }
            const result = await response.json();
            return result;
    }
  return (
    <div className={`${styles.home}`}>
        <div className={`${styles.main}`}>     
            <div className={`${styles.app}`}>
                <div className={`${styles.leftColumn}`}>
                    <div className={`${styles.card} ${styles.profileBox}`} id="profile-box">
                        <div className={`${styles.cardInner}`}>
                            <div className={`${styles.cardContent}`}>
                                <div className={`${styles.profileMain}`}>
                                    <div className={`${styles.playerImage}`}> 
                                        
                                    </div>
                                    <div className={`${styles.userName}`}>
                                        <div className={`${styles.NAME}`}>NAME</div> 
                                        <div className={`${styles.NAMEValue}`}>
                                            {HomeData.user.name}
                                        </div> 
                                    </div>
                                    <div className={`${styles.jobName}`}>
                                        <div className={`${styles.CLASS}`}>CLASS</div>
                                        <div className={`${styles.CLASSValue}`}>{HomeData.user.current_job_name ?? "なし"}</div>
                                    </div>
                                </div>
                            
                                <div className={`${styles.lvExpCard}`}>
                                    <div className={`${styles.userLevel}`}>
                                        <div className={`${styles.LEVEL}`}>Lv.<span className={`${styles.LEVELValue}`}>{HomeData.user.level}</span>
                                        </div>  
                                    </div>  
                                    <div className={`${styles.levelUp}`}>LEVEL UP!!</div>   
                        

                                    <div className={`${styles.expText}`}>
                                        EXP <span id="current-exp">{HomeData.exp.current}</span>/<span id="next-exp">{HomeData.exp.next}</span>    
                                    </div>
                                    <div className={`${styles.expBar}`}>
                                        <div className={`${styles.expFill}`} 
                                            data-width={HomeData.exp.percent} 
                                            style={{ width: `${HomeData.exp.percent}%`}}>
                                        </div>
                                    </div>     
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className={`${styles.card} ${styles.statusBox}`} id="status-box">
                        <div className={`${styles.cardInner}`}>
                            <div className={`${styles.cardContent}`}>
                                <div id="status-list" className={`${styles.statusList}`}>
                                    <div id="status-hp" className={`${styles.statusHp}`}>
                                        <span className={`${styles.statusName}`}>{HP.name}</span>
                                        <div className={`${styles.hpBar}`}>
                                            <div className={`${styles.hpFill}`}></div>
                                        </div>
                                        <span id="hp-value" className={`${styles.hpValue}`}>{Math.floor(HP.value)}/{Math.floor(HP.value)}</span>
                                    </div>
                                    <div id="status-mp" className={`${styles.statusMp}`}>
                                        <span className={`${styles.statusName}`}>{MP.name}</span>
                                        <div className={`${styles.mpBar}`}>
                                            <div className={`${styles.mpFill}`}></div>
                                        </div>
                                        <span id="mp-value" className={`${styles.mpValue}`}>{Math.floor(MP.value)}/{Math.floor(MP.value)}</span>
                                    </div>

                                    {HomeData.user_statuses
                                    .filter(status =>
                                        status.name !== "HP" &&
                                        status.name !== "MP" 
                                    )
                                    .map((status) => {
                                        const status_percent = Math.max(0,Math.min(status.value,100));
                                        
                                        return(
                                            <div className={`${styles.statusRow}`} key={status.id}>
                                                <div className={`${styles.statusName}`}>{status.name}</div>
                                                <div className={`${styles.statusBar}`}>
                                                    <div className={`${styles.statusFill}`} style={{ width: `${status_percent}%`}} ></div>
                                                </div>
                                                <div>
                                                    <span className={`${styles.statusValue}`}>{Math.floor(status.value)}</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className={`${styles.rightColumn}`}>
                    <div id="stopwatch" className={`${styles.card} ${styles.stopwatchCard}`}>
                        <div className={`${styles.cardInner}`}>
                            <div className={`${styles.cardContent}`}>
                                <h4 >{formatTime(DurationSeconds)}</h4>      
                                <button 
                                type="button" 
                                className={`${styles.btn}`} 
                                onClick={timerButton} 
                                disabled={user_categories.length===0}>
                                <span>{IsRunning ? "STOP" : "START"}</span>
                                </button>     
                                <select 
                                aria-label="カテゴリー"
                                className={`${styles.selectBox}`}
                                value={CategoryId}
                                onChange={(e) => setCategoryId(e.target.value)}
                                required>
                                
                                {user_categories.map((category) =>(
                                    <option key={category.id} value={category.id}>
                                        {category.name}
                                    </option>
                                ))}
                                </select>        
                            </div>
                        </div>
                    </div>
            
                    <div className={`${styles.card} ${styles.todayBox}`}>
                        <div className={`${styles.cardInner}`}>
                            <div className={`${styles.cardContent}`}>
                                <table>
                                    <thead>
                                    <tr>
                                        <th>開始時刻</th>
                                        <th>カテゴリー名</th>
                                        <th>時間</th>
                                    </tr>
                                    </thead>

                                    <tbody id="today-log-list">
                                    {HomeData.today_logs.map((log,index) => (
                                    <tr key={index}>
                                    <td>{log.start_time}</td>
                                    <td>{log.category_name}</td>
                                    <td>{log.duration_seconds} 秒</td>
                                    </tr>  
                                    ))}
                                    </tbody>                          
                                </table>
                            </div>
                        </div>
                    </div>

                    <div className={`${styles.card} ${styles.menuBox}`}>
                        <div className={`${styles.cardInner}`}>
                            <div className={`${styles.menuLinks}`}>
                            <Link to="/status">ステータス詳細</Link>
                            <Link to="/category">カテゴリー設定</Link>
                            <Link to="/history">活動履歴</Link>
                            </div>
                        </div>
                    </div>
                
                    {HomeData.is_admin && (
                        <div className={`${styles.admin}`}>
                            <Link to="/admin">管理画面</Link>
                        </div>
                    )}
                
                    <button 
                        className={`${styles.logoutBtn}`}
                        onClick={() => setIsLogoutModalOpen(true)}
                    >
                    ログアウト
                    </button>
                    
                    {isLogoutModalOpen && (
                        <div className={`${styles.modal}`}>
                            <div className={`${styles.modalContent}`}>
                                <h3>ログアウトしますか？</h3>

                                <div className={`${styles.modalButtons}`}>
                                    <button onClick={logout}>
                                        はい
                                    </button>
                                    <button
                                        onClick={() => setIsLogoutModalOpen(false)}
                                    >
                                        キャンセル
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                <div
                    id="notification"
                    role="status"
                    aria-live="polite"
                    className={`${styles.notification}`}
                >
                    {SaveMessage}
                </div>
            </div>
        </div>
    </div>
  );
}

export default Home;
