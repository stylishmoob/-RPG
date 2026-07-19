import { useState,useRef,useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import "../styles/home.css";

type UserType = {
    id: number;
    name: string;
    level: string;
};

type ExpType = {
    current: string;
    next: string;
    percent: string;
};

type JobType = {
    name: string | null;
};

type StatusType = {
    id: string;
    name: string;
    value: number;
    type: string;
};

type AchievementType = {
    achievement_name: string;
    title_name: string;
};

type CategoryType = {
    id: string;
    name: string;
};

type TodayLogType = {
    category_id: string;
    category_name: string;
    start_time: string;
    end_time: string;
    duration_seconds: string;
};

type HomeDataType = {
    success: boolean;
    user: UserType;
    exp: ExpType;
    job: JobType;
    status: StatusType[];
    achievements: AchievementType[];
    categories: CategoryType[];
    today_logs: TodayLogType[];
    is_admin: boolean;
};

type savedataType = {
    category_id: string;
    start_time: string | null;
    end_time: string;
    duration_seconds: number;
};

function Home() {
    const [HomeData,setHomeData] = useState<HomeDataType | null>(null);

    const [CategoryId,setCategoryId] = useState(
        localStorage.getItem("CategoryId") ?? ""
    );
    const navigate = useNavigate();

    const categories = HomeData?.categories ?? [];

    const saveId = localStorage.getItem("CategoryId");

    const exists = categories.some(
        category => String(category.id) === saveId
    );

    const [StartTime,setStartTime] = useState<string | null>(null);   
    const [DurationSeconds,setDurationSeconds] = useState(0);
    const [IsRunning,setIsRunning] = useState(false);

    const timerIdRef = useRef<number | null>(null);
    const startTimerRef = useRef<number>(0);
    const elapsedSecondsRef = useRef<number>(0);
   
    const [isLogoutModalOpen,setIsLogoutModalOpen] = useState(false);

    useEffect(() => {
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
        fetchHomeData();
    },[navigate]);

    useEffect(() => {
        if (categories.length === 0) return;

        if (exists){
        setCategoryId(saveId!);
        }else{
        setCategoryId(String(categories[0].id));
        }
    },[categories]);

    useEffect(() => {
        localStorage.setItem("CategoryId",CategoryId);
    },[CategoryId]);

    if (!HomeData){
        return <div>Loading...</div>;
    }

    const HP = HomeData.status.find(s => s.name === "HP");
    const MP = HomeData.status.find(s => s.name === "MP");

     if (!HP || !MP){
        return <div>ステータスデータが不足しています</div>;
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

                console.log(result);
                }catch(error){
                    console.error(error);
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
    <div className="main">     
        <div className="app">
            <div className="left-column">
                <div className="card profile-box" id="profile-box">
                    <div className="card-inner">
                        <div className="card-content">
                            <h3>PROFILE</h3>
                            <div className="profile-main">
                                <div className="player-image"> 
                                    
                                </div>
                                <div id="user_name" className="user-name">
                                    <div className="NAME">NAME</div> 
                                    <div className="NAME-value">{HomeData.user.name}</div> 
                                </div>
                                <div id="job_name" className="job-name">
                                    <div className="className">CLASS</div>
                                    <div className="className-value">{HomeData.job.name ?? "なし"}</div>
                                </div>
                            </div>
                        
                            <div className="lv-exp-card">
                                <div id="user_level" className="user-level">
                                    <div className="LEVEL">Lv.<span className="LEVEL-value">{HomeData.user.level}</span>
                                    </div>  
                                </div>  
                                <div id="level-up" className="level-up">LEVEL UP!!</div>   
                    

                                <div className="exp-text">
                                    EXP <span id="current-exp">{HomeData.exp.current}</span>/<span id="next-exp">{HomeData.exp.next}</span>    
                                </div>
                                <div className="exp-bar">
                                    <div className="exp-fill"
                                        id="exp-fill" 
                                        data-width={HomeData.exp.percent} 
                                        style={{ width: `${HomeData.exp.percent}%`}}>
                                    </div>
                                </div>     
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card status-box" id="status-box">
                    <div className="card-inner">
                        <div className="card-content">
                            <div id="status-list" className="status-list">
                                <h3>STATUS</h3>
                                <div id="status-hp" className="status-hp">
                                    <span className="status-name">{HP.name}</span>
                                    <div className="hp-bar">
                                        <div className="hp-fill"></div>
                                    </div>
                                    <span id="hp-value" className="hp-value">{HP.value}/{HP.value}</span>
                                </div>
                                <div id="status-mp" className="status-mp">
                                    <span className="status-name">{MP.name}</span>
                                    <div className="mp-bar">
                                        <div className="mp-fill"></div>
                                    </div>
                                    <span id="mp-value" className="mp-value">{MP.value}/{MP.value}</span>
                                </div>

                                {HomeData.status
                                .filter(status =>
                                    status.name !== "HP" &&
                                    status.name !== "MP" 
                                )
                                .map((status) => {
                                    const status_percent = Math.max(0,Math.min(status.value,100));
                                    
                                    return(
                                        <div className="status-row" key={status.id}>
                                            <div className="status-name">{status.name}</div>
                                            <div className="status-bar">
                                                <div className="status-fill" style={{ width: `${status_percent}%`}} ></div>
                                            </div>
                                            <div>
                                                <span className="status-value">{status.value}</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="right-column">
                <div id="stopwatch" className="card stopwatch-card">
                    <div className="card-inner">
                        <div className="card-content">
                            <h3>STOP WATCH</h3>
                            <h4 >{formatTime(DurationSeconds)}</h4>      
                            <button 
                            type="button" 
                            className="btn" 
                            onClick={timerButton} 
                            disabled={categories.length===0}>
                            <span>{IsRunning ? "STOP" : "START"}</span>
                            </button>     
                            <select 
                            className="select-box"
                            value={CategoryId}
                            onChange={(e) => setCategoryId(e.target.value)}
                            required>
                            
                            {categories.map((category) =>(
                                <option key={category.id} value={category.id}>
                                    {category.name}
                                </option>
                            ))}
                            </select>        
                        </div>
                    </div>
                </div>
          
                <div className="card today-box">
                    <div className="card-inner">
                        <div className="card-content">
                            <h3>TODAY</h3>
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

                <div className="card menu-box">
                    <div className="card-inner">
                        <h3>MENU</h3>
                        <div className="menu-links">
                          <Link to="/status">ステータス詳細</Link>
                          <Link to="/category">カテゴリー設定</Link>
                          <Link to="/history">活動履歴</Link>
                        </div>
                    </div>
                </div>
              
                {HomeData.is_admin && (
                    <div className="admin">
                        <Link to="/admin">管理画面</Link>
                    </div>
                )}
              
                <button 
                    className="logout-btn"
                    onClick={() => setIsLogoutModalOpen(true)}
                >
                ログアウト
                </button>
                
                {isLogoutModalOpen && (
                    <div className="modal">
                        <div className="modal-content">
                            <h3>ログアウトしますか？</h3>

                            <div className="modal-buttons">
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
            <div id="notification" className="notification"></div>     
        </div>
    </div>
  );
}

export default Home;