import { useState,useEffect } from "react";
import { Link,useNavigate } from "react-router-dom";
import type { StatusDataType } from "../types/api";


function Status() {
    const [StatusData,setStatusData] = useState<StatusDataType | null>(null);

    const navigate = useNavigate();

    const [activeTab,setActiveTab] = useState<
        "profile" | "status" | "achievement"
        >("profile");
        
    useEffect(() => {
        async function fetchStatusData(){
            try{
                const response = await fetch("/api/status");
                if(response.status === 401){
                    navigate("/login");
                    return;
                }
                if(!response.ok){
                    throw new Error("データの取得に失敗しました");
                }
                const data: StatusDataType = await response.json();
                setStatusData(data);
            }catch(error){
                console.error(error);
            }
        }
        fetchStatusData();
    },[navigate]);

    if(!StatusData){
        return <div>Loading...</div>
    }

    const {user,exp,job,status,achievements} = StatusData;
    
    const HP = status.find(s => s.name === "HP");
    const MP = status.find(s => s.name === "MP");

    if (!HP || !MP){
        return <div>ステータスデータが不足しています</div>;
    }   

    return (
        <div className="main">
            <div className="main-inner">
                <h1>ステータス</h1>
                <div className="tab-menu">
                    <button 
                        className=
                            {`tab-button ${activeTab === "profile" ? "active" : ""}`} 
                        data-tab="profile-box"
                        onClick={() => setActiveTab("profile")}
                    >
                        <h2>プロフィール</h2>
                    </button>

                    <button 
                        className=
                            {`tab-button ${activeTab === "status" ? "active" : ""}`} 
                        data-tab="status-box"
                         onClick={() => setActiveTab("status")}
                    >
                        <h2>ステータス</h2>
                    </button>

                    <button 
                        className=
                            {`tab-button ${activeTab === "achievement" ? "active" : ""}`} 
                        data-tab="status-box"
                         onClick={() => setActiveTab("achievement")}>
                        <h2>勲章・称号</h2>
                    </button>

                    <div className="home">
                        <div className="home-inner">
                            <Link to="/">ホームへ</Link>
                        </div>
                    </div>
                </div>
                {activeTab === "profile" && (
                <div className="tab-content active" id="profile-box">
                    <div className="profile-box">
                        <div className="card-inner">
                            <div className="profile-main">
                                <div className="player-image"> 
                                    {/* <img src="player.png"> */}
                                </div>
                                <div className="user-name">
                                    <div className="NAME">NAME</div> 
                                    <div className="NAME-value">{user.name}</div> 
                                </div>
                                <div className="job-name">
                                    <div className="CLASS">CLASS</div>
                                    <div className="CLASS-value">{job.name ?? "なし"}</div>
                                </div>
                            </div>
                        
                            <div className="lv-exp-card">
                                <div className="user-level">
                                    <div className="LEVEL">Lv.<span className="LEVEL-value">{user.level}</span>
                                    </div>  
                                </div>  
                                <div className="level-up">LEVEL UP!!</div>   
                
                                <div className="exp-text">
                                    EXP <span id="current-exp">{exp.current}</span>/<span id="next-exp">{exp.next}</span>    
                                </div>
                                <div className="exp-bar">
                                    <div className="exp-fill"
                                        id="exp-fill" 
                                        data-width={exp.percent}
                                        style={{width: `${exp.percent}%` }}>
                                    </div>
                                </div>     
                            </div>

    
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
                        </div>
                    </div>
                </div>
                    )}

                {activeTab === "profile" && (
                <div className="tab-content" id="status-box">
                    <div className="status-box">
                        <div className="card-inner">
                            <div id="status-list" className="status-list">
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

                                {status.filter(s =>
                                    s.name !== "HP" &&
                                    s.name !== "MP" &&
                                    s.type === "front"
                                )
                                .map((s) => {
                                    const status_percent = Math.max(0,Math.min(s.value,100));
                                    
                                    
                                    return(
                                            <div className="status-row" key={s.id}>
                                                <div className="status-name">{s.name}</div>
                                                <div className="status-bar">
                                                    <div className="status-fill" style={{ width: `${status_percent}%`}} ></div>
                                                </div>
                                                <div>
                                                    <span className="status-value">{s.value}</span>
                                                </div>
                                            </div>    
                                    );
                                }
                                )       
                            }
                            </div>
                        </div>
                    </div>
                </div>
                )};
                
                {activeTab === "profile" && (
                <div className="tab-content" id="achievement-box">
                    <div className="achievement-box">
                        <div className="card-inner">
                            {achievements.map((achievement,index) => {

                                return(
                                    <div key={index}>
                                        <strong>{achievement.achievement_name}</strong><br />
                                        {achievement.title_name}
                                    </div>
                                )
                                })
                            }
                        </div>
                    </div>
                </div>
                )};
            </div>
        </div> 
    )
};                               
                                  
export default Status;