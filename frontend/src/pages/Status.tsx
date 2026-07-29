import { useState,useEffect } from "react";
import { Link,useNavigate } from "react-router-dom";
import type { StatusDataType } from "../types/api";
import styles from "../styles/status.module.css";

function Status() {
    const [StatusData,setStatusData] = useState<StatusDataType | null>(null);

    const navigate = useNavigate();

    const [currentJobId,setCurrentJobId] = useState<string>("");

    const [activeTab,setActiveTab] = useState<
        "profile" | "status" | "achievement"
        >("profile");

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
            setCurrentJobId(String(data.user.current_job_id ?? ""));
        }catch(error){
            console.error(error);
        }
    }

    useEffect(() => {
        fetchStatusData();
    },[navigate]);

    async function handleCurrentJobChange(nextJobId:string){
        setCurrentJobId(nextJobId);

        try{
            const response = await fetch("/api/status/current_job", {
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body:JSON.stringify({
                    currentJobId:nextJobId,
                }),
            });

            if(response.status === 401){
                navigate("/login");
                return;
            }

            if(!response.ok){
                throw new Error("職業の変更に失敗しました");
            }

            await fetchStatusData();
        }catch(error){
            console.error(error);
        }
    }

    if(!StatusData){
        return <div>Loading...</div>
    }

    const {user,exp,job:userJobs,status,achievements} = StatusData;
    
    const HP = status.find(s => s.name === "HP");
    const MP = status.find(s => s.name === "MP");

    if (!HP || !MP){
        return <div>ステータスデータが不足しています</div>;
    }   

    return (
        <div className={styles.main}>
            <div className={styles.mainInner}>
                <h1>ステータス</h1>
                <div className={styles.tabMenu}>
                    <button 
                        className=
                            {`${styles.tabButton} ${activeTab === "profile" ? styles.active : ""}`} 
                        data-tab="profile-box"
                        onClick={() => setActiveTab("profile")}
                    >
                        <h2>プロフィール</h2>
                    </button>

                    <button 
                        className=
                            {`${styles.tabButton} ${activeTab === "status" ? styles.active : ""}`} 
                        data-tab="status-box"
                         onClick={() => setActiveTab("status")}
                    >
                        <h2>ステータス</h2>
                    </button>

                    <button 
                        className=
                            {`${styles.tabButton} ${activeTab === "achievement" ? styles.active : ""}`} 
                        data-tab="achievement-box"
                         onClick={() => setActiveTab("achievement")}>
                        <h2>勲章・称号</h2>
                    </button>

                    <div className={styles.home}>
                        <div className={styles.homeInner}>
                            <Link to="/">ホームへ</Link>
                        </div>
                    </div>
                </div>
                {activeTab === "profile" && (
                <div className={[styles.tabContent, styles.active].join(" ")} id="profile-box">
                    <div className={styles.profileBox}>
                        <div className={styles.cardInner}>
                            <div className={styles.profileMain}>
                                <div className={styles.playerImage}> 
                                    {/* <img src="player.png"> */}
                                </div>
                                <div className={styles.userName}>
                                    <div className={styles.nameLabel}>NAME</div> 
                                    <div className={styles.nameValue}>{user.name}</div> 
                                </div>
                                <div className={styles.jobName}>
                                    <div className={styles.classLabel}>CLASS</div>
                                    <div className={styles.classValue}>{user.current_job_name}</div>
                                </div>
                            </div>
                        
                            <div className={styles.lvExpCard}>
                                <div className={styles.userLevel}>
                                    <div className={styles.levelLabel}>Lv.<span className={styles.levelValue}>{user.level}</span>
                                    </div>  
                                </div>  
                                <div className={styles.levelUp}>LEVEL UP!!</div>   
                
                                <div className={styles.expText}>
                                    EXP <span id="current-exp">{exp.current}</span>/<span id="next-exp">{exp.next}</span>    
                                </div>
                                <div className={styles.expBar}>
                                    <div className={styles.expFill}
                                        id="exp-fill" 
                                        data-width={exp.percent}
                                        style={{width: `${exp.percent}%` }}>
                                    </div>
                                </div>     
                            </div>

    
                            <div id="status-hp" className={styles.statusHp}>
                                <span className={styles.statusName}>{HP.name}</span>
                                <div className={styles.hpBar}>
                                    <div className={styles.hpFill}></div>
                                </div>
                                <span id="hp-value" className={styles.hpValue}>{HP.value}/{HP.value}</span>
                            </div>
                            <div id="status-mp" className={styles.statusMp}>
                                <span className={styles.statusName}>{MP.name}</span>
                                <div className={styles.mpBar}>
                                    <div className={styles.mpFill}></div>
                                </div>
                                <span id="mp-value" className={styles.mpValue}>{MP.value}/{MP.value}</span>
                            </div>
                        </div>
                    </div>
                </div>
                    )}

                {activeTab === "status" && (
                <div className={[styles.tabContent, styles.active].join(" ")} id="status-box">
                    <div className={styles.statusBox}>
                        <div className={styles.cardInner}>
                            <div className={styles.cardContent}>
                                <div className={styles.statusDetail}>
                                    <h3 className={styles.statusTabHeading}>ステータス詳細</h3>

                                    <div id="status-list" className={styles.statusList}>
                                        <div id="status-hp" className={styles.statusHp}>
                                            <span className={styles.statusName}>{HP.name}</span>
                                            <div className={styles.hpBar}>
                                                <div className={styles.hpFill}></div>
                                            </div>
                                            <span id="hp-value" className={styles.hpValue}>{HP.value}/{HP.value}</span>
                                        </div>
                                        <div id="status-mp" className={styles.statusMp}>
                                            <span className={styles.statusName}>{MP.name}</span>
                                            <div className={styles.mpBar}>
                                                <div className={styles.mpFill}></div>
                                            </div>
                                            <span id="mp-value" className={styles.mpValue}>{MP.value}/{MP.value}</span>
                                        </div>

                                        {status.filter(s =>
                                            s.name !== "HP" &&
                                            s.name !== "MP"
                                        )
                                        .map((s) => {
                                            const status_percent = Math.max(0,Math.min(s.value,100));

                                            return(
                                                    <div className={styles.statusRow} key={s.id}>
                                                        <div className={styles.statusName}>{s.name}</div>
                                                        <div className={styles.statusBar}>
                                                            <div className={styles.statusFill} style={{ width: `${status_percent}%`}} ></div>
                                                        </div>
                                                        <div>
                                                            <span className={styles.statusValue}>{s.value}</span>
                                                        </div>
                                                    </div>
                                            );
                                        }
                                        )
                                    }
                                    </div>
                                </div>

                                <div className={styles.jobList}>
                                    <h3 className={styles.statusTabHeading}>職業選択</h3>
                                    <select
                                        className={styles.jobSelect}
                                        value={currentJobId}
                                        onChange={(e) =>
                                            handleCurrentJobChange(e.target.value)
                                        }
                                    >
                                       {userJobs.map((job) => (
                                            <option key={job.id} value={job.id}>
                                                {job.name ?? "なし"}
                                            </option>
                                       ))}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                )}
                
                {activeTab === "achievement" && (
                <div className={[styles.tabContent, styles.active].join(" ")} id="achievement-box">
                    <div className={styles.achievementBox}>
                        <div className={styles.cardInner}>
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
                )}
            </div>
        </div> 

    )
};                               
                                  
export default Status;
